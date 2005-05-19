"""Represents data stored in cache, especially shared file information"""

import os
import sys
import solipsis

from twisted.trial import unittest
from twisted.internet import reactor, error, defer
from twisted.trial.util import deferredResult
from solipsis.navigator.netclient.tests import waiting
from solipsis.navigator.netclient.tests.TestClient import TestClientFactory
from solipsis.navigator.netclient.app import NavigatorApp
from solipsis.navigator.netclient.main import build_params

PORT = 1081

class CommandTestCase(unittest.TestCase):
    """Test good completion of basic commands"""
    
    def __init__(self, *args):
        # creating environment
        solipsis_dir =  os.path.dirname(solipsis.__file__)
        main_dir = os.path.dirname(solipsis_dir)
        os.chdir(main_dir)
        # reset arguments otherwise build_params tries them on
        # NavigatorApp and gets confused
        sys.argv = []
        params = build_params()
        # launching navigator
        self.navigator = NavigatorApp(params, port=PORT, log_file="test.log")
        self.waiting = False
        
    def setUp(self):
        """overrides TestCase method"""
        # create TCP client
        self.factory = TestClientFactory()
        self.navigator.startListening()
        self.connector = reactor.connectTCP("localhost", PORT, self.factory)
        # set timeout
        self.timeout = reactor.callLater(5, self._failed, "timeout")

    def tearDown(self):
        """overrides TestCase method"""
        # close connection
        self.factory.stopTrying()
        del self.factory
        self.connector.disconnect()
        # remove timeout
        try:
            d = self.timeout.cancel()
        except (error.AlreadyCancelled, error.AlreadyCalled):
            print "timeout canceled"
        # stop listening
        deferred = self.navigator.stopListening()
        if deferred:
            self.waiting = True
            deferred.addCallback(self._finished)
            deferred.addErrback(self._failed)
            while self.waiting:
                waiting()

# SIDE METHODS TO EASE TESTING
# ============
    def wait_for(self, msg):
        self.waiting = True
        deferred = self.factory.wait(msg)
        deferred.addCallback(self._finished)
        deferred.addErrback(self._failed)
        while self.waiting:
            waiting()

    def check_next(self, in_msg, out_msg):
        self.waiting = True
        def _assert_msg(msg):
            self.waiting = False
            self.assertEquals(msg, out_msg)
        deferred = self.factory.check(in_msg)
        deferred.addCallback(_assert_msg)
        deferred.addErrback(self._failed)
        while self.waiting:
            waiting()
        # NB: we could make assertion using 'deferredResult'
        # but this function swallows excemption (including timeout)
        # and is then not appropriate to unit tests
        #
        #    deferred = self.factory.check("dummy")
        #    self.assertEquals(unittest.deferredResult(deferred),
        #                      """do_dummy not a valid command""")

    def write(self, msg):
        self.factory.write(msg)
        
    def _failed(self, why):
        """used by callbacks when self.assertXxx not available"""
        self.waiting = False
        raise AssertionError("Failed:", why)

    def _finished(self):
        """complete test by setting flag done to True"""
        self.waiting = False

# TESTS
# =====
    def test_about(self):
        """command about"""
        self.check_next("about", """Solipsis Navigator 0.1.1

Licensed under the GNU LGPL
(c) France Telecom R&D""")

    def test_not_valid(self):
        """command not valid"""
        self.check_next("", "do_ not a valid command")
        self.check_next("dummy", "do_dummy not a valid command")

    def test_check_connection(self):
        """command check"""
        self.check_next("check", "False")
        self.write("connect")
        self.write("bots.netofpeers.net:8555")
        self.wait_for("Connected")
        self.check_next("check", "True")

    def test_disconnect(self):
        """command disconnect"""
        self.check_next("disconnect", "not connected")
        self.write("connect")
        self.write("bots.netofpeers.net:8555")
        self.wait_for("Connected")
        self.check_next("disconnect", "Not connected")

    def test_display(self):
        """command display"""
        self.check_next("display", "not connected")
        self.write("connect")
        self.write("bots.netofpeers.net:8555")
        self.wait_for("Connected")
        self.check_next("display", "192.33.178.29:6005")

    def test_go(self):
        """command go"""
        self.write("go")
        self.check_next("", "2 parameters instead of 2, using default\nnot connected\n")
        self.write("connect")
        self.write("bots.netofpeers.net:8555")
        self.wait_for("Connected")
        self.write("go")
        self.check_next("", "2 parameters instead of 2, using default\nmoved to 0.0,0.0\n")
        self.factory.write("go")
        self.check_next("0.25,0.43", "moved to 0.25,0.43\n")

    def test_help(self):
        """command help"""
        self.check_next("help", "[all]")
        self.check_next("", """{'about': ['display general information', ''],
 'check': ['chech status of connection', ''],
 'connect': ['connect to specified node', 'bots.netofpeers.net:8551'],
 'create': ['create Node', 'Guest'],
 'disconnect': ['discoonnect from current node', ''],
 'display': ['display current address', ''],
 'go': ['go to position', '0,0'],
 'help': ['display help [on cmd]', 'all'],
 'hover': ['emumate hover on peer', '0,0'],
 'jump': ['jump to node', '192.33.178.29:5010'],
 'kill': ['kill node', ''],
 'mem': ['dump a snapshot of memory (debugging tool)', ''],
 'menu': ['display peer menu', ''],
 'pref': ['change preferences', ''],
 'quit': ['close navigator', '']}\n""")

    def test_jump(self):
        """command jump"""
        self.check_next("jump", "[192.33.178.29:5010]")
        self.check_next("", "not connected")
        self.write("connect")
        self.write("bots.netofpeers.net:8555")
        self.wait_for("Connected")
        self.check_next("jump", "192.33.178.29:5010")
        
# LAUNCHER
# ========
def main(test_case=None):
    sys.path.insert(0, os.getcwd())
    if test_case:
        os.system("trial %s.%s"% (__file__.split('.')[0], test_case))
    else:
        os.system("trial %s"% __file__)
    
if __name__ == '__main__':
    if len(sys.argv)>1:
        main(sys.argv[1])
    else:
        main()
