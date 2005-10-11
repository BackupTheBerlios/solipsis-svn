# pylint: disable-msg=C0103
#
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
from solipsis.services.profile.network import Message
from solipsis.services.profile.message import display_error, \
     display_warning, display_status
from solipsis.services.profile.prefs import get_prefs
from solipsis.services.profile.document import read_document
from solipsis.services.profile.facade import get_facade, get_filter_facade

# CLIENT #############################################################
class ProfileClientProtocol(basic.LineReceiver):
    """Intermediate client checking that a remote server exists."""

    def __init__(self):
        self.factory = None
        self.size = 0
        self.file = None

    def lineReceived(self, line):
        """incomming connection from other peer"""
        print "Client Manager received from %s:"\
              % self.transport.getPeer().host, line
    
    def rawDataReceived(self, data):
        """specialised in Client/Server protocol"""
        self.size += len(data)
        self.factory.manager.update_download(self.size)
        self.file.write(data)
            
    def rawDataReceived(self, data):
        """called upon upload of a file, when server acting as a client"""
        remote_ip = self.transport.getPeer().host
        peers_state = self.factory.network.peers.remote_ips[remote_ip]
        peers_state.received_data(data)

    def sendLine(self, line):
        """overrides in order to ease debug"""
        print "Client manager sending:", line
        assert isinstance(line, str), "%s must be a string"% line
        basic.LineReceiver.sendLine(self, line)
        
    def connectionMade(self):
        """a peer has connected to us"""
        # check ip
        remote_host  = self.transport.getPeer().host
        assert remote_host == self.factory.remote_ip, \
               "UNAUTHORIZED %s"% remote_host        # check action to be made
        if self.factory.download.startswith(ASK_DOWNLOAD_FILES):
            if self.factory.files:
                self.setRawMode()
                # TODO: check place where to download and non overwriting
                # create file
                file_path, size = self.factory.files.pop()
                self.factory.manager.update_file(file_path[-1], size)
                down_path = os.path.abspath(os.path.join(
                    get_prefs("download_repo"),
                    file_path[-1]))
                print "loading into", down_path
                self.file = open(down_path, "w+b")
                self.sendLine("%s %s"% (self.factory.download,
                                        UNIVERSAL_SEP.join(file_path)))
            else:
                self.factory.manager._on_all_files()
        elif self.factory.download.startswith(ASK_DOWNLOAD_BLOG)\
                 or self.factory.download.startswith(ASK_DOWNLOAD_SHARED):
            self.setRawMode()
            self.file = StringIO()
            self.sendLine(self.factory.download)
        elif self.factory.download.startswith(ASK_DOWNLOAD_PROFILE):
            self.setRawMode()
            self.file = tempfile.NamedTemporaryFile()
            self.sendLine(self.factory.download)
        elif self.factory.download.startswith(ASK_UPLOAD):
            self.file = None
            self.setLineMode()
            self.sendLine(self.factory.download)
        else:
            print "unexpected command %s"% self.factory.download

    def connectionLost(self, reason):
        """called when transfer complete"""
        PeerProtocol.connectionLost(self, reason)
        if self.file:
            self.file.seek(0)
            self.factory.deferred.callback(self.file)
            self.file.close()
            self.file = None
        #else: was an upload, no file opened
        
class ProfileClientFactory(ClientFactory):
    """client connecting on known port thanks to TCP. call UDP on failure."""

    protocol = ProfileClientProtocol

    def __init__(self, manager):
        # service api (UDP transports)
        self.manager = manager
        self.remote_ip = remote_ip
        self.remote_port  = None
        self.peer_id = None
        # flag download/upload
        self.connector = None
        self.download = None
        self.deferred = None
        self.files = []

    def connect(self):
        """connect to remote server"""
        if self.remote_port:
            self.deferred = defer.Deferred()
            self.connector = reactor.connectTCP(self.remote_ip,
                                                self.remote_port, self)
            return self.deferred
        return False

    def disconnect(self):
        """close connection with server"""
        if self.connector:
            self.connector.disconnect()
            self.connector = None
            self.download = None
            self.files = []

    def clientConnectionFailed(self, connector, reason):
        """Called when a connection has failed to connect."""
        # clean dictionaries of client/server in upper lever
        self.disconnect()
        self.manager.client.lose_dedicated_client(self.remote_ip)

    def _on_profile_complete(self, document, peer_id):
        """callback when autoloading of profile successful"""
        get_facade().set_data(peer_id, document, flag_update=False)
        get_facade().set_connected(peer_id, True)
        get_filter_facade().fill_data(peer_id, document)
        
    def _on_complete_profile(self, file_obj):
        """callback when finished downloading profile"""
        return read_document(file_obj)

    def _on_complete_pickle(self, file_obj):
        """callback when finished downloading blog"""
        try:
            obj_str = file_obj.getvalue()
            return pickle.loads(obj_str)
        except Exception, err:
            display_error(_("Your version of Solipsis is not compatible with the one "
                            "of the peer you wish to download from. "
                            "Make sure you both use the latest (%s)"% VERSION),
                          title="Download error", error=err)

    def _on_complete_file(self, file_obj):
        """callback when finished downloading file"""
        # proceed next
        self.connect().addCallback(self._on_complete_file)
        # flag this one
        return file_obj.name
        
    def get_profile(self):
        """download peer profile using self.get_file. Automatically
        called on client creation"""
        self.download = ASK_DOWNLOAD_PROFILE
        return self.connect().addCallback(self._on_complete_profile)
            
    def get_blog_file(self):
        """donload blog file using self.get_file"""
        self.download = ASK_DOWNLOAD_BLOG
        return self.connect().addCallback(self._on_complete_pickle)
            
    def get_shared_files(self):
        """donload blog file using self.get_file"""
        self.download = ASK_DOWNLOAD_SHARED
        return self.connect().addCallback(self._on_complete_pickle)
            
    def get_files(self, file_descriptors):
        """download given list of file"""
        for split_path, size in file_descriptors:
            self.files.append((split_path, size))
        self.download = ASK_DOWNLOAD_FILES
        return self.connect().addCallback(self._on_complete_file)
    
# SERVER #############################################################
class ProfileServerProtocol(basic.LineReceiver):

    def __init__(self, *args, **kwargs):
        basic.LineReceiver.__init__(self, *args, **kwargs)
        self.peer_sate = None

    def lineReceived(self, line):
        """incomming connection from other peer"""
        if line == "ping":
            self.sendLine("pong")
            return
        else:
            message = Message.create_message(line)
            self.factory.network.add_message(self.peer_state,
                                             message)
        # donwnload file
        elif line.startswith(MESSAGE_FILES):
            file_path = line[len(ASK_DOWNLOAD_FILES)+1:].strip()
            file_name = os.sep.join(file_path.split(UNIVERSAL_SEP))
            file_desc = get_facade().get_file_container(file_name)
            # check shared
            if file_desc._shared:
                print "sending", file_name
                deferred = basic.FileSender().\
                           beginFileTransfer(open(file_name), self.transport)
                deferred.addCallback(lambda x: self.transport.loseConnection())
            else:
                print "permission denied"
        # donwnload blog
        elif line == MESSAGE_BLOG:
            blog_stream = get_facade().get_blog_file()
            deferred = basic.FileSender().\
                       beginFileTransfer(blog_stream, self.transport)
            deferred.addCallback(lambda x: self.transport.loseConnection())
        # donwnload list of shared files
        elif line == ASK_DOWNLOAD_SHARED:
            files_stream = get_facade().get_shared_files()
            print "Sending", files_stream
            deferred = basic.FileSender().beginFileTransfer(files_stream,
                                                            self.transport)
            deferred.addCallback(lambda x: self.transport.loseConnection())
        # donwnload profile
        elif line == ASK_DOWNLOAD_PROFILE:
            file_obj = get_facade()._desc.document.to_stream()
            deferred = basic.FileSender().\
                       beginFileTransfer(file_obj, self.transport)
            deferred.addCallback(lambda x: self.transport.loseConnection())
        elif line == ASK_UPLOAD:
            self.setRawMode()
            remote_host = self.transport.getPeer().host
            deferred = self.factory.deferreds[remote_host]
            self.sendLine(deferred.get_message())
        else:
            print "unexpected line", line
            
    def connectionMade(self):
        """a peer has connect to us"""
        remote_ip = self.transport.getPeer().host
        peers_ip = self.factory.network.peers.remote_ips
        if not peers_ip.has_key(remote_ip):
            self.transport.loseConnection()
            if not remote_ip in self.factory.warnings:
                self.factory.warnings[remote_ip] = 1
                display_warning("host %s had not registered"% remote_ip,
                                title="security warning")
            else:
                self.factory.warnings[remote_ip] += 1
                display_status(_("%d retries of potential hacker %s "\
                                 % (self.factory.warnings[remote_ip],
                                    remote_ip)))
        else:
            display_status(_("%s has connected"% remote_ip))
            self.peer_state = peers_ip[remote_ip]
            self.peer_state.connected()
        
    def connectionLost(self, reason):
        """called when transfer complete"""
        display_status(_("%s disconnected"% self.peer_state.ip))
        self.peer_state.disconnected()

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
        self.warnings = {}    # dictionary of potential hackers 
        # followings are set by STUN response
        self.public_ip = None
        self.public_port = None

    def wrap_message(self, command, data=None):
        message = Message(command)
        message.ip = self.public_ip
        message.port = self.public_port
        message.data = data
        return message

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
