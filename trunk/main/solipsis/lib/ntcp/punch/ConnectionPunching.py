import struct, socket, time, logging, random, os, sys

from twisted.internet.protocol import Protocol, Factory, ClientFactory
import twisted.internet.defer as defer
import twisted.python.failure as failure
from twisted.internet import reactor
from twisted.internet import threads

class ConnectionPunching(Protocol, ClientFactory, object):
  """
  This class chooses, in function of the NAT information,
  the method to use for the connection and implements it.
  If the connection established the twisted methods
  are called to menage the TCP connection
  """
  
  log = logging.getLogger("ntcp")
  
  def __init__(self, punch = None, _s = None):      
      self.factory = None
      self._super = _s
      self.method = None
      self.connected = 0
      self.attempt = 0
      self.sameLanAttempt = 1
      self.t = 5
      self.peerConn = None #  An object implementing IConnector.
      self.timeout = None
      self.error = 0
      self.stunt = 0

      try:
        if punch != None and punch.natObj:
          self.init_puncher_var(punch)
      except: pass

  def init_puncher_var(self, punch):
    """
    Initialise all the variables from puncher object

    @param punch: the ntcp.punch.Puncher object
    """
    if punch != None:
      self.punch = punch
      self.reactor = punch.reactor
      self.punchListen = punch.punchListen
      self.cbAddress = punch.cbAddress
      
      self.remoteUri = punch.remoteUri
      self.remotePublicAddress = punch.remotePublicAddress
      self.remotePrivateAddress = punch.remotePrivateAddress
      self.remoteNatType = punch.remoteNatType
      
      #self.remoteUri = punch.remoteUri
      self.publicAddress = punch.publicAddr
      self.privateAddress = punch.privateAddr
      self.natType = punch.natObj.type

      self.requestor = punch.requestor
      self.d = punch.d
      self.d_conn = punch.d_conn
      self.error = punch.error
  
  def natTraversal(self, factory=None):
    """
    Chooses the right method for NAT traversal TCP
    """
    if factory != None:
      self.factory = factory
      
    self.attempt = 0
    
    if self.publicAddress[0] == self.remotePublicAddress[0] \
           and self.sameLanAttempt:
      # The two endpoints are in the same LAN
      # but there can be several NATs
      self.method = 'sameLan'
      self.sameLan()
    elif self.natType == 'None' or self.remoteNatType == 'None':
      # One peers is not behind a NAT
      self.oneNat()            
    else:
      # Call the STUNT2 method implementation
      self.method = 'stunt2'
      self.stunt2()

  def setFactory(self, factory):
    """
    Sets the Factory
    
    @param factory: a twisted.internet.protocol.Factory instance 
    """
    self.factory = factory
    
  def getFactory(self):
    """
    Gets the Factory 

    @return factory: a twisted.internet.protocol.Factory instance 
    """
    return self.factory
  
# ----------------------------------------------------------
# Methods implementation
# ----------------------------------------------------------

# ----------------------------------------------------------
  def sameLan(self):
      """
      This method is called when the peers are in the same LAN.
      Multiple layers of NATs can be present in the same LAN
      and this method could fail if the peers are behind
      different internal NATs.
      """
      print 'Endpoints in the same LAN.'
      if self.requestor:
          self.transport = None
          self.peerConn = self.reactor.connectTCP(\
                  self.remotePrivateAddress[0], \
                  self.remotePrivateAddress[1], self)
      else:
          # listen
          print 'Same LAN: listen on:', self.privateAddress[1]
          self.transport = None
          self.peerConn = self.reactor.listenTCP(\
              self.privateAddress[1], self)
          self.sameLanAttempt = 0
          self.timeout = self.reactor.callLater(\
              6, self._sameLan_clientConnectionFailed)
          
  def _sameLan_clientConnectionFailed(self):
      if self.requestor:
          if self.attempt <= 3:
              # connect
              time.sleep(self.attempt)
              self.attempt = self.attempt + 1
              self.sameLan()
          else:
              self.sameLanAttempt = 0
              self.natTraversal()
      else:
          # listen
          self.natTraversal()

  def oneNat(self):
      """
      One peers is not behind a NAT
      The user not NAT'ed starts a TCP server
      The other starts a client connection
      """
      #self.log.debug('One endpoint is not NATed')
      print 'One endpoint is not NATed'
      if self.natType != 'None':
          self.transport = None
          self.peerConn = self.reactor.connectTCP(\
                  self.remotePrivateAddress[0], \
                  self.remotePrivateAddress[1], self)
      else:
          # listen
          print 'One NAT: listen on:', self.privateAddress[1]
          self.transport = None
          self.peerConn = self.reactor.listenTCP(\
              self.privateAddress[1], self)
           
  def _oneNat_clientConnectionFailed(self):
    """
    The connection with one NAT failed.
    Try the NAT traversal methods
    """
    if self.natType != 'None':
      if self.attempt <= 3:
        # connect
        time.sleep(self.attempt)
        self.attempt = self.attempt + 1
        self.oneNat()
      else:
        self.stunt2()
    else:
      # listen
      pass

  def stunt2(self):
      """
      STUNT 2 implementation.
      """
      if self.requestor:
        # Here I try just several client connection
        print 'STUNT2:Connect -> from:', self.privateAddress, \
              'to:', self.remotePublicAddress
        
        self.transport = None
        self.peerConn = self.reactor.connectTCP(\
                  self.remotePublicAddress[0], \
                  self.remotePublicAddress[1], \
                  self, \
                  timeout = 1, \
                  bindAddress=self.privateAddress)
        
        # Try several connect for t seconds
        if self.method == 'stunt2' and self.timeout == None:
          self.timeout = reactor.callLater(self.t, self.stopConnect)
        elif self.method == 'stunt2_inv' and self.timeout == None:
          self.timeout = reactor.callLater(self.t, self.stopConnect)
          
      else:
        # Here I try with an initial client connection
        # that fail --> try to listen
        # self.transport = None
        self.peerConn = self.reactor.connectTCP(\
              self.remotePublicAddress[0], \
              self.remotePublicAddress[1], \
              self, \
              timeout = 1, \
              bindAddress = self.privateAddress)
    
  def stunt2_inv(self):
      """
      STUNT 2 implementation: flip the roles
      """
      self.method = 'stunt2_inv' # Fail: call the next method
      self.timeout = None
      if self.requestor:
          self.requestor = 0
      else:
          self.peerConn.loseConnection()
          self.requestor = 1
      self.stunt2()
          
  def _stunt2_clientConnectionFailed(self):
    """
    STUNT 2 implementation failed.
    Try several times
    """
      
    if self.requestor:
      if self.attempt < self.t * 100:
        # connect
        time.sleep(self.attempt)
        self.attempt = self.attempt + 1
        self.stunt2()
      else:
        # If exist, stop timeout
        try: self.timeout.cancel()
        except: pass
        if self.method == 'stunt2':
          self.stunt2_inv()
        elif self.method == 'stunt2_inv':
          self.attempt = 0
          self.p2pnat()
    else:
      # listen
      print 'STUNT2:Listen on:', self.privateAddress, \
            'for:', (self.remotePublicAddress[0], self.remotePrivateAddress[1])
      self.peerConn = self.reactor.listenTCP(\
              self.privateAddress[1], self)
      if self.method == 'stunt2':
        self.timeout = self.reactor.callLater(self.t, self.stunt2_inv)
      elif self.method == 'stunt2_inv':
        self.attempt = 0
        self.timeout = self.reactor.callLater(self.t, self.p2pnat)

  def stopConnect(self):
    self.attempt = self.t * 10000
      
  def p2pnat(self):
      """
      P2PNAT implementation.
      This method try to establish a simultaneous TCP connection
      """
      try: self.peerConn.loseConnection()
      except: pass
      self.method = 'p2pnat' # Fail: call the next method
      if self.attempt < self.t * 10:
          # connect
          self.attempt = self.attempt + 1
          print 'P2PNAT: From:', self.privateAddress, \
                'to:', self.remotePublicAddress
          delay = random.random()
          self.peerConn = self.reactor.connectTCP(\
                  self.remotePublicAddress[0], \
                  self.remotePublicAddress[1]+1, \
                  self, \
                  timeout = 1+delay, \
                  bindAddress=self.privateAddress)   
          # Try several connect for t seconds
          if self.attempt == 1:
            self.timeout = reactor.callLater(self.t, self.stopConnect)
      else:
        #self.ntcp_fail()
        self.stunt1()

  def stunt1(self):
    """
    STUNT 1 implementation:
    This method try to establish a connection using spoofing
    """
    self.method = 'stunt1'
    try:
      import ntcp.punch.UdpSniffy as udp_sniffer
      import ntcp.punch.sniffy as sniffer
    except:
      self.clientConnectionFailed(self.punch, 'NTCP failed: Impacket library required')
      return
    
    try:
      # Start to listen for UDP communication
      udp_obj = udp_sniffer.UDP_factory(self)

      self.remotePublicAddress = (self.remotePublicAddress[0], self.remotePublicAddress[1]-1)
      self.publicAddress = (self.publicAddress[0], self.publicAddress[1]-1)
      self.privateAddress = (self.privateAddress[0], self.privateAddress[1]-1)
      print 'STUNT1: from:', self.privateAddress, \
                'to:', self.remotePublicAddress
      # Start to sniff packets (run method in thread)
      argv = ('', 'eth0', 'tcp port %d and ip dst host %s'%(self.privateAddress[1], self.remotePublicAddress[0]))
      self.reactor.callInThread(sniffer.sniff, argv, udp_obj, self)
    except:
      self.clientConnectionFailed(self.punch, 'NTCP failed: impossible to travers the NATs. You probably have not administrator privileges')
      return
    
    time.sleep(1)
    self.reactor.connectTCP(\
                  self.remotePublicAddress[0], \
                  self.remotePublicAddress[1], \
                  self, \
                  bindAddress=self.privateAddress)
    



  def ntcp_fail(self, reason=None):
    """
    All the methods have failed
    """
    if reason == None:
      self.factory.clientConnectionFailed(self.punch, \
                                          'NTCP: failed to connect with: %s:%d'%self.remotePublicAddress)
    else:
      self.factory.clientConnectionFailed(self.punch, reason)

# ----------------------------------------------------------




# ----------------------------------------------------------
# Wrapping of the twisted.internet.protocol classes
# ----------------------------------------------------------    
  def dataReceived(self, data):
    self._super.protocol.dataReceived(data)
      
  def connectionMade(self):
    self.connected = 1
    # If exist, stop timeout
    try:
      self._super.timeout.cancel()
    except:
      pass
    
    #self._super.d.callback(self._super.peerConn)
    
    self._super.protocol.transport = self.transport
    self._super.protocol.connectionMade()
    
  def connectionLost(self, reason):
    #self.factory.clientConnectionLost(None, reason)
    self._super.factory.clientConnectionLost(None, reason)
    
  def startedConnecting(self, connector):
    self.factory.startedConnecting(connector)
    
  def buildProtocol(self, addr):
    self.protocol = self.factory.buildProtocol(addr)
    return ConnectionPunching(self, _s=self)
        
  def clientConnectionFailed(self, connector, reason):
    """
    Try several methods before to call
    the real clientConnectionFailed function
    """
    if self.connected == 0 and not self.error:
      if self.method == 'sameLan':
        self._sameLan_clientConnectionFailed()
      elif self.method == 'stunt2':
        self._stunt2_clientConnectionFailed()
      elif self.method == 'stunt2_inv':
        self._stunt2_clientConnectionFailed()
      elif self.method == 'p2pnat':
        self.p2pnat()
      elif self.method == 'stunt1':
        self.ntcp_fail()
      else:
        self.factory.clientConnectionFailed(connector, reason)
        
    else:
      self.factory.clientConnectionFailed(connector, reason)



