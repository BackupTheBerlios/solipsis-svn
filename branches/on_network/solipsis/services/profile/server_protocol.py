# pylint: disable-msg=W0131,C0103
# Missing docstring, Invalid name
"""client server module for file sharing"""

__revision__ = "$Id$"

import socket
import os, os.path
import gettext
_ = gettext.gettext

from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor
from twisted.protocols import basic

from solipsis.node.discovery import stun
from solipsis.navigator.main import build_params
from solipsis.util.network import get_free_port, release_port
from solipsis.services.profile import UNIVERSAL_SEP
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.message import display_warning, display_status
from solipsis.services.profile.network import Message, SecurityAlert, \
     MESSAGE_PROFILE, MESSAGE_BLOG, MESSAGE_SHARED, MESSAGE_FILES, \
     MESSAGE_HELLO, MESSAGE_ERROR
            
class PeerServer(object):
    """trace messages received for this peer"""

    def __init__(self, peer):
        self.peer = peer
        # states
        self.registered_state = PeerRegistered(self)
        self.connected_state = PeerConnected(self)
        self.disconnected_state = PeerDisconnected(self)
        self.current_sate = PeerState(self)

    def connected(self, protocol):
        self.current_sate.connected(protocol)
        
    def disconnected(self):
        self.current_sate.disconnected()
        
    def execute(self, message):
        self.current_sate.execute(message)
    
class PeerState(object):
    """trace messages received for this peer"""

    def __init__(self, peer_server):
        self.protocol = None
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
        self.protocol = protocol
        self.peer_server.current_sate = self.peer_server.connected_state
    
class PeerConnected(PeerState):
    """trace messages received for this peer"""

    def connected(self, protocol):
        self.protocol = protocol

    def disconnected(self):
        self.peer_server.current_sate = self.peer_server.disconnected_state

    def execute(self, message):
        transport = self.protocol.transport
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
            file_path = message.data
            file_name = os.sep.join(file_path.split(UNIVERSAL_SEP))
            file_desc = get_facade().get_file_container(file_name)
            # check shared
            if file_desc._shared:
                display_status("sending %s"% file_name)
                deferred = basic.FileSender().\
                           beginFileTransfer(open(file_name), transport)
                deferred.addCallback(lambda x: transport.loseConnection())
            else:
                self.protocol.factory.send_udp_message(
                    self.peer_server.peer.peer_id, MESSAGE_ERROR, message.data)
                SecurityAlert(self.peer_server.peer.peer_id,
                              "Trying to download unshare file %s"\
                              % file_name)
        else:
            raise ValueError("ERROR in _connect: %s not valid"% message.command)

class PeerDisconnected(PeerState):
    """trace messages received for this peer"""

    def connected(self, protocol):
        self.protocol = protocol
        self.peer_server.current_sate = self.peer_server.connected_state

    def disconnected(self):
        pass
    
# SERVER #############################################################
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
        if not self.factory.network.peers.assert_ip(remote_ip):
            self.transport.loseConnection()
        else:
            display_status(_("%s has connected"% remote_ip))
            peer = self.factory.network.peers.remote_ips[remote_ip]
            peer.server.connected(self)
        
    def connectionLost(self, reason):
        """called when transfer complete"""
        remote_ip = self.transport.getPeer().host
        if self.factory.network.peers.assert_ip(remote_ip):
            display_status(_("%s disconnected"% remote_ip))
            peer = self.factory.network.peers.remote_ips[remote_ip]
            peer.server.disconnected()
        else:
            display_status(_("%s already disconnected"% remote_ip))

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
