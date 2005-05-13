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
        # create TCP client
        self.factory = TestClientFactory()
        self.done = False
        self.waiting = False

    def _failed(self, why):
        """used by callbacks when self.assertXxx not available"""
        self.done = True
        raise AssertionError("Failed:", why)

    def _finished(self):
        """complete test by setting flag done to True"""
        self.done = True

    def _stop_waiting(self, data):
        """complete test by setting flag done to True"""
        self.waiting = False

    def _wait_for(self, msg):
        self.waiting = True
        deferred = self.factory.wait(msg)
        deferred.addCallback(self._stop_waiting)
        while self.waiting:
            waiting()
        
    def setUp(self):
        """overrides TestCase method"""
        self.navigator.startListening()
        self.connector = reactor.connectTCP("localhost", PORT, self.factory)
        # set timeout
        self.timeout = reactor.callLater(5, self._failed, "timeout")
        self.done = False

    def tearDown(self):
        """overrides TestCase method"""
        # close connection
        self.factory.stopTrying()
        self.connector.disconnect()
        self.done = True
        # remove timeout
        try:
            self.timeout.cancel()
            reactor.iterate(0.1)
        except (error.AlreadyCancelled, error.AlreadyCalled):
            pass
        # stop listening
        defered = self.navigator.stopListening()
        if defered:
            self.done = False
            defered.addCallback(self._finished)
            defered.addErrback(self._failed)
            while not self.done:
                waiting()

    def test_not_valid(self):
        """command not valid"""
        # assert using 'deferredResult'
        deferred = self.factory.check("dummy")
        self.assertEquals(unittest.deferredResult(deferred),
                          """do_dummy not a valid command""")
        # assert using custom callback
        deferred = self.factory.check("")
        deferred.addCallback(self._assert_not_valid)
        while not self.done:
            reactor.iterate(0.1)
            
    def _assert_not_valid(self, msg):
        """call back expected on not valid command'"""
        self.done = True
        self.assertEquals(msg, "do_ not a valid command")

    def test_about(self):
        """command about"""
        deferred = self.factory.check("about")
        self.assertEquals(unittest.deferredResult(deferred),
                          """Solipsis Navigator 0.1.1

Licensed under the GNU LGPL
(c) France Telecom R&D""")

    def test_check_connection(self):
        """command check"""
        deferred = self.factory.check("check")
        self.assertEquals(unittest.deferredResult(deferred),
                          """False""")
        self.factory.write("connect")
        self.factory.write("bots.netofpeers.net:8555")
        self._wait_for("Connected")
        deferred = self.factory.check("check")
        self.assertEquals(unittest.deferredResult(deferred),
                          """True""")

# FIXME
#     def test_create(self):
#         """command create"""
#         deferred = self.factory.check("check")
#         self.assertEquals(unittest.deferredResult(deferred),
#                           """False""")
#         self.factory.write("connect")
#         self.factory.write("bots.netofpeers.net:8555")
#         self._wait_for("Connected")
#         self.factory.write("create")
#         deferred = self.factory.check("Tester")

    def test_disconnect(self):
        """command disconnect"""
        deferred = self.factory.check("disconnect")
        self.assertEquals(unittest.deferredResult(deferred),
                          """not connected""")
        self.factory.write("connect")
        self.factory.write("bots.netofpeers.net:8555")
        self._wait_for("Connected")
        deferred = self.factory.check("disconnect")
        self.assertEquals(unittest.deferredResult(deferred),
                          """Not connected""")

    def test_display(self):
        """command display"""
        deferred = self.factory.check("display")
        self.assertEquals(unittest.deferredResult(deferred),
                          """not connected""")
        self.factory.write("connect")
        self.factory.write("bots.netofpeers.net:8555")
        self._wait_for("Connected")
        # not using deferredResult here since it swallows timeout
        deferred = self.factory.check("display")
        deferred.addCallback(self._assert_display)
        while not self.done:
            reactor.iterate(0.1)
            
    def _assert_display(self, msg):
        """call back expected on not valid command'"""
        self.done = True
        self.assertEquals(msg, "192.33.178.29:6005")

    def test_go(self):
        """command go"""
        deferred = self.factory.write("go")
        deferred = self.factory.check("")
        self.assertEquals(unittest.deferredResult(deferred),
                          """2 parameters instead of 2, using default\nnot connected\n""")
        self.factory.write("connect")
        self.factory.write("bots.netofpeers.net:8555")
        self._wait_for("Connected")
        self.factory.write("go")
        deferred = self.factory.check("")
        self.assertEquals(unittest.deferredResult(deferred),
                          """2 parameters instead of 2, using default\nmoved to 0.0,0.0\n""")
        self.factory.write("go")
        deferred = self.factory.check("0.25,0.43")
        self.assertEquals(unittest.deferredResult(deferred),
                          """moved to 0.25,0.43""")

    def test_help(self):
        """command help"""
        deferred = self.factory.check("help")
        self.assertEquals(unittest.deferredResult(deferred),
                          """[all]""")
        deferred = self.factory.check("")
        self.assertEquals(unittest.deferredResult(deferred),
                          """{'about': ['display general information', ''],
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

#FIXME
#     def test_hover(self):
#         """command hover"""
#         while not self.done:
#             reactor.iterate(0.1)
#             self.deferred.addCallback(self._assert_hover)
#             self.factory.write("hover", self.deferred)

    def test_jump(self):
        """command jump"""
        deferred = self.factory.check("jump")
        self.assertEquals(unittest.deferredResult(deferred),
                          """[192.33.178.29:5010]""")
        deferred = self.factory.check("")
        self.assertEquals(unittest.deferredResult(deferred),
                          """not connected""")
        self.factory.write("connect")
        self.factory.write("bots.netofpeers.net:8555")
        self._wait_for("Connected")
        self.factory.check("jump")
        self.assertEquals(unittest.deferredResult(deferred),
                          """192.33.178.29:5010""")

#FIXME
#     def test_kill(self):
#         """command kill"""
#         while not self.done:
#             reactor.iterate(0.1)
#             self.deferred.addCallback(self._assert_kill)
#             self.factory.write("kill", self.deferred)


    def test_menu(self):
        """command menu"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_menu)
            self.factory.write("menu", self.deferred)

    def test_quit(self):
        """command quit"""
        # not using deferredResult here since it swallows timeout
        deferred = self.factory.check("quit")
        deferred.addCallback(self._assert_quit)
        while not self.done:
            reactor.iterate(0.1)
            
    def _assert_quit(self, msg):
        """call back expected on not valid command'"""
        self.done = True
        self.assertEquals(msg, "connection reset")
        
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
