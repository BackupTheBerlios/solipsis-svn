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

    def test_check(self):
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

    def test_connect(self):
        """command connect"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_connect)
            self.factory.write("connect")
            self.factory.write("bots.netofpeers.net:8555", self.deferred)

    def test_create_off(self):
        """command create"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_not_connected)
            self.factory.write("create", self.deferred)

    def test_create(self):
        """command create"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_create)
            self.factory.write("connect")
            self.factory.write("bots.netofpeers.net:8555")
            self.factory.write("create")
            self.factory.write("Tester", self.deferred)

    def test_disconnect_off(self):
        """command disconnect"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_not_connected)
            self.factory.write("disconnect", self.deferred)

    def test_disconnect(self):
        """command disconnect"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_disconnect)
            self.factory.write("connect")
            self.factory.write("bots.netofpeers.net:8555")
            self.factory.write("disconnect", self.deferred)

    def test_display_off(self):
        """command display"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_not_connected)
            self.factory.write("display", self.deferred)

    def test_display(self):
        """command display"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_display)
            self.factory.write("connect")
            self.factory.write("bots.netofpeers.net:8555")
            self.factory.write("display", self.deferred)

    def test_go_off(self):
        """command go"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_not_connected)
            self.factory.write("go", self.deferred)

    def test_go_default(self):
        """command go"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_go_default)
            self.factory.write("connect")
            self.factory.write("bots.netofpeers.net:8555")
            self.factory.write("go")
            self.factory.write("", self.deferred)

    def test_go(self):
        """command go"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_go)
            self.factory.write("connect")
            self.factory.write("bots.netofpeers.net:8555")
            self.factory.write("go")
            self.factory.write("0.25,0.43", self.deferred)

    def test_help(self):
        """command help"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_help)
            self.factory.write("help")
            self.factory.write("", self.deferred)

    def test_hover(self):
        """command hover"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_hover)
            self.factory.write("hover", self.deferred)

    def test_jump(self):
        """command jump"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_jump)
            self.factory.write("jump")
            self.factory.write("", self.deferred)

    def test_kill(self):
        """command kill"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_kill)
            self.factory.write("kill", self.deferred)

    def test_mem(self):
        """command mem"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_mem)
            self.factory.write("mem", self.deferred)

    def test_menu(self):
        """command menu"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_menu)
            self.factory.write("menu", self.deferred)

    def test_pref(self):
        """command pref"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_pref)
            self.factory.write("pref", self.deferred)

    def test_quit(self):
        """command quit"""
        while not self.done:
            reactor.iterate(0.1)
            self.deferred.addCallback(self._assert_quit)
            self.factory.write("quit", self.deferred)
            
    def _assert_about(self, msg):
        """call back expected on 'about'"""
        print "2 *****", msg
        if msg == """Solipsis NAVIGATOR 0.1.1
 
 Licensed under the GNU LGPL
 (c) France Telecom R&D)""":
            self.done = True

    def _assert_check(self):
        """call back expected on  check"""
        self.done = True
        self.assertEquals(msg, "False")

    def _assert_connect(self):
        """call back expected on  connect"""
        self.done = True
        self.assertEquals(msg, """connecting to bots.netofpeers.net:8555""")

    def _assert_create(self):
        """call back expected on  create"""
        self.done = True
        self.assertEquals(msg, """creating node for Tester""")
        #TODO: also check second msg: 'connecting to localhost:8550'

    def _assert_disconnect(self):
        """call back expected on  disconnect"""
        self.done = True
        self.assertEquals(msg, """Not connected""")

    def _assert_display(self):
        """call back expected on  display"""
        self.done = True
        self.assertEquals(msg, """192.33.178.29:6005""")

    def _assert_go_default(self):
        """call back expected on  go"""
        self.done = True
        self.assertEquals(msg, """2 parameters instead of 2, using default
moved to 0.0,0.0""")

    def _assert_go(self):
        """call back expected on  go"""
        self.done = True
        self.assertEquals(msg, """moved to 0.25,0.43""")
            
    def _assert_help(self, msg):
        """call back expected on 'help'"""
        self.done = True
        self.assertEquals(msg, """{'about': ['display general information', ''],
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
 'quit': ['close navigator', '']}""")
        
    def _assert_hover(self):
        """call back expected on  hover"""
        self.done = True
        self.assertEquals(msg, """""")

    def _assert_jump(self):
        """call back expected on  jump"""
        self.done = True
        self.assertEquals(msg, """192.33.178.29:5010""")

    def _assert_kill(self):
        """call back expected on  kill"""
        self.done = True
        self.assertEquals(msg, """""")

    def _assert_mem(self):
        """call back expected on  mem"""
        self.done = True
        self.assertEquals(msg, """navigator not launched in debug mode""")

    def _assert_menu(self):
        """call back expected on  menu"""
        self.done = True
        self.assertEquals(msg, """Disconnect
About Solipsis""")

    def _assert_pref(self):
        """call back expected on  pref"""
        self.done = True
        self.assertEquals(msg, """{'always_try_without_proxy': [True],
 'bookmarks': [<solipsis.navigator.wxclient.bookmarks.BookmarkList object at 0xf6998d4c>],
 'host': ['bots.netofpeers.net'],
 'node_autokill': [True],
 'port': [8551],
 'proxy_autodetect_done': [False],
 'proxy_host': ['p-goodway'],
 'proxy_mode': ['manual'],
 'proxy_pac_url': [''],
 'proxy_port': [3128],
 'proxymode_auto': [False],
 'proxymode_manual': [True],
 'proxymode_none': [False],
 'pseudo': [u'atao'],
 'service_config': [{'avatar': u'/home/emb/svn/solipsis/trunk/main/avatars/ours.jpg'}],
 'services': [[<solipsis.util.entity.Service object at 0xf5cfb12c>]],
 'solipsis_port': [6010]}""")

    def _assert_quit(self):
        """call back expected on  quit"""
        self.done = True
        self.assertEquals(msg, """Connection closed by foreign host.""")

    def _assert_not_connected(self):
        """call back on failure of action which required connection"""
        self.done = True
        self.assertEquals(msg, """not connected""")

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
