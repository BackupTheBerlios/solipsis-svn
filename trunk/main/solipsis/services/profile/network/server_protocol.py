# pylint: disable-msg=W0131,C0103
# Missing docstring, Invalid name
"""client server module for file sharing"""

__revision__ = "$Id: server_protocol.py 907 2005-10-26 15:04:24Z emb $"

import socket
import gettext
_ = gettext.gettext

from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor
from twisted.protocols import basic

from solipsis.node.discovery import stun
from solipsis.navigator.main import build_params
from solipsis.util.network import get_free_port, release_port
from solipsis.services.profile.tools.message import log, display_warning, \
     display_status
from solipsis.services.profile.network.messages import Message

class ProfileServerProtocol(basic.LineOnlyReceiver):

    def lineReceived(self, line):
        """incomming connection from other peer"""
        if line == "ping":
            self.sendLine("pong")
        else:
            message = Message.create_message(line)
            self.factory.network.peers.add_message(message)
            
    def connectionMade(self):
        """a peer has connect to us"""
        remote_ip = self.transport.getPeer().host
        # check that ip has been suscribed (by high-level funciton 'on_new_peer')
        if not self.factory.network.peers.assert_ip(remote_ip):
            self.transport.loseConnection()
        else:
            log(_("%s has connected"% remote_ip))
            peer = self.factory.network.peers.remote_ips[remote_ip]
            peer.server.connected(self)
        
    def connectionLost(self, reason):
        """called when transfer complete"""
        remote_ip = self.transport.getPeer().host
        if self.factory.network.peers.assert_ip(remote_ip):
            log(_("%s disconnected"% remote_ip))
            peer = self.factory.network.peers.remote_ips[remote_ip]
            peer.server.disconnected()
        else:
            log(_("%s already disconnected"% remote_ip))

class ProfileServerFactory(ServerFactory):
    """server listening on known port. It will spawn a dedicated
    server on new connection"""

    protocol = ProfileServerProtocol

    def __init__(self, network):
        self.network = network
        self.local_ip = socket.gethostbyname(socket.gethostname())
        # followings initialised when server started
        self.local_port = None
        self.listener = None
        # followings are set by STUN response
        self.public_ip = None
        self.public_port = None

    def start_listening(self, conf_file=None):
        """launch well-known server of profiles"""
        self.local_port = get_free_port()
        # define callbacks on public_ip discovery
        def _stun_succeed(address):
            """Discovery succeeded"""
            self.public_ip, self.public_port = address
            display_status(_("STUN discovery found address %s:%d" \
                             % (self.public_ip, self.public_port)))
            self.listener = reactor.listenTCP(self.local_port, self)
            return True
        def _stun_fail(failure):
            self.public_ip, self.public_port = self.local_ip, self.local_port
            display_warning(_("STUN failed:", failure.getErrorMessage()),
                            title=_("File server Error"))
            self.listener = reactor.listenTCP(self.local_port, self)
            return False
        # get public ip
        deferred = stun.DiscoverAddress(self.local_port,
                                        reactor,
                                        build_params(conf_file))
        deferred.addCallback(_stun_succeed)
        deferred.addErrback(_stun_fail)
        return deferred

    def stop_listening(self):
        """shutdown well-known server"""
        self.listener.stopListening()
        release_port(self.local_port)

    def send_udp_message(self, peer_id, command, data=None):
        from solipsis.services.profile.plugin import Plugin
        message = Message(command)
        message.ip = self.public_ip
        message.port = self.public_port
        message.data = data
        if Plugin.service_api:
            Plugin.service_api.SendData(peer_id, str(message))
