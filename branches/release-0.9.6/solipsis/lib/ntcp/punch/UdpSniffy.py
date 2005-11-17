
class UDP_factory:
  """An UDP service to allow a TCP connection:
   - Hole punching to connect in UDP to the other peer
   - Forces the ack number in a TCP response packet sent via UDP hole"""

  def __init__(self, connector):
    self.connector = connector
    self.punch = self.connector.punch
    
  def send_SYN_to_ConnectionBroker(self, syn):
    """Sends the SYN number of my connect()ion to:
    - the connection broker for spoofing"""


    listAttr = ()
    self.SYN=int(syn)
    listAttr = listAttr + ((0x0005, \
                            self.punch.getPortIpList(self.connector.publicAddress)),)
    listAttr = listAttr + ((0x0002, \
                            self.punch.getPortIpList(self.connector.remotePublicAddress)),)
    listAttr = listAttr + ((0x1001, self.SYN),)

    self.punch.messageType = 'Forcing TCP Request'
    self.punch.tid = self.punch.getRandomTID()
    self.punch.sendMessage(self.connector.cbAddress, listAttr)
