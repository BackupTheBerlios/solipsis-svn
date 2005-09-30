"""test basic commands of net navigator"""

import sys
import time
import os, os.path
import twisted.scripts.trial as trial
    
from Queue import Queue
from twisted.trial import unittest, util
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

from solipsis.navigator.netclient.tests import LOCAL_PORT
from solipsis.services.profile.tests import PROFILE_DIR, FILE_BRUCE, FILE_TEST, \
     write_test_profile, get_bruce_profile
from solipsis.services.profile.prefs import get_prefs
        

##### WATCH OUT !!! ###################################################################

# All these test needs an Netnavigator running on the local machine.
# call ./launch.py before running the tests

# see also specific needs for ProfileTest

class NetworkTest(unittest.TestCase):

    def __init__(self):
        self.wake_up = time.time()

    def setUp(self):
        from twisted.internet import reactor
        # launch 'telnet'
        self.factory = ReconnectingFactory()
        self.connector = reactor.connectTCP("localhost",
                           LOCAL_PORT,
                           self.factory)
        # wait for connection to app establisehd
        return self.assertMessage("Ready")
    setUp.timeout = 6

    def tearDown(self):
        self.factory.stopTrying()
        self.factory.stopFactory()
        self.connector.disconnect()

    def wait(self, sec_delay):
        self.wake_up = time.time()+sec_delay
        util.spinWhile(self._waiting, sec_delay+1)

    def _waiting(self):
        return time.time() < self.wake_up

    def assertMessage(self, message, factory=None):
        if factory is None:
            factory = self.factory
        deferred = Deferred()
        factory.deferred.put(deferred)
        deferred.addCallback(self.assertEquals, message)
        return deferred

    def assertResponse(self, cmd, response, factory=None):
        if factory is None:
            factory = self.factory
        deferred = self.assertMessage(response, factory)
        factory.sendLine(cmd)
        return deferred

    def useResponse(self, cmd, action, factory, *args):
        deferred = Deferred()
        factory.deferred.put(deferred)
        deferred.addCallback(action, *args)
        factory.sendLine(cmd)
        return deferred

    def assertPosition(self, response, rounding=0.03, factory=None):
        if factory is None:
            factory = self.factory
        deferred = Deferred()
        factory.deferred.put(deferred)
        def assert_position(msg):
#             print "COMPARE", msg, response
            # convert to float
            x, y = msg.split(" ")
            x, y = float(x), float(y)
            expected_x, expected_y = response.split(" ")
            expected_x, expected_y = float(expected_x), float(expected_y)
            # evaluate difference
            diff_x = abs(expected_x - x)
            diff_y = abs(expected_y - y)
            try: 
                self.assert_(diff_x < rounding or diff_x > 1-rounding)
                self.assert_(diff_y < rounding or diff_y > 1-rounding)
            except AssertionError:
                print "%.2f, %.2f out of %.2f %.2f"% (x, y, diff_x, diff_y)
                raise
        deferred.addCallback(assert_position)
        factory.sendLine('where')
        return deferred
        
class DisconnectedTest(NetworkTest):
    """Test good completion of basic commands"""

    def test_about(self):
        return self.assertResponse("about", """About...: Solipsis Navigator 0.9.5svn

Licensed under the GNU LGPL
(c) France Telecom R&D""")
    test_about.timeout = 2

    def test_connect(self):
        util.wait(self.assertResponse("connect bots.netofpeers.net:8553", "Connected"))
        return self.assertResponse("disconnect", "Disconnected")
    test_connect.timeout = 2

    def test_display(self):
        return self.assertResponse("display", "Not connected")
    test_display.timeout = 2

    def test_menu(self):
        return self.assertResponse("menu", "Not connected")
    test_menu.timeout = 2

    def test_help(self):
        return self.assertResponse("help", "available commands are: ['quit', 'about', 'disconnect', 'help', 'launch', 'menu', 'who', 'display', 'jump', 'kill', 'connect', 'go', 'where', 'id']\n")
    test_help.timeout = 2

class ConnectedTest(NetworkTest):
    """Test good completion of basic commands"""

    def setUp(self):
        util.wait(NetworkTest.setUp(self))
        util.wait(self.assertResponse("connect bots.netofpeers.net:8553", "Connected"))
        util.wait(self.assertResponse("go", "ok"))
        self.wait(0.5)
    setUp.timeout = 8

    def tearDown(self):
        util.wait(self.assertResponse("disconnect", "Disconnected"))
        NetworkTest.tearDown(self)
    tearDown.timeout = 2

    def test_display(self):
        return self.assertResponse("display", "Address: 192.33.178.29:6003")
    test_display.timeout = 2

    def test_go(self):
        util.wait(self.assertPosition("0.0 0.0", rounding=0.05))
        util.wait(self.assertResponse("go 0.1 0.3", "ok"))
        return self.assertPosition("0.1 0.3")
    test_go.timeout = 2

    def test_menu(self):
        return self.assertResponse("menu", "Modify Profile...\nFilter Profiles...")
        return self.assertResponse("menu self Modify Profile...",
                                   "PeerDescriptor bruce")
        return self.assertResponse("menu self Filter Profiles...",
                                   "PeerDescriptor bruce")
    test_menu.timeout = 2

    def test_who(self):
        util.wait(self.assertResponse("go 0.67 0.33", "ok"))
        return self.assertResponse("who profile", "")
    test_who.timeout = 3

##### WATCH OUT !!! ###################################################################

# this test uses a remote hard coded profile

# it will work properly with ./launch.py executed on the remote
# machine OTHER_IP. 
    
class ProfileTest(NetworkTest):
    """Test good completion of basic commands"""

    OTHER_IP = "172.17.1.68" # "10.193.171.41"
    FIRST_NODE = "bots.netofpeers.net:8553"
    OTHER_NODE = "bots.netofpeers.net:8554"
    first_id = None
    second_id = None

    def __init__(self):
        NetworkTest.__init__(self)
        # create profiles used for tests
        write_test_profile() 
        bruce = get_bruce_profile()
        bruce.save(directory=PROFILE_DIR) 
        # call setUp once to set first_id & second_id
        self.setUp()

    def assertOtherMessage(self, message):
        return NetworkTest.assertMessage(self, message,
                                           factory=self.other_factory)

    def assertOtherResponse(self, cmd, response):
        return NetworkTest.assertResponse(self, cmd, response,
                                            factory=self.other_factory)

    def useResponse(self, cmd, response, *args):
        return NetworkTest.useResponse(self, cmd, response, self.factory, *args)

    def useOtherResponse(self, cmd, response, *args):
        return NetworkTest.useResponse(self, cmd, response, self.other_factory, *args)

    def assertOtherPosition(self, position):
        return NetworkTest.assertPosition(self, position,
                                            factory=self.other_factory)

    def _rename_files(self, node_id, old_name):
        # function called only twice
        if self.first_id != None and self.second_id != None:
            return
        if old_name == FILE_TEST:
            self.first_id = node_id
        else:
            self.second_id = node_id
        # update files
        new_name = os.path.join(get_prefs('profile_dir'), node_id)
        for extension in ['.prf', '.blog']:
            os.rename(old_name + extension,
                      new_name + extension)

    def setUp(self):
        # launch fisrt navigator
        util.wait(NetworkTest.setUp(self))
        util.wait(self.assertResponse("connect %s"% self.FIRST_NODE, "Connected"))
        util.wait(self.assertResponse("go 0.1 0.3", "ok"))
        util.wait(self.useResponse("id", self._rename_files, FILE_TEST))
        # launch 'telnet' on second navigator
        from twisted.internet import reactor
        self.other_factory = ReconnectingFactory()
        self.other_connector = reactor.connectTCP(self.OTHER_IP,
                                                  LOCAL_PORT,
                                                  self.other_factory)
        # wait for connection to app establisehd
        util.wait(self.assertOtherMessage("Ready"))
        util.wait(self.assertOtherResponse("connect %s"% self.OTHER_NODE, "Connected"))
        util.wait(self.assertOtherResponse("go 0.11 0.31", "ok"))
        util.wait(self.useOtherResponse("id", self._rename_files, FILE_BRUCE))
        # wait until both navigators have received meta data (no message usable from node)
        self.wait(2)
    setUp.timeout = 8


    def tearDown(self):
        # disconnect first one
        util.wait(self.assertResponse("disconnect", "Disconnected"))
        NetworkTest.tearDown(self)
        # second one
        util.wait(self.assertOtherResponse("disconnect", "Disconnected"))
        self.other_factory.stopTrying()
        self.other_factory.stopFactory()
        self.other_connector.disconnect()

    def test_where(self):
        util.wait(self.assertPosition("0.1 0.3"))
        return self.assertOtherPosition("0.11 0.31")
    test_where.timeout = 2

    def test_who(self):
        return self.assertResponse("who profile", self.second_id)
    test_who.timeout = 2

    def test_view_profile(self):
        util.wait(self.assertResponse("who profile", self.second_id))
        return self.assertResponse("menu %s View profile..."% self.second_id,
                                   "File document for bruce")
    test_view_profile.timeout = 4

    def test_view_blog(self):
        util.wait(self.assertResponse("who profile", self.second_id))
        return self.assertResponse("menu %s View blog..."% self.second_id,
                                   "Hi Buddy")
    test_view_blog.timeout = 4
    
    def test_view_files(self):
        util.wait(self.assertResponse("who profile", self.second_id))
        return self.assertResponse("menu %s Get files..."% self.second_id,
                                    """date.txt
date.doc""")
    test_view_files.timeout = 4

# Network classes
# ===============
class SimpleProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.sendLine = self.sendLine

    def sendLine(self, line):
        LineReceiver.sendLine(self, line)

    def lineReceived(self, data):
        if not self.factory.deferred.empty():
            self.factory.deferred.get().callback(data)
        
class ReconnectingFactory(ReconnectingClientFactory):

    protocol = SimpleProtocol

    def __init__(self):
        self.deferred = Queue()

    def startedConnecting(self, connector):
        self.resetDelay()

    def clientConnectionLost(self, connector, reason):
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    
    def clientConnectionFailed(self, connector, reason):
        ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

# LAUNCHER
# ========
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
