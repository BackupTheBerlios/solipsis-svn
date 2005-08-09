"""test basic commands of net navigator"""

import sys
import twisted.scripts.trial as trial
    
from twisted.trial import unittest, util
from twisted.internet import defer
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

from solipsis.navigator.netclient.tests import LOCAL_PORT

class CommandTest(unittest.TestCase):
    """Test good completion of basic commands"""

    def setUp(self):
        from twisted.internet import reactor
        # launch 'telnet'
        self.factory = ReconnectingFactory()
        self.connector = reactor.connectTCP("localhost",
                           LOCAL_PORT,
                           self.factory)
        # wait for connection to app establisehd
        self.factory.deferred = defer.Deferred()
        self.factory.deferred.addCallback(self.assertEquals, "Ready")
        return self.factory.deferred
    setUp.timeout = 6

    def tearDown(self):
        self.factory.stopTrying()
        self.factory.stopFactory()
        self.connector.disconnect()

    def assertResponse(self, cmd, response):
        self.factory.deferred = defer.Deferred()
        self.factory.deferred.addCallback(self.assertEquals, response)
        self.factory.sendLine(cmd)

    def test_about(self):
        self.assertResponse("about", """About...: Solipsis Navigator 0.9.3svn

Licensed under the GNU LGPL
(c) France Telecom R&D""")
        return self.factory.deferred
    test_about.timeout = 2

    def test_help(self):
        self.assertResponse("help", "available commands are: ['quit', 'about', 'disconnect', 'help', 'launch', 'menu', 'jump', 'kill', 'connect', 'go', 'display']\n")
        return self.factory.deferred
    test_about.timeout = 2

    def test_menu(self):
        self.assertResponse("menu", "Not implemented yet")
        return self.factory.deferred
    test_about.timeout = 2

# Network classes
# ===============
class SimpleProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.sendLine = self.sendLine

    def lineReceived(self, data):
        if not self.factory.deferred is None:
            self.factory.deferred.callback(data)
            self.deferred = None
        
class ReconnectingFactory(ReconnectingClientFactory):

    protocol = SimpleProtocol

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
