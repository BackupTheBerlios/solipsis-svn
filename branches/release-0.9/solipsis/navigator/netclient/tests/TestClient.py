from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, defer

from solipsis.navigator.netclient.tests import waiting

import sys

class WaitingDeferred(defer.Deferred):

    def __init__(self, msg):
        defer.Deferred.__init__(self)
        self.msg = msg

# connect to server with user_name (defined in factory)
# print received data
class TestProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.transport = self.transport

    def lineReceived(self, data):
        if not self.factory.expected_response:
            raise AssertionError("unexpected response: %s"% data)
        deferred = self.factory.expected_response.pop()
        if deferred:
            if isinstance(deferred, WaitingDeferred):
                if deferred.msg == data:
#                     print "!!!", data
                    deferred.callback(data)
                else:
#                     print ">>>", data
                    self.factory.expected_response.append(deferred)
            else:
#                 print "===", data
                deferred.callback(data)
        else:
            pass
#             print "...", data

# store persistent data (user_name)
# echo steps of connecting
class TestClientFactory(ReconnectingClientFactory):

    def __init__(self):
        self.transport = None
        self.expected_response = []

    def buildProtocol(self, addr):
        self.resetDelay()
        instance = TestProtocol()
        # !! do not forget to set factory attribute
        setattr(instance, 'factory', self)
        return instance

    def wait(self, msg):
        while not self.transport:
            waiting()
        # wait for msg
        deferred = WaitingDeferred(msg)
        self.expected_response.insert(0, deferred)
        return deferred

    def write(self, msg):
        while not self.transport:
            waiting()
        # send msg
        self.expected_response.insert(0, None)
        self.transport.write(msg+"\r\n")

    def check(self, msg, deferred=None):
        while not self.transport:
            waiting()
        # send msg
        if not deferred:
            deferred = defer.Deferred()
        self.expected_response.insert(0, deferred)
        self.transport.write(msg+"\r\n")
        return deferred
    
    def clientConnectionLost(self, connector, reason):
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    
    def clientConnectionFailed(self, connector, reason):
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
