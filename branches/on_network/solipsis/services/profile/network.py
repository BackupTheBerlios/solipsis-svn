# pylint: disable-msg=W0131
# Missing docstring
"""client server module for file sharing"""

__revision__ = "$Id$"

import datetime
import threading
import gettext
_ = gettext.gettext

from Queue import Queue, Empty

from solipsis.services.profile.message import display_warning, display_status
from solipsis.services.profile.protocols import Message, Peer, MESSAGE_HELLO, \
     ProfileClientFactory, ProfileServerFactory

class SecurityException(Exception):
    pass

class PeerManager(threading.Thread):
    """manage known ips (along with their ids) and timeouts"""

    CHECKING_FREQUENCY = 5

    def __init__(self):
        threading.Thread.__init__(self)
        self.queue = Queue(-1) # infinite size
        self.remote_ips = {}   # {ip : peer}
        self.remote_ids = {}   # {id : peer}
        self.warnings = {}     # potential hackers {id: nb_hack}
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

    def assert_ip(self, remote_ip):
        if self.remote_ips.has_key(remote_ip):
            return True
        else:
            # security exception -> archive warning
            if not remote_ip in self.warnings:
                self.warnings[remote_ip] = 1
                # first time warning occurs -> display_warning
                display_warning("host %s had not registered"% remote_ip,
                                title="security warning")
            else:
                self.warnings[remote_ip] += 1
                # n time warning occurs -> display_status
                display_status(_("%d retries of potential hacker %s "\
                                 % (self.warnings[remote_ip],
                                    remote_ip)))
            return False
        
    def assert_id(self, peer_id):
        if self.remote_ids.has_key(peer_id):
            return True
        else:
            display_warning(_("Your request on peer %s could not be granted "
                              "since no connection is available %s "% peer_id),
                            title=_("Download impossible"))
            return False

    def add_peer(self, peer_id):
        try:
            self.lock.acquire()
            peer = Peer(peer_id)
            self.remote_ids[peer_id] = peer
            self.remote_ips[peer_ip] = peer
        finally:
            self.lock.release()

    def add_message(self, peer, message):
        """Synchronized method called either from peer_manager thread
        or network thread"""
        try:
            self.lock.acquire()
            # check ip
            if message.ip !=  peer.ip:
                raise SecurityException(
                    "two ip (msg=%s, cache=%s) for same peer (%s)"\
                    (message.ip,  self.remote_ids[peer.peer_id], peer.peer_id))
            # put message in queue
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

class NetworkManager:
    """high level class managing clients and servers for each peer"""

    def __init__(self, download_dlg=None):
        self.download_dlg = download_dlg
        self.client = ProfileClientFactory(self)
        self.server = ProfileServerFactory(self)
        self.peers = PeerManager()

    # calls from plugin ##############################################
    def on_new_peer(self, peer):
        """tries to connect to new peer"""
        self.peers.add_peer(peer.id_)
        from solipsis.services.profile.plugin import Plugin
        # declare known port to other peer throug service_api
        message = self.server.wrap_message(MESSAGE_HELLO)
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
    def get_profile(self, peer_id):
        """retreive peer's profile"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.get_profile(self.client)
        #else: return None

    def get_blog_file(self, peer_id):
        """retreive peer's blog"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.get_blog(self.client)
        #else: return None

    def get_shared_files(self, peer_id):
        """retreive peer's shared list"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.get_shared_files(self.client)
        #else: return None

    def get_files(self, peer_id, file_descriptors, _on_all_files):
        """retreive file"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.get_files(self.client, file_descriptors, _on_all_files)
        #else: return None
