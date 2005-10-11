# pylint: disable-msg=C0103
#
"""client server module for file sharing"""

import datetime
import threading
import pickle
import gettext
_ = gettext.gettext

from Queue import Queue, Empty
from twisted.internet import defer

from solipsis import VERSION
from solipsis.util.network import parse_address
from solipsis.services.profile.message import display_warning

# messages
MESSAGE_HELLO = "HELLO"
MESSAGE_ERROR = "ERROR"
MESSAGE_PROFILE = "REQUEST_PROFILE"
MESSAGE_BLOG = "REQUEST_BLOG"
MESSAGE_SHARED = "REQUEST_SHARED"
MESSAGE_FILES = "REQUEST_FILES"

SERVICES_MESSAGES = [MESSAGE_HELLO, MESSAGE_ERROR, MESSAGE_PROFILE,
                     MESSAGE_BLOG, MESSAGE_SHARED, MESSAGE_FILES]

class SecurityException(Exception):
    pass

class Message(object):
    """Simple wrapper for a communication message"""

    def __init__(self, command):
        if command not in SERVICES_MESSAGES:
            raise ValueError("%s should be in %s"% (command, SERVICES_MESSAGES))
        self.command = command
        self.ip = None
        self.port = None
        self.data = None
        # creation_time is used as reference when cleaning
        self.creation_time = datetime.datetime.now()

    def __str__(self):
        return " ".join([self.command,
                         "%s:%d"% (self.ip or "?",
                                   self.port or -1),
                         self.data or ''])

    def create_message(message):
        """extract command, address and data from message.
        
        Expected format: MESSAGE host:port data
        returns Message instance"""
        # 2 maximum splits: data may contain spaces
        items = message.split(' ', 2)
        if not len(items) >= 2:
            raise ValueError("%s should define host's ip and port"% command)
        message = Message(items[0])
        message.ip, port = parse_address(items[1])
        message.port = int(port)
        # check data
        if len(items) > 2:
            message.data = items[2]
        return message
    create_message = staticmethod(create_message)

class PeerState(object):
    """trace messages received for this peer"""
    
    PEER_TIMEOUT = 120

    def __init__(self, peer_id):
        self.peer_id = peer_id
        self.ip = None
        self.lost = None

    def lose(self):
        self.lost = datetime.datetime.now() \
                    + datetime.timedelta(seconds=self.PEER_TIMEOUT)

    def connected(self):
        pass

    def received_data(self, data):
        pass

    def disconnected(self):
        pass

    def execute(self, manager, message):
        pass

class PeerManager(threading.Thread):
    """manage known ips (along with their ids) and timeouts"""

    CHECKING_FREQUENCY = 5

    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = Queue(-1) # infinite size
        self.remote_ips = {}   # {ip : peer}
        self.remote_ids = {}   # {id : peer}
        self.running = True
        self.lock = threading.RLock()

    def run(self):
        while self.running:
            try:
                # block until new message or TIMEOUT
                message = self.queue.get(timeout=self.CHECKING_FREQUENCY)
                if message is None:
                    self.running = False
                else:
                    self.remote_ips[message.ip].execute(self, message)
                    self._check_peers(datetime.datetime.now())
            except Empty:
                # Empty exception is expected when no message received
                # during period defined by CHECKING_FREQUENCY.
                self._check_peers(datetime.datetime.now())

    def stop(self):
        self.queue.put(None)

    def get_ip(self, peer_id):
        return self.remote_ids[peer_id].ip

    def add_peer(self, peer_id, peer_ip):
        try:
            self.lock.acquire()
            peer_state = PeerState(peer_id, peer_ip)
            self.remote_ids[peer_id] = peer_state
            self.remote_ips[peer_ip] = peer_state
        finally:
            self.lock.release()

    def add_message(self, peer_state, message):
        """Synchronized method called either from peer_manager thread
        or network thread"""
        try:
            self.lock.acquire()
            # check ip
            if message.ip !=  peer_state.ip:
                raise SecurityException(
                    "two ip (msg=%s, cache=%s) for same peer (%s)"\
                    (message.ip,  self.remote_ids[peer_id], peer_id))
            # put message in queue
            self.queue.put(message)
        finally:
            self.lock.release()

    def _check_peers(self, now):
        """Synchronized method to clean up dict of peers, always
        called from peer_manager thread."""
        try:
            self.lock.acquire()
            for peer_id, peer_state in self.remote_ids.items():
                if peer_state.lost and peer_state.lost < now:
                    self._del_peer(peer_id)
        finally:
            self.lock.release()

    def _del_peer(self, peer_id):
        """Synchronized method called either from peer_manager thread
        or network thread"""
        try:
            self.lock.acquire()
            del self.remote_ips[self.remote_ids[peer_id].ip]
            del self.remote_ids[peer_id]
        finally:
            self.lock.release()

class NetworkManager:
    """high level class managing clients and servers for each peer"""

    def __init__(self, download_dlg=None):
        from solipsis.services.profile.protocols import \
             ProfileClientFactory, ProfileServerFactory
        self.download_dlg = download_dlg
        self.client = ProfileClientFactory(self)
        self.server = ProfileServerFactory(self)
        self.peers = PeerManager()

    # calls from plugin ##############################################
    def on_new_peer(self, peer):
        """tries to connect to new peer"""
        from solipsis.services.profile.plugin import Plugin
        # declare known port to other peer throug service_api
        message = server.wrap_message(MESSAGE_HELLO)
        Plugin.service_api.SendData(peer.id_, str(message))

    def on_change_peer(self, peer, service):
        """tries to connect to new peer"""
        if self.peers.remote_ids.has_key(peer.id_):
            self.peers.remote_ids[peer.id_].lose()
        self.on_new_peer(peer)

    def on_lost_peer(self, peer_id):
        """tries to connect to new peer"""
        if self.peers.remote_ids.has_key(peer_id):
            self.peers.remote_ids[peer_id].lose()

    def on_service_data(self, peer_id, message):
        """demand to establish connection from peer that failed to
        connect through TCP"""
        message = Message.create_message(message)
        self.peers.add_message(peer_id, message)

    # dialog processus ###############################################
    def update_download(self, size):
        """available to wx navigators only. update status of download
        in specific dialog"""
        if self.download_dlg:
            self.download_dlg.update_download(size)

    def update_file(self, file_name, size):
        """available to wx navigators only. update downloaded file in
        specific dialog"""
        if self.download_dlg:
            self.download_dlg.update_file(file_name, size)

    # high level functions
    def assert_peer(self, peer_id):
        if self.peers.remote_ids.has_key(peer_id):
            return True
        else:
            display_warning(_("Your request on peer %s could not be granted "
                              "since no connection is available %s "% peer_id),
                            title=_("Download impossible"))
            return False
        
    def get_profile(self, peer_id):
        """retreive peer's profile"""
        if self.assert_peer(peer_id):
            peer_state = self.peers.remote_ids[peer_id]
            return self.client.get_profile(self.peers.remote_ids[peer_id])
        #else: return None

    def get_blog_file(self, peer_id):
        """retreive peer's blog"""
        if self.assert_peer(peer_id):
            peer_state = self.peers.remote_ids[peer_id]
            return self.client.get_blog(peer_state)
        #else: return None

    def get_shared_files(self, peer_id):
        """retreive peer's shared list"""
        if self.assert_peer(peer_id):
            peer_state = self.peers.remote_ids[peer_id]
            return self.client.get_shared_files(peer_state)
        #else: return None

    def get_files(self, peer_id, file_descriptors, _on_all_files):
        """retreive file"""
        self._on_all_files = _on_all_files
        if self.assert_peer(peer_id):
            peer_state = self.peers.remote_ids[peer_id]
            return self.client.get_files(peer_state, file_descriptors,)
        #else: return None

# custom deferred ####################################################
class DeferredUpload(defer.Deferred):
    """Deferred (from twisted.internet.defer) with information about
    its status"""

    def __init__(self, peer_id, message, manager, split_path=None, size=0):
        defer.Deferred.__init__(self)
        self.message = message
        self.peer_id = peer_id
        self.split_path = split_path
        self.manager = manager
        self.size = size
        self.file = None
        self.set_callbacks()

    def get_message(self):
        """format message to send to client according to file to be
        uploaded"""
        if self.message == MESSAGE_PROFILE:
            self.file = tempfile.NamedTemporaryFile()
            message = ASK_UPLOAD_PROFILE
        elif self.message == MESSAGE_BLOG:
            self.file = StringIO()
            message = ASK_UPLOAD_BLOG
        elif self.message == MESSAGE_SHARED:
            self.file = StringIO()
            message = ASK_UPLOAD_SHARED
        elif self.message == MESSAGE_FILES:
            # TODO: check place where to download and non overwriting
            down_path = os.path.abspath(os.path.join(
                get_prefs("download_repo"),
                self.split_path[-1]))
            self.file = open(down_path, "w+b")
            self.manager.update_file(self.split_path, self.size)
            message = "%s %s"% (ASK_UPLOAD_FILES,
                                UNIVERSAL_SEP.join(self.split_path))
        else:
            print "%s not valid"% self.message
            message = MESSAGE_ERROR
        return message

    def set_callbacks(self):
        """add first callbacks"""
        self.addCallback(self._first_callback)
        if self.message == MESSAGE_PROFILE:
            self.addCallback(self._on_complete_profile)
        elif self.message == MESSAGE_BLOG:
            self.addCallback(self._on_complete_pickle)
        elif self.message == MESSAGE_SHARED:
            self.addCallback(self._on_complete_pickle)
        elif self.message == MESSAGE_FILES:
            # callback added by factory
            pass
        else:
            print "%s not valid"% self.message
        self.addErrback(self._on_error)

    def close(self):
        """close file, clean upload"""
        if self.file:
            self.file.close()
            self.file = None

    def _first_callback(self, reason):
        """call user's callback with proper file"""
        if self.file:
            self.file.seek(0)
            return self.file

    def _on_error(self, err):
        """callback on exception"""
        print "ERROR:", err
        import traceback
        traceback.print_exc()

    # FIXME factorize with server
    def _on_complete_profile(self, file_obj):
        """callback when finished downloading profile"""
        return read_document(file_obj)

    # FIXME factorize with server
    def _on_complete_pickle(self, file_obj):
        """callback when finished downloading blog"""
        obj_str = file_obj.getvalue()
        if len(obj_str):
            return pickle.loads(obj_str)
        else:
            print "no file"    

    # FIXME factorize with server
    def _on_complete_file(self, file_obj):
        """callback when finished downloading file"""
        # flag this one
        return file_obj
    
