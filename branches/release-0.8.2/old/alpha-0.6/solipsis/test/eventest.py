import unittest
import os,sys

searchPath = os.path.dirname(os.path.dirname(sys.path[0]))
sys.path.append(searchPath)

from solipsis.core.node import Node
from solipsis.util.parameter import Parameters
from optparse import OptionParser
from solipsis.core.event import EventFactory, Notification
from solipsis.core.peerevent import PeerEventFactory, PeerEvent,PeerEventParser
from solipsis.core.controlevent import ControlEventFactory, ControlEvent 

class PeerEventTestCase(unittest.TestCase):
	
    def setUp(self):
        configFileName = "../../conf/solipsis.conf"
        configFileName = "../../conf/solipsis.conf"
        parser = OptionParser('')
        param = Parameters(parser, configFileName)
        self.node = Node(param)
        EventFactory.init(self.node)
        EventFactory.register(PeerEventFactory.TYPE, PeerEventFactory())
        EventFactory.register(ControlEventFactory.TYPE, ControlEventFactory())

    def testCreateEvent(self):
        pf = EventFactory.getInstance(PeerEvent.TYPE)
        evt = pf.createHELLO()
        
        print evt.__dict__
        print '\n'
        n = Notification()
        n.setFromEvent(evt)
        print n.__dict__
        print '\n'
        e= n.createEvent()
        print e.__dict__
        print '\n'

        e2 = pf.createHEARTBEAT()
        parser = PeerEventParser()
        print parser.getData(e2)
        
if __name__ == "__main__":
    unittest.main()
        
