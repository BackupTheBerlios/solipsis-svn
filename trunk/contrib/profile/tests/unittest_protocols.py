"""test basic commands of net navigator"""

import sys
import os, os.path
import time
import twisted.scripts.trial as trial

from os.path import abspath
from Queue import Queue
from twisted.trial import unittest, util
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols import basic

from solipsis.services.profile import QUESTION_MARK
from solipsis.services.profile.tools.prefs import set_prefs
from solipsis.services.profile.tools.peer import PeerDescriptor
from solipsis.services.profile.tests import write_test_profile, \
     PROFILE_TEST, PROFILE_BRUCE, PROFILE_DIR, TEST_DIR, \
     DATA_DIR, GENERATED_DIR
from solipsis.services.profile.editor.facade import get_facade, create_facade
from solipsis.services.profile.network.messages import SecurityWarnings

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
    print "xxx ERR:", reason
    raise AssertionError(str(reason))
    
class NetworkTest(unittest.TestCase, AsynchroneMixin):

    def __init__(self):
        AsynchroneMixin.__init__(self)
        
    def setUp(self):
        from solipsis.services.profile.network.manager import NetworkManager
        self.network = NetworkManager()
        util.wait(self.network.start(), timeout=10)
    setUp.timeout = 10
        
    def tearDown(self):
        del SecurityWarnings.instance()["boby"]
        self.network.stop()

    def test_intrusion(self):
        self.assert_(not SecurityWarnings.instance().has_key("boby"))
        self.network.get_profile("boby")
        self.network.get_blog_file("boby")
        self.network.get_shared_files("boby")
        self.network.get_files("boby", ["whatever"])
        self.assertEquals(4, SecurityWarnings.instance().count("boby"))
        self.network.on_service_data("boby", "HELLO 127.0.0.1:1111")
        self.assertEquals(4, SecurityWarnings.instance().count("boby"))

    def test_bad_init(self):
        self.assert_(not SecurityWarnings.instance().has_key("boby"))
        self.network.on_new_peer(FakePeer("boby"))
        self.network.on_service_data("boby", "bf 127.0.0.1:1111")
        self.network.on_service_data("boby", "REQUEST_PROFILE 127.0.0.1:1111")
        self.assertEquals(2, SecurityWarnings.instance().count("boby"))
        self.network.get_profile("boby")
        self.network.get_blog_file("boby")
        self.network.get_shared_files("boby")
        self.network.get_files("boby", ["whatever"])
        self.assertEquals(6, SecurityWarnings.instance().count("boby"))
    
class ServerTest(unittest.TestCase, AsynchroneMixin):

    def __init__(self):
        AsynchroneMixin.__init__(self)
        
    def setUp(self):
        # import here not to get twisted.internet.reactor imported too soon
        from solipsis.services.profile.network.manager import NetworkManager
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
    test_server.timeout = 10

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
    test_connection.timeout = 10

class ClientTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        write_test_profile()
        create_facade(PROFILE_TEST).load(directory=PROFILE_DIR)
        
    def setUp(self):
        # import here not to get twisted.internet.reactor imported too soon
        from solipsis.services.profile.network.manager import NetworkManager
        self.network = NetworkManager()
        util.wait(self.network.start(), timeout=10)
        self.network.on_new_peer(FakePeer("boby"))
        self.network.on_service_data(
            "boby", "HELLO 127.0.0.1:%s"% str(self.network.server.local_port))
        
    def tearDown(self):
        self.network.stop()

    def assert_profile(self, doc):
        """check validity of content"""
        self.assertEquals(u"atao", doc.get_pseudo())
        self.assertEquals(u"Mr", doc.get_title())
        self.assertEquals(u"manu", doc.get_firstname())
        self.assertEquals(u"breton", doc.get_lastname())
        self.assertEquals(QUESTION_MARK(), doc.get_photo())
        self.assertEquals(u"manu@ft.com", doc.get_email())
        self.assertEquals({'City': u'', 'color': u'blue', 'Country': u'',
                           'Favourite Book': u'', 'homepage': u'manu.com',
                           'Favourite Movie': u'', 'Studies': u''},
                          doc.get_custom_attributes())
        # peers
        peers = doc.get_peers()
        self.assertEquals(peers.has_key(PROFILE_BRUCE), True)
        self.assertEquals(peers[PROFILE_BRUCE].state, PeerDescriptor.FRIEND)
        self.assertEquals(peers[PROFILE_BRUCE].connected, False)

    def assert_blog(self, blog):
        self.assertEquals(blog.count_blogs(), 1)
        self.assertEquals(blog.get_blog(0).text, u"This is a test")
        self.assertEquals(blog.get_blog(0).count_blogs(), 0)

    def assert_files(self, files):
        shared_files = ["date.doc", "routage", "null", "TOtO.txt", "dummy.txt"]
        for container in files[TEST_DIR]:
            self.assert_(container.name in shared_files)
            if container.name == "date.txt":
                self.assertEquals("tagos", container._tag)

    def test_downloads(self):
        def _on_test_profile(result):
            self.assert_(result)
            self.assert_profile(result)
        deferred = self.network.get_profile("boby")
        util.wait(deferred.addCallbacks(_on_test_profile, on_error))
        def _on_test_blog(result):
            self.assert_(result)
            self.assert_blog(result)
        deferred = self.network.get_blog_file("boby")
        util.wait(deferred.addCallbacks(_on_test_blog, on_error))
        def _on_test_shared_files(result):
            self.assert_(result)
            self.assert_files(result)
        deferred = self.network.get_shared_files("boby")
        util.wait(deferred.addCallbacks(_on_test_shared_files, on_error))
        def _on_test_files(result):
            file_name = os.path.join(GENERATED_DIR, "arc en ciel 6.gif")
            self.assert_(os.path.exists(file_name))
            self.assertEquals(163564, os.stat(file_name)[6])
            file_name = os.path.join(GENERATED_DIR, "02_b_1280x1024.jpg")
            self.assert_(os.path.exists(file_name))
            self.assertEquals(629622, os.stat(file_name)[6])
            file_name = os.path.join(GENERATED_DIR, "pywin32-203.win32-py2.3.exe")
            self.assert_(os.path.exists(file_name))
            self.assertEquals(3718120, os.stat(file_name)[6])
        get_facade().share_files(DATA_DIR,
                                 ["arc en ciel 6.gif",
                                  "02_b_1280x1024.jpg",
                                  "pywin32-203.win32-py2.3.exe"],
                                 share=True)
        set_prefs("download_repo", GENERATED_DIR)
        deferred = self.network.get_files("boby", [
            (DATA_DIR.split(os.sep) + ["arc en ciel 6.gif"], 163564),
            (DATA_DIR.split(os.sep) + ["02_b_1280x1024.jpg"], 629622),
            (DATA_DIR.split(os.sep) + ["pywin32-203.win32-py2.3.exe"], 3718120)])
        return deferred.addCallbacks(_on_test_files, on_error)
    test_downloads.timeout = 15
    
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
