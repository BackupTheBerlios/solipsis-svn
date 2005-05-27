"""client server module for file sharing"""

import socket
import threading
import tempfile

from twisted.internet.protocol import ClientFactory, ServerFactory
from twisted.internet import reactor
from twisted.protocols import basic

from solipsis.services.profile import FREE_PORTS
from solipsis.services.profile.document import FileDocument

TIMEOUT = 60

# messages
CLIENT_SEND_ACK = "CONNECTED"
SERVER_SEND_ID = "SERVER_ID"

MESSAGE_HELLO = "HELLO"
MESSAGE_PROFILE = "REQUEST_PROFILE"
MESSAGE_BLOG = "REQUEST_BLOG"
MESSAGE_FILES = "REQUEST_FILES"
MESSAGE_ERROR = "UPLOAD_IMPOSSIBLE"

ASK_DOWNLOAD_FILES = "DOWNLOAD_FILES"
ASK_DOWNLOAD_BLOG = "DOWNLOAD_BLOG"
ASK_DOWNLOAD_PROFILE = "DOWNLOAD_PROFILE"
COMPLETE_DOWNLOAD_FILES = "COMPLETE_FILES"
COMPLETE_DOWNLOAD_BLOG = "COMPLETE_BLOG"
COMPLETE_DOWNLOAD_PROFILE = "COMPLETE_PROFILE"

ASK_UPLOAD = "UPLOAD"

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

def parse_message(message):
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
    print "sending", message
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

    def __init__(self, host, known_port, service_api, facade):
        # service socket
        self.host = host
        self.port = known_port
        self.service_api = service_api
        self.facade = facade
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
        for peer_id in self.deferreds.keys():
            self.on_lost_peer(peer_id)

    def disconnect(self):
        self.client.disconnect()

    def on_new_peer(self, peer, service):
        """tries to connect to new peer"""
        # parse address, 
        ip, port = parse_address(service.address)
        # set up information in cache
        self._init_peer(peer.id_, ip)
        # declare known port to other peer throug service_api
        message = make_message(MESSAGE_HELLO, self.host, self.port)
        self.service_api.SendData(peer.id_, message)

    def _init_peer(self, peer_id, ip):
        """set up cache for given peer"""
        self.deferreds[peer_id] = []
        self.remote_ips[peer_id] = ip

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
        try:
            # parse message
            command, r_ip, r_port, data = parse_message(data)
            # create client if necessary
            if not self.remote_ips.has_key(peer_id):
                self._init_peer(peer_id, r_ip)
            assert r_ip == self.remote_ips[peer_id], \
                   "incoherent ip %s instead of %s"\
                   % (r_ip, self.remote_ips[peer_id])
            # get dedicated client (or None if not yet initialized)
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
                self.service_api.SendData(peer_id, message)
                # FIXME set callback
            else:
                print "DOWNLOAD PROFILE IMPOSSIBLE"

    def get_blog(self, peer_id, callback):
        """retreive peer's blog"""
        client = self.client.get_dedicated_client(self.remote_ips[peer_id])
        if client:
            client.get_blog(callback)
        else:
            server = self.server.get_local_server(self.remote_ips[peer_id])
            if server:
                message = make_message(MESSAGE_BLOG, self.host, server.port)
                self.service_api.SendData(peer_id, message)
                # FIXME set callback
            else:
                print "DOWNLOAD BLOG IMPOSSIBLE"

    def get_files(self, peer_id, file_names, callback):
        """retreive file"""
        client = self.client.get_dedicated_client(self.remote_ips[peer_id])
        if client:
            client.get_files(file_names, callback)
        else:
            server = self.server.get_local_server(self.remote_ips[peer_id])
            if server:
                for file_name in file_names:
                    message = make_message(MESSAGE_PROFILE, self.host, server.port,
                                       file_name)
                    self.service_api.SendData(peer_id, message)
                # FIXME set callback
            else:
                print "DOWNLOAD FILES IMPOSSIBLE"

    def _on_profile_complete(self, document):
        """callback when autoloading of profile successful"""
        print "downloaded profile", document.get_pseudo()
        self.facade.fill_data((document.get_pseudo(), document))

    def _upload_impossible(self, peer_id, remote_ip, remote_port):
        """notify via udp that upload is not possible"""
        message = make_message(MESSAGE_ERROR, remote_ip, remote_port)
        self.service_api.SendData(peer_id, message)

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
        #print "received", line
        # on greeting, stores info about remote host (profile id)
        if line.startswith(SERVER_SEND_ID):
            # get remote information
            remote_host = self.transport.getPeer().host
            peer_id, remote_port = parse_address(line[len(SERVER_SEND_ID):])
            # store remote information
            client = self.factory.get_dedicated_client(remote_host)
            client.set_remote(peer_id, remote_port)
        else:
            print "client received unexpected line:", line
        # acknowledge
        self.sendLine(CLIENT_SEND_ACK)

    def sendLine(self, line):
        """overrides in order to ease debug"""
        #print "sending", line
        basic.LineOnlyReceiver.sendLine(self, line)  
        
    def connectionMade(self):
        """a peer has connected to us"""
        # create dedicated client
        remote_host = self.transport.getPeer().host
        self.factory.create_dedicated_client(remote_host)

    def connectionLost(self, reason):
        """switch to dedicated client and ask for profile"""
        # get dedicated client
        remote_host = self.transport.getPeer().host
        basic.LineOnlyReceiver.connectionLost(self, reason)
        client = self.factory.get_dedicated_client(remote_host)
        # download profile
        client.get_profile(self.factory.manager._on_profile_complete)

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
        remote_ip = connector.getDestination().host
        self.disconnect_tcp(remote_ip)
        
    def lose_dedicated_client(self, remote_ip):
        """clean dedicated client to remote_ip"""
        self.disconnect_tcp(remote_ip)
    
# SERVER
class ProfileServerProtocol(basic.LineOnlyReceiver):
    """Shake hand protocol willing to switch to dedicated server"""

    def lineReceived(self, line):
        """incomming connection from other peer"""
        #print "received", line
        if line.startswith(CLIENT_SEND_ACK):
            self.transport.loseConnection()
        else:
            print "server received unexpected line:", line 

    def sendLine(self, line):
        """overrides in order to ease debug"""
        #print "sending", line
        basic.LineOnlyReceiver.sendLine(self, line)           
            
    def connectionMade(self):
        """a peer has connect to us"""
        # great peer (with transport.getHost and profile.id_)
        remote_ip = self.transport.getPeer().host
        local_ip = self.transport.getHost().host
        server = self.factory.get_local_server(remote_ip)
        message = "%s %s:%d"% (SERVER_SEND_ID, local_ip, server.port)
        self.sendLine(message)

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
class PeerProtocol(basic.LineReceiver):
    """common part of protocol between client and server"""
        
    def connectionMade(self):
        """Called when a connection is made."""
        # check ip
        remote_host  = self.transport.getPeer().host
        assert remote_host == self.factory.remote_ip, \
               "UNAUTHORIZED %s"% remote_host

    def sendLine(self, line):
        """overrides in order to ease debug"""
        print "sending", line
        basic.LineReceiver.sendLine(self, line)
        
    def lineReceived(self, line):
        """specialised in Client/Server protocol"""
        raise NotImplementedError
    
    def rawDataReceived(self, data):
        """specialised in Client/Server protocol"""
        raise NotImplementedError

    # beginFileTransfer(self, file, consumer, transform=None)
        
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

    def rawDataReceived(self, data):
        """write file"""
        self.file.write(data)

    def connectionMade(self):
        """after ip is checked, begin connection"""
        PeerProtocol.connectionMade(self)
        self.setRawMode()
        # check action to be made
        if self.factory.download.startswith(ASK_DOWNLOAD_FILES):
            if self.factory.files:
                # TODO: check place to download and existing files
                # create file
                self.file = open(self.factory.files.pop(), "w+b")
                self.sendLine("%s %s"% (self.factory.download, self.factory.files.pop()))
            else:
                print "No more file to download!!"
        else:
            self.file = tempfile.NamedTemporaryFile()
            self.sendLine(self.factory.download)

    def _on_complete_profile(self):
        """callback when finished downloading profile"""
        self.file.seek(0)
        file_doc = FileDocument()
        file_doc.read(self.file)
        self.file.close()
        self.file = None
        self.factory.callback(file_doc)

    def _on_complete_blog(self):
        """callback when finished downloading blog"""
        pass

    def _on_complete_file(self):
        """callback when finished downloading file"""
        self.file.close()
        if self.factory.files:
            self.factory.connect()
        else:
            self.factory.callback()
        
    def connectionLost(self, reason):
        PeerProtocol.connectionLost(self, reason)
        if self.factory.download.startswith(ASK_DOWNLOAD_PROFILE):
            self._on_complete_profile()
        elif self.factory.download.startswith(ASK_DOWNLOAD_BLOG):
            self._on_complete_blog()
        elif self.factory.download.startswith(ASK_DOWNLOAD_FILES):
            self._on_complete_file()
        else:
            print "upload?", self.factory.download
        
class PeerClientFactory(ClientFactory):
    """client part of protocol"""

    protocol = PeerClientProtocol

    def __init__(self, manager, remote_ip):
        # remote address
        self.manager = manager
        self.remote_ip = remote_ip
        self.remote_port  = None
        self.peer_id = None
        # flag download/upload
        self.connector = None
        self.download = None
        self.callback = None

    def clientConnectionFailed(self, connector, reason):
        """Called when a connection has failed to connect."""
        # clean dictionaries of client/server in upper lever
        self.disconnect()
        self.manager.lose_dedicated_client(self.remote_ip)

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
            self.connector = None
            self.files = []

    # FIXME: tie download & callback to protocol...
    def get_profile(self, callback):
        """download peer profile using self.get_file. Automatically called on client creation"""
        self.download = ASK_DOWNLOAD_PROFILE
        self.callback = callback
        if not self.connect():
            self.download = None
            print "could not connect"
            
    def get_blog(self, callback):
        """donload blog file using self.get_file"""
        self.download = ASK_DOWNLOAD_BLOG
        self.callback = callback
        if not self.connect():
            self.download = None
            print "could not connect"
            
    def get_files(self, callback, file_names):
        """download given list of file"""
        for file_name in file_names:
            self.files.append(file_name)
        self.download = ASK_DOWNLOAD_FILES
        self.callback = callback
        if not self.connect():
            self.download = None
            del self.files[:]
            print "could not connect"

    def upload_profile(self):
        """when no server running, peer uses 'client' to upload the
        requested file"""

    def upload_blog(self):
        """when no server running, peer uses 'client' to upload the
        requested file"""
        # check file is shared
        # check ip
        # connect remote server UPLOAD
        self.download = False

    def upload_files(self, files):
        """when no server running, peer uses 'client' to upload the
        requested file"""
        # check file is shared
        files = self.manager.facade.get_files()
        # connect remote server UPLOAD
        self.download = False

# SERVER
class PeerServerProtocol(PeerProtocol):
    """server part of protocol"""
        
    def lineReceived(self, line):
        """Override this for when each line is received."""
        print "received", line
        # donwnload file
        if line == ASK_DOWNLOAD_FILES:
            file_name = line[len(ASK_DOWNLOAD_FILES)+1:].strip()
            file_container = self.factory.manager.facade.get_file_container(file_name)
            # check exists
            if file_container.has_key(file_name):
                file_desc = file_container[file_name]
                # check shared
                if file_desc._shared:
                    deferred = basic.FileSender().beginFileTransfer(open(file_name), self.transport)
                else:
                    print "permission denied"
            else:
                print "unknown file %s"% file_name
        # donwnload blog
        if line == ASK_DOWNLOAD_BLOG:
            pass
#             file_name = self.factory.manager.facade.get_blog_obj()
#             deferred = basic.FileSender().beginFileTransfer(open(file_name), self.transport)
        # donwnload profile
        if line == ASK_DOWNLOAD_PROFILE:
            file_obj = self.factory.manager.facade.get_profile_obj()
            deferred = basic.FileSender().beginFileTransfer(file_obj, self.transport)
            deferred.addCallback(lambda x: self.transport.loseConnection())
        elif line == ASK_UPLOAD:
            # DOWNLOAD file:// | profile://
            # if not download, lose connection
            # send file
            pass
        # COMPLETE
        #     switch back to line mode
        #     reset status
        #     write file / store profile and flag completion
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
        # file transfered
        self.files = []
        
    def start_listening(self):
        """open local server of profiles"""
        self.listener = reactor.listenTCP(self.port, self)

    def stop_listening(self):
        """shutdown local server"""
        self.listener.stopListening()
        release_port(self.port)
