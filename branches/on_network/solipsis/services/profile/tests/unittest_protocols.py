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

from solipsis.services.profile.tests import write_test_profile, \
     PROFILE_TEST, PROFILE_DIR
from solipsis.services.profile.facade import create_facade
from solipsis.services.profile.network_data import SecurityWarnings

# side class #########################################################
class AsynchroneMixin:

    def __init__(self):
        self.deferreds = Queue(-1)

    def wait(self, sec_delay):
        wake_up = time.time() + sec_delay
        def _waiting():
            return time.time() < wake_up
        util.spinWhile(_waiting, sec_delay+1)

    def send(self, connector, msg):
        """to be used with ReconnectingFactory"""
        deferred = Deferred()
        self.deferreds.put(deferred)
        connector.transport.write(msg + "\r\n")
        return deferred

class FakePeer:

    def __init__(self, peer_id):
        self.id_ = peer_id

# tests classes ######################################################
def on_error(reason):
    print "ERR:", reason
    raise AssertionError(str(reason))
    
class NetworkTest(unittest.TestCase, AsynchroneMixin):

    def __init__(self):
        AsynchroneMixin.__init__(self)
        
    def setUp(self):
        from solipsis.services.profile.network import NetworkManager
        self.network = NetworkManager()
        util.wait(self.network.start(), timeout=10)
        
    def tearDown(self):
        del SecurityWarnings.instance()["boby"]
        self.network.stop()

    def test_intrusion(self):
        self.assert_(not SecurityWarnings.instance().has_key("boby"))
        self.network.on_service_data("boby", "HELLO 127.0.0.1:1111")
        self.assertEquals(1, SecurityWarnings.instance().count("boby"))
        self.network.get_profile("boby")
        self.network.get_blog_file("boby")
        self.network.get_shared_files("boby")
        self.network.get_files("boby", ["whatever"], None)
        self.assertEquals(5, SecurityWarnings.instance().count("boby"))

    def test_bad_init(self):
        self.assert_(not SecurityWarnings.instance().has_key("boby"))
        self.network.on_new_peer(FakePeer("boby"))
        self.network.on_service_data("boby", "bf 127.0.0.1:1111")
        self.network.on_service_data("boby", "REQUEST_PROFILE 127.0.0.1:1111")
        self.assertEquals(2, SecurityWarnings.instance().count("boby"))
        self.network.get_profile("boby")
        self.network.get_blog_file("boby")
        self.network.get_shared_files("boby")
        self.network.get_files("boby", ["whatever"], None)
        self.assertEquals(6, SecurityWarnings.instance().count("boby"))
    
class ServerTest(unittest.TestCase, AsynchroneMixin):

    def __init__(self):
        AsynchroneMixin.__init__(self)
        
    def setUp(self):
        # import here not to get twisted.internet.reactor imported too soon
        from solipsis.services.profile.network import NetworkManager
        self.network = NetworkManager()
        self.network.on_new_peer(FakePeer("boby"))
        self.network.on_service_data("boby", "HELLO 127.0.0.1:1111")
        self.network.peers.start()
        
    def tearDown(self):
        self.network.peers.stop()

    def test_server(self):
        deferred = self.network.server.start_listening()
        ## TESTS ##
        def _on_test(result):
            # values set
            self.assertEquals(True, result)
            self.assertNotEquals(None, self.network.server.listener)
            self.assertNotEquals(None, self.network.server.public_ip)
            self.assertNotEquals(None, self.network.server.public_port)
            self.assertNotEquals(self.network.server.public_ip, self.network.server.local_ip)
            self.network.server.stop_listening()
        deferred.addCallbacks(_on_test, on_error)
        return deferred
    test_server.timeout = 8

    def test_connection(self):
        util.wait(self.network.server.start_listening(), timeout=10)
        # start client
        from twisted.internet import reactor
        factory = ReconnectingFactory(self.deferreds)
        connector = reactor.connectTCP("localhost",
                                       self.network.server.local_port,
                                       factory)
        # send ping
        self.wait(1)
        deferred = self.send(connector, "ping")
        ## TESTS ##
        def _on_test(result):
            self.assertEquals("pong", result)
            self.network.server.stop_listening()
            factory.stopTrying()
            factory.stopFactory()
            connector.disconnect()
            self.wait(1)
        deferred.addCallbacks(_on_test, on_error)
        return deferred
    test_connection.timeout = 8

class ClientTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        write_test_profile()
        create_facade(PROFILE_TEST).load(directory=PROFILE_DIR)
        
    def setUp(self):
        # import here not to get twisted.internet.reactor imported too soon
        from solipsis.services.profile.network import NetworkManager
        self.network = NetworkManager()
        util.wait(self.network.start(), timeout=10)
        self.network.on_new_peer(FakePeer("boby"))
        self.network.on_service_data(
            "boby", "HELLO 127.0.0.1:%s"% str(self.network.server.local_port))

    def test_downloads(self):
        def _on_test(result):
            print "xxx ", result
        deferred = self.network.get_profile("boby")
        deferred.addCallbacks(_on_test, on_error)
        print "xxx ", deferred
        return deferred
    test_downloads.timeout = 8
    
# network classes ####################################################
class SimpleProtocol(basic.LineReceiver):

    def connectionMade(self):
        pass
    
    def lineReceived(self, data):
        """to be used when sending data with AsynchroneMixin.send"""
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

# launcher ###########################################################
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
