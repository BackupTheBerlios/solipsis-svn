# pylint: disable-msg=W0131,C0103
# Missing docstring, Invalid name
"""client server module for file sharing"""

__revision__ = "$Id: $"

import pickle
import gettext
_ = gettext.gettext

from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor, defer
from twisted.protocols import basic

from solipsis import VERSION
from solipsis.services.profile.document import read_document
from solipsis.services.profile.facade import get_facade, get_filter_facade
from solipsis.services.profile.message import display_error, display_status
from solipsis.services.profile.network import SecurityAlert, DownloadMessage, \
     MESSAGE_PROFILE, MESSAGE_BLOG, MESSAGE_SHARED, MESSAGE_FILES, \
     MESSAGE_HELLO

class PeerClient(dict):
    """dictionary of all dowloads"""
    
    def __init__(self, peer, connect_method, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.peer = peer
        self.connect = connect_method

    def __setitem__(self, transport):
        dict.__setitem__(self, id(transport))

    def __getitem__(self, transport):
        try:
            return dict.__getitem__(self, id(transport))
        except KeyError:
            raise SecurityAlert(transport.getPeer().host,
                                _("Corrupted client"))
            
        
    # high level API #################################################
    def get_profile(self):
        """download peer profile using self.get_file. Automatically
        called on client creation"""
        return self._connect(MESSAGE_PROFILE)
            
    def get_blog_file(self):
        """donload blog file using self.get_file"""
        return self._connect(MESSAGE_BLOG)
            
    def get_shared_files(self):
        """donload blog file using self.get_file"""
        return self._connect(MESSAGE_SHARED)
            
    def get_files(self, file_descriptors):
        """download given list of file"""
        return self._connect(MESSAGE_FILES, file_descriptors)

    # connection management ##########################################
    def _connect(self, command, data=None):
        # set download information
        message = self.peer.wrap_message(command, data)
        connector =  self.connect(self)
        deferred = defer.Deferred()
        download = DownloadMessage(connector.transport, deferred, message)
        self[connector.transport] = download
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
            raise ValueError("ERROR in _connect: %s not valid"% command)
        return deferred
        
    def _fail_client(self, transport, reason):
        self[transport].close(reason)

    def _on_connected(self, transport):
        self[transport].send_message()
        self[transport].setup_download()
    
    def rawDataReceived(self, transport, data):
        self[transport].write_data(data)

    def _on_disconnected(self, transport, reason):
        self[transport].teardown_download()
        self[transport].close(reason)

    # callbacks ######################################################
    def _on_hello(self, file_obj):
        """callback when autoloading of profile successful"""
        document = read_document(file_obj)
        get_facade().set_data(self.peer.peer_id, document, flag_update=False)
        get_filter_facade().fill_data(self.peer.peer_id, document)
        
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
        pass
    
# Twisted Client #####################################################
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
        self.transports[connector.transport] = peer
        return connector

    def clientConnectionFailed(self, connector, reason):
        """Called when a connection has failed to connect."""
        peer = self.transports[connector.transport]
        peer.client._fail_client(connector.transport, reason)
