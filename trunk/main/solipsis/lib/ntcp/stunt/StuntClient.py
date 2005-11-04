import struct, socket, time, logging, random, os

import twisted.internet.defer as defer
from twisted.internet import threads
from twisted.internet.protocol import Protocol, Factory

from ntcp.stunt.StuntProtocol import StuntProtocol

DefaultServers = [
    ('p-maul.rd.francetelecom.fr', 3478),
    ('new-host-2.mmcbill2', 3478),
]

CHANGE_NONE = struct.pack('!i',0)
CHANGE_PORT = struct.pack('!i',2)
CHANGE_IP = struct.pack('!i',4)
CHANGE_BOTH = struct.pack('!i',6)

class _NatType:
  """
  The NAT handler
  A NAT object to save the NAT's information (used just in STUNT class)
  """
  def __init__(self, type, useful=True, blocked=False, 
               _publicIp=None, _privateIp=None, _delta=0):
    
    self.type = type
    self.useful = useful
    self.blocked = blocked
    self.publicIp = _publicIp
    self.privateIp = _privateIp
    self.delta = _delta
    self.filter = None
    
  def __repr__(self):
    return '<NatType %s>'%(self.type)

class StuntClient(StuntProtocol, object):
  """
  Implements the STUNT discovery procedure to discover
  the NAT's configuration.  (see draft STUNT)
  """
  
  log = logging.getLogger("ntcp")

  publicIp = None
  privateIp = None
  delta = 0

  def __init__(self, servers=DefaultServers):
    super(StuntClient, self).__init__()
    self.deferred = defer.Deferred()
    self.localPort = 0
    self.localIp = socket.gethostbyname(socket.gethostname())
    self.privateIp = self.localIp
    self.state = '1a'
    self.natType = None
    for host, port in servers:
      try:
        self.servers = [(socket.gethostbyname(host), port)]
      except: pass
    self.serverAddress = servers[0]

  def connectionMade(self):
    self.sendMessage()
 
  def parseIfClient(self):
    """
    Control if the response is in the pending request

    @return int : 1 if is an good response, 0 otherwise
    """
    if self.tid in self._pending:
      del self._pending[self.tid]
      return 1
    return 0
  
  def startDiscovery(self):
    """
    Starts the discovery method (test1 - see diagram above)
    """
    print ''
    print '===================================================='
    print '>> STUNT'
    self.log.debug('>> Test 1a')
    # Chose a port for discovery
    self.localPort = random.randrange(49152, 65535)
    self.test(self.serverAddress)
    return self.d
  
  def portDiscovery(self, port):
    """
    Starts the dicovery method to know the situation for a given port
    just before a TCP connection (test 1 implemented)
    """
    self.localPort = port
    self.d = defer.Deferred()
    print ''
    print '===================================================='
    print '>> STUNT: Port discovery'
    self.state = '4'
    self.test(self.serverAddress)
    return self.d
  
  def sndBindingRequest(self):
    """
    Sends a Binding Request (see draft STUNT)
    """
    self.messageType = 'Binding Request'
    self.sndMessage()

  def sndCaptureRequest(self, attributes=()):
    """
    Sends a Capture Request (see draft STUNT)
    """
    self.messageType = 'Binding Request'
    self.messageType = 'Capture Request'
    self.sndMessage(attributes)
    
  def sndMessage(self, attributes=()):
    """
    Adds a tid to packet and call the funtion to pack it
    """
    self.tid = self.getRandomTID()
    self._pending[self.tid] = (time.time(), self.serverAddress)
    self.createMessage(attributes)

  def finishedStunt(self):
    pass

  def _resolveStunServers(self):
    # reactor.resolve the hosts!
    for host, port in self.servers:
      d = reactor.resolve(host)
      d.addCallback(lambda x,p=port: self.test1((x, p))) # x=host
      
# ---------------------------------------------------------------
# TEST (1, 2, 3) in STUNT protocol:  Binding Behaviour
# ---------------------------------------------------------------

  def test(self, remoteAddress):
    """Test 1 in STUNT"""
    self.sndBindingRequest()
    self.connect(remoteAddress, (self.localIp, self.localPort))
  
  def rcvBindingResponse(self):
    if self.state == '1a':
      self.handleState1a()
    elif self.state == '1b':
      self.handleState1b()
    elif self.state == '2':
      self.handleState2()
    elif self.state == '3':
      self.handleState3()
    elif self.state == '4':
      self.handleStateDiscover()
  
  def handleState1a(self):
    """
    Handle the response to test 1
    """
    if self.resdict['externalAddress'] == (self.localIp, self.localPort):
      # No NAT
      self.natType = _NatType('None', \
                              _publicIp=self.localIp, \
                              _privateIp=self.localIp)
      self.finishedStunt()
    else:
      # Start Test1 second time
      self.log.debug('>> Test 1b')
      self.state = '1b'
      self.publicIp = self.resdict['externalAddress'][0]
      self.previousExternalAddress = self.resdict['externalAddress']
      time.sleep(1)

      #-----------------------------------------------------------
      self.test(self.serverAddress) # ==> commented for the test
      #self.handleState1b()           # ==> for the test (comment it!!!)
      #-----------------------------------------------------------

  def handleState1b(self):
    """
    Handle the response to test 1 (second time)
    """
    if self.resdict['externalAddress'] != self.previousExternalAddress:
      # NAT Session Dependent
      self.delta = self.resdict['externalAddress'][1] - \
                   self.previousExternalAddress[1]
      self.natType = _NatType('SessionDependent', \
                              _publicIp=self.publicIp, \
                              _privateIp=self.privateIp)
      #self.startFileringDiscovery()
      self.finishedStunt()
    else:
      # Start Test 2
      self.log.debug('>> Test 2')
      self.state = '2'
      address = (self.serverAddress[0], self.resdict['_altStunAddress'][1])
      self.test(address)    

  def handleState2(self):
    """
    Handle the response to test 2
    """
    if self.resdict['externalAddress'] != self.previousExternalAddress:
      # NAT Address & Port Dependent
      self.delta = self.resdict['externalAddress'][1] - \
                   self.previousExternalAddress[1]
      self.natType = _NatType('AddressPortDependent', \
                              _publicIp=self.publicIp, \
                              _privateIp=self.privateIp, \
                              _delta=self.delta)
      #self.startFileringDiscovery()
      self.finishedStunt()
    else:
      # Start Test 3
      self.log.debug('>> Test 3')
      self.state = '3'
      address = self.resdict['_altStunAddress']
      self.test(address)    

  def handleState3(self):
    """
    Handles the response to test 3
    """
    if self.resdict['externalAddress'] != self.previousExternalAddress:
      # NAT Address Dependent
      self.delta = self.resdict['externalAddress'][1] - self.previousExternalAddress[1]
      self.natType = _NatType('AddressDependent', \
                              _publicIp=publicIp, \
                              _privateIp=privateIp, \
                              _delta=self.delta)
      #self.startFileringDiscovery()
      self.finishedStunt()
    else:
      # NAT Independent
      self.natType = _NatType('Independent', \
                              _publicIp=self.publicIp, \
                              _privateIp=self.privateIp)
      #self.startFileringDiscovery()
      self.finishedStunt()

  def handleStateDiscover(self):
    """
    Handles the responde to address discovery for successive TCP connection
    """
    print '====================================================\n'
    print ''
    self.finishedPortDiscovery(self.resdict['externalAddress'])
      
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# TEST (1, 2, 3) in STUNT protocol: Endpoint Filtering Behaviour
# This section is be created but not sufficently tested.
# It could be usefull for future improvements
# ---------------------------------------------------------------

  def startFileringDiscovery(self):
    
    self.factory = Factory()
    self.factory.protocol = TcpServer
    self.listen = 0
    
    attributes = ()
    self.localPort = random.randrange(7000, 7100)
    #self.listenPort = random.randrange(7000, 7100)
    self.listenPort = self.localPort
    self.log.debug('>> Filter: Test 2')
    attributes = attributes + ((0x0002, self.getPortIpList((self.publicIp,\
                                                           self.listenPort))),)
##     attributes = attributes + ((0x0003, CHANGE_BOTH),)
    self.state = 'f2' # It doesn't try test 1
    self.filterTest(self.serverAddress, attributes)
  
  def filterTest(self, remoteAddress, attributes = ()):
    """Test 1 in STUNT"""
    self.sndCaptureRequest(attributes)
    self.connect(remoteAddress, (self.localIp, self.localPort))
      
  def rcvCaptureResponse(self):
    if self.state == 'f1':
      self.handleFState1()
    elif self.state == 'f2':
      self.handleFState2()
    elif self.state == 'f3':
      self.handleFState3()

  def handleFState2(self):
    attributes = ()
    if self.receivedSYN == 0:
      self.log.debug('>> Filter: Test 3')
      self.state = 'f3'
      attributes = attributes + ((0x0003, CHANGE_PORT),)
      self.localPort = random.randrange(7000, 7100)
      self.filterTest(self.serverAddress, attributes)    
    else:
      self.natType.filter = 'EndpointIndependent'
      self.finishedStunt()

  def handleFState3(self):
    if self.receivedSYN == 0:
      self.natType.filter = 'EndpointAddressDependent'
      self.finishedStunt()
    else:
      self.natType.filter = 'EndpointAddressPortDependent'
      self.finishedStunt()
      
# ---------------------------------------------------------------
      
# ---------------------------------------------------------------
# In this section we have rewrite the function to menage a TCP connection
# This allows a better utilisation of the socket options (ttl, REUSE ADDRESS, timeout, ...)
# ---------------------------------------------------------------
  
  def connect(self, remoteAddress, localAddress):
    """
    Create and bind a socket.
    Connect to STUNT server
    """
    #create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Sets socket option to allow a fast reuse of the bound address
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind socket
    s.bind(localAddress)
    self.s = s
    # connect to STUNT server
    s.connect(remoteAddress)
    #self.connectionMade()
    self._sendMessage(s)

  def _sendMessage(self, s):
    """
    Sends a message on TCP connection
    """
    s.send(self.pkt)
    
    if self.state == '1a' or self.state == '1b' \
           or self.state == '2' or self.state == '3'\
           or self.state == '4': 
      self.recvMessage(s)
      
    if self.state == 'f1' or self.state == 'f2' or self.state == 'f3':
      # For endpoint filtering behavior
      if not self.listen:
        self.listen += 1
        self.closeSocket(s)
        self.reactor.listenTCP(self.listenPort, self.factory)
        self.reactor.callLater(5, self.synNotReceived)
      
  def recvMessage(self, s):
    """
    Wait for a response message from STUNT server
    """
    data = s.recv(65535)
    self.closeSocket(s)
    self.dataReceived(data)


        
  def closeSocket(self, s):
    """
    Close definitively a socket
    """
    try:
      s.shutdown(2)
      s.close
    except: pass

  def synReceived(self, (s, addr)):
    """
    Tests incoming SYN packet
    """
    print 'synReceived'
    self.closeSocket(s)
    if addr != '127.0.0.1' and addr != self.localIp:
      self.log.debug('synReceived')
      self.receivedSYN = 1
      self.rcvCaptureResponse()
    
  def synNotReceived(self):
    print 'Syn not received'
    self.transport.loseConnection()
    
##     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
##     s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
##     s.connect((self.localIp, self.localPort))
##     #self.closeSocket(s)
##     self.closeSocket(sock)
    
    self.log.debug('synNotReceived')
    self.receivedSYN = 0
    #self.closeSocket(self.s)
    self.rcvCaptureResponse()

  def error(self, reason):
    pass
  
# ---------------------------------------------------------------
class TcpServer(Protocol):
    """
    All the Twisted functions for a TCP connection (c/s) 
    """
        
    def dataReceived(self, data):
        print '>>',data

    def connectionMade(self):
        print 'Connection Made...now you can receive data...'

    def connectionLost(self, reason):
        print 'Lost connection.  Reason:', reason

    def startedConnecting(self, connector):
        pass
    
    def buildProtocol(self, addr):
        return self
        
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
    

# ---------------------------------------------------------------


##########################################################
##
## Binding Behaviour
##
##                               /\
##              +--------+      /  \ N    +--------+
##              | Test 1 |---->/Addr\---->| Test 1 |
##              +--------+     \Same/     +--------+
##                              \? /          |
##                               \/           |
##                                | Y         |
##                                V           V
##                  /\         No NAT         /\
##                 /  \                      /  \
##              N /Bind\     +--------+   Y /Bind\
##    NB=ADP <----\Same/<----| Test 2 |<----\Same/
##                 \? /      +--------+      \? /
##                  \/                        \/
##                   | Y                       | N
##                   |                         V
##                   V            /\         NB=SD
##               +--------+      /  \ N
##               | Test 3 |---->/Bind\----> NB=AD
##               +--------+     \Same/
##                               \? /
##                                \/
##                                 | Y
##                                 |
##                                 V
##                               NB=I
##
##########################################################
        
##########################################################
##
## Endpoint Filtering Behaviour
##
##                               /\
##              +--------+      /  \ N    +--------+
##              | Test 1 |---->/Recv\---->| Test 2 |
##              +--------+     \ SYN/     +--------+
##                              \? /          |
##                               \/           |
##                                | Y         |
##                                V           |
##                              EF=O         /\
##                 /\                       /  \
##              Y /  \      +--------+   N /Recv\
##    EF=AD <----/Recv\<----| Test 3 |<----\ SYN/
##               \ SYN/     +--------+      \? /
##                \? /                       \/
##                 \/                         | Y
##                 | N                        V
##                 V                        EF=I
##               EF=ADP
##
##
##########################################################
