# pylint: disable-msg=W0131
# Missing docstring
"""client server module for file sharing"""

import socket
import datetime
import threading
import random
import tempfile
import pickle
import os.path
import traceback
import gettext
_ = gettext.gettext

from twisted.internet.protocol import ClientFactory, ServerFactory
from twisted.internet import reactor, defer
from twisted.internet import error
from twisted.protocols import basic
from StringIO import StringIO
from Queue import Queue, Empty

from solipsis import VERSION
from solipsis.node.discovery import stun, local
from solipsis.navigator.main import build_params
from solipsis.util.network import parse_address, get_free_port, release_port
from solipsis.services.profile import UNIVERSAL_SEP
from solipsis.services.profile.prefs import get_prefs
from solipsis.services.profile.document import read_document
from solipsis.services.profile.facade import get_facade, get_filter_facade
from solipsis.services.profile.message import display_error, \
     display_warning, display_status
from solipsis.services.profile.network import Message, DownloadMessage, \
     MESSAGE_PROFILE, MESSAGE_BLOG, MESSAGE_SHARED, MESSAGE_FILES, \
     MESSAGE_HELLO, MESSAGE_ERROR

# State pattern ######################################################
#         # donwnload file
#         elif line.startswith(MESSAGE_FILES):
#             file_path = line[len(ASK_DOWNLOAD_FILES)+1:].strip()
#             file_name = os.sep.join(file_path.split(UNIVERSAL_SEP))
#             file_desc = get_facade().get_file_container(file_name)
#             # check shared
#             if file_desc._shared:
#                 print "sending", file_name
#                 deferred = basic.FileSender().\
#                            beginFileTransfer(open(file_name), self.transport)
#                 deferred.addCallback(lambda x: self.transport.loseConnection())
#             else:
#                 print "permission denied"
#         # donwnload blog
#         elif line == MESSAGE_BLOG:
#             blog_stream = get_facade().get_blog_file()
#             deferred = basic.FileSender().\
#                        beginFileTransfer(blog_stream, self.transport)
#             deferred.addCallback(lambda x: self.transport.loseConnection())
#         # donwnload list of shared files
#         elif line == MESSAGE_SHARED:
#             files_stream = get_facade().get_shared_files()
#             print "Sending", files_stream
#             deferred = basic.FileSender().beginFileTransfer(files_stream,
#                                                             self.transport)
#             deferred.addCallback(lambda x: self.transport.loseConnection())
#         # donwnload profile
#         elif line == MESSAGE_PROFILE:
#             file_obj = get_facade()._desc.document.to_stream()
#             deferred = basic.FileSender().\
#                        beginFileTransfer(file_obj, self.transport)
#             deferred.addCallback(lambda x: self.transport.loseConnection())
        
#         if self.factory.download.startswith(ASK_DOWNLOAD_FILES):
#             if self.factory.files:
#                 self.setRawMode()
#                 # TODO: check place where to download and non overwriting
#                 # create file
#                 file_path, size = self.factory.files.pop()
#                 self.factory.manager.update_file(file_path[-1], size)
#                 down_path = os.path.abspath(os.path.join(
#                     get_prefs("download_repo"),
#                     file_path[-1]))
#                 print "loading into", down_path
#                 self.file = open(down_path, "w+b")
#                 self.sendLine("%s %s"% (self.factory.download,
#                                         UNIVERSAL_SEP.join(file_path)))
#             else:
#                 self.factory.manager._on_all_files()
#         elif self.factory.download.startswith(ASK_DOWNLOAD_BLOG)\
#                  or self.factory.download.startswith(ASK_DOWNLOAD_SHARED):
#             self.setRawMode()
#             self.file = StringIO()
#             self.sendLine(self.factory.download)
#         elif self.factory.download.startswith(ASK_DOWNLOAD_PROFILE):
#             self.setRawMode()
#             self.file = tempfile.NamedTemporaryFile()
#             self.sendLine(self.factory.download)
#         elif self.factory.download.startswith(ASK_UPLOAD):
#             self.file = None
#             self.setLineMode()
#             self.sendLine(self.factory.download)
#         else:
#             print "unexpected command %s"% self.factory.download
            
class PeerServer(object):
    """trace messages received for this peer"""

    def __init__(self, peer):
        self.peer = peer
        # states
        registered_state = PeerRegistered(self)
        connected_state = PeerConnected(self)
        disconnected_state = PeerDisconnected(self)
        current_sate = PeerState(self)

    def connected(self, protocol):
        self.current_sate.connected(protocol)
        
    def disconnected(self):
        self.current_sate.disconnected()
        
    def execute(self, manager, message):
        self.current_sate.execute()
    
class PeerState(object):
    """trace messages received for this peer"""

    def __init__(self, peer_server):
        self.peer_server = peer_server
        
    def connected(self, protocol):
        raise NotImplementedError
    def disconnected(self):
        raise NotImplementedError
    def execute(self, manager, message):
        raise NotImplementedError
    
class PeerRegistered(PeerState):
    """trace messages received for this peer"""

    def connected(self, protocol):
        pass

    def disconnected(self):
        pass

    def execute(self, manager, message):
        pass
    
class PeerConnected(PeerState):
    """trace messages received for this peer"""

    def connected(self, protocol):
        pass

    def disconnected(self):
        pass

    def execute(self, manager, message):
        pass
    
class PeerDisconnected(PeerState):
    """trace messages received for this peer"""

    def connected(self, protocol):
        pass

    def disconnected(self):
        pass

    def execute(self, manager, message):
        pass
    
# SERVER #############################################################
class ProfileServerProtocol(basic.LineReceiver):

    def sendMessage(self, command, data=None):
        message = self.factory.wrap_message(command, data)
        self.sendLine(str(message))

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
            peer.server.disconnected(self)
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

    def wrap_message(self, command, data=None):
        message = Message(command)
        message.ip = self.public_ip
        message.port = self.public_port
        message.data = data
        return message
