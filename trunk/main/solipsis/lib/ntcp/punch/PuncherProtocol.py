import struct, socket, time, logging
import ConfigParser

from twisted.internet.protocol import DatagramProtocol

# This is a list of allowed arguments in the "Hole Punching" protocol.
# The Message Types
MsgTypes = {0x1001 : 'Lookup Request',
            0x1101 : 'Lookup Response',
            0x1201 : 'Keep Alive Request',
            0x1202 : 'Keep Alive Response',
            0x1111 : 'Connection Request',
            0x1121 : 'Connection Response',
            0x1131 : 'Configuration Request',
            0x1132 : 'Configuration Response',
            0x1002 : 'Registration Request',
            0x1003 : 'Registration Response',
            0x1301 : 'Forcing TCP Request',
            0x1102 : 'Hole Punching',
            0x1112 : 'Error Response'}

# The Message Attributes types
MsgAttributes = { 0x0001 : 'USER-ID',
                  0x0002 : 'PUBLIC-ADDRESSE',
                  0x0003 : 'PRIVATE-ADDRESSE',
                  0x0004 : 'NAT-TYPE',
                  0x1005 : 'REQUESTOR-USER-ID',
                  0x0005 : 'REQUESTOR-PUBLIC-ADDRESSE',
                  0x0006 : 'REQUESTOR-PRIVATE-ADDRESSE',
                  0x0007 : 'REQUESTOR-NAT-TYPE',
                  0x0008 : 'ERROR-CODE', 
                  0x0009 : 'UNKNOWN-ATTRIBUTES',
                  0x1001 : 'SYN',
                  }

# The Error Code
ErrorCodes = {
   400 : 'Bad Request',
   420 : 'Unknown attribute',
   431 : 'Integrity Check Failure',
   500 : 'Server Error',
   600 : 'Global Failure',
   700 : 'Unknown user'
   }


class PuncherProtocol(DatagramProtocol):

  """
  This class has all the functions for a connectivity through NATs
  :version: 0.2
  :author: Luca Gaballo
  """
  
  def __init__(self):
    self._pending = {}
    self.mt, self.pktlen, self.tid = (0, 0, '0')
    self.toAddr = ('0.0.0.0', 0)
    self.fromAddr = ('0.0.0.0', 0)

    # Load configuration
    import ntcp, os
    path = os.path.dirname(ntcp.__file__)
    file =  os.path.join(path, "p2pNetwork.conf")
    self.p2pConfig = ConfigParser.ConfigParser()
    self.p2pConfig.read(file)
    
  def datagramReceived(self, message, fromAddr):
    """
    Listen for incoming message

    @param message : The message received
    @param fromAddr : The remote address (ip, port)
    @return void :
    """
    self.fromAddr = fromAddr
    self.parseMessage(message)
    self.analyseMessage()

  def parseMessage(self, message):
    """
    Parses the message received

    @param message : The message to parse
    @return void :
    """
    self.avtypeList = {}
    # Header
    self.mt, self.pktlen, self.tid = struct.unpack('!hh16s', message[:20])
    # Payload
    remainder = message[20:]
    while remainder:
      avtype, avlen = struct.unpack('!hh', remainder[:4])
      val = remainder[4:4+avlen]
      avtype = MsgAttributes.get(avtype, 'Unknown type:%04x'%avtype)
      self.avtypeList[avtype] = val
      remainder = remainder[4+avlen:]


  def analyseMessage(self):
    """
    Analyses the message received

    @return void :
    """
    if self.mt == 0x1001:
      # Lookup Request
      self.rcvLookupRequest()
      
    elif self.mt == 0x1101:
      # Lookup Response
      self.rcvLookupResponse()
      
    elif self.mt == 0x1201:
      # Keep Alive Request
      self.rcvKeepAliveRequest()
      
    elif self.mt == 0x1202:
      # Keep Alive Response
      self.rcvKeepAliveResponse()
      
    elif self.mt == 0x1111:
      # Connection Request
      self.rcvConnectionRequest()
      
    elif self.mt == 0x1121:
      # Connection Response
      self.rcvConnectionResponse()
      
    elif self.mt == 0x1131:
      # Configuration Request
      self.rcvConfigurationRequest()
      
    elif self.mt == 0x1132:
      # Configuration Response
      self.rcvConfigurationResponse()
      
    elif self.mt == 0x1002:
      # Registration Request
      self.rcvRegistrationRequest()
      
    elif self.mt == 0x1003:
      # Registration Response
      self.rcvRegistrationResponse()
      
    elif self.mt == 0x1301:
      # Forcing TCP Request
      self.rcvForcingTcpRequest()
      
    elif self.mt == 0x1102:
      # Hole Punching
      self.rcvHolePunching()
      
    elif self.mt == 0x1112:
      # Error Response
      self.rcvErrorResponse()
  
  def createMessage(self, attributes):
    """
    Creates the message to send

    @param dictionary attributes : The attributes to make the message content
    @return void :
    """
    avpairs = ()
    # The message Type
    if self.messageType   == "Lookup Request":
      self.mt = 0x1001
    elif self.messageType == "Lookup Response":
      self.mt = 0x1101
    elif self.messageType == "Keep Alive Request":
      self.mt = 0x1201
    elif self.messageType == "Keep Alive Response":
      self.mt = 0x1202
    elif self.messageType == "Connection Request":
      self.mt = 0x1111
    elif self.messageType == "Connection Response":
      self.mt = 0x1121
    elif self.messageType == "Configuration Request":
      self.mt = 0x1131
    elif self.messageType == "Configuration Response":
      self.mt = 0x1132
    elif self.messageType == "Registration Request":
      self.mt = 0x1002
    elif self.messageType == "Registration Response":
      self.mt = 0x1003
    elif self.messageType == "Forcing TCP Request":
      self.mt = 0x1301
    elif self.messageType == "Hole Punching":
      self.mt = 0x1102
    elif self.messageType == "Error Response":
      self.mt = 0x1112
    avpairs = avpairs + attributes

    avstr = ''
    # The Message Attributes
    # add any attributes in Payload
    for a,v in avpairs:

      if a == 0x0001 or a == 0x1005 or a == 0x0004 or a == 0x0007:
        # USER-ID, NAT-TYPE
        flength = len(v)
        if flength%4 != 0:
          flength = 4 - len(v)%4 + len(v)
          v = v.zfill(flength)
        avstr = avstr + struct.pack( \
                    '!hh%ds'%flength, a, len(v), v)

      elif a == 0x0002 or a == 0x0003 or a == 0x0005 or a == 0x0006:
        # XXX-ADDRESS
        avstr = avstr + struct.pack( \
                    '!hhcch4s', a, len(v[5:])+4, '0', \
                    '%d' % 0x01, int(v[:5]), v[5:])

      elif a == 0x0008:
        # ERROR-CODE
        err_class = int(v[0])
        number = int(v) - err_class*100
        phrase = ErrorCodes[int(v)]
        avstr = avstr + struct.pack( \
                    '!hhi%ds' % len(phrase), a, 4 + len(phrase), \
                    (err_class<<8) + number, phrase)

      elif a == 0x0009:
        # UNKNOWN-ATTRIBUTES
        avstr = avstr + struct.pack('!hh', a, len(v)*2)
        for unkAttr in v:
          avstr = avstr + struct.pack('!h', unkAttr)

      elif a == 0x1001:
        # SYN
        avstr = avstr + struct.pack('!hhL', a, 4, v)
            
    pktlen = len(avstr)
    if pktlen > 65535:
      raise ValueError, "message request too big (%d bytes)" % pktlen
    # Add header and send
    self.pkt = struct.pack('!hh16s', self.mt, pktlen, self.tid) + avstr

  def sendPack(self):
    """
    Sends the packed message

    @return void :
    """
    pass

  def sendMessage(self, toAddr, attributes=()):
    """
    Sends the message

    @return void :
    """
    self.createMessage(attributes)
    self.transport.write(self.pkt, toAddr)

  def getAddress(self, key):
    """
    Gets the unpacked address in the message for the given key

    @param key: Message Attributes value
    @return address: the (ip, port) tuple in the message
    """
    dummy,family,port,ip = struct.unpack( \
                    '!ccH4s', self.avtypeList[key])
    return (socket.inet_ntoa(ip), port)


  def getRandomTID(self):
    """Returns a random id number"""
    # It's not necessary to have a particularly strong TID here
    import random
    tid = [ chr(random.randint(0,255)) for x in range(16) ]
    tid = ''.join(tid)
    return tid
  
  def getPortIpList(self, address):
    """Return a well formatted string with the address"""
    return '%5d%s' % (address[1], socket.inet_aton(address[0]))

  def sndErrorResponse(self, attributes):
    """Send an error response

    @param attributes: the attributes' list
    """
    self.messageType = "Error Response"    
    self.sendMessage(self.requestor, attributes)
    
  def rcvErrorResponse(self):
    pass

  def getErrorCode(self):
    """If an error occurred: return the error code"""
    
    # Extract the class and number
    error, phrase = struct.unpack('!i%ds' % \
                                  (len(self.avtypeList["ERROR-CODE"])-4), \
                                  self.avtypeList["ERROR-CODE"])
    number = error - ((error>>8)<<8)
    err_class = ((error - number)>>8)*100
    return err_class + number, phrase

  def getListUnkAttr(self):
    """Return the list of Unknown attributes"""
    
    _listUnkAttr = ()
    listUnkAttr = struct.unpack( \
            '!%dh' % int(len(self.avtypeList["UNKNOWN-ATTRIBUTES"])/2), \
            self.avtypeList["UNKNOWN-ATTRIBUTES"])
    for attr in listUnkAttr:
      _listUnkAttr = _listUnkAttr + ('0x%04x'%attr,)
    return _listUnkAttr

# TODO: Error Check
# TODO: functions' interface
