

from twisted.internet.protocol import DatagramProtocol


class Protocol(DatagramProtocol):
    def __init__(self):
        self.hosts = []
        #~ DatagramProtocol.__init__(self)

    def SetHosts(self, hosts):
        self.hosts = list(hosts)
    
    def SendMessage(self, data, exclude_addr=None):
        for to_host, to_port in self.hosts:
            if exclude_addr is not None and (to_host, to_port) != exclude_addr:
                continue
            self.transport.write(data, (to_host, to_port))

    def datagramReceived(self, data, (from_host, from_port)):
        print "received %r from %s:%d" % (data, from_host, from_port)
        self.SendMessage(data, (from_host, from_port))


class NetworkLauncher(object):
    def __init__(self, reactor, plugin, port):
        self.reactor = reactor
        self.plugin = plugin
        self.port = port
        self.listening = None
        self.protocol = None

    def Start(self):
        if self.listening:
            self.Stop()
        self.protocol = Protocol()
        self.listening = self.reactor.listenUDP(self.port, self.protocol)
        # For test purposes
        host = self.listening.getHost().host
        self.protocol.SetHosts([(host, self.port)])
        self.protocol.SendMessage("ha! ha! ha!")

    def Stop(self):
        self.listening.stopListening()
        self.listening = None
        self.protocol = None

    def SendMessage(self, data):
        assert self.protocol is not None, "Tried to send message but protocol is None"
        self.protocol.SendMessage(data)
