# pylint: disable-msg=W0131,C0103
# Missing docstring, Invalid name

"""Testing messages and cache structure of network. See
unittest_communication to test comm over network"""

__revision__ = "$Id$"

import unittest
import time

from solipsis.node.peer import Peer
from solipsis.services.profile.network import Message, \
     NetworkManager, PeerManager

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

class PeerTest(BaseTest):

    def setUp(self):
        # create manager with small timeout (not to slow down test)
        self.manager = PeerManager(None)
        self.manager.CHECKING_FREQUENCY = 0.3
        self.manager.start()
        # create default message
        self.message =  Message.create_message(
            "HELLO 127.0.0.1:23501 data youpi")

    def tearDown(self):
        # stop manager
        self.manager.stop()

    def test_message(self):
        # errors when message not well formatted
        self.assertRaises(ValueError, Message, "DOWNLOAD_FILES")
        self.assertRaises(ValueError, Message, "FILES 127.0.0.1:23")
        self.assertRaises(ValueError, Message, "download 127.0.0.1:23")
        # well formated
        self.assertEquals("HELLO", self.message.command)
        self.assertEquals("127.0.0.1", self.message.ip)
        self.assertEquals(23501, self.message.port)
        self.assertEquals("data youpi", self.message.data)
        # reverse message received from a Message structure
        self.assertEquals("HELLO 127.0.0.1:23501 data youpi", str(self.message))

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
        self.manager.remote_ids["toto"].PEER_TIMEOUT = 0.7
        # loose peer. it should be deleted after PEER_TIMEOUT
        self.manager.remote_ids["toto"].lose()
        self.assert_peer_lost()
        time.sleep(1.3)
        self.assert_no_peer()

class NetworkTest(BaseTest):

    def setUp(self):
        # create manager with small timeout (not to slow down test)
        self.network = NetworkManager()
        self.manager = self.network.peers
        self.manager.CHECKING_FREQUENCY = 0.3

    def tearDown(self):
        # stop manager
        self.network.stop()
        
    def test_network_manager(self):
        peer = Peer("toto")
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
        self.assert_new_peer()
        self.network.on_service_data("toto",
                                     "HELLO 127.0.0.1:23501 data youpi")
        self.assert_peer()
        # lose peer
        self.manager.remote_ids["toto"].PEER_TIMEOUT = 0.7
        self.network.on_lost_peer("toto")
        self.assert_peer_lost()
        time.sleep(1.3)
        self.assert_no_peer()
    
if __name__ == "__main__":
    unittest.main()
