import struct, socket, time, logging, random
import ConfigParser

import twisted.internet.defer as defer
from twisted.internet.protocol import Factory
from twisted.internet import reactor

from ntcp.stunt.StuntProtocol import StuntProtocol

# Load configuration
p2pConfig = ConfigParser.ConfigParser()
p2pConfig.read("p2pNetwork.conf")

class StuntServer(StuntProtocol, object):

  logging.basicConfig()
  log = logging.getLogger("stunt")
  log.setLevel(logging.DEBUG)
  
  def __init__(self):

    self.stuntAddress = p2pConfig.get('stunt', 'stuntIp'), \
                      int(p2pConfig.get('stunt', 'stuntPort'))
    self.otherStuntAddress = p2pConfig.get('stunt', 'otherStuntIp'), \
                      int(p2pConfig.get('stunt', 'otherStuntPort'))


  def connectionMade(self):
    """
    Connection with client has be established
    """
    self.clientAddress = (self.transport.getPeer().host, self.transport.getPeer().port)
    self.log.debug('Stunt: connection received by: %s:%d'%self.clientAddress)

  def connectionLost(self, reason):
    """
    Connection with client lost
    """
    self.log.debug('Lost connection.  Reason:%s'%reason)

  def rcvBindingRequest(self):
    """
    Binding request received from a client
    """
    self.sndBindingResponse()

  def sndBindingResponse(self):
    """
    Sends a binding response to binding request
    """
    self.messageType = 'Binding Response'
    
    listAttr = ()
    # Put client public address in the message
    listAttr = listAttr + ((0x0001, self.getPortIpList(self.clientAddress)),)
    listAttr = listAttr + ((0x0005, self.getPortIpList(self.otherStuntAddress)),)
    self.createMessage(listAttr)
    self.sendMessage()
    self.transport.loseConnection()

  def rcvCaptureRequest(self):
    """
    Capture request received from a client
    """
    # Send a SYN packet from different address
    print "received Capture Request"
    avtype = 'CHANGE-REQUEST'
    
    #change = (struct.unpack('!i', self.avtypeList[avtype]))[0]
    #toAddr = self.getAddress('RESPONSE-ADDRESS')
    print avtype
      
 
factory = Factory()
factory.protocol = StuntServer

# Listen on two different addresses and two ports
port1 =  int(p2pConfig.get('stunt', 'stuntPort'))
port2 =  int(p2pConfig.get('stunt', 'otherStuntPort'))
reactor.listenTCP(port1, factory)
reactor.listenTCP(port2, factory)

reactor.run()
