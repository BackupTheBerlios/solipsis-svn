import unittest
from peer import Peer, PeersManager
from node import Node
from parameter import Parameters
from exception import SolipsisInternalError
from util import Geometry

class CreatePeerManagerTestCase(unittest.TestCase):
	
  def setUp(self):
    configFileName = "solipsis.conf"
    param = Parameters(configFileName)
    n = Node(param)            
    self.manager = PeersManager(n, param.getPeersParams())
    
    p0 = Peer("0","h1","1",[0,0])
    p1 = Peer("1","h1","2",[0,10])
    p2 = Peer("2","h1","3",[5,0])
    p3 = Peer("3","h1","3",[5,20])
    p4 = Peer()
		
    self.peers = [p0, p1, p2, p3, p4]
    
  def testAddPeer(self):          
    self.manager.addPeer(self.peers[0])    
    assert ( len(self.manager.peers) == 1 )
    
    self.manager.addPeer(self.peers[1])
    assert ( len(self.manager.peers) == 2 )
    
    self.manager.removePeer(self.peers[1])
    assert ( len(self.manager.peers) == 1 )
		
    self.manager.addPeer(self.peers[2])
    self.assertRaises(SolipsisInternalError, self.manager.addPeer, self.peers[2])
		
    self.assertRaises(SolipsisInternalError, self.manager.addPeer, self.peers[4])
        
    self.checkConsistency()

		
  def testRemovePeer(self):
    for i in range(4):      
      self.manager.addPeer(self.peers[i])

    self.manager.removePeer(self.peers[1])
    assert ( len(self.manager.peers) ==  3)
    
    self.assertRaises(SolipsisInternalError, self.manager.removePeer, self.peers[1])
    self.assertRaises(SolipsisInternalError, self.manager.removePeer, self.peers[4])
    
  def checkConsistency(self):
    assert (len(self.manager.peers) == len(self.manager.ccwPeers),
            'inconsistent peer lists')
    assert (len(self.manager.peers) == len(self.manager.distPeers),
            'inconsistent peer lists')

		
  def testGetClosestPeer(self):
    for i in range(4):      
      self.manager.addPeer(self.peers[i])

    p5 = Peer("5", "h1","21",[-5, -2])

    self.manager.addPeer(p5)


    assert (self.manager.getClosestPeer([0,0]).getId() == "0" )
    assert (self.manager.getClosestPeer([20,20]).getId() == "3" )
    assert (self.manager.getClosestPeer([-5,-15]).getId() == "5" )
    assert (self.manager.getClosestPeer([3,1]).getId() == "2" )
    assert (self.manager.getClosestPeer([-115,-115]).getId() == "5" )
    
    assert (self.manager.getClosestPeer([Geometry.SIZE - 10,
                                         Geometry.SIZE - 10]).getId() == "5" )
    assert (self.manager.getClosestPeer([Geometry.SIZE - 1,
                                         Geometry.SIZE - 1]).getId() == "0" )

  def testGetWorstPeer(self):
    p0 = Peer("0","h1","1",[2,2])
    p1 = Peer("1","h1","2",[7,2])
    p2 = Peer("2","h1","3",[5,3])
    p3 = Peer("3","h1","3",[3,6])
    p4 = Peer("4","h","44",[4,-6])
    p5 = Peer("5","h","44",[4,0])
    self.manager.addPeer(p0)
    self.manager.addPeer(p1)
    self.manager.addPeer(p2)
    self.manager.addPeer(p3)
    self.manager.addPeer(p4)
    
    id = self.manager.getWorstPeer().getId()
    # p4 is farther but is needed for global connectivity 
    assert (id == "3")

    self.manager.addPeer(p5)
    id = self.manager.getWorstPeer().getId()
    # with p5 added p4 is no longer needed for the global connectivity rule
    # as p4 is the farthest it should be elected
    assert (id == "4")
    
    print "worst=" + id
    print self.manager.node.position

    print "ccw"
    for e in self.manager.ccwPeers.ll:
      print e.getId()
    print "dist"
    for e in self.manager.distPeers.ll:
      print e.getId()

      
if __name__ == "__main__":
  unittest.main()
