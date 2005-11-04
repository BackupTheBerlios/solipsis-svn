import struct, socket, time, logging
import ConfigParser

from twisted.internet.protocol import Protocol, ClientFactory

# This is a list of allowed arguments in STUNT
# The Message Types
MsgTypes = {
   0x0001: "Binding Request",
   0x0101: "Binding Response",
   0x0111: "Binding Error Response",
   0x0002: "Shared Secret Request",
   0x0102: "Shared Secret Response",
   0x0112: "Shared Secret Error Response",
   0x0003: "Capture Request",
   0x0103: "Capture Response",
   0x0113: "Capture Error Response",
   0x0123: "Capture Acknowledge Response"
}  

# The Message Attributes types
MsgAttributes = { 
   0x0001: 'MAPPED-ADDRESS',
   0x0002: 'RESPONSE-ADDRESS',
   0x0003: 'CHANGE-REQUEST',
   0x0004: 'SOURCE-ADDRESS',
   0x0005: 'CHANGED-ADDRESS',
   0x0006: 'USERNAME',
   0x0007: 'PASSWORD',
   0x0008: 'MESSAGE-INTEGRITY',
   0x0009: 'ERROR-CODE',
   0x000a: 'UNKNOWN-ATTRIBUTES',
   0x000b: 'REFLECTED-FROM',
   0x0100: 'PACKET-REQUEST',
   0x0101: 'CAPTURE-TIMEOUTS',
   0x0102: 'CAPTURED-PACKET',
}

# The Error Code
ErrorCodes = {
   400 : 'Bad Request',
   420 : 'Unknown attribute',
   431 : 'Integrity Check Failure',
   500 : 'Server Error',
   600 : 'Global Failure'
   }

CHANGE_NONE = struct.pack('!i',0)
CHANGE_PORT = struct.pack('!i',2)
CHANGE_IP = struct.pack('!i',4)
CHANGE_BOTH = struct.pack('!i',6)

class StuntProtocol(Protocol):
  
  def __init__(self):
    self._pending = {}
    self.mt, self.pktlen, self.tid = (0, 0, '0')
    self.toAddr = ('0.0.0.0', 0)
    self.fromAddr = ('0.0.0.0', 0)

    self.messageType = None
    
    # Load configuration
    import ntcp, os
    path = os.path.dirname(ntcp.__file__)
    file =  os.path.join(path, "p2pNetwork.conf")
    self.p2pConfig = ConfigParser.ConfigParser()
    self.p2pConfig.read(file)
    
  def dataReceived(self, message):
    """
    Listen for incoming message

    @param string message : The message received
    @return void :
    """
    
    self.parseMessage(message)
    self.analyseMessage()

  def connectionMade(self):
    pass

  def connectionLost(self, reason):
    pass

  def parseMessage(self, message):
    """
    Parses the message received

    @param string message : The message to parse
    @return void :
    """
    self.avtypeList = {}
    # Header
    self.mt, self.pktlen, self.tid = struct.unpack('!hh16s', message[:20])
    if self.parseIfClient():
      # Payload
      remainder = message[20:]
      self.resdict = {}
      while remainder:
        avtype, avlen = struct.unpack('!hh', remainder[:4])
        val = remainder[4:4+avlen]
        avtype = MsgAttributes.get(avtype, 'Unknown type:%04x'%avtype)
        self.avtypeList[avtype] = val
        remainder = remainder[4+avlen:]
        if avtype in ('MAPPED-ADDRESS',
                      'CHANGED-ADDRESS',
                      'SOURCE-ADDRESS',
                      'RESPONSE-ADDRESS'):
          dummy,family,port,addr = struct.unpack('!ccH4s', val)
          addr = socket.inet_ntoa(addr)
          if avtype == 'MAPPED-ADDRESS':
            self.resdict['externalAddress'] = (addr, port)
          elif avtype == 'CHANGED-ADDRESS':
            self.resdict['_altStunAddress'] = (addr, port)
          elif avtype == 'RESPONSE-ADDRESS':
            self.resdict['toAddress'] = (addr, port)
          elif address[0] != addr:
            # Someone is rewriting packets on the way back. AAARGH.
            self.log.msg('WARNING: packets are being rewritten %r != %r'%
                    (address, (addr,port)), system='stun')
            return
        elif avtype in ('CHANGE-REQUEST'):
          pass
        else:
          self.log.msg("STUN: unhandled AV %s, val %r"%(avtype,\
                                                   repr(val)), system='stun')

  def parseIfClient(self):
    """Implemented only in client for tid control"""
    return 1
 

  def analyseMessage(self):
    """
    Analyses the message received

    @return void :
    """
    if self.mt == 0x0001:
      # Binding Request
      self.rcvBindingRequest()
      
    elif self.mt == 0x0101:
      # Binding Response
      self.rcvBindingResponse()
      
    elif self.mt == 0x0111:
      # Binding Error Response
      self.rcvBindingErrorResponse()
      
    elif self.mt == 0x0003:
      # Capture Request
      self.rcvCaptureRequest()
      
    elif self.mt == 0x0103:
      # Capture Response
      self.rcvCaptureResponse()
      
    elif self.mt == 0x0113:
      # Capture Error Response
      self.rcvCaptureErrorResponse()
  

  def createMessage(self, attributes=()):
    """
    Creates the message to send

    @param attributes : The attributes to make the message content
    @return void :
    """
    avpairs = ()
    # The message Type
    if self.messageType   == "Binding Request":
      self.mt = 0x0001
    elif self.messageType == "Binding Response":
      self.mt = 0x0101
    elif self.messageType == "Binding Error Response":
      self.mt = 0x0111
    if self.messageType   == "Capture Request":
      self.mt = 0x0003
    elif self.messageType == "Capture Response":
      self.mt = 0x0103
    elif self.messageType == "Capture Error Response":
      self.mt = 0x0113
    elif self.messageType == "Capture Acknowledge Response":
      self.mt = 0x0123
    avpairs = avpairs + attributes

    avstr = ''
    # The Message Attributes
    # add any attributes in Payload
    for a,v in avpairs:
      if a == 0x0001 or a == 0x0002 or a == 0x0004 \
                   or a == 0x0005 or a == 0x000b:
        # XXX-ADDRESS
        avstr = avstr + struct.pack( \
                    '!hhcch4s', a, len(v[5:])+4, '0', '%d' % 0x01, int(v[:5]), v[5:])
      elif a == 0x0003:
        # CHANGE-REQUEST
        avstr = avstr + struct.pack('!hh', a, len(v)) + v
      elif a == 0x0009:
        # ERROR-CODE
        err_class = int(v[0])
        number = int(v) - err_class*100
        phrase = responseCodes[int(v)]
        avstr = avstr + struct.pack( \
                    '!hhi%ds' % len(phrase), a, 4 + len(phrase), \
                    (err_class<<8) + number, phrase)
      elif a == 0x000a:
        # UNKNOWN-ATTRIBUTES
        avstr = avstr + struct.pack('!hh', a, len(v)*2)
        for unkAttr in v:
          avstr = avstr + struct.pack('!h', unkAttr)
            
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

  def sendMessage(self):
    """
    Sends the message

    @return void :
    """
    #self.createMessage(attributes)
    self.transport.write(self.pkt)

  def getRandomTID(self):
    """
    Gets a random Transmission ID
    """
    # It's not necessary to have a particularly strong TID here
    import random
    tid = [ chr(random.randint(0,255)) for x in range(16) ]
    tid = ''.join(tid)
    return tid
  
  def getPortIpList(self, address):
    """Return a well formatted string with the address"""
    return '%5d%s' % (address[1], socket.inet_aton(address[0]))
  
  def getAddress(self, key):
    """
    Gets the unpacked address in the message for the given key

    @param key: Message Attributes value
    @return address: the (ip, port) tuple in the message
    """
    dummy,family,port,ip = struct.unpack( \
                    '!ccH4s', self.avtypeList[key])
    return (socket.inet_ntoa(ip), port)

  def rcvErrorResponse(self):
    print "STUN got an error response:"
    # Extract the class and number
    error, phrase = self.getErrorCode()
    if error == 420:
      _listUnkAttr = self.getListUnkAttr()
      print (error, phrase, _listUnkAttr)
    else:
      print (error, phrase)

# TODO: Error Check
# TODO: functions' interface
