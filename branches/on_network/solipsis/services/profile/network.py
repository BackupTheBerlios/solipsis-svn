# pylint: disable-msg=W0131
# Missing docstring
"""client server module for file sharing"""

__revision__ = "$Id$"

import datetime
import threading
import tempfile
import gettext
_ = gettext.gettext

from Queue import Queue, Empty

from solipsis.util.network import parse_address
from solipsis.services.profile.message import display_warning, display_status


class SecurityAlert(Exception):

    def __init__(self, key, *args, **kwargs):
        Exception. __init__(self, *args, **kwargs)
        SecurityWarnings.instance()[key] = self
        SecurityWarnings.instance().display(key)

class SecurityWarnings(dict):

    _instance = None
    def instance(cls, *args, **kwargs):
        """Mise en oeuvre du pattern singleton"""
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance
    instance = classmethod(instance)
        
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __setitem__(self, key, value):
        if key in self:
            self[key].append(value)
        else:
            dict.__setitem__(self, key, [value])

    def count(self, key):
        if key in self:
            return len(self[key])
        else:
            return 0

    def display(self, key):
        if key in self:
            nb_tries = self.count(key)
            if nb_tries > 1:
                display_status(_("%d retries of potential hacker '%s'"\
                                 % (nb_tries, key)))
            elif nb_tries == 1:
                display_warning(_("'%s' has not registered properly: %s"\
                                  % (key, str(self[key][0]))),
                                title="Security Warning")
        #else no warning...

# Messages ###########################################################
MESSAGE_HELLO = "HELLO"
MESSAGE_ERROR = "ERROR"
MESSAGE_PROFILE = "REQUEST_PROFILE"
MESSAGE_BLOG = "REQUEST_BLOG"
MESSAGE_SHARED = "REQUEST_SHARED"
MESSAGE_FILES = "REQUEST_FILES"

SERVICES_MESSAGES = [MESSAGE_HELLO, MESSAGE_ERROR, MESSAGE_PROFILE,
                     MESSAGE_BLOG, MESSAGE_SHARED, MESSAGE_FILES]

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
            raise ValueError("%s should define command & host's address"\
                             % message)
        message = Message(items[0])
        message.ip, port = parse_address(items[1])
        message.port = int(port)
        # check data
        if len(items) > 2:
            message.data = items[2]
        return message
    create_message = staticmethod(create_message)

class DownloadMessage(object):
    """Simple wrapper to link connection, message sent and deferred to
    be called when download complete"""

    def __init__(self, transport, deferred, message):
        self.transport = transport
        self.deferred = deferred
        self.message = message
        self.file = None
        self.size = 0

    def send_message(self):
        self.transport.write(str(self.message)+"\r\n")

    # TODO: check place where to download and non overwriting
    def setup_download(self):
        self.file = tempfile.NamedTemporaryFile()
        self.size = 0
        pass

    def write_data(self, data):
        pass

    def teardown_download(self):
        pass

    def close(self, reason=None):
        pass
            
# peers ##############################################################
class Peer(object):
    """contain 'static' information about a peer: its is, ip, port..."""
    
    PEER_TIMEOUT = 120

    def __init__(self, peer_id, connect_method):
        self.peer_id = peer_id
        self.lost = None
        # protocols
        from solipsis.services.profile.client_protocol import PeerClient
        from solipsis.services.profile.server_protocol import PeerServer
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

class PeerManager(threading.Thread):
    """manage known ips (along with their ids) and timeouts"""

    CHECKING_FREQUENCY = 5

    def __init__(self, connect_method):
        threading.Thread.__init__(self)
        self.queue = Queue(-1) # infinite size
        self.remote_ips = {}   # {ip : peer}
        self.remote_ids = {}   # {id : peer}
        self.running = True
        self.connect_method = connect_method
        self.lock = threading.RLock()

    def run(self):
        while self.running:
            try:
                # block until new message or TIMEOUT
                message = self.queue.get(timeout=self.CHECKING_FREQUENCY)
                if message is None:
                    self.running = False
                else:
                    if message.ip in self.remote_ips:
                        self.remote_ips[message.ip].execute(self, message)
                    else:
                        SecurityAlert(message.ip,
                                      _("Message '%s' out of date."\
                                        % str(message)))
                    self._check_peers(datetime.datetime.now())
            except Empty:
                # Empty exception is expected when no message received
                # during period defined by CHECKING_FREQUENCY.
                self._check_peers(datetime.datetime.now())

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
            peer.server.current_sate =  peer.server.registered_state
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
            del self.remote_ips[self.remote_ids[peer_id].ip]
            del self.remote_ids[peer_id]
        finally:
            self.lock.release()

# network interface ##################################################
class NetworkManager:
    """high level class managing clients and servers for each peer"""

    def __init__(self, download_dlg=None):
        from solipsis.services.profile.client_protocol \
             import ProfileClientFactory
        from solipsis.services.profile.server_protocol \
             import ProfileServerFactory
        self.client = ProfileClientFactory(self)
        self.server = ProfileServerFactory(self)
        self.download_dlg = download_dlg
        self.peers = PeerManager(self.client.connect)
        self.peers.start()

    def stop(self):
        self.peers.stop()

    # calls from plugin ##############################################
    def on_new_peer(self, peer):
        """tries to connect to new peer"""
        self.peers.add_peer(peer.id_)
        self.server.send_udp_message(MESSAGE_HELLO)

    def on_change_peer(self, peer, service):
        """tries to connect to new peer"""
        if self.peers.remote_ids.has_key(peer.id_):
            self.peers._del_peer(peer.id_)
        self.on_new_peer(peer)

    def on_lost_peer(self, peer_id):
        """tries to connect to new peer"""
        if self.peers.remote_ids.has_key(peer_id):
            self.peers.remote_ids[peer_id].lose()

    def on_service_data(self, peer_id, message):
        """demand to establish connection from peer that failed to
        connect through TCP"""
        if self.peers.assert_id(peer_id):
            message = Message.create_message(message)
            if message.command != MESSAGE_HELLO:
                SecurityAlert(peer_id,
                              "unexpected message '%s' from %s"\
                              % (str(message), peer_id))
            else:
                self.peers.set_peer(peer_id, message)
            
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
    def get_profile(self, peer_id):
        """retreive peer's profile"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.client.get_profile()
        #else: return None

    def get_blog_file(self, peer_id):
        """retreive peer's blog"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.client.get_blog()
        #else: return None

    def get_shared_files(self, peer_id):
        """retreive peer's shared list"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.client.get_shared_files()
        #else: return None

    def get_files(self, peer_id, file_descriptors, _on_all_files):
        """retreive file"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.client.get_files(file_descriptors, _on_all_files)
        #else: return None
