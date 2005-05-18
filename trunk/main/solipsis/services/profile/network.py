"""client server module for file sharing"""

from twisted.internet.protocol import ClientFactory, ServerFactory
from twisted.internet import reactor, defer
from twisted.protocols import basic

# FIXME: common method with avatar.plugin._ParserAddress... how about putting it
# into global service? How generic is it?
def parse_address(address):
    """Parse network address as supplied by a peer.
    Returns a (host, port) tuple."""
    try:
        items = address.split(':')
        if len(items) != 2:
            raise ValueError
        host = str(items[0]).strip()
        port = int(items[1])
        if not host:
            raise ValueError
        if port < 1 or port > 65535:
            raise ValueError
        return host, port
    except ValueError:
        raise

class ProfileNetwork:
    """high level class managing clients and servers for each peer"""

    def __init__(self, service_api):
        # service api (UDP transports)
        self.service_api = service_api
        # client & server status
        # deferred downloads (especially profiles)
        # listening to well-known ports
        pass

    def get_file(self, peer_id, file_name):
        """retreive file"""
        # get existing connection (client or uploading-server)
        # calls get_file on it
        pass

    def get_profile(self, peer_id, display_callback):
        """retreive peer's profile"""
        # profile is download automatically on peer aproach: check completion
        # if running: DEFERRED: add display callback 
        # if done, display profile content
        pass

    def start_listening(self):
        """launching main server listening to well-known port"""
        # delegate to ProfileServerFactory
        pass

    def stop_listening(self):
        """stops main server and desactivate profile sharing"""
        # delegate to ProfileServerFactory
        pass

    def on_new_peer(self, peer, service):
        """tries to connect to new peer"""
        # delegate connection to ProfileClientFactory
        pass

    def on_change_peer(self, peer, service):
        """tries to connect to new peer"""
        # delegate connection to ProfileClientFactory
        pass

    def on_lost_peer(self, peer_id):
        """tries to connect to new peer"""
        # finish transfer in progress
        # close connection
        pass

    def on_service_data(self, peer_id, data):
        """demand to establish connection from peer that failed to
        connect through TCP"""
        # REQUEST_TCP
        #    check status
        #    connect TCP
        pass

# WELL-KNOWN PORTS: main gate
#-----------------
# CLIENT
class ProfileClientProtocol(basic.LineOnlyReceiver):
    """Intermediate client checking that a remote server exists."""

    def __init__(self):
        # remote: ip, port, profile
        pass

    def lineReceived(self, line):
        """incomming connection from other peer"""
        # on greeting, stores info about remote host (profile id)
        # on listenning ack, set info about remote server (address)
        # update client status
        # (use dedicated server instead of well-known one)
        # close connection
        pass
        
    def connectionMade(self):
        """a peer has connected to us"""
        # great peer (with profile._id)
        # stores server address (transport.getPeer)
        # set client status
        pass

class ProfileClientFactory(ClientFactory):
    """client connecting on known port thanks to TCP. call UDP on failure."""

    protocol = ProfileClientProtocol

    def __init__(self):
        # service api (UDP transports)
        # remote info: {ips: client}
        pass

    def connect_peer(self, peer_ip):
        """open connection to peer"""
        # if client already defined, calls its connect method
        # otherwise, tries connectTCP on well-known port
        pass

    def _connect_tcp(self, peer_ip):
        """tries TCP server on well-known port"""
        #connect
        pass

    def _connect_udp(self):
        """declares itself through UDP when could not connect through TCP"""
        # use service_api to send data through nodes
        pass

    def clientConnectionFailed(self, connector, reason):
        """Called when a connection has failed to connect."""
        # connect through UDP to request the spawning of a remote server
        pass
    
    def clientConnectionLost(self, connector, reason):
        """Called when an established connection is lost."""
        # assert a remote server has been defined
        pass
    
# SERVER
class ProfileServerProtocol(basic.LineOnlyReceiver):
    """Shake hand protocol willing to switch to dedicated server"""

    def __init__(self):
        # local info: dedicated port
        # remote info: address, profile
        pass

    def lineReceived(self, line):
        """incomming connection from other peer"""
        # on greeting, stores info about remote client (profile id)
        # prepare callbacks
        # check no local server already running
        # spawn local server
        pass

    def send_local_address(self):
        """callback on sucessfull launch of dedicated server"""
        # send local server address
        # update local server status (factory)
        pass

    def fail_local_server(self):
        """callback on failure to launch local server"""
        # send failure
        # update local server status (factory)
        pass
        
    def connectionLost(self, reason):
        """Called when the connection is shut down."""
        # update local server status
        pass
        
    def connectionMade(self):
        """a peer has connect to us"""
        # great peer (with transport.getHost and profile._id)
        # stores client address (transport.getPeer)
        # set server status (factory)
        pass

class ProfileServerFactory(ServerFactory):
    """server listening on known port. It will spawn a dedicated
    server on new connection"""

    protocol = ProfileServerProtocol

    def __init__(self):
        # servers info: {ips: server}
        pass

    def start_listening(self):
        """launch well-known server of profiles"""
        pass

    def stop_listening(self):
        """shutdown well-known server"""
        pass

    def get_local_server(self, peer_ip, deferred):
        """return local server bound to owner of protocol"""
        # is server running
        # if not, spawn it
        pass
        
    def _spawn_local_server(self, peer_ip, deferred):
        """forward opened connection on well-known port into dedicated
        one"""
        # build up dedicated factory
        # start listening
        # callback
        pass


# SPECIFIC PORTS: once we'be been through main gate, use of a little
# more privacy...
#---------------
# COMMON
class PeerProtocol(basic.FileSender, basic.LineReceiver):
    """common part of protocol between client and server"""
        
    def connectionLost(self, reason):
        """Called when the connection is shut down."""
        # check file complete
        pass
        
    def connectionMade(self):
        """Called when a connection is made."""
        # check ip
        # send DOWNLOAD/UPLOAD flag
        # check file
        pass

    def send_file(self):
        """senf file on request"""
        # beginFileTransfer(self, file, consumer, transform=None)
        # deferred send COMPLETE
        pass

    def send_profile(self):
        """send profile on request"""
        # open stram on document profile
        # beginFileTransfer(self, profile, consumer, transform=None)
        # deferred send COMPLETE
        pass
    
    def lineReceived(self, line):
        """specialised in Client/Server protocol"""
        raise NotImplementedError
    
    def rawDataReceived(self, data):
        """specialised in Client/Server protocol"""
        raise NotImplementedError
        
# CLIENT
class PeerClientProtocol(PeerProtocol):
    """client part of protocol"""
        
    def lineReceived(self, line):
        """Override this for when each line is received."""
        # UPLOAD
        #     if not upload, lose connection
        # READY
        #     send file
        # DOWNLOAD
        #     if not download, lose connection
        #     change mode
        #     send READY
        # COMPLETE
        #     switch back to line mode
        #     reset status
        pass
        
class PeerClientFactory(ClientFactory):
    """manages all connections to all peers"""

    protocol = PeerClientProtocol

    def __init__(self):
        # remote address
        # upload/download flag
        pass

    def clientConnectionFailed(self, connector, reason):
        """Called when a connection has failed to connect."""
        # clean dictionaries of client/server in upper lever
        pass

    def get_file(self):
        """in case no server at the other end: server used as 'client'
        to get a file"""
        # connect specific server DOWNLOAD file://
        # receive file
        pass

    def get_profile(self):
        """in case no server at the other end: server used as 'client'
        to get profile"""
        # connect specific server DOWNLOAD profile://
        # receive profile
        pass

    def upload_file(self):
        """when no server running, peer uses 'client' to upload the
        requested file"""
        # check file is shared
        # check ip
        # connect remote server
        pass

# SERVER
class PeerServerProtocol(PeerProtocol):
    """server part of protocol"""
        
    def lineReceived(self, line):
        """Override this for when each line is received."""
        # UPLOAD
        #     if not upload, lose connection
        #     change mode
        #     send READY
        # COMPLETE
        #     switch back to line mode
        #     reset status
        #     write file / store profile and flag completion
        # DOWNLOAD file:// | profile://
        #     if not download, lose connection
        # READY
        #     call [send_profile, send_file]
        #     set callbacks
        pass
        
    def rawDataReceived(self, data):
        """called upon upload of a file, when server acting as a client"""
        # check that serverFactory.get_file has been called
        # clearLineBuffer
        # store file
        # call send_file on profile file
        pass

class PeerServerFactory(ServerFactory):
    """server listening on known port. It will spawn a dedicated
    server on new connection"""

    protocol = PeerServerProtocol

    def __init__(self):
        # remote address
        pass

    def start_listening(self):
        """open well-known server of profiles"""
        pass

    def stop_listening(self):
        """shutdown well-known server"""
        pass

    def get_file(self):
        """in case no server at the other end: server used as 'client'
        to get a file"""
        # connect UDP
        # send command of connection
        # other part connects and upload file
        pass

    def get_profile(self):
        """in case no server at the other end: server used as 'client'
        to get profile"""
        # call get_file on profile file
        pass
