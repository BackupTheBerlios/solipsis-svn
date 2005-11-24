# pylint: disable-msg=W0131,C0103
# Missing docstring, Invalid name

"""Testing messages and cache structure of network. See
unittest_communication to test comm over network"""

__revision__ = "$Id$"

import unittest
import time

from StringIO import StringIO
from twisted.internet import defer

from solipsis.node import peer as peer_node
from solipsis.services.profile.network.peers import PeerManager, Peer, \
     PeerRegistered, PeerConnected, PeerDisconnected, PeerState
from solipsis.services.profile.network.messages import DownloadMessage, Message, \
     SecurityAlert, SecurityWarnings, MESSAGE_HELLO
from solipsis.services.profile.network.manager import NetworkManager

class BaseTest(unittest.TestCase):

    def assert_no_peer(self):
        self.assertEquals(False, self.manager.assert_id("toto"))
        self.assertEquals(False, self.manager.assert_ip("127.0.0.1"))

    def assert_new_peer(self):
        self.assertEquals(True, self.manager.assert_id("toto"))
        self.assertEquals(False, self.manager.assert_ip("127.0.0.1"))
        self.assertEquals(None, self.manager.remote_ids["toto"].ip)
        self.assertEquals(None, self.manager.remote_ids["toto"].port)
        self.assertEquals(None, self.manager.remote_ids["toto"].lost)

    def assert_peer(self):
        self.assertEquals(True, self.manager.assert_id("toto"))
        self.assertEquals(True, self.manager.assert_ip("127.0.0.1"))
        self.assertEquals("127.0.0.1", self.manager.remote_ids["toto"].ip)
        self.assertEquals(23501, self.manager.remote_ids["toto"].port)

    def assert_peer_lost(self):
        self.assert_peer()
        self.assertNotEquals(None, self.manager.remote_ids["toto"].lost)

class DataTest(unittest.TestCase):

    def test_count_and_display(self):
        SecurityAlert("bob", "first")
        self.assertEquals(1, SecurityWarnings.instance().count("bob"))
        self.assertEquals(0, SecurityWarnings.instance().count("boby"))
        SecurityAlert("bob", "sec")
        SecurityAlert("bob", "third")
        self.assertEquals(3, SecurityWarnings.instance().count("bob"))
        self.assertEquals(0, SecurityWarnings.instance().count("boby"))
        SecurityAlert("boby", "first")
        self.assertEquals(1, SecurityWarnings.instance().count("boby"))
        SecurityWarnings.instance().display("bob")
        SecurityWarnings.instance().display("boby")

    def test_message(self):
        message =  Message.create_message(
            "HELLO 127.0.0.1:23501 data youpi")
        # errors when message not well formatted
        self.assertRaises(ValueError, Message, "DOWNLOAD_FILES")
        self.assertRaises(ValueError, Message, "FILES 127.0.0.1:23")
        self.assertRaises(ValueError, Message, "download 127.0.0.1:23")
        # well formated
        self.assertEquals("HELLO", message.command)
        self.assertEquals("127.0.0.1", message.ip)
        self.assertEquals(23501, message.port)
        self.assertEquals("data youpi", message.data)
        # reverse message received from a Message structure
        self.assertEquals("HELLO 127.0.0.1:23501 data youpi", str(message))

    def test_download_message(self):
        transport = StringIO()
        message =  DownloadMessage(
            transport,
            defer.Deferred(),
            Message.create_message("HELLO 127.0.0.1:23501 data youpi"))
        message.send_message()
        self.assertEquals("HELLO 127.0.0.1:23501 data youpi\r\n",
                          transport.getvalue())

class PeerTest(unittest.TestCase):

    def setUp(self):
        self.peer = Peer("bob", lambda x: x)
        self.msg = Message.create_message(
            "HELLO 127.0.0.1:23501 data youpi")

    def test_server(self):
        self.assert_(isinstance(self.peer.server.current_state, PeerState))
        self.assertRaises(SecurityAlert, self.peer.server.connected, None)
        self.assertRaises(SecurityAlert, self.peer.server.disconnected)
        self.assertRaises(SecurityAlert, self.peer.server.execute, self.msg)
        # registered
        self.peer.server.current_state = self.peer.server.registered_state
        self.assertRaises(SecurityAlert, self.peer.server.execute, self.msg)
        # connected
        self.peer.server.connected("transport")
        self.assert_(isinstance(self.peer.server.current_state, PeerConnected))
        # disconnected
        self.peer.server.disconnected()
        self.assert_(isinstance(self.peer.server.current_state, PeerDisconnected))
        self.assertRaises(SecurityAlert, self.peer.server.execute, self.msg)
        # connected
        self.peer.server.connected("transport")
        self.assert_(isinstance(self.peer.server.current_state, PeerConnected))

    def test_peer(self):
        msg = self.peer.wrap_message(MESSAGE_HELLO)
        self.assertEquals("HELLO ?:-1 ", str(msg))
        
class PeerManagerTest(BaseTest):

    def setUp(self):
        # create manager with small timeout (not to slow down test)
        self.manager = PeerManager(None)
        self.manager.CHECKING_FREQUENCY = 0.2
        self.manager.start()
        # create default message
        self.message =  Message.create_message(
            "HELLO 127.0.0.1:23501 data youpi")

    def tearDown(self):
        # stop manager
        self.manager.stop()

    def test_add_manager(self):
        self.assert_no_peer()
        self.manager.add_peer("toto")
        self.manager.set_peer("toto", self.message)
        self.assert_peer()
        self.assertEquals(self.manager.remote_ids["toto"],
                          self.manager.remote_ips["127.0.0.1"])

    def test_del_manager(self):
        self.manager.add_peer("toto")
        self.manager.set_peer("toto", self.message)
        time.sleep(0.1)
        self.manager._del_peer("toto")
        self.assert_no_peer()

    def test_lose_manager(self):
        # add peer
        self.manager.add_peer("toto")
        self.manager.set_peer("toto", self.message)
        # reduce timeout in order not to slow down test
        self.manager.remote_ids["toto"].PEER_TIMEOUT = 0.5
        # loose peer. it should be deleted after PEER_TIMEOUT
        self.manager.remote_ids["toto"].lose()
        self.assert_peer_lost()
        time.sleep(1)
        self.assert_no_peer()

class NetworkTest(BaseTest):

    def setUp(self):
        # create manager with small timeout (not to slow down test)
        self.network = NetworkManager()
        self.manager = self.network.peers
        self.manager.CHECKING_FREQUENCY = 0.2
        self.network.peers.start()

    def tearDown(self):
        # stop manager
        self.network.peers.stop()
        
    def test_network_manager(self):
        peer = peer_node.Peer("toto")
        self.assert_no_peer()
        # add peer
        self.network.on_new_peer(peer)
        self.assert_new_peer()
        # set peer information
        self.network.on_service_data("toto",
                                     "HELLO 127.0.0.1:23501 data youpi")
        self.assert_peer()
        # change peer
        self.network.on_change_peer(peer, "profile")
        self.assertEquals(True, self.manager.assert_id("toto"))
        self.assertEquals(True, self.manager.assert_ip("127.0.0.1"))
        self.network.on_service_data("toto",
                                     "HELLO 127.0.0.1:23501 data youpi")
        self.assert_peer()
        # lose peer
        self.manager.remote_ids["toto"].PEER_TIMEOUT = 0.5
        self.network.on_lost_peer("toto")
        self.assert_peer_lost()
        time.sleep(1)
        self.assert_no_peer()
    
if __name__ == "__main__":
    unittest.main()
