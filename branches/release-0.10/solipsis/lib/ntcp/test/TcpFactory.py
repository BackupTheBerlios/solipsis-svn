from twisted.internet.protocol import Protocol, ClientFactory, DatagramProtocol
from twisted.internet import reactor
from sys import stdout, stdin

class TcpConnection(Protocol):
    """
    All the Twisted functions for a TCP connection (c/s) 
    """
        
    def dataReceived(self, data):
        print '>>',data

    def connectionMade(self):
        print ''
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Connection Made...now you can send data...'

        print '>> ',
        data=stdin.readline()
        while data != 'exit\n':
            self.transport.write(data)
            print '>> ',
            data=stdin.readline()
        self.transport.loseConnection()

    def connectionLost(self, reason):
        print 'Lost connection.  Reason:', reason

    def startedConnecting(self, connector):
        pass
      
class TcpServer(Protocol):
    """
    All the Twisted functions for a TCP connection (c/s) 
    """
        
    def dataReceived(self, data):
        print '>>',data

    def connectionMade(self):
        print ''
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Connection Made...now you can receive data...'

    def connectionLost(self, reason):
        print 'Lost connection.  Reason:', reason

    def startedConnecting(self, connector):
        pass
    
    def buildProtocol(self, addr):
        return TcpServer()
        
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
    
      
class TcpFactory(ClientFactory):
    
    def startedConnecting(self, connector):
        pass
    
    def buildProtocol(self, addr):
        return TcpConnection()
    
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
    
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
