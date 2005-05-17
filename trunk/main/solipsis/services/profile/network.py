from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor, defer
from twisted.protocols import basic

class ProfileNetwork:

    def __init__(self):
        # client & server status
        # listening to well-known ports

    def get_file(self, peer_id, file_name):
        """retreive file"""
        # get existing connection (client or uploading-server)
        # calls get_file on it

    def get_profile(self, peer_id):
        """retreive peer's profile"""
        # calls get_file on profile file

    def start_listening(self):
        """launching main server listening to well-known port"""
        # delegate to ProfileServerFactory

    def on_new_peer(self, peer_id):
        """tries to connect to new peer"""
        # delegate connection to ProfileClientFactory
    

# WELL-KNOWN PORTS: main gate
#-----------------
# CLIENT
class ProfileClientProtocol(basic.LineOnlyReceiver):
    """Intermediate client checking that a remote server exists."""

    def __init__(self):
        # remote: ip, port, profile

    def lineReceived(self, line):
        """incomming connection from other peer"""
        # on greeting, stores info about remote host (profile id)
        # on listenning ack, set info about remote server (address)
        # update client status (use dedicated server instead of well-known one)
        # close connection
        
    def connectionMade(self):
        """a peer has connected to us"""
        # great peer (with profile._id)
        # stores server address (transport.getPeer)
        # set client status

class ProfileClientFactory(ClientFactory):
    """client connecting on known port thanks to TCP. call UDP on failure."""

    protocol = ProfileClientProtocol

    def __init__(self):
        # remote info: {ips: client}

    def connect_peer(self, peer_ip):
        """open connection to peer"""
        # if client already defined, calls its connect method
        # otherwise, tries connectTCP on well-known port

    def _connectTCP(self, peer_ip):
        """tries TCP server on well-known port"""
        #connect

    def _connectUDP(self):
        """declares itself through UDP when could not connect through TCP"""
        #connect

    def clientConnectionFailed(self, connector, reason):
        """Called when a connection has failed to connect."""
        # connect through UDP to request the spawning of a remote server
    
    def clientConnectionLost(self, connector, reason):
        """Called when an established connection is lost."""
        # assert a remote server has been defined
    
# SERVER
class ProfileServerProtocol(basic.LineOnlyReceiver):
    """Shake hand protocol willing to switch to dedicated server"""

    def __init__(self):
        # local info: dedicated port
        # remote info: address, profile

    def lineReceived(self, line):
        """incomming connection from other peer"""
        # on greeting, stores info about remote client (profile id)
        # prepare callbacks
        # check no local server already running
        # spawn local server

    def send_local_address(self):
        """callback on sucessfull launch of dedicated server"""
        # send local server address
        # update local server status (factory)

    def fail_local_server(self):
        """callback on failure to launch local server"""
        # send failure
        # update local server status (factory)
        
    def connectionLost(self, reason):
        """Called when the connection is shut down."""
        # update local server status
        
    def connectionMade(self):
        """a peer has connect to us"""
        # great peer (with transport.getHost and profile._id)
        # stores client address (transport.getPeer)
        # set server status (factory)

class ProfileServerFactory(ServerFactory):
    """server listening on known port. It will spawn a dedicated server on new connection"""

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
        
    def _spawn_local_server(self, peer_ip, deferred):
        """forward opened connection on well-known port into dedicated one"""
        # build up dedicated factory
        # start listening
        # callback


# SPECIFIC PORTS: once we'be been through main gate, use of a little more privacy...
#---------------
# COMMON
class PeerProtocol(basic.FileSender, basic.LineReceiver):
        
    def connectionLost(self, reason):
        """Called when the connection is shut down."""
        # check file complete
        
    def connectionMade(self):
        """Called when a connection is made."""
        # check ip
        # send DOWNLOAD/UPLOAD flag

    def send_file(self):
        """senf file on request"""
        # beginFileTransfer(self, file, consumer, transform=None)
        # deferred send COMPLETE

    def send_profile(self):
        """send profile on request"""
        # call send_file on profile file
        
# CLIENT
class PeerClientProtocol(PeerProtocol):
        
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
        
class PeerClientFactory(ClientFactory):

    protocol = PeerClientProtocol

    def __init__(self):
        # remote address
        # upload/download flag

    def clientConnectionFailed(self, connector, reason):
        """Called when a connection has failed to connect."""
        # clean dictionaries of client/server in upper lever

    def get_file(self):
        """in case no server at the other end: server used as 'client' to get a file"""
        # connect specific server
        # send command of download
        # ask for file

    def get_profile(self):
        """in case no server at the other end: server used as 'client' to get profile"""
        # call get_file on profile file

    def upload_file(self):
        """when no server running, peer uses 'client' to upload the requested file"""
        # check file is shared
        # check ip
        # connect remote server

# SERVER
class PeerServerProtocol(PeerProtocol):
        
    def lineReceived(self, line):
        """Override this for when each line is received."""
        # UPLOAD
        #     if not upload, lose connection
        #     change mode
        #     send READY
        # COMPLETE
        #     switch back to line mode
        #     reset status
        # DOWNLOAD
        #     if not download, lose connection
        # READY
        #     call [send_profile, send_file]
        #     set callbacks
        
    def rawDataReceived(self, data):
        """called upon upload of a file, when server acting as a client"""
        # check that serverFactory.get_file has been called
        # clearLineBuffer
        # store file
        # call send_file on profile file

class PeerServerFactory(ServerFactory):
    """server listening on known port. It will spawn a dedicated server on new connection"""

    protocol = PeerServerProtocol

    def __init__(self):
        # remote address

    def start_listening(self):
        """open well-known server of profiles"""
        pass

    def stop_listening(self):
        """shutdown well-known server"""
        pass

    def get_file(self):
        """in case no server at the other end: server used as 'client' to get a file"""
        # connect UDP
        # send command of connection
        # other part connects and upload file

    def get_profile(self):
        """in case no server at the other end: server used as 'client' to get profile"""
        # call get_file on profile file
