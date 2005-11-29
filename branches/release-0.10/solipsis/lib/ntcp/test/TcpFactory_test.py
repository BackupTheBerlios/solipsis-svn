from twisted.internet.protocol import Protocol, ClientFactory, DatagramProtocol
from twisted.internet import reactor
from sys import stdout, stdin


class Chat:
    def readWrite(self, transport, simulator):
                  
        print ' ',simulator.uri,'>> ',
        data=stdin.readline()
        while data != 'exit\n':
            transport.write(data)
            print simulator.uri,'>> ',
            data=stdin.readline()
        transport.loseConnection() 
      
class TcpConnection(Protocol):
    """
    All the Twisted functions for a TCP connection (c/s) 
    """
    def __init__(self, reactor, simulator):
        self.reactor = reactor
        self.simulator = simulator 
        
    def dataReceived(self, data):
        print self.simulator.remote,'>>',data

    def connectionMade(self):
        print ''
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Connection Made...now you can send data...'

        print ' ',self.simulator.uri,'>> ',
        data=stdin.readline()
        while data != 'exit\n':
            data = ''.join((data,'\r\n'))
            self.transport.write(data)
            print self.simulator.uri,'>> ',
            data=stdin.readline()
        self.transport.loseConnection()
        
##         chat = Chat()
##         self.reactor.callInThread(chat.readWrite, self.transport, self.simulator)
        
    def connectionLost(self, reason):
        print 'Lost connection.  Reason:', reason

    def startedConnecting(self, connector):
        pass
      
class TcpServer(Protocol):
    """
    All the Twisted functions for a TCP connection (c/s) 
    """
    def __init__(self, reactor, simulator):
        self.reactor = reactor
        self.simulator = simulator 
        
    def dataReceived(self, data):
        print self.simulator.remote,'>>',data

    def connectionMade(self):
        print ''
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Connection Made...now you can receive data...'

    def connectionLost(self, reason):
        print 'Lost connection.  Reason:', reason

    def startedConnecting(self, connector):
        pass
    
    def buildProtocol(self, addr):
        return TcpServer(self.reactor, self.simulator)
        
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
    
class TcpFactory(ClientFactory):
    
    def __init__(self, reactor, simulator):
        self.reactor = reactor
        self.simulator = simulator 
        
        
    def startedConnecting(self, connector):
        pass
    
    def buildProtocol(self, addr):
        return TcpConnection(self.reactor, self.simulator)
    
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
    
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
