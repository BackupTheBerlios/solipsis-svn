# pylint: disable-msg=W0131,C0103
# Missing docstring, Invalid name
"""client server module for file sharing"""

__revision__ = "$Id: network.py 902 2005-10-14 16:18:06Z emb $"

import os, os.path
import sys
import pickle
import datetime
import threading
import gettext
_ = gettext.gettext

from Queue import Queue, Empty
from twisted.protocols import basic
from twisted.internet import defer

from solipsis.services.profile import VERSION, UNIVERSAL_SEP
from solipsis.services.profile.tools.prefs import get_prefs
from solipsis.services.profile.tools.files import ContainerException
from solipsis.services.profile.tools.message import display_status, display_error
from solipsis.services.profile.editor.document import read_document
from solipsis.services.profile.editor.facade import get_facade
from solipsis.services.profile.filter.facade import get_filter_facade
from solipsis.services.profile.network.messages import SecurityAlert, \
     DownloadMessage, Message, MESSAGE_HELLO, MESSAGE_ERROR, \
     MESSAGE_PROFILE, MESSAGE_BLOG, MESSAGE_SHARED, MESSAGE_FILES
          
def format_data_file(split_path, size=0):
    new_path = UNIVERSAL_SEP.join(split_path)
    return "%s,%s"% (size, new_path)
            
def extract_data_file(description):
    size, file_path = description.split(',', 1)
    new_path = file_path.split(UNIVERSAL_SEP)
    return (new_path, size)
    
# server #############################################################
class PeerServer(object):
    """trace messages received for this peer"""

    def __init__(self, peer):
        self.peer = peer
        self.protocol = None
        # states
        self.new_state = PeerState(self)
        self.registered_state = PeerRegistered(self)
        self.connected_state = PeerConnected(self)
        self.disconnected_state = PeerDisconnected(self)
        self.current_state = self.new_state

    def connected(self, protocol):
        self.current_state.connected(protocol)
        
    def disconnected(self):
        self.current_state.disconnected()
        
    def execute(self, message):
        self.current_state.execute(message)
    
class PeerState(object):
    """trace messages received for this peer"""

    def __init__(self, peer_server):
        self.peer_server = peer_server
        
    def connected(self, protocol):
        raise SecurityAlert(self.peer_server.peer.peer_id,
                            "Connection impossible in state %s"%
                            self.__class__.__name__)
    def disconnected(self):
        raise SecurityAlert(self.peer_server.peer.peer_id,
                            "Disconnection impossible in state %s"%
                            self.__class__.__name__)
    def execute(self, message):
        raise SecurityAlert(self.peer_server.peer.peer_id,
                            "Action impossible in state %s"%
                            self.__class__.__name__)
    
class PeerRegistered(PeerState):
    """trace messages received for this peer"""

    def connected(self, protocol):
        self.peer_server.protocol = protocol
        self.peer_server.current_state = self.peer_server.connected_state

    def disconnected(self):
        self.peer_server.current_state = self.peer_server.disconnected_state

class PeerDisconnected(PeerState):
    """trace messages received for this peer"""

    def connected(self, protocol):
        self.peer_server.protocol = protocol
        self.peer_server.current_state = self.peer_server.connected_state

    def disconnected(self):
        pass
    
class PeerConnected(PeerState):
    """trace messages received for this peer"""

    def connected(self, protocol):
        self.peer_server.protocol = protocol

    def disconnected(self):
        self.peer_server.protocol = None
        self.peer_server.current_state = self.peer_server.disconnected_state

    def execute(self, message):
        transport = self.peer_server.protocol.transport
        if message.command in [MESSAGE_HELLO, MESSAGE_PROFILE]:
            file_obj = get_facade()._desc.document.to_stream()
            deferred = basic.FileSender().\
                       beginFileTransfer(file_obj, transport)
            deferred.addCallback(lambda x: transport.loseConnection())
        elif message.command == MESSAGE_BLOG:
            blog_stream = get_facade().get_blog_file()
            deferred = basic.FileSender().\
                       beginFileTransfer(blog_stream, transport)
            deferred.addCallback(lambda x: transport.loseConnection())
        elif message.command == MESSAGE_SHARED:
            files_stream = get_facade().get_shared_files()
            deferred = basic.FileSender().beginFileTransfer(files_stream,
                                                            transport)
            deferred.addCallback(lambda x: transport.loseConnection())
        elif message.command == MESSAGE_FILES:
            split_path, file_size = extract_data_file(message.data)
            file_name = os.sep.join(split_path)
            try:
                file_desc = get_facade().get_file_container(file_name)
                 # check shared
                if file_desc._shared:
                    display_status("sending %s"% file_name)
                    deferred = basic.FileSender().\
                               beginFileTransfer(open(file_name, "rb"), transport)
                    deferred.addCallback(lambda x: transport.loseConnection())
                else:
                    self.peer_server.protocol.factory.send_udp_message(
                        self.peer_server.peer.peer_id, MESSAGE_ERROR, message.data)
                    SecurityAlert(self.peer_server.peer.peer_id,
                                  "Trying to download unshare file %s"\
                                  % file_name)
            except ContainerException:
                SecurityAlert(self.peer_server.peer.peer_id,
                              "Trying to download unvalid file %s"\
                              % file_name)
        else:
            raise ValueError("ERROR in _connect: %s not valid"% message.command)
          
# client #############################################################
class PeerClient(dict):
    """dictionary of all dowloads: {id(transport): }"""
    
    def __init__(self, peer, connect_method):
        dict.__init__(self)
        self.peer = peer
        self.connect = connect_method
        self.download_dlg = None
        # [ [split path], size]
        self.files = []
        self.files_deferred = None

    def __setitem__(self, transport, download_msg):
        dict.__setitem__(self, id(transport), download_msg)

    def __getitem__(self, transport):
        try:
            return dict.__getitem__(self, id(transport))
        except KeyError:
            raise SecurityAlert(transport.getPeer().host,
                                _("Corrupted client"))
            
        
    # high level API #
    def auto_load(self):
        """download profile when meeting peer for the first time"""
        return self._connect(MESSAGE_HELLO)
    
    def get_profile(self):
        """download peer profile using self.get_file. Automatically
        called on client creation"""
        if self.peer.server.current_state == self.peer.server.new_state:
            SecurityAlert(self.peer.peer_id,
                          "Can't get profile: peer's server not known yet")
        else:
            return self._connect(MESSAGE_PROFILE)
            
    def get_blog_file(self):
        """donload blog file using self.get_file"""
        if self.peer.server.current_state == self.peer.server.new_state:
            SecurityAlert(self.peer.peer_id,
                          "Can't get blog: peer's server not known yet")
        else:
            return self._connect(MESSAGE_BLOG)
            
    def get_shared_files(self):
        """donload blog file using self.get_file"""
        if self.peer.server.current_state == self.peer.server.new_state:
            SecurityAlert(self.peer.peer_id,
                          "Can't get list: peer's server not known yet")
        else:
            return self._connect(MESSAGE_SHARED)
            
    def get_files(self, file_descriptors):
        """download given list of file

        file_descriptor is a list: [ [split path], size ]"""
        if self.peer.server.current_state == self.peer.server.new_state:
            SecurityAlert(self.peer.peer_id,
                          "Can't get files: peer's server not known yet")
        else:
            # display downlaod dialog if necessary
            if get_prefs("display_dl") \
                   and "wx" in sys.modules:
                from solipsis.util.uiproxy import UIProxy
                from solipsis.services.profile.gui.DownloadDialog \
                     import DownloadDialog
                self.download_dlg = UIProxy(DownloadDialog(
                    get_prefs("display_dl"), None, -1))
                self.download_dlg.init()
                self.download_dlg.Show()
            # launch first download
            self.files = file_descriptors
            if self.files:
                split_path, size = self.files.pop()
                self.update_file(split_path[-1], size)
                self._connect(MESSAGE_FILES,
                                     format_data_file(split_path, size))
                # create deferred to be called when all files downloaded
                deferred = defer.Deferred()
                self.files_deferred = deferred
                return self.files_deferred
            else:
                display_warning(_("Empty List"),
                                _("No file selected to download"))

    # connection management #
    def _connect(self, command, data=None):
        # set download information
        message = self.peer.wrap_message(command, data)
        connector =  self.connect(self.peer)
        deferred = defer.Deferred()
        download = DownloadMessage(connector.transport,
                                   deferred,
                                   message)
        self[connector.transport] = download
        # set callback
        if command == MESSAGE_HELLO:
            deferred.addCallback(self._on_hello)
        elif command == MESSAGE_PROFILE:
            deferred.addCallback(self._on_complete_profile)
        elif command == MESSAGE_BLOG:
            deferred.addCallback(self._on_complete_pickle)
        elif command == MESSAGE_SHARED:
            deferred.addCallback(self._on_complete_pickle)
        elif command == MESSAGE_FILES:
            deferred.addCallback(self._on_complete_file)
        else:
            raise ValueError("ERROR in _connect: %s not valid"% command)
        return deferred
    
    def rawDataReceived(self, transport, data):
        self[transport].write_data(data)
        self.update_download(self[transport].size)
        
    def _fail_client(self, transport, reason):
        display_warning("Action [%s] failed: %s"\
                        % (str(self[transport].message), reason))
        self[transport].close(reason)

    def _on_connected(self, transport):
        self[transport].send_message()
        self[transport].setup_download()

    def _on_disconnected(self, transport, reason):
        self[transport].teardown_download()
        self[transport].close(reason)

    # callbacks #
    def _on_hello(self, donwload_msg):
        """callback when autoloading of profile successful"""
        document = read_document(donwload_msg.file)
        get_facade().set_data(self.peer.peer_id, document, flag_update=False)
        get_filter_facade().fill_data(self.peer.peer_id, document)
        
    def _on_complete_profile(self, donwload_msg):
        """callback when finished downloading profile"""
        return read_document(donwload_msg.file)

    def _on_complete_pickle(self, donwload_msg):
        """callback when finished downloading blog"""
        try:
            return pickle.load(donwload_msg.file)
        except Exception, err:
            display_error(_("Your version of Solipsis is not compatible "
                            "with the peer'sone you wish to download from "
                            "Make sure you both use the latest (%s)"\
                            % VERSION),
                          title="Download error", error=err)

    def _on_complete_file(self, donwload_msg):
        """callback when finished downloading file"""
        # write downloaded file
        split_path = extract_data_file(donwload_msg.message.data)[0]
        download_path = os.path.join(get_prefs("download_repo"),
                                     split_path[-1])
        download_file = open(download_path, "wb")
        download_file.write(donwload_msg.file.read())
        download_file.close()
        # download next
        if self.files:
            split_path, size = self.files.pop()
            self.update_file(split_path[-1], size)
            self._connect(MESSAGE_FILES,
                          format_data_file(split_path, size))
        else:
            self.complete_all_files()
            
    # dialog processus ###############################################
    def update_download(self, size):
        """available to wx navigators only. update status of download
        in specific dialog"""
        if self.download_dlg:
            self.download_dlg.update_download(size)
        #else do not print: too much

    def update_file(self, file_name, size):
        """available to wx navigators only. update downloaded file in
        specific dialog"""
        if self.download_dlg:
            self.download_dlg.update_file(file_name, size)
        else:
            display_status("downloading %s (%d)"% (file_name, size))

    def complete_all_files(self):
        self.files_deferred.callback("callback complete all")
        if self.download_dlg:
            self.download_dlg.complete_all_files()
            self.download_dlg = None
        else:
            display_status("All files downloaded")
        
# wrapper of server & client #########################################
class Peer(object):
    """contain 'static' information about a peer: its is, ip, port..."""
    
    PEER_TIMEOUT = 120

    def __init__(self, peer_id, connect_method):
        self.peer_id = peer_id
        self.lost = None
        # protocols
        self.client = PeerClient(self, connect_method)
        self.server = PeerServer(self)
        # vars set UDP message
        self.ip = None
        self.port = None

    def lose(self):
        self.lost = datetime.datetime.now() \
                    + datetime.timedelta(seconds=self.PEER_TIMEOUT)

    def wrap_message(self, command, data=None):
        message = Message(command)
        message.ip = self.ip
        message.port = self.port
        message.data = data
        return message

# manager ############################################################
class PeerManager(threading.Thread):
    """manage known ips (along with their ids) and timeouts"""

    CHECKING_FREQUENCY = 5

    def __init__(self, connect_method):
        """connect method expects a peer and is implemented in
        PeerClientFactory in our case"""
        threading.Thread.__init__(self)
        self.queue = Queue(-1) # infinite size
        self.remote_ips = {}   # {ip : peer}
        self.remote_ids = {}   # {id : peer}
        self.connect_method = connect_method
        self.lock = threading.RLock()

    def run(self):
        while True:
            try:
                # block until new message or TIMEOUT
                message = self.queue.get(timeout=self.CHECKING_FREQUENCY)
                if message is None:
                    break
                else:
                    if message.ip in self.remote_ips:
                        self.remote_ips[message.ip].server.execute(message)
                    else:
                        SecurityAlert(message.ip,
                                      _("Message '%s' out of date."\
                                        % str(message)))
                    self._check_peers(datetime.datetime.now())
            except Empty:
                # Empty exception is expected when no message received
                # during period defined by CHECKING_FREQUENCY.
                self._check_peers(datetime.datetime.now())
        display_status("stopping server")

    def stop(self):
        self.queue.put(None)

    def assert_ip(self, remote_ip):
        if self.remote_ips.has_key(remote_ip):
            return True
        else:
            SecurityAlert(remote_ip, "Host has not registered")
            return False
        
    def assert_id(self, peer_id):
        if self.remote_ids.has_key(peer_id):
            return True
        else:
            SecurityAlert(peer_id, "Peer has not registered")
            return False

    def add_peer(self, peer_id):
        try:
            self.lock.acquire()
            peer = Peer(peer_id, self.connect_method)
            self.remote_ids[peer_id] = peer
        finally:
            self.lock.release()

    def set_peer(self, peer_id, message):
        try:
            self.lock.acquire()
            peer = self.remote_ids[peer_id]
            self.remote_ips[message.ip] = peer
            peer.ip = message.ip
            peer.port = message.port
            peer.server.current_state =  peer.server.registered_state
        finally:
            self.lock.release()

    def add_message(self, message):
        """Synchronized method called either from peer_manager thread
        or network thread"""
        try:
            self.lock.acquire()
            # put in queue after checking ip up
            if not self.remote_ips.has_key(message.ip):
                SecurityAlert(message.ip,
                              _("Incomming '%s' from unknown host"\
                                % str(message)))
            else:
                self.queue.put(message)
        finally:
            self.lock.release()

    def _check_peers(self, now):
        """Synchronized method to clean up dict of peers, always
        called from peer_manager thread."""
        try:
            self.lock.acquire()
            for peer_id, peer in self.remote_ids.items():
                if peer.lost and peer.lost < now:
                    self._del_peer(peer_id)
        finally:
            self.lock.release()

    def _del_peer(self, peer_id):
        """Synchronized method called either from peer_manager thread
        or network thread"""
        try:
            self.lock.acquire()
            if peer_id in self.remote_ids:
                if self.remote_ids[peer_id].ip in self.remote_ips:
                    del self.remote_ips[self.remote_ids[peer_id].ip]
                del self.remote_ids[peer_id]
        finally:
            self.lock.release()
