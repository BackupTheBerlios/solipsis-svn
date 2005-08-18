"""test basic commands of net navigator"""

import sys
import time
import twisted.scripts.trial as trial
    
from Queue import Queue
from twisted.trial import unittest, util
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver

from solipsis.navigator.netclient.tests import LOCAL_PORT
        

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
        return self.assertResponse("about", """About...: Solipsis Navigator 0.9.3svn

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
        return self.assertResponse("help", "available commands are: ['quit', 'about', 'disconnect', 'help', 'launch', 'menu', 'who', 'jump', 'kill', 'connect', 'go', 'where', 'display']\n")
    test_help.timeout = 2

class ConnectedTest(NetworkTest):
    """Test good completion of basic commands"""

    def setUp(self):
        util.wait(NetworkTest.setUp(self))
        util.wait(self.assertResponse("connect bots.netofpeers.net:8553", "Connected"))
        return self.assertResponse("go", "ok")
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
    test_who.timeout = 2

##### WATCH OUT !!! ###################################################################

# this test uses a remote hard coded profile

# it will work properly with a profile 'zoé' created on the remote machine WINDOWS_IP
# and running an instance of the netNavigator (launch.py on remote machine).
# WINDOWS_ID will also depends on the remote machine and you will need to coordinate zoé's
# profile with hard coded vars ZOE_BLOG & ZOE_FILES
    
class ProfileTest(NetworkTest):
    """Test good completion of basic commands"""

    WINDOWS_IP = "10.193.171.41"
    WINDOWS_ID = "6000_5_34e59f3a65f4555fdab1761a6aeb65c7b228bec7"
    WINDOWS_NODE = "bots.netofpeers.net:8555"
    ZOE_BLOG = "[bzz bzz I am a bee! (0)]"
    ZOE_FILES = """pscp.exe
PIL-1.1.5.win32-py2.4.exe
GoogleEarth.exe
Firefox Setup 1.0.6.exe
putty.exe
TwistedWeb-0.5.0.tar.bz2
python-2.4.1.msi
wrar342fr.exe
sc32r238.exe
dxwebsetup.exe
TortoiseSVN-1.2.1.3895-svn-1.2.1.msi
aeack01.exe
LanguagePack_1.2.1_fr.exe
GenuineCheck.exe
Twisted_NoDocs-2.0.1.win32-py2.4.exe
wxPython2.6-win32-unicode-2.6.1.0-py24.exe
psftp.exe
pageant.exe"""

    def assertOtherMessage(self, message):
        return NetworkTest.assertMessage(self, message,
                                           factory=self.other_factory)

    def assertOtherResponse(self, cmd, response):
        return NetworkTest.assertResponse(self, cmd, response,
                                            factory=self.other_factory)

    def assertOtherPosition(self, position):
        return NetworkTest.assertPosition(self, position,
                                            factory=self.other_factory)

    def setUp(self):
        # launch fisrt navigator
        util.wait(NetworkTest.setUp(self))
        util.wait(self.assertResponse("connect bots.netofpeers.net:8553", "Connected"))
        util.wait(self.assertResponse("go 0.1 0.3", "ok"))
        # launch 'telnet' on second navigator
        from twisted.internet import reactor
        self.other_factory = ReconnectingFactory()
        self.other_connector = reactor.connectTCP(self.WINDOWS_IP,
                                                  LOCAL_PORT,
                                                  self.other_factory)
        # wait for connection to app establisehd
        util.wait(self.assertOtherMessage("Ready"))
        util.wait(self.assertOtherResponse("connect %s"% self.WINDOWS_NODE, "Connected"))
        util.wait(self.assertOtherResponse("go 0.11 0.31", "ok"))
        # wait until both navigators have received meta data (no message usable from node)
        self.wait(1.0)
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
        return self.assertResponse("who profile", self.WINDOWS_ID)
    test_who.timeout = 2

    def test_view_profile(self):
        util.wait(self.assertResponse("who profile", self.WINDOWS_ID))
        return self.assertResponse("menu %s View profile..."% self.WINDOWS_ID,
                                   "File document for zoé")
    test_view_profile.timeout = 4

    def test_view_blog(self):
        util.wait(self.assertResponse("who profile", self.WINDOWS_ID))
        return self.assertResponse("menu %s View blog..."% self.WINDOWS_ID, self.ZOE_BLOG)
    test_view_blog.timeout = 4
    
    def test_view_files(self):
        util.wait(self.assertResponse("who profile", self.WINDOWS_ID))
        return self.assertResponse("menu %s Get files..."% self.WINDOWS_ID, self.ZOE_FILES)
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
