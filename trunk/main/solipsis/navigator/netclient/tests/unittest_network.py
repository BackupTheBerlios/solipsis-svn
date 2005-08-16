"""test basic commands of net navigator"""

import sys
import twisted.scripts.trial as trial
    
from Queue import Queue
from twisted.trial import unittest, util
from twisted.internet.defer import Deferred
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

    def assertMessage(self, message, factory=None):
        if factory is None:
            factory = self.factory
        deferred = Deferred()
        factory.deferred.put(deferred)
        deferred.addCallback(self.assertEquals, message)
        return deferred

    def assertResponse(self, cmd, response, factory=None):
        if factory is None:
            factory = self.factory
        deferred = self.assertMessage(response, factory)
        factory.sendLine(cmd)
        return deferred

    def assertPosition(self, response, rounding=0.03, factory=None):
        if factory is None:
            factory = self.factory
        deferred = Deferred()
        factory.deferred.put(deferred)
        def assert_position(msg):
#             print "COMPARE", msg, response
            # convert to float
            x, y = msg.split(" ")
            x, y = float(x), float(y)
            expected_x, expected_y = response.split(" ")
            expected_x, expected_y = float(expected_x), float(expected_y)
            # evaluate difference
            diff_x = abs(expected_x - x)
            diff_y = abs(expected_y - y)
            try: 
                self.assert_(diff_x < rounding or diff_x > 1-rounding)
                self.assert_(diff_y < rounding or diff_y > 1-rounding)
            except AssertionError:
                print "%.2f, %.2f out of %.2f %.2f"% (x, y, diff_x, diff_y)
                raise
        deferred.addCallback(assert_position)
        factory.sendLine('where')
        return deferred
        
class DisconnectedTest(NetworkTest):
    """Test good completion of basic commands"""

    def test_about(self):
        return self.assertResponse("about", """About...: Solipsis Navigator 0.9.3svn

Licensed under the GNU LGPL
(c) France Telecom R&D""")
    test_about.timeout = 2

    def test_connect(self):
        util.wait(self.assertResponse("connect bots.netofpeers.net:8553", "Connected"))
        util.wait(self.assertResponse("display", "Address: 192.33.178.29:6003"))
        util.wait(self.assertResponse("disconnect", "Disconnected"))
    test_connect.timeout = 2

    def test_display(self):
        return self.assertResponse("display", "Not connected")
    test_display.timeout = 2

    def test_menu(self):
        return self.assertResponse("menu", "Not implemented yet")
    test_menu.timeout = 2

    def test_help(self):
        return self.assertResponse("help", "available commands are: ['quit', 'about', 'disconnect', 'help', 'launch', 'menu', 'who', 'jump', 'kill', 'connect', 'go', 'where', 'display']\n")
    test_help.timeout = 2

class ConnectedTest(NetworkTest):
    """Test good completion of basic commands"""

    def setUp(self):
        util.wait(NetworkTest.setUp(self))
        return self.assertResponse("connect bots.netofpeers.net:8553", "Connected")
    setUp.timeout = 8

    def tearDown(self):
        util.wait(self.assertResponse("disconnect", "Disconnected"))
        NetworkTest.tearDown(self)
    tearDown.timeout = 2

    def test_display(self):
        return self.assertResponse("display", "Address: 192.33.178.29:6003")
    test_display.timeout = 2

    def test_go(self):
        self.factory.sendLine("go")
        util.wait(self.assertPosition("0.0 0.0", rounding=0.05))
        self.factory.sendLine("go 0.1 0.3")
        return self.assertPosition("0.1 0.3")
    test_go.timeout = 2
        
class ProfileTest(NetworkTest):
    """Test good completion of basic commands"""

    def assertOtherMessage(self, message):
        return NetworkTest.assertMessage(self, message,
                                           factory=self.other_factory)

    def assertOtherResponse(self, cmd, response):
        return NetworkTest.assertResponse(self, cmd, response,
                                            factory=self.other_factory)

    def assertOtherPosition(self, position):
        return NetworkTest.assertPosition(self, position,
                                            factory=self.other_factory)

    def setUp(self):
        # launch fisrt navigator
        util.wait(NetworkTest.setUp(self))
        util.wait(self.assertResponse("connect bots.netofpeers.net:8553", "Connected"))
        self.factory.sendLine("go 0.1 0.3")
        # launch 'telnet' on second navigator
        from twisted.internet import reactor
        self.other_factory = ReconnectingFactory()
        self.other_connector = reactor.connectTCP("localhost",
                                                  LOCAL_PORT+1,
                                                  self.other_factory)
        # wait for connection to app establisehd
        util.wait(self.assertOtherMessage("Ready"))
        util.wait(self.assertOtherResponse("connect bots.netofpeers.net:8554", "Connected"))
        self.other_factory.sendLine("go 0.6 0.8")
    setUp.timeout = 6

    def tearDown(self):
        # disconnect first one
        NetworkTest.tearDown(self)
        # second one
        self.other_factory.stopTrying()
        self.other_factory.stopFactory()
        self.other_connector.disconnect()

    def test_where(self):
        util.wait(self.assertPosition("0.1 0.3"))
        return self.assertOtherPosition("0.6 0.8")
    test_where.timeout = 2

    def test_jump(self):
        self.factory.sendLine("jump slp://192.33.178.29:6004")
        return self.assertPosition("0.6 0.8", rounding=0.05)
    test_jump.timeout = 2

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
        test_case = ".".join([__file__.split('.')[0], sys.argv[1]])
    else:
        test_case = __file__.split('.')[0]
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
