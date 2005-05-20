"""client server module for file sharing"""

import socket
import sys

from twisted.internet.protocol import ClientFactory, ServerFactory
from twisted.internet import reactor, defer
from twisted.protocols import basic

from solipsis.services.profile import FREE_PORTS

# messages

REQ_CLIENT_CONNECT = ""
MSG_CLIENT_ACK = ""

MSG_SERVER_ID = ""

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

def get_free_port():
    """return available port on localhost"""
    free_port = FREE_PORTS.pop()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        
    try:
        # connect to the given host:port
        sock.bind(("127.0.0.1", free_port))
    except socket.error:
        free_port = get_free_port()
    else:
        sock.close()
    return free_port

def release_port(port):
    """call when server stops listening"""
    FREE_PORTS.append(port)

def defer_download(deferred):
    """add method abort on a deferred object"""
    def abort():
        """closing active download"""
        # TODO: what behavior expected with download in progress ?
        pass
    setattr(deferred, 'abort', abort)
    return deferred

class NetworkManager:
    """high level class managing clients and servers for each peer"""

    def __init__(self, known_port, service_api):
        # servers
        self.client = ProfileClientFactory(self, service_api)
        self.server = ProfileServerFactory(self, known_port)
        # {peer_id: [downloads]}
        self.deferreds = {}
        # {peer_id: remote_ip}
        self.remote_ips = {}

    def start_listening(self):
        """launching main server listening to well-known port"""
        # delegate to ProfileServerFactory
        self.server.start_listening()

    def stop_listening(self):
        """stops main server and desactivate profile sharing"""
        # delegate to ProfileServerFactory
        self.server.stop_listening()
        for peer_id in self.deferreds:
            self.on_lost_peer(peer_id)

    def on_new_peer(self, peer, service):
        """tries to connect to new peer"""
        # delegate connection to ProfileClientFactory
        ip, port = parse_address(service.address)
        self.deferreds[peer.id_] = []
        self.remote_ips[peer.id_] = ip
        self.client.connect_peer(peer.id_, ip, port)

    def on_lost_peer(self, peer_id):
        """tries to connect to new peer"""
        self.clear_downloads(peer_id)
        del self.remote_ips[peer_id]

    def on_change_peer(self, peer, service):
        """tries to connect to new peer"""
        # delegate connection to ProfileClientFactory
        self.on_lost_peer(peer.id_)
        self.on_new_peer(peer, service)

    def get_downloads(self, peer_id):
        """return list of deferred corresponding to active downloads"""
        return self.deferreds.get(peer_id, [])

    def add_download(self, peer_id, deferred):
        """enqueue download"""
        self.deferreds[peer_id].append(defer_download(deferred))

    def clear_downloads(self, peer_id):
        """clean list of deferred downloads"""
        for download in self.deferreds[peer_id]:
            download.abort()
        del self.deferreds[peer_id]

    def on_service_data(self, peer_id, data):
        """demand to establish connection from peer that failed to
        connect through TCP"""
        # REQUEST_TCP
        if data.startswith(REQ_CLIENT_CONNECT):
            # get remote information
            r_ip, r_port = parse_address(data[len(REQ_CLIENT_CONNECT):])
            assert r_ip ==self.remote_ips[peer_id], "incoherent ip"
            # check status
            client = self.client.create_dedicated_client(\
                self.remote_ips[peer_id])
            client.set_remote(peer_id, r_port)
            # connect TCP
            client.connect()
        else:
            print "unexpected data:", data

    def get_profile(self, peer_id, display_callback):
        """retreive peer's profile"""
        # profile is download automatically on peer aproach: check completion
        # if running: DEFERRED: add display callback 
        # if done, display profile content
        pass

    def get_blog(self, peer_id, display_callback):
        """retreive peer's blog"""
        # ask for blog page
        # DEFERRED: add display callback 
        pass

    def get_file(self, peer_id, file_name):
        """retreive file"""
        # get existing connection (client or uploading-server)
        # calls get_file on it
        pass
    
# WELL-KNOWN PORTS: main gate
#-----------------
# CLIENT
class ProfileClientProtocol(basic.LineOnlyReceiver):
    """Intermediate client checking that a remote server exists."""

    def lineReceived(self, line):
        """incomming connection from other peer"""
        # on greeting, stores info about remote host (profile id)
        if line.startswith(MSG_SERVER_ID):
            # get remote information
            remote_host, known_port = self.transport.getPeer()
            peer_id, remote_port = parse_address(line[len(MSG_SERVER_ID):])
            # store remote information
            client = self.factory.create_dedicated_client(remote_host)
            client.set_remote(peer_id, remote_port)
        else:
            print "client received unexpected line:", line
        # acknowledge
        self.transport.sendLine(MSG_CLIENT_ACK)
        
    def connectionMade(self):
        """a peer has connected to us"""
        # stores server address
        remote_host, remote_port = self.transport.getPeer()
        self.factory.create_dedicated_client(remote_host)

class ProfileClientFactory(ClientFactory):
    """client connecting on known port thanks to TCP. call UDP on failure."""

    protocol = ProfileClientProtocol

    def __init__(self, manager, service_api):
        # service api (UDP transports)
        self.manager = manager
        self.service_api = service_api
        # remote info: {ips: client}
        self.connectors = {}
        self.dedicated_clients = {}

    def connect_peer(self, peer_id, remote_ip, known_port):
        """open connection to peer"""
        # if client already defined, calls its connect method
        # otherwise, tries connectTCP on well-known port
        if not self.dedicated_clients.has_key(remote_ip):
            self.connectors[remote_ip] = self._connect_tcp(remote_ip, known_port)
        else:
            self.dedicated_clients[remote_ip].connect()

    def disconnect_peer(self, remote_ip):
        """close open connection"""
        if self.connectors.has_key(remote_ip):
            self.connectors[remote_ip].disconnect()
            del self.connectors[remote_ip]
        
    def create_dedicated_client(self, remote_ip):
        """returns client assigned to remote_ip"""
        if not self.dedicated_clients.has_key(remote_ip):
            client = PeerClientFactory(self, remote_ip)
            self.dedicated_clients[remote_ip] = client
            return client
        else:
            return self.dedicated_clients[remote_ip]
        
    def _connect_tcp(self, remote_ip, port):
        """tries TCP server on well-known port"""
        #connect
        return reactor.connectTCP(remote_ip, port, self)

    def _connect_udp(self, remote_ip):
        """declares itself through UDP when could not connect through TCP"""
        # get address of local server
        server = self.manager.server.get_local_server(remote_ip)
        # use service_api to send data through nodes
        self.service_api.SendData(remote_ip, "%s %s:%d"\
                                  % (REQ_CLIENT_CONNECT, remote_ip, server.port))

    def clientConnectionFailed(self, connector, reason):
        """on TCP failure, use udp"""
        protocol, remote_ip, remote_port = connector.getDestination()
        self.disconnect_peer(remote_ip)
        self._connect_udp(remote_ip)
        
    def lose_dedicated_client(self, remote_ip):
        """clean dedicated client to remote_ip"""
        if self.dedicated_clients.has_key(remote_ip):
            self.dedicated_clients[remote_ip].stopFactory()
            del self.dedicated_clients[remote_ip]
    
# SERVER
class ProfileServerProtocol(basic.LineOnlyReceiver):
    """Shake hand protocol willing to switch to dedicated server"""

    def lineReceived(self, line):
        """incomming connection from other peer"""
        if line.startswith(MSG_CLIENT_ACK):
            self.loseConnection()
        else:
            print "server received unexpected line:", line            
            
    def connectionMade(self):
        """a peer has connect to us"""
        # great peer (with transport.getHost and profile.id_)
        remote_ip, remote_port = self.transport.getPeer()
        local_ip, local_port = self.transport.getHost()
        server = self.factory.get_local_server(remote_ip)
        self.transport.sendLine("%s %s:%d"\
                                % (MSG_SERVER_ID, local_ip, server.port))

class ProfileServerFactory(ServerFactory):
    """server listening on known port. It will spawn a dedicated
    server on new connection"""

    protocol = ProfileServerProtocol

    def __init__(self, manager, local_port):
        # servers info
        self.manager = manager
        self.port = local_port
        # {ips: server}
        self.local_servers = {}
        # listener
        self.listener = None

    def start_listening(self):
        """launch well-known server of profiles"""
        self.listener = reactor.listenTCP(self.port, self)

    def stop_listening(self):
        """shutdown well-known server"""
        self.listener.stopListening()
        for remote_ip in self.local_servers:
            self.lose_local_server(remote_ip)

    def get_local_server(self, remote_ip):
        """return local server bound to owner of protocol"""
        if self.local_servers.has_key(remote_ip):
            # is server running
            return self.local_servers[remote_ip]
        else:
            # if not, spawn it
            local_port = get_free_port()
            new_server = PeerServerFactory(remote_ip, local_port)
            self.local_servers[remote_ip] = new_server
            new_server.start_listening()
            return new_server

    def lose_local_server(self, remote_ip):
        """clean local server listening to remote_ip"""
        if self.local_servers.has_key(remote_ip):
            self.local_servers[remote_ip].stop_listening()
            del self.local_servers[remote_ip]
        

# SPECIFIC PORTS: once we'be been through main gate, provides a little
# more privacy...
#---------------
# COMMON
class PeerProtocol(basic.FileSender, basic.LineReceiver):
    """common part of protocol between client and server"""
        
    def connectionLost(self, reason):
        """Called when the connection is shut down."""
        # check file complete
        self.factory.manager.clear_downloads()
        
    def connectionMade(self):
        """Called when a connection is made."""
        # check ip
        remote_host, remote_port = self.transport.getPeer()
        assert remote_host == self.factory.remote_ip, \
               "UNAUTHORIZED %s"% remote_host

    def send_file(self, file_object):
        """senf file on request"""
        # beginFileTransfer(self, file, consumer, transform=None)
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

    def __init__(self, manager, remote_ip):
        # remote address
        self.manager = manager
        self.remote_ip = remote_ip
        self.remote_port  = None
        self.peer_id = None

    def clientConnectionFailed(self, connector, reason):
        """Called when a connection has failed to connect."""
        # clean dictionaries of client/server in upper lever
        print "dedicated client to %s out"% self.peer_id
        self.manager._lose_dedicated_client(self.peer_id)

    def set_remote(self, peer_id, remote_port):
        """set host and port of remote server"""
        self.peer_id = peer_id
        self.remote_port = remote_port
        
    def connect(self):
        """connect to remote server"""
        # check initialized
        if not self.remote_port:
            return False
        # connect
        pass

    def get_file(self):
        """in case no server at the other end: server used as 'client'
        to get a file"""
        # connect specific server DOWNLOAD [file:// , profile:// , blog://]
        # receive file
        pass

    def upload_file(self):
        """when no server running, peer uses 'client' to upload the
        requested file"""
        # check file is shared
        # check ip
        # connect remote server UPLOAD
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

    def __init__(self, remote_ip, local_port):
        # remote address
        self.remote_ip = remote_ip
        self.port = local_port
        # listener
        self.listener = None
        
    def start_listening(self):
        """open local server of profiles"""
        self.listener = reactor.listenTCP(self.port)

    def stop_listening(self):
        """shutdown local server"""
        self.listener.stopListening()
        release_port(self.port)

    def get_file(self):
        """in case no server at the other end: server used as 'client'
        to get a file"""
        # connect UDP
        # send command of connection
        # other client uploads file
        pass
