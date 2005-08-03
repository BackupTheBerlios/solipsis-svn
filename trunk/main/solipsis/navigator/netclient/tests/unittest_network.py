"""test basic commands of net navigator"""

import sys, os
import threading
    
from twisted.trial import unittest
from twisted.internet import base
from twisted.internet import reactor, defer
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver
import twisted.scripts.trial as trial

from solipsis.navigator.main import build_params
from solipsis.navigator.netclient.app import NavigatorApp

class CommandTest(unittest.TestCase):
    """Test good completion of basic commands"""
    
    def setUp(self):
        # enable rich trace when exception on DelayedCalls
        print "setUp"
        base.DelayedCall.debug = True
        self.factory.deferred = defer.Deferred()
        self.factory.deferred.addCallback(self.assertEquals, "Ready")
              
    def tearDown(self):
        # diable rich traces
        print "tearDown"
        base.DelayedCall.debug = False

    def test_about(self):
        """command about"""
        print "test_about"
        self.factory.deferred.addCallback(self.assertEquals, """Solipsis Navigator 0.1.1

Licensed under the GNU LGPL
(c) France Telecom R&D""")
        self.factory.sendLine("about")
        return self.factory.deferred

# Network classes
# ===============
class TestProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.sendLine = self.sendLine
        global test_case
        sys.path.insert(0, os.getcwd())
        if test_case:
            test_case = ".".join([__file__.split('.')[0], test_case])
        else:
            test_case = __file__.split('.')[0]
        print "trial %s"% test_case
        sys.argv = [sys.argv[0], test_case]
        trial.run()

    def lineReceived(self, data):
        self.factory.deferred.callback(data)
        
class TestClientFactory(ReconnectingClientFactory):

    protocol = TestProtocol

    def __init__(self):
        self.deferred = None

    def startedConnecting(self, connector):
        self.resetDelay()

    def clientConnectionLost(self, connector, reason):
        print "clientConnectionLost"
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    
    def clientConnectionFailed(self, connector, reason):
        print "clientConnectionFailed"
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

# LAUNCHER
# ========
def main(test_case=None):
    # init application
    import solipsis
    solipsis_path = os.path.abspath(os.path.dirname(solipsis.__file__))
    conf_file = os.path.normpath(os.sep.join([solipsis_path, "..", "conf", "solipsis.conf"]))
    # application
    navigator = NavigatorApp(params=build_params(conf_file))
    factory = TestClientFactory()
    reactor.connectTCP("localhost",
                       navigator.local_port,
                       factory)
    
if __name__ == '__main__':
    global test_case
    if len(sys.argv)>1:
        test_case = sys.argv[1]
    else:
        test_case = "CommandTest"
    main()
