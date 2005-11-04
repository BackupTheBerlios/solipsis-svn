import struct, socket, time, logging

from twisted.internet import reactor
from ntcp.punch.PuncherProtocol import PuncherProtocol

class SNConnectionBroker (PuncherProtocol, object):

  """
  The Super Node Connection Broker.
  Helps a user to establish a connection with another peer that is behind a NAT.

  :version: 0.2
  :author: Luca Gaballo
  """
  
  logging.basicConfig()
  log = logging.getLogger("CB")
  log.setLevel(logging.DEBUG)
  
  # The IP table with:
  # | id (=primary key) | public IP (=primary key)| private IP | NAT type | 
  peersTable = {}

  def __init__(self):
    super(SNConnectionBroker, self).__init__()
    reactor.callLater(60, self.refreshTable)
    self.spoofyTable = {}
    

  def rcvRegistrationRequest(self):
    """
    A Registration Request is received. 

    @return void :
    """
    
    uri = self.avtypeList['USER-ID']
    publAddr = self.fromAddr
    dummy,family,port,ip = struct.unpack( \
                '!cch4s', self.avtypeList['PRIVATE-ADDRESSE'])
    privAddr = (socket.inet_ntoa(ip), port)
    natType = self.avtypeList['NAT-TYPE']
    peerInfo = (uri, publAddr, privAddr, natType)
    self.registrePeer(peerInfo)
    self.printActiveConnection()

    # Reply with a Registration Response
    self.sndRegistrationResponse(publAddr, privAddr)
    
  def sndRegistrationResponse(self, publAddr, privAddr):
    """
    Reply to a registration request

    @param publAddr: the private address tuple (host, port)
    @param privAddr: the public address tuple (host, port)
    @return void :
    """
    listAttr = ()
    self.messageType = 'Registration Response'
    listAttr = listAttr + ((0x0002, self.getPortIpList(publAddr)),)
    listAttr = listAttr + ((0x0003, self.getPortIpList(privAddr)),)
    
    self.sendMessage(publAddr, listAttr)

  def rcvKeepAliveRequest(self):
    """A message from a user is received to keep the NAT hole active"""
    userId = self.avtypeList['USER-ID']
    if userId in self.peersTable:
      self.peersTable[userId] = (self.peersTable[userId][:3] + (time.time(),))
      self.sndKeepAliveResponse()

  def sndKeepAliveResponse(self):
    """Sends the keep alive message"""
    self.messageType = 'Keep Alive Response'
    self.sendMessage(self.fromAddr)

  def rcvConnectionRequest(self):
    """
    A lookup request is received. 

    @return void :
    """
    self.requestor = self.fromAddr

    # Load the peer configuration
    key = self.avtypeList['USER-ID']
    peerInfo = self.getPeerInfo(key)
    if peerInfo == ():
      # TODO: contact other connection broker
      self.sndErrorResponse(((0x0008, '700'),))
      self.log.warn('User not registered!')
      return

    self.log.debug('Received Connection Request:')
    self.log.debug('from: %s'%self.avtypeList['REQUESTOR-USER-ID'])
    self.log.debug('to: %s'%key)
    # Sends a Connection request to the other endpoint
    # to get information about it
    self.sndConnectionRequest(peerInfo)
 
  def sndConnectionRequest(self, peerInfo):
    """
    Sends a Connection Request Message to the remote endpoint.
    
    @param peerInfo : the remote endpoint's information
    @return void 
    """
    toAddr = peerInfo[1] # the peer's address
    listAttr = ()
    
    if "REQUESTOR-USER-ID" in self.avtypeList:
      listAttr = listAttr + ((0x1005, self.avtypeList['REQUESTOR-USER-ID']),)
    addr = self.getAddress('REQUESTOR-PUBLIC-ADDRESSE')
    listAttr = listAttr + ((0x0005, self.getPortIpList(addr)),)
    addr = self.getAddress('REQUESTOR-PRIVATE-ADDRESSE')
    listAttr = listAttr + ((0x0006, self.getPortIpList(addr)),)
    listAttr = listAttr + ((0x0007, self.avtypeList['REQUESTOR-NAT-TYPE']),)
    
    self.messageType = "Connection Request"   
    self.sendMessage(toAddr, listAttr)
  
  def rcvConnectionResponse(self):
    """
    Sends a Connection Request Message to the remote endpoint.
    
    @param peerInfo : the remote endpoint's information
    @return void 
    """
    self.sndConnectionResponse()
    
  def sndConnectionResponse(self):
    """
    Sends a connection response to the to the user
    
    @return void :
    """ 
    listAttr = ()
    
    listAttr = listAttr + ((0x0001, self.avtypeList['USER-ID']),)
    addr = self.getAddress('PUBLIC-ADDRESSE')
    listAttr = listAttr + ((0x0002, self.getPortIpList(addr)),)
    addr = self.getAddress('PRIVATE-ADDRESSE')
    listAttr = listAttr + ((0x0003, self.getPortIpList(addr)),)
    listAttr = listAttr + ((0x0004, self.avtypeList['NAT-TYPE']),)
    # Requestor conf
    if "REQUESTOR-USER-ID" in self.avtypeList:
      listAttr = listAttr + ((0x1005, self.avtypeList['REQUESTOR-USER-ID']),)
    addr = self.getAddress('REQUESTOR-PUBLIC-ADDRESSE')
    listAttr = listAttr + ((0x0005, self.getPortIpList(addr)),)
    addr = self.getAddress('REQUESTOR-PRIVATE-ADDRESSE')
    listAttr = listAttr + ((0x0006, self.getPortIpList(addr)),)
    listAttr = listAttr + ((0x0007, self.avtypeList['REQUESTOR-NAT-TYPE']),)   

    print 'send Connection Response to:', self.requestor
    self.messageType = "Connection Response"    
    self.sendMessage(self.requestor, listAttr)

# -- Connnection (end)

# -- Configuration

  def rcvConfigurationRequest(self):
    """
    A Configuration request is received. 

    @return void :
    """
    print 'rcv configuration req'
    self.requestor = self.fromAddr

    # Load the peer configuration
    key = self.avtypeList['USER-ID']
    peerInfo = self.getPeerInfo(key)
    if peerInfo == ():
      # TODO: contact other connection broker
      self.sndErrorResponse(((0x0008, '700'),))
      self.log.warn('User not registered!')
      return

    # Sends a Connection request to the other endpoint
    # to get information about it
    self.sndConfigurationResponse(peerInfo)

  def sndConfigurationResponse(self, peerInfo):
    """
    Sends a Configuration Response Message to the remote endpoint.
    
    @param peerInfo : the remote endpoint's information
    @return void 
    """
    print 'snd configuration resp'
    toAddr = self.requestor # the peer's address
    listAttr = ()
    
    listAttr = listAttr + ((0x0001, self.avtypeList['USER-ID']),)
    listAttr = listAttr + ((0x0002, self.getPortIpList(peerInfo[1])),)
    listAttr = listAttr + ((0x0003, self.getPortIpList(peerInfo[2])),)
    listAttr = listAttr + ((0x0004, peerInfo[3]),)
    # Requestor conf    
    if "REQUESTOR-USER-ID" in self.avtypeList:
      listAttr = listAttr + ((0x1005, self.avtypeList['REQUESTOR-USER-ID']),)
    addr = self.requestor
    listAttr = listAttr + ((0x0005, self.getPortIpList(addr)),)
    if "REQUESTOR-PRIVATE-ADDRESSE" in self.avtypeList:
      addr = self.getAddress('REQUESTOR-PRIVATE-ADDRESSE')
      listAttr = listAttr + ((0x0006, self.getPortIpList(addr)),)
    listAttr = listAttr + ((0x0007, self.avtypeList['REQUESTOR-NAT-TYPE']),)
    
    self.messageType = "Configuration Response"   
    self.sendMessage(toAddr, listAttr)
 
# -- Configuration (end)

# --- Lookup

  def rcvLookupRequest(self):
    """
    A lookup request for UDP hole punching is received
    Starts hole punching mechanisl

    @return void :
    """
    self.requestor = self.fromAddr

    # Load the peer configuration
    key = self.avtypeList['USER-ID']
    peerInfo = self.getPeerInfo(key)
    if peerInfo == ():
      # TODO: contact other connection broker
      self.sndErrorResponse(((0x0008, '700'),))
      self.log.warn('User not registered!')
      return
 
    # Send a Lookup Request message
    self.sndLookupRequest(peerInfo)
    # Send a Lookup Response message
    self.sndLookupResponse(peerInfo)
    
  def sndLookupRequest(self, peerInfo):
    """
    Send a lookup request to advise a remote user
    behind a NAT of UDP hole punchingattempt by another user.

    @param peerInfo : the remote endpoint's information
    @return void :
    """
    toAddr = peerInfo[1] # the peer's address
    listAttr = ()
    
    listAttr = listAttr + ((0x1005, self.avtypeList['REQUESTOR-USER-ID']),)
    #addr = self.getAddress('REQUESTOR-PUBLIC-ADDRESSE')
    addr = self.fromAddr
    listAttr = listAttr + ((0x0005, self.getPortIpList(addr)),)
    addr = self.getAddress('REQUESTOR-PRIVATE-ADDRESSE')
    listAttr = listAttr + ((0x0006, self.getPortIpList(addr)),)
    listAttr = listAttr + ((0x0007, self.avtypeList['REQUESTOR-NAT-TYPE']),)
    
    self.messageType = "Lookup Request"   
    self.sendMessage(toAddr, listAttr)
    
  def sndLookupResponse(self, peerInfo):
    """
    A lookup response is received (from CB or endpoint)from a user
    Forward it to the initial demandant

    @return void :
    """
    listAttr = ()
    
    listAttr = listAttr + ((0x0001, self.avtypeList['USER-ID']),)
    #addr = self.getAddress('PUBLIC-ADDRESSE')
    addr = peerInfo[1]
    listAttr = listAttr + ((0x0002, self.getPortIpList(addr)),)
    #addr = self.getAddress('PRIVATE-ADDRESSE')
    addr = peerInfo[2]
    listAttr = listAttr + ((0x0003, self.getPortIpList(addr)),)
    listAttr = listAttr + ((0x0004, peerInfo[3]),) 
    

    self.messageType = "Lookup Response"    
    self.sendMessage(self.requestor, listAttr)

# ---

# --- Forcing Tcp Request
  def rcvForcingTcpRequest(self):
    """
    A request of spoofing is received.
    Create a spoofing object to spoof message
    """
    from ntcp.punch.Spoofy import Spoofy

    spoofy = Spoofy(self)
    spoofy.rcvForcingTcpRequest()
    
# --- /Forcing Tcp Request
  
  def registrePeer(self, (userId, publicIP, privateIp, natInfo)):
    """Records the customer in the customer table"""
    self.peersTable[userId] = (publicIP, privateIp, natInfo, time.time())
        
  def getPeerInfo(self, key):
    """Return the client's infos: search by key.
    (id, public address, private address, NAT type)
    
    @param key : the user's uri (the key for the users' table)"""

    l = (key,)
    if key in self.peersTable:
      for i in self.peersTable[key]:
        l = l + (i,)
      return l
    return ()

  def refreshTable(self):
    """
    Refresh the peerTable every 'timeout' seconds
    """
    timeout = 60
    deleted = 0
    dead_list = ()
    for peer in self.peersTable:
      if (time.time() - self.peersTable[peer][3]) > timeout:
        dead_list += (peer,) 
        deleted = 1
    for peer in dead_list:
        del self.peersTable[peer]
    if deleted:
      self.printActiveConnection()
    reactor.callLater(timeout, self.refreshTable)
  
  def printActiveConnection(self):
    """
    Prints the active user registrations

    @return void :
    """
    try:
      print '*-----------------------------------------------------------------------*'
      print '* Active connections                                                    *'
      for peer in self.peersTable:
        print "| %12s | \n\t\\--> | %22s | %22s | %4s |" % \
              (peer, self.peersTable[peer][0], \
               self.peersTable[peer][1], \
               self.peersTable[peer][2])                       
      print '*-----------------------------------------------------------------------*'
    except:
      pass
    
reactor.listenUDP(6060, SNConnectionBroker())
reactor.run()
