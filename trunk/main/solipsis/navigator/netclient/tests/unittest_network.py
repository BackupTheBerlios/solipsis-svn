"""test basic commands of net navigator"""

import sys, os
import threading
import twisted.scripts.trial as trial
    
from twisted.trial import unittest, util
from twisted.internet import base, defer
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

class CommandTest(unittest.TestCase):
    """Test good completion of basic commands"""

    def __init__(self):
        import solipsis
        # app needs logging dir
        os.mkdir("log")
        os.mkdir("state")
        # get conf file
        solipsis_path = os.path.abspath(os.path.dirname(solipsis.__file__))
        self.conf_file = os.path.normpath(os.sep.join([solipsis_path, "..", "conf", "solipsis.conf"]))

    def setUp(self):
        from twisted.internet import reactor
        from solipsis.navigator.main import build_params
        from solipsis.navigator.netclient.app import NavigatorApp
        # launch application
        self.factory = ReconnectingFactory()
        params = build_params(self.conf_file)
        params.testing = True
        navigator = NavigatorApp(params=params)
        reactor.connectTCP("localhost",
                           navigator.local_port,
                           self.factory)
        # wait for connection to app establisehd
        self.factory.deferred = defer.Deferred()
        self.factory.deferred.addCallback(self.assertEquals, "Ready")
        return self.factory.deferred
    setUp.timeout = 4

    def tearDown(self):
        # close application
        self.factory.sendLine("quit")

    def test_about(self):
        """command about"""
        self.factory.deferred = defer.Deferred()
        self.factory.deferred.addCallback(self.assertEquals, """About...: Solipsis Navigator 0.9.2svn

Licensed under the GNU LGPL
(c) France Telecom R&D""")
        self.factory.sendLine("about")
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
    main()
