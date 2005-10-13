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
            raise ValueError("%s should define host's ip and port"% command)
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

    def send_message(self):
        self.transport.write(str(self.message)+"\r\n")

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
            
class Peer(object):
    """trace messages received for this peer"""
    
    PEER_TIMEOUT = 120

    def __init__(self, peer_id):
        self.peer_id = peer_id
        self.lost = None
        # states
        registered_state = PeerRegistered(self)
        connected_state = PeerConnected(self)
        disconnected_state = PeerDisconnected(self)
        current_sate = None
        # vars set by states
        self.ip = None
        self.port = None
        self.downloads = {}

    # client side ####################################################
    def wrap_message(self, command, data=None):
        message = Message(command)
        message.ip = self.ip
        message.port = self.port
        message.data = data
        return message
        
    def get_profile(self, client):
        """download peer profile using self.get_file. Automatically
        called on client creation"""
        return self._connect_client(client, MESSAGE_PROFILE)
            
    def get_blog_file(self, client):
        """donload blog file using self.get_file"""
        return self._connect_client(client, MESSAGE_BLOG)
            
    def get_shared_files(self, client):
        """donload blog file using self.get_file"""
        return self._connect_client(client, MESSAGE_SHARED)
            
    def get_files(self, client, file_descriptors):
        """download given list of file"""
        return self._connect_client(client, MESSAGE_FILES, file_descriptors)

    def _fail_client(self, connector, reason):
        download = self.downloads[id(connector.transport)]
        pass

    def _connect_client(self, client, command, data=None):
        # set download information
        message = self.wrap_message(command, data)
        connector =  client.connect(self)
        deferred = defer.Deferred()
        download = DownloadMessage(connector.transport, deferred, message)
        self.downloads[id(connector.transport)] = download
        # set callback
        if command == MESSAGE_HELLO:
            deferred.addCallback(self._on_hello)
        if command == MESSAGE_PROFILE:
            deferred.addCallback(self._on_complete_profile)
        elif command == MESSAGE_BLOG:
            deferred.addCallback(self._on_complete_pickle)
        elif command == MESSAGE_SHARED:
            deferred.addCallback(self._on_complete_pickle)
        elif command == MESSAGE_FILES:
            deferred.addCallback(self._on_complete_file)
        else:
            raise ValueError("ERROR in add_client: %s not valid"% command)
        return deferred

    def _on_connected(self, transport):
        download = self.downloads[id(transport)]
        download.send_message()
        self.file = tempfile.NamedTemporaryFile()
        pass

    def _on_disconnected(self, transport):
        download = self.downloads[id(transport)]
        pass

    def _on_hello(self, file_obj):
        """callback when autoloading of profile successful"""
        get_facade().set_data(self.peer_id, document, flag_update=False)
        get_facade().set_connected(self.peer_id, True)
        get_filter_facade().fill_data(self.peer_id, document)
        
    def _on_complete_profile(self, file_obj):
        """callback when finished downloading profile"""
        return read_document(file_obj)

    def _on_complete_pickle(self, file_obj):
        """callback when finished downloading blog"""
        try:
            obj_str = file_obj.getvalue()
            return pickle.loads(obj_str)
        except Exception, err:
            display_error(_("Your version of Solipsis is not compatible "
                            "with the peer'sone you wish to download from "
                            "Make sure you both use the latest (%s)"\
                            % VERSION),
                          title="Download error", error=err)

    def _on_complete_file(self, file_obj):
        """callback when finished downloading file"""
        # proceed next
        self.connect().addCallback(self._on_complete_file)
        # flag this one
        return file_obj.name

    # server side ####################################################
    def lose(self):
        self.lost = datetime.datetime.now() \
                    + datetime.timedelta(seconds=self.PEER_TIMEOUT)

    def connected(self, protocol):
        self.current_sate.connected(protocol)
    def disconnected(self):
        self.current_sate.disconnected()
    def execute(self, manager, message):
        self.current_sate.execute()
    def received_data(self, data):
        self.current_sate.received_data()
    
class PeerState(object):
    """trace messages received for this peer"""

    def __init__(self, peer):
        self.peer = peer
        
    def connected(self, protocol):
        raise NotImplementedError
    def disconnected(self):
        raise NotImplementedError
    def execute(self, manager, message):
        raise NotImplementedError
    def received_data(self, data):
        raise NotImplementedError
    
class PeerRegistered(PeerState):
    """trace messages received for this peer"""

    def connected(self, protocol):
        pass

    def disconnected(self):
        pass

    def execute(self, manager, message):
        pass
    
    def received_data(self, data):
        pass
    
class PeerConnected(PeerState):
    """trace messages received for this peer"""

    def connected(self, protocol):
        pass

    def disconnected(self):
        pass

    def execute(self, manager, message):
        pass
    
    def received_data(self, data):
        pass
    
class PeerDisconnected(PeerState):
    """trace messages received for this peer"""

    def connected(self, protocol):
        pass

    def disconnected(self):
        pass

    def execute(self, manager, message):
        pass
    
    def received_data(self, data):
        pass
    
# Client #############################################################
class ProfileClientProtocol(basic.LineReceiver):
    """Intermediate client checking that a remote server exists."""

    def __init__(self):
        self.size = 0
        self.file = None
        
    def connectionMade(self):
        """a peer has connected to us"""
        remote_ip = self.transport.getPeer().host
        if not self.factory.network.peers.assert_ip(remote_ip):
            self.transport.loseConnection()
        else:
            peer = self.factory.network.peers.remote_ips[remote_ip]
            self.setRawMode()
            peer._on_connected(self.transport)

    def connectionLost(self, reason):
        """called when transfer complete"""
        remote_ip = self.transport.getPeer().host
        peer = self.factory.network.peers.remote_ips[remote_ip]
        peer._on_disconnected(self.transport)

        
class ProfileClientFactory(ClientFactory):
    """client connecting on known port thanks to TCP. call UDP on failure."""

    protocol = ProfileClientProtocol

    def __init__(self, *args, **kwargs):
        ClientFactory.__init__(self, *args, **kwargs)
        self.transports = {}

    def connect(self, peer):
        """connect to remote server"""
        
        connector = reactor.connectTCP(self.peer.ip,
                                       self.peer.port,
                                       self)
        self.transports[id(connector.transport)] = peer
        return connector

    def clientConnectionFailed(self, connector, reason):
        """Called when a connection has failed to connect."""
        peer = self.transports[id(connector.transport)]
        peer._fail_client(connector, reason)
    
# SERVER #############################################################
class ProfileServerProtocol(basic.LineReceiver):

    def sendMessage(self, command, data=None):
        message = self.factory._wrap_message(command, data)
        self.sendLine(str(message))

    def lineReceived(self, line):
        """incomming connection from other peer"""
        if line == "ping":
            self.sendLine("pong")
        else:
            message = Message.create_message(line)
            self.factory.network.add_message(message)
            
    def connectionMade(self):
        """a peer has connect to us"""
        remote_ip = self.transport.getPeer().host
        if not self.factory.network.peers.assert_ip(remote_ip):
            self.transport.loseConnection()
        else:
            display_status(_("%s has connected"% remote_ip))
            peer_ips = self.factory.network.peers.remote_ips
            peer_ips[remote_ip].connected(self)
        
    def connectionLost(self, reason):
        """called when transfer complete"""
        remote_ip = self.transport.getPeer().host
        display_status(_("%s disconnected"% remote_ip))
        peer_ips = self.factory.network.peers.remote_ips
        peer_ips[remote_ip].disconnected()

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

    def _wrap_message(self, command, data=None):
        message = Message(command)
        message.ip = self.public_ip
        message.port = self.public_port
        message.data = data
        return message
