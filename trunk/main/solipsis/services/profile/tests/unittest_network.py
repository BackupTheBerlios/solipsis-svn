"""Represents data stored in cache, especially shared file information"""


import os
import sys
from twisted.trial import unittest
from solipsis.navigator.netclient.tests.NetTestCase import NetTestCase

class NetworkTest(NetTestCase, unittest.TestCase):
    """Test good completion of basic commands"""
    
    def test_disconnect(self):
        """command disconnect"""
        self.check_next("disconnect", "not connected")
        self.write("connect")
        self.write("bots.netofpeers.net:8555")
        self.wait_for("Connected")
        self.check_next("disconnect", "Not connected")

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
