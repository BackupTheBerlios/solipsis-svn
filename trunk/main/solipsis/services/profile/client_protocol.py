# pylint: disable-msg=W0131,C0103
# Missing docstring, Invalid name
"""client server module for file sharing"""

__revision__ = "$Id: client_protocol.py 907 2005-10-26 15:04:24Z emb $"

import gettext
_ = gettext.gettext

from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
from twisted.protocols import basic

from solipsis.services.profile.message import display_status

class ProfileClientProtocol(basic.LineReceiver):
    """Intermediate client checking that a remote server exists."""

    def __init__(self):
        self.peer_client = None

    def lineReceived(self, line):
        display_status(_("Unexpected line received: %s"% line))

    def rawDataReceived(self, data):
        self.peer_client.rawDataReceived(self.transport, data)
        
    def connectionMade(self):
        """a peer has connected to us"""
        remote_ip = self.transport.getPeer().host
        # check that ip has been suscribed (by high-level funciton 'on_new_peer')
        if not self.factory.network.peers.assert_ip(remote_ip):
            self.transport.loseConnection()
        else:
            self.setRawMode()
            peer = self.factory.network.peers.remote_ips[remote_ip]
            self.peer_client = peer.client
            self.peer_client._on_connected(self.transport)

    def connectionLost(self, reason):
        """called when transfer complete"""
        self.peer_client._on_disconnected(self.transport, reason)

        
class ProfileClientFactory(ClientFactory):
    """client connecting on known port thanks to TCP. call UDP on failure."""

    protocol = ProfileClientProtocol

    def __init__(self, network):
        self.network = network
        self.transports = {}

    def connect(self, peer):
        """connect to remote server"""
        connector = reactor.connectTCP(peer.ip,
                                       peer.port,
                                       self)
        self.transports[id(connector.transport)] = peer
        return connector

    def clientConnectionFailed(self, connector, reason):
        """Called when a connection has failed to connect."""
        peer = self.transports[id(connector.transport)]
        peer.client._fail_client(connector.transport, reason)
