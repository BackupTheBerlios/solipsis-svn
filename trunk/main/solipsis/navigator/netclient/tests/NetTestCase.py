"""generic test case class for net navigator"""
import os
import sys
import solipsis

from twisted.internet import reactor, error, defer
from solipsis.navigator.netclient.tests import waiting, PORT
from solipsis.navigator.netclient.tests.TestClient import TestClientFactory
from solipsis.navigator.netclient.app import NavigatorApp
from solipsis.navigator.netclient.main import build_params

class NetTestCase:
    """Test good completion of basic commands"""
    
    def __init__(self):
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
