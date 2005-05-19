"""test basic commands of net navigator"""

import os
import sys
from twisted.trial import unittest
from solipsis.navigator.netclient.tests.NetTestCase import NetTestCase

class CommandTest(NetTestCase, unittest.TestCase):
    """Test good completion of basic commands"""
    
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
