"""test basic commands of net navigator"""

import sys
import os, os.path
import time
import twisted.scripts.trial as trial

from Queue import Queue
from twisted.trial import unittest, util
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols import basic


class ServerTest(unittest.TestCase):

    def __init__(self):
        self.deferreds = Queue(-1)

    def setUp(self):
        from solipsis.services.profile.protocols \
             import ProfileServerFactory
        self.server = ProfileServerFactory()

    def wait(self, sec_delay):
        wake_up = time.time() + sec_delay
        def _waiting():
            return time.time() < wake_up
        util.spinWhile(_waiting, sec_delay+1)

    def send(self, connector, msg):
        deferred = Deferred()
        self.deferreds.put(deferred)
        connector.transport.write(msg + "\r\n")
        return deferred

    def test_server(self):
        # wrapping when not initialised
        msg = self.server.wrap_message("HELLO")
        self.assertEquals("HELLO ?:-1 ", str(msg))
        def _on_test(result):
            # values set
            self.assertEquals(True, result)
            self.assertNotEquals(None, self.server.listener)
            self.assertNotEquals(None, self.server.public_ip)
            self.assertNotEquals(None, self.server.public_port)
            self.assertNotEquals(self.server.public_ip, self.server.local_ip)
            # wrapping
            msg = self.server.wrap_message("HELLO")
            self.assertNotEquals("HELLO ?:-1 ", str(msg))
            self.server.stop_listening()
        deferred = self.server.start_listening()
        deferred.addCallbacks(_on_test)
        return deferred
    test_server.timeout = 8

    def test_connection(self):
        # start server
        util.wait(self.server.start_listening(), timeout=8)
        # start client
        from twisted.internet import reactor
        factory = ReconnectingFactory(self.deferreds)
        connector = reactor.connectTCP("localhost",
                                       self.server.local_port,
                                       factory)
        def _on_test(result):
            self.assertEquals("pong", result)
            self.server.stop_listening()
            factory.stopTrying()
            factory.stopFactory()
            connector.disconnect()
            self.wait(1)
        self.wait(1)
        deferred = self.send(connector, "ping")
        deferred.addCallbacks(_on_test)
        return deferred
    test_connection.timeout = 8

# Network classes
# ===============
class SimpleProtocol(basic.LineReceiver):

    def connectionMade(self):
        print "***SimpleProtocol connectionMade"

    def lineReceived(self, data):
        print "***SimpleProtocol lineReceived", data
        self.factory.deferreds.get().callback(data)
        
class ReconnectingFactory(ReconnectingClientFactory):

    protocol = SimpleProtocol

    def __init__(self, deferreds):
        self.deferreds = deferreds

    def startedConnecting(self, connector):
        self.resetDelay()

    def clientConnectionLost(self, connector, reason):
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    
    def clientConnectionFailed(self, connector, reason):
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

# LAUNCHER
# ========
def main():
    # init test cases
    if len(sys.argv)>1:
        test_case = ".".join([__file__.split('.')[0], sys.argv[1]])
    else:
        test_case = __file__.split('.')[0]
    # launch trial
    sys.argv = [sys.argv[0], test_case]
    trial.run()
    
if __name__ == '__main__':
    import socket
    sock = socket.socket()
    try:
        sock.Bind("localhost", LOCAL_PORT)
        sock.close()
        print "be sure to execute ./launch.py -d first"
    except:
        main()
