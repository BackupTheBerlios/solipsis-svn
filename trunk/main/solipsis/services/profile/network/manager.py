# pylint: disable-msg=W0131
# Missing docstring
"""client server module for file sharing"""

__revision__ = "$Id$"

import gettext
_ = gettext.gettext

from solipsis.services.profile.network.peers import PeerManager
from solipsis.services.profile.network.client_protocol import \
     ProfileClientFactory
from solipsis.services.profile.network.server_protocol import \
     ProfileServerFactory
from solipsis.services.profile.network.messages import Message, SecurityAlert, \
     MESSAGE_HELLO

class NetworkManager:
    """high level class managing clients and servers for each peer"""

    def __init__(self):
        self.client = ProfileClientFactory(self)
        self.server = ProfileServerFactory(self)
        self.peers = PeerManager(self.client.connect)

    def start(self):
        self.peers.start()
        return self.server.start_listening()

    def stop(self):
        self.server.stop_listening()
        self.peers.stop()

    # calls from plugin ##############################################
    def on_new_peer(self, peer):
        """tries to connect to new peer"""
        self.peers.add_peer(peer.id_)
        self.server.send_udp_message(peer.id_, MESSAGE_HELLO)

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
            try:
                message = Message.create_message(message)
                if message.command != MESSAGE_HELLO:
                    SecurityAlert(peer_id,
                                  "unvalid message '%s' from %s"\
                                  % (str(message), peer_id))
                else:
                    self.peers.set_peer(peer_id, message)
            except ValueError, err:
                SecurityAlert(peer_id, str(err))
        #else: alert raises by assert_id
            
    # high level functions ###########################################
    def get_profile(self, peer_id):
        """retreive peer's profile"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.client.get_profile()
        #else: alert raises by assert_id

    def get_blog_file(self, peer_id):
        """retreive peer's blog"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.client.get_blog_file()
        #else: alert raises by assert_id

    def get_shared_files(self, peer_id):
        """retreive peer's shared list"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.client.get_shared_files()
        #else: alert raises by assert_id

    def get_files(self, peer_id, file_descriptors):
        """retrieve file"""
        if self.peers.assert_id(peer_id):
            peer = self.peers.remote_ids[peer_id]
            return peer.client.get_files(file_descriptors)
        #else: alert raises by assert_id
