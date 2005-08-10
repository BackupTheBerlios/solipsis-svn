"""test basic commands of net navigator"""

import sys
import twisted.scripts.trial as trial
    
from Queue import Queue
from twisted.trial import unittest, util
from twisted.internet import defer
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

from solipsis.navigator.netclient.tests import LOCAL_PORT
        
class NetworkTest(unittest.TestCase):

    def setUp(self):
        from twisted.internet import reactor
        # launch 'telnet'
        self.factory = ReconnectingFactory()
        self.connector = reactor.connectTCP("localhost",
                           LOCAL_PORT,
                           self.factory)
        # wait for connection to app establisehd
        return self.assertMessage("Ready")
    setUp.timeout = 6

    def tearDown(self):
        self.factory.stopTrying()
        self.factory.stopFactory()
        self.connector.disconnect()

    def assertMessage(self, message):
        deferred = defer.Deferred()
        self.factory.deferred.put(deferred)
        deferred.addCallback(self.assertEquals, message)
        return deferred

    def assertResponse(self, cmd, response):
        deferred = self.assertMessage(response)
        self.factory.sendLine(cmd)
        return deferred
        
class DisconnectedTest(NetworkTest):
    """Test good completion of basic commands"""

    def test_about(self):
        return self.assertResponse("about", """About...: Solipsis Navigator 0.9.3svn

Licensed under the GNU LGPL
(c) France Telecom R&D""")
    test_about.timeout = 2

    def _test_launch(self):
        self.assertResponse("launch", "Connected")
        return self.assertResponse("disconnect", "Disconnected")
    _test_launch.timeout = 2

    def test_display(self):
        return self.assertResponse("display", "Not connected")
    test_display.timeout = 2

    def test_menu(self):
        return self.assertResponse("menu", "Not implemented yet")
    test_menu.timeout = 2

    def test_help(self):
        return self.assertResponse("help", "available commands are: ['quit', 'about', 'disconnect', 'help', 'launch', 'menu', 'jump', 'kill', 'connect', 'go', 'display']\n")
    test_help.timeout = 2

class ConnectedTest(NetworkTest):
    """Test good completion of basic commands"""

    def setUp(self):
        deferred = NetworkTest.setUp(self)
        deferred.addCallback(self._setUp)
        return deferred
    setUp.timeout = 8

    def _setUp(self, result):
        self.assertResponse("display", "Not connected")
        self.assertResponse("connect bots.netofpeers.net:8554", "Connected")

    def tearDown(self):
        deferred = self.assertResponse("disconnect", "Disconnected")
        deferred.addCallback(NetworkTest.tearDown)
        return deferred
    tearDown.timeout = 2

    def test_display(self):
        return self.assertResponse("display", "192.33.178.29:6004")
    test_display.timeout = 2

# Network classes
# ===============
class SimpleProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.sendLine = self.sendLine

    def lineReceived(self, data):
        if not self.factory.deferred.empty():
            self.factory.deferred.get().callback(data)
        
class ReconnectingFactory(ReconnectingClientFactory):

    protocol = SimpleProtocol

    def __init__(self):
        self.deferred = Queue()

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
        test_case = sys.argv[1]
    else:
        test_case = "CommandTest"
    test_case = ".".join([__file__.split('.')[0], test_case])
    # launch trial
    sys.argv = [sys.argv[0], test_case]
    trial.run()
    
if __name__ == '__main__':
    import os
    print "./launch.py"
    os.spawnv(os.P_NOWAIT, "./launch.py", ["launch.py"])
    print "./launch.py -p 23501"
    os.spawnv(os.P_NOWAIT, "./launch.py", ["launch.py", "-p",  "23501"])
    main()
