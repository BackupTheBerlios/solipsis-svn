from twisted.internet.protocol import Protocol, ReconnectingClientFactory
from twisted.internet import reactor, defer

import sys

# connect to server with user_name (defined in factory)
# print received data
class TestProtocol(Protocol):

    def connectionMade(self):
        self.factory.transport = self.transport

    def dataReceived(self, data):
        if self.factory.deferred:
            self.factory.deferred.callback(data)
            self.factory.deferred = None

# store persistent data (user_name)
# echo steps of connecting
class TestClientFactory(ReconnectingClientFactory):

    def __init__(self):
        self.transport = None
        self.deferred = None

    def buildProtocol(self, addr):
        self.resetDelay()
        instance = TestProtocol()
        # !! do not forget to set factory attribute
        setattr(instance, 'factory', self)
        return instance

    def write(self, msg):
        if self.transport:
            self.deferred = defer.Defered()
            self.transport.write(msg+"\r\n")
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
        return self.deferred
    
    def clientConnectionLost(self, connector, reason):
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    
    def clientConnectionFailed(self, connector, reason):
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
