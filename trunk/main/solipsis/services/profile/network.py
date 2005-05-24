"""client server module for file sharing"""

import socket
import threading

from twisted.internet.protocol import ClientFactory, ServerFactory
from twisted.internet import reactor
from twisted.protocols import basic

from solipsis.services.profile import FREE_PORTS

TIMEOUT = 60

# messages
CLIENT_SEND_ACK = "CONNECTED"
SERVER_SEND_ID = "SERVER_ID"
MESSAGE_HELLO = "HELLO"
MESSAGE_PROFILE = "REQUEST_PROFILE"
MESSAGE_BLOG = "REQUEST_BLOG"
MESSAGE_FILES = "REQUEST_FILES"
MESSAGE_ERROR = "UPLOAD_IMPOSSIBLE"

SERVICES_MESSAGES = [MESSAGE_HELLO, MESSAGE_PROFILE,
                     MESSAGE_BLOG, MESSAGE_FILES,
                     MESSAGE_ERROR]

# TODO: common method with avatar.plugin._ParserAddress... how about putting it
# into global service? How generic is it?
def parse_address(address):
    """Parse network address as supplied by a peer.
    Returns a (host, port) tuple."""
    try:
        items = address.split(':')
        if len(items) != 2:
            raise ValueError("address %s expected as host:port"% address)
        host = str(items[0]).strip()
        port = int(items[1])
        if not host:
            raise ValueError("no host in %s"% address)
        if port < 1 or port > 65535:
            raise ValueError("port %d should be in [1, 65535]"% port)
        return host, port
    except ValueError:
        raise ValueError("address %s not valid"% address)

def parse_service_data(message):
    """extract command, address and data from message.

    Expected format: MESSAGE host:port data
    returns [COMMAND, HOST, port, DATA"""
    result = []
    # 2 maximum splits: data may contain spaces
    items = message.split(' ', 2)
    message = items[0]
    # check command
    if message not in SERVICES_MESSAGES:
        raise ValueError("%s should be in %s"% (message, SERVICES_MESSAGES))
    result.append(message)
    # check address
    result += parse_address(items[1])
    # check data
    if len(items) > 2:
        data = items[2]
        result.append(data)
    else:
        result.append(None)
    return result

def make_message(command, host, port, data=''):
    """format message to be sent via service_api"""
    message = "%s %s:%d %s"% (command, host, port, data)
    print "sending api", message
    return message

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

    def __init__(self, host, known_port, service_api):
        # service socket
        self.host = host
        self.port = known_port
        self.service_api = service_api
        # server and client manager (listening to known port and
        # spawing dedicated servers / clients
        self.client = ProfileClientFactory(self, service_api)
        self.server = ProfileServerFactory(self, host, known_port)
        # {peer_id: remote_ip}
        self.remote_ips = {}
        # {peer_id: [downloads]}
        self.deferreds = {}

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

    def disconnect(self):
        self.client.disconnect()

    def on_new_peer(self, peer, service):
        """tries to connect to new peer"""
        # parse address, set up information in cache
        ip, port = parse_address(service.address)
        self.deferreds[peer.id_] = []
        self.remote_ips[peer.id_] = ip
        # declare known port to other peer throug service_api
        message = make_message(MESSAGE_HELLO, self.host, self.port)
        self.service_api.SendData(peer.id_, message)

    def on_lost_peer(self, peer_id):
        """tries to connect to new peer"""
        # TODO: do this cleanup after a TIMEOUT
        # close connections and clean server
        self.server.lose_local_server(self.remote_ips[peer_id])
        self.client.lose_dedicated_client(self.remote_ips[peer_id])
        # clean cache
        self.clear_downloads(peer_id)
        del self.remote_ips[peer_id]

    def on_change_peer(self, peer, service):
        """tries to connect to new peer"""
        r_ip, r_port = parse_address(service.address)
        if r_ip != self.remote_ips[peer.id_]:
            self.on_lost_peer(peer.id_)
            self.on_new_peer(peer, service)
        else:
            print "peer moved"

    def on_service_data(self, peer_id, data):
        """demand to establish connection from peer that failed to
        connect through TCP"""
        print "api received", data
        try:
            # parse message
            command, r_ip, r_port, data = parse_service_data(data)
            assert r_ip == self.remote_ips[peer_id], \
                   "incoherent ip %s instead of %s"\
                   % (r_ip, self.remote_ips[peer_id])
            dedicated_client = self.client.\
                               get_dedicated_client(self.remote_ips[peer_id])
            # making tcp connection
            if command == MESSAGE_HELLO:
                self.client.connect_tcp(r_ip, r_port)
            # upload
            elif command == MESSAGE_PROFILE:
                dedicated_client and dedicated_client.upload_profile() \
                                 or self._upload_impossible(peer_id, r_ip, r_port)
            elif command == MESSAGE_BLOG:
                dedicated_client and dedicated_client.upload_blog() \
                                 or self._upload_impossible(peer_id, r_ip, r_port)
            elif command == MESSAGE_FILES:
                dedicated_client and dedicated_client.upload_files(data) \
                                 or self._upload_impossible(peer_id, r_ip, r_port)
            # fail to upload
            elif command == MESSAGE_ERROR:
                print "peer could not connect to server"
            # exceptions...
            else:
                print "unexpected command %s"% command
        except ValueError, err:
            print "ERROR:", err
        except AssertionError, err:
            print "ERROR Client corrupted:", err

    def get_profile(self, peer_id, callback):
        """retreive peer's profile"""
        client = self.client.get_dedicated_client(self.remote_ips[peer_id])
        if client:
            client.get_profile(callback)
        else:
            server = self.server.get_local_server(self.remote_ips[peer_id])
            if server:
                message = make_message(MESSAGE_PROFILE, self.host, server.port)
                self.manager.service_api.SendData(peer_id, message)
                # FIXME set callback
            else:
                print "DOWNLOAD PROFILE IMPOSSIBLE"

    def get_blog(self, peer_id, display_callback):
        """retreive peer's blog"""
        client = self.client.get_dedicated_client(self.remote_ips[peer_id])
        if client:
            client.get_blog(callback)
        else:
            server = self.server.get_local_server(self.remote_ips[peer_id])
            if server:
                message = make_message(MESSAGE_BLOG, self.host, server.port)
                self.manager.service_api.SendData(peer_id, message)
                # FIXME set callback
            else:
                print "DOWNLOAD BLOG IMPOSSIBLE"

    def get_files(self, peer_id, files, callback):
        """retreive file"""
        client = self.client.get_dedicated_client(self.remote_ips[peer_id])
        if client:
            client.get_files(files, callback)
        else:
            server = self.server.get_local_server(self.remote_ips[peer_id])
            if server:
                file_names = ','.join(files)
                message = make_message(MESSAGE_PROFILE, self.host, server.port,
                                       file_names)
                self.manager.service_api.SendData(peer_id, message)
                # FIXME set callback
            else:
                print "DOWNLOAD FILES IMPOSSIBLE"

    def _upload_impossible(self, peer_id, remote_ip, remote_port):
        """notify via udp that upload is not possible"""
        message = make_message(MESSAGE_ERROR, remote_ip, remote_port)
        self.service_api.SendData(peer_id, message)
        print "UPLOAD IMPOSSIBLE"

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

    
# WELL-KNOWN PORTS: main gate
#-----------------
# CLIENT
class ProfileClientProtocol(basic.LineOnlyReceiver):
    """Intermediate client checking that a remote server exists."""

    def lineReceived(self, line):
        """incomming connection from other peer"""
        print "received", line
        # on greeting, stores info about remote host (profile id)
        if line.startswith(SERVER_SEND_ID):
            # get remote information
            protocol, remote_host, known_port = self.transport.getPeer()
            peer_id, remote_port = parse_address(line[len(SERVER_SEND_ID):])
            # store remote information
            client = self.factory.get_dedicated_client(remote_host)
            client.set_remote(peer_id, remote_port)
        else:
            print "client received unexpected line:", line
        # acknowledge
        self.sendLine(CLIENT_SEND_ACK)
        
    def connectionMade(self):
        """a peer has connected to us"""
        # create dedicated client
        protocol, remote_host, remote_port = self.transport.getPeer()
        self.factory.create_dedicated_client(remote_host)

    def connectionLost(self):
        """switch to dedicated client and ask for profile"""
        # get dedicated client
        protocol, remote_host, remote_port = self.transport.getPeer()
        client = self.factory.get_dedicated_client(remote_host)
        # download profile
        client.get_profile()

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

    def disconnect(self):
        """close all connection"""
        for peer_id in self.connectors:
            self.disconnect_tcp(peer_id)
        for client in self.dedicated_clients.values():
            client.disconnect()
        
    def connect_tcp(self, remote_ip, port):
        """tries TCP server on well-known port"""
        return reactor.connectTCP(remote_ip, port, self)

    def disconnect_tcp(self, remote_ip):
        """close open connection"""
        if self.connectors.has_key(remote_ip):
            self.connectors[remote_ip].disconnect()
            del self.connectors[remote_ip]
        else:
            print "already disconnected"
        
    def create_dedicated_client(self, remote_ip):
        """returns client assigned to remote_ip"""
        if not self.dedicated_clients.has_key(remote_ip):
            client = PeerClientFactory(self, remote_ip)
            self.dedicated_clients[remote_ip] = client
        else:
            print "already created"
        
    def get_dedicated_client(self, remote_ip):
        """returns client assigned to remote_ip"""
        return self.dedicated_clients.get(remote_ip, None)

    def clientConnectionFailed(self, connector, reason):
        """on TCP failure, use udp"""
        # clean cache
        protocol, remote_ip, remote_port = connector.getDestination()
        self.disconnect_tcp(remote_ip)
        # 'download' profile through server
        self.manager.get_profile()
        
    def lose_dedicated_client(self, remote_ip):
        """clean dedicated client to remote_ip"""
        self.disconnect_tcp(remote_ip)
    
# SERVER
class ProfileServerProtocol(basic.LineOnlyReceiver):
    """Shake hand protocol willing to switch to dedicated server"""

    def lineReceived(self, line):
        """incomming connection from other peer"""
        if line.startswith(CLIENT_SEND_ACK):
            self.connectionLost(reason = "switch to dedicated server")
        else:
            print "server received unexpected line:", line            
            
    def connectionMade(self):
        """a peer has connect to us"""
        # great peer (with transport.getHost and profile.id_)
        protocol, remote_ip, remote_port = self.transport.getPeer()
        protocol, local_ip, local_port = self.transport.getHost()
        server = self.factory.get_local_server(remote_ip)
        self.sendLine("%s %s:%d"\
                      % (SERVER_SEND_ID, local_ip, server.port))
        print "sending %s %s:%d"% (SERVER_SEND_ID, local_ip, server.port)

class ProfileServerFactory(ServerFactory):
    """server listening on known port. It will spawn a dedicated
    server on new connection"""

    protocol = ProfileServerProtocol

    def __init__(self, manager, host, local_port):
        # servers info
        self.manager = manager
        self.host = host
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
            new_server = PeerServerFactory(self.manager, remote_ip, local_port)
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
        
    def connectionMade(self):
        """Called when a connection is made."""
        # check ip
        protocol, remote_host, remote_port = self.transport.getPeer()
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
        print "received", line
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
        self.connector = None

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
        if self.remote_port:
            self.connector = reactor.connectTCP(self.remote_ip,
                                                self.remote_port, self)
            return True
        return False

    def disconnect(self):
        """close connection with server"""
        if self.connector:
            self.connector.disconnect()

    def get_profile(self):
        """download peer profile. Automatically called on client creation"""
        # check download started / in progress / finished
        # flag download
        # do download
        pass
            
    def get_file(self):
        """in case no server at the other end: server used as 'client'
        to get a file"""
        # connect specific server DOWNLOAD [file:// , profile:// , blog://]
        # receive file
        pass

    def upload_profile(self):
        """when no server running, peer uses 'client' to upload the
        requested file"""
        # check file is shared
        # check ip
        # connect remote server UPLOAD
        pass

    def upload_blog(self):
        """when no server running, peer uses 'client' to upload the
        requested file"""
        # check file is shared
        # check ip
        # connect remote server UPLOAD
        pass

    def upload_files(self, files):
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
        print "received", line
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

    def __init__(self, manager, remote_ip, local_port):
        self.manager = manager
        # remote address
        self.remote_ip = remote_ip
        self.port = local_port
        # listener
        self.listener = None
        
    def start_listening(self):
        """open local server of profiles"""
        self.listener = reactor.listenTCP(self.port, self)

    def stop_listening(self):
        """shutdown local server"""
        self.listener.stopListening()
        release_port(self.port)
