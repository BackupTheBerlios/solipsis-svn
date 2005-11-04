import logging, random, time

import twisted.internet.defer as defer
from twisted.internet import threads
import twisted.python.failure as failure

from ntcp.punch.Puncher import Puncher
import ntcp.stunt.StuntDiscovery as stunt

configurationText = ['NAT presence ', \
                     'NAT type     ', \
                     'My private IP', \
                     'My public IP ', \
                     'Binding delta'] 

# The NAT types: code and decode
NatTypeCod = {
  'None' : 'NONE',
  'Independent' : '000I',
  'AddressDependent' : '00AD',
  'AddressPortDependent' : '0APD',
  'SessionDependent' : '00SD'
   }

NatTypeDec = {
  'NONE' : 'None',
  '000I' : 'Independent',
  '00AD' : 'AddressDependent',
  '0APD' : 'AddressPortDependent',
  '00SD' : 'SessionDependent'
   }

class NtcpFactory:
    """
    Just to privide some methods to wrap^twisted methods
    """
    def __init__(self, d):
        self.defer = d
    def stopListening(self):
        pass

class Nat:
  """
  The NAT handler
  A NAT object to save the NAT's information
  """
  def __init__(self, type, delta=None, publicAddress=None, privateAddress=None):
    self.type = NatTypeDec[type]
    self.delta = delta
    self.publicAddress = publicAddress
    self.privateAddress = privateAddress
    
class NatManager:
  """
  It's a NAT mirror. It has all the information about a NAT (if there is one).
  It discovers the NAT information (type and mapping)
  :version: 0.2
  :author: Luca Gaballo
  """
  log = logging.getLogger("ntcp")
  
  def __init__(self):
    # The nat configuration
    self.discover = 0
    self.type = None
    self.delta = None
    # TODO: delete publicIP, publicPort, privateIP, privatePort
    self.publicIP = None
    self.publicPort = None
    self.publicAddr = (self.publicIP, self.publicPort)
    self.privateIp = None
    self.privatePort = None
    self.privateAddr = (self.privateIp, self.privatePort)

    self.localNat = Nat('NONE')
    self.remoteNat = None

  def _natDiscoveryDefer(self):
    """Makes NAT discovery in bloking mode

    @return defer: 
    """
    d = defer.Deferred()
    d2 = defer.Deferred()
   
    def succeed(natConfig):
      """The STUNT discovery has be done."""
      self.setNatConf(natConfig)
      self.printNatConf()
      d2.callback((self.publicIp, 0))
      return d2
              
    def fail(failure):
      d = defer.Deferred()
      d.errback(failure)
      
    # Start to discover the public network address and NAT configuration
    d = stunt.NatDiscovery(self.reactor)
    d.addCallback(succeed)
    d.addErrback(fail) 

    return d2

  def _natDiscoveryThread(self):
    """Makes NAT discovery in non-bloking mode
    start the discovery process in a thread

    @return void:
    """
    d = defer.Deferred()
   
    def succeed(natConfig):
      """The STUN/STUNT discovery has be done."""
      self.setNatConf(natConfig)
      self.printNatConf()
      d.callback(None)
              
    def fail(failure):
      print "STUNT failed:", failure.getErrorMessage()
      
    # Start to discover the public network address and NAT configuration
    self.reactor.callInThread(stunt.NatDiscovery, self.reactor, succeed)
    return d
    
  def publicAddrDiscovery(self, localPort=0):
    """
    Discover the mapping for the tuple (int IP, int port, ext IP, ext port)
    
    @param int localPort : The connection local port (default any)
    @return tuple publicAddress : The previewed mapped address on the NAT
    """
    d = defer.Deferred()
    d2 = defer.Deferred()

    if localPort == 0:
      localPort = random.randrange(49152, 65535)
      
    # Set the private address too
    self.privatePort = localPort
    self.privateAddr = (self.privateIp, self.privatePort)

    def discovery_fail(failure):
      d = defer.Deferred()
      d.errback(failure)
        
    def discover_succeed(publicAddress):
      self.publicIp = publicAddress[0]
      # Discover the public address (from NAT config)
      if self.type == 'Independent':
        self.publicPort = publicAddress[1] - 1

      if self.type == 'AddressDependent':
        self.publicPort = publicAddress[1] - 1 + self.delta
        
      if self.type == 'AddressPortDependent':
        self.publicPort = publicAddress[1] - 1 + self.delta
        
      if self.type == 'SessionDependent':
        self.publicPort = publicAddress[1] - 1 + self.delta
        
      publicAddr = (self.publicIp, self.publicPort)

      d2.callback(publicAddr)

    if self.type == 'None':
      d2.callback((self.publicIp, localPort))
    else:      
      d = stunt.AddressDiscover(self.reactor, localPort+1)
      d.addCallback(discover_succeed)
      d.addErrback(discovery_fail)

    return d2
      

  def setNatConf(self, natConfig):
    """
    Sets the NAT's configuration

    @param NatConf : the NAT configuration tuple 
    @return void :
    """    
    self.discover = 1
    self.type = natConfig.type 
    self.delta = natConfig.delta
    self.publicIp = natConfig.publicIp
    self.privateIp = natConfig.privateIp
    self.publicAddr = (natConfig.publicIp, 0)
    self.privateAddr = (natConfig.privateIp, 0)
    
    self.localNat = Nat(NatTypeCod[self.type], self.delta, \
                        self.publicAddr, self.privateAddr)

    # Upload the NAT configuration link in puncher
    self._puncher.setNatObj(self)

  def setRemoteNatConf(self, type, delta, publicAddress, privateAddress):
    """
    Sets the remote NAT's configuration

    @param type: the remote NAT type 
    @param delta: the remote NAT delta binding 
    @param publicAddress: the remote public address
    @param privateAddress: the remote private address
    @return void :
    """
    self.remoteNat = Nat(type, delta, publicAddress, privateAddress)
    
  def printNatConf(self):
    """
    Prints the NAT's configuration
    
    @return void :
    """
    print "*------------------------------------------------------*"
    print "NTCP Configuration:\n"
    print "\t", configurationText[1], "\t", self.type
    print "\t", configurationText[2], "\t", self.privateIp
    print "\t", configurationText[3], "\t", self.publicIp
    print "\t", configurationText[4], "\t", self.delta
    print "*------------------------------------------------------*"
    
class NatConnectivity(NatManager, object):

    """
    Interface with the application.
    Discover NAT information (type and mapping) and force a connection
    through NATs with the Super Node Connection Broker's help
    or by a directly UDP connection with the remote endpoint.
    """
  
    logging.basicConfig()
    log = logging.getLogger("ntcp")
    log.setLevel(logging.DEBUG)

    def __init__(self, reactor, udpListener=None):
        super(NatConnectivity, self).__init__()
        self.reactor = reactor
        self.udpListener = udpListener # A listener for UDP communication
        self._puncher = Puncher(self.reactor, self, self.udpListener) # the puncher to establish the connection

    def datagramReceived(self, message, fromAddr):
        """A link to the internal datagramReceived function"""
        self._puncher.datagramReceived(message, fromAddr)
    
    def holePunching(self, uri, myUri):
        """
        Starts the hole punching procedure to punch a hole
        for UDP communication with peer identified by URI

        @param uri: the remote peer to contact
        @param myUri: personal uri 
        """
        return self._puncher.sndLookupRequest(remoteUri=uri, localUri=myUri)

    def setServerFactory(self, factory):
        """Sets a factory for TCP connection
        @param factory - a twisted.internet.protocol.*Factory instance 
        """
        self._puncher.setServerFactory(factory)
        self._puncher.s_factory = factory
        
    def getFactory(self):
        """Gets the TCP factory
        @return: factory - a twisted.internet.protocol.ServerFactory instance
        """
        return self._puncher.getFactory()

    def natDiscovery(self, bloking = 1):
        """
        Discover NAT presence and information about.
        
        @param bloking: if 0 makes NAT discovery in non bloking mode (default 1)
        @return void :
        """
        if bloking:
            return self._natDiscoveryDefer()
        else:
            return self._natDiscoveryThread()
 
    def listenTCP(self, port=0, factory=None, backlog=5, interface='',  myUri=None):
        """Make a registration to CB and listen for incoming connection request
        
        @param port: a port number on which to listen, default to 0 (any) (only default implemented)
        @param factory: a twisted.internet.protocol.ServerFactory instance 
        @param backlog: size of the listen queue (not implemented)
        @param interface: the hostname to bind to, defaults to '' (all) (not implemented)
        @param myUri: the user's URI for registration to Connection Broker
        return: void
        """
        d = defer.Deferred()
        # self._puncher = Puncher(self.reactor, self, self.udpListener)
    
        if factory != None:
            # Sets the factory for TCP connection
            self.setServerFactory(factory)

        d = self._puncher.sndRegistrationRequest(myUri)
        return NtcpFactory(d)
    
    def connectTCP(self, \
                   host=None, \
                   port=None, \
                   remoteUri=None, \
                   factory=None, \
                   timeout=30, \
                   bindAddress=None, \
                   myUri=None):
        """
        Force a connection with another user through NATs
        helped by the ConnectionBroker.
        It needs at least one between (host, port) and 'remoteUri'
        
        @param host: a host ip address, default None
        @param port: a port number, the UDP remote port (it's mandatory if host is present)
        @param remoteUri : The remote endpoint's uri, default None
        @param factory: a twisted.internet.protocol.ClientFactory instance 
        @param timeout: number of seconds to wait before assuming the connection has failed.  (not implemented)
        @param bindAddress: a (host, port) tuple of local address to bind to, or None.
        @param myUri : The uri for future incoming connection request
        
        @return :  An object implementing IConnector.
        This connector will call various callbacks on the factory
        when a connection is made,failed, or lost
        - see ClientFactory docs for details.
        """
        d = defer.Deferred()
        d_conn = defer.Deferred()
        
        if host == None:
            remoteAddress = None
        else:
            remoteAddress = (host, port)
            
        localPort = 0 # any
        if bindAddress != None:
            localPort = bindAddress[1]
            
        if self._puncher == None:
            self._puncher = Puncher(self.reactor, self)

        if self._puncher.getClientFactory() == None and factory == None:
            # Error
            d.errback(failure.DefaultException('You have to specify a factory'))
        elif factory != None:
            self._puncher.setClientFactory(factory)
            self._puncher.c_factory = factory

        def fail(failure):
            """ Error in NAT Traversal TCP """
            print 'ERROR in NAT Traversal (registration):', failure#.getErrorMessage()

        def connection_succeed(result):
            print 'connection succeed:', result
            d_conn.callback(result)

        def connection_fail(failure):
            print 'connection fail', failure
            d = defer.Deferred()
            d.errback(failure)

        def discovery_fail(failure):
            d = defer.Deferred()
            d.errback(failure)

        def discovery_succeed(publicAddress):
            self.publicAddr = publicAddress
            #print 'Address discovered:', publicAddress
            if self.publicAddr != None:
                d = defer.Deferred()
                d = self._puncher.sndConnectionRequest(remoteUri, remoteAddress)
                d.addCallback(connection_succeed)
                d.addErrback(connection_fail)
            else:
                self.d.errback('The NAT doesn\'t allow inbound TCP connection')

        def registrationSucceed(result):
            
            print 'Registration to the SN Connection Broker has be done' 
            print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'  
            
            # Discovery external address
            d = self.publicAddrDiscovery(localPort)
            d.addCallback(discovery_succeed)
            d.addErrback(discovery_fail)
            
        # Registration to Connection Broker for incoming connection
        if myUri != None and not self._puncher.registered:
            print '\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^' 
            d = self._puncher.sndRegistrationRequest(myUri)
            d.addCallback(registrationSucceed)
            d.addErrback(fail)
        else:
            d = self.publicAddrDiscovery(localPort)
            d.addCallback(discovery_succeed)
            d.addErrback(discovery_fail)
            
        return d_conn

    def getP2PConfiguration(self, \
                            host=None, \
                            port=None, \
                            remoteUri=None):
        """
        Gets the local and remote NAT type.
        It requires at least one between parameters (host, port) and remoteUri

        @param host: a host name, default None
        @param port: a port number, the UDP remote port (it's mandatory if host is present)
        @param remoteUri : The remote endpoint's uri, default None
        @return: defer the callback result is (local NAT type, remote NAT type)
        """
        
        d = defer.Deferred()
        if host == None:
            remoteAddress = None
        else:
            remoteAddress = (host, port)

        def fail(failure):
            """ Error in NTCP"""
            print 'ERROR in NTCP (get configuration):', failure.getErrorMessage()
            return None
        
        def discoveryConfigurationSucceed(remote):
            # Returns the result
            if remote == 'Unknown':
                d.callback((self.type, None))
            else:
                d.callback((self.type, self.remoteNat.type))

        def discoverySucceed(result):
            # Asks for remote NAT configuration
            d = defer.Deferred()
            d = self._puncher.sndConfigurationRequest(\
                remoteUri, remoteAddress)
            d.addCallback(discoveryConfigurationSucceed)
            d.addErrback(fail)
            
        
        if self.discover == 0:
            # Discover local NAT configuration
            d = defer.Deferred()
            d = self.natDiscovery()
            d.addCallback(discoverySucceed)
            d.addErrback(fail)
        else:
            # We know already the NAT configuration
            discoverySucceed(None)

        return d

    def getlocalNatConf(self):
        """
        Gets the NAT objet with the NAT's configuration

        @return localNat: an ntcp.NatConnectivity.Nat object
        """
        return self.localNat
