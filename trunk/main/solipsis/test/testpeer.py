import unittest
import os,sys

searchPath = os.path.dirname(os.path.dirname(sys.path[0]))
sys.path.append(searchPath)

from solipsis.node.peer import Peer, PeersManager
from solipsis.node.peer import UnknownIdError, DuplicateIdError, EmptyIdError
from solipsis.util.geometry import Position, Geometry
from solipsis.util.address import Address
from solipsis.node.node import Node
from solipsis.util.parameter import Parameters
from solipsis.util.exception import InternalError


from optparse import OptionParser

TEST_DEBUG=False

class CreatePeerManagerTestCase(unittest.TestCase):

    def setUp(self):
        configFileName = "../../conf/solipsis.conf"
        parser = OptionParser('')
        param = Parameters(parser, configFileName)
        n = Node(param)
        n.setPosition(Position(4,1))
        self.manager = PeersManager(n, param)

        p0 = Peer(id="0",position=Position(0,0))
        p1 = Peer(id="1",position=Position(0,10))
        p2 = Peer(id="2",position=Position(5,0))
        p3 = Peer(id="3",position=Position(5,20))
        p4 = Peer()

        self.peers = [p0, p1, p2, p3, p4]

        p10 = Peer(id="0", position=Position(2,2))
        p11 = Peer(id="1", position=Position(7,2))
        p12 = Peer(id="2", position=Position(5,3))
        p13 = Peer(id="3", position=Position(3,6))
        p14 = Peer(id="4", position=Position(4,-6))
        p15 = Peer(id="5", position=Position(4,0))

        self.geoPeers = [p10, p11, p12, p13, p14, p15]

    def testAddPeer(self):
        self.manager.addPeer(self.peers[0])
        assert ( self.manager.getNumberOfPeers() == 1 )

        self.manager.addPeer(self.peers[1])
        assert ( self.manager.getNumberOfPeers() == 2 )

        self.manager.removePeer(self.peers[1].getId())
        assert ( self.manager.getNumberOfPeers() == 1 )

        self.manager.addPeer(self.peers[2])
        self.assertRaises(DuplicateIdError, self.manager.addPeer, self.peers[2])

        self.assertRaises(EmptyIdError, self.manager.addPeer, self.peers[4])

        self.checkConsistency()


    def testRemovePeer(self):
        for i in range(4):
            self.manager.addPeer(self.peers[i])

        self.manager.removePeer(self.peers[1].getId())
        assert ( self.manager.getNumberOfPeers() ==  3)
        self.checkConsistency()
        self.assertRaises(UnknownIdError, self.manager.removePeer,
                          self.peers[1].getId())
        self.assertRaises(UnknownIdError, self.manager.removePeer,
                          self.peers[4].getId())

    def checkConsistency(self):
        if TEST_DEBUG:
            print 'in check consistency: '
            print 'nb:%d' %(self.manager.getNumberOfPeers())
            print 'ccw:%d' %(len(self.manager.ccwPeers.ll))
            print 'dist:%d' %(len(self.manager.distPeers.ll))

        assert (self.manager.getNumberOfPeers() == len(self.manager.ccwPeers.ll))
        assert (self.manager.getNumberOfPeers() == len(self.manager.distPeers.ll))


    def testGetClosestPeer(self):
        for i in range(4):
            self.manager.addPeer(self.peers[i])

        p5 = Peer(id="5", position=Position(-5, -2))

        self.manager.addPeer(p5)


        assert (self.manager.getClosestPeer(Position(0,0)).getId() == "0" )
        assert (self.manager.getClosestPeer(Position(20,20)).getId() == "3" )
        assert (self.manager.getClosestPeer(Position(-5,-15)).getId() == "5" )
        assert (self.manager.getClosestPeer(Position(3,1)).getId() == "2" )
        assert (self.manager.getClosestPeer(Position(-115,-115)).getId() == "5" )

        assert (self.manager.getClosestPeer(Position(Geometry.SIZE - 10,
                                                     Geometry.SIZE - 10)).getId() == "5" )
        assert (self.manager.getClosestPeer(Position(Geometry.SIZE - 1,
                                                     Geometry.SIZE - 1)).getId() == "0" )

    def testGetWorstPeer(self):
        [p10, p11, p12, p13, p14, p15] = self.geoPeers
        self.manager.addPeer(p10)
        self.manager.addPeer(p11)
        self.manager.addPeer(p12)
        self.manager.addPeer(p13)
        self.manager.addPeer(p14)
        self.manager.setExpectedPeers(3)
        id = self.manager.getWorstPeer().getId()

        # p4 is farther but is needed for global connectivity
        assert (id == "3")

        self.manager.addPeer(p15)
        id = self.manager.getWorstPeer().getId()
        # with p5 added p4 is no longer needed for the global connectivity rule
        # as p4 is the farthest it should be elected
        assert (id == "4")


        if TEST_DEBUG:
            print "worst=" + id
            print "node=" + str(self.manager.node.getPosition())

            print "ccw"
            for e in self.manager.ccwPeers.ll:
                print e.getId()

            print "dist"
            for e in self.manager.distPeers.ll:
                print e.getId()


    def testGetBadGlobalConnectivityPeers(self):
        for p in self.geoPeers:
            self.manager.addPeer(p)

        [p10, p11, p12, p13, p14, p15] = self.geoPeers
        # global connectivity is OK
        gcPeers = self.manager.getBadGlobalConnectivityPeers()
        assert( len(gcPeers) == 0 )

        self.manager.removePeer(p14.getId())
        self.manager.removePeer(p15.getId())

        # now, GC is NOK and we should get p0 and p1
        gcPeers = self.manager.getBadGlobalConnectivityPeers()
        if  TEST_DEBUG:
            print gcPeers[0]
            print gcPeers[1]

        assert ( len(gcPeers) == 2 )
        assert ( gcPeers[0].getId() == "1" )
        assert ( gcPeers[1].getId() == "0" )

    def testGetPeerAround(self):
        for p in self.geoPeers:
            self.manager.addPeer(p)


        print "---"
        print str(self.manager.getPeerAround(Position(6,2), "", True))
        print str(self.manager.getPeerAround(Position(6,2), "", False))
        print "---"

if __name__ == "__main__":
    unittest.main()
