# pylint: disable-msg=W0131,C0103
# Missing docstring, Invalid name

"""Testing messages and cache structure of network. See
unittest_communication to test comm over network"""

__revision__ = "$Id$"

import unittest
import time

from solipsis.services.profile.network import Message, PeerManager

class NetworkTest(unittest.TestCase):

    def setUp(self):
        # create manager with small timeout (not to slow down test)
        self.manager = PeerManager()
        self.manager.CHECKING_FREQUENCY = 0.3
        self.manager.start()
        # create default message
        # create message
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
        self.manager.add_message("toto", self.message)
        self.assertEquals("127.0.0.1", self.manager.remote_ids["toto"].ip)
        self.assertEquals("toto", self.manager.remote_ips["127.0.0.1"].peer_id)
        self.assertEquals("127.0.0.1", self.manager.get_ip("toto"))
        self.assertEquals(self.manager.remote_ids["toto"],
                          self.manager.remote_ips["127.0.0.1"])

    def test_del_manager(self):
        self.manager.add_message("toto", self.message)
        self.assertEquals("127.0.0.1", self.manager.remote_ids["toto"].ip)
        self.assertEquals("toto", self.manager.remote_ips["127.0.0.1"].peer_id)
        time.sleep(0.1)
        self.manager._del_peer("toto")
        self.assertEquals(False, self.manager.remote_ids.has_key("toto"))
        self.assertEquals(False, self.manager.remote_ips.has_key("127.0.0.1"))

    def test_lose_manager(self):
        # add peer
        self.manager.add_message("toto", self.message)
        self.assertEquals(None, self.manager.remote_ids["toto"].lost)
        # reduce timeout in order not to slow down test
        self.manager.remote_ids["toto"].PEER_TIMEOUT = 1
        # loose peer. it should be deleted after PEER_TIMEOUT (3s)
        self.manager.remote_ids["toto"].lose()
        self.assertNotEquals(None, self.manager.remote_ids["toto"].lost)
        self.assertEquals("127.0.0.1", self.manager.remote_ids["toto"].ip)
        self.assertEquals("toto", self.manager.remote_ips["127.0.0.1"].peer_id)
        time.sleep(1.3)
        self.assertEquals(False, self.manager.remote_ids.has_key("toto"))
        self.assertEquals(False, self.manager.remote_ips.has_key("127.0.0.1"))
    
if __name__ == "__main__":
    unittest.main()
