import unittest
import os,sys

searchPath = os.path.dirname(os.path.dirname(sys.path[0]))
sys.path.append(searchPath)

from solipsis.core.node import Node
from solipsis.core.entity import Position, Address
from solipsis.util.parameter import Parameters
from solipsis.core.protocol import Message
from optparse import OptionParser

class ProtocolTestCase(unittest.TestCase):
    def setUp(self):
        configFileName = "../../conf/solipsis.conf"
        param = Parameters(OptionParser(''), configFileName)
        n = Node(param)         

    def testFINDNEAREST(self):
        line1 = "FINDNEAResT SOLIPSIS/1.0"
        line2 = "Position: 1235989454545 - 45457878788878787"
        line3 = "Remote-Address: 192.235.25.3:5678"
        line4 = "Id: john"
        line5 = "Orientation: 10"
        buffer = [line1, line2, line3, line4, line5]

        rawData = "\r\n".join(buffer)
        
        msg = Message()
        msg.fromData(rawData)
        assert( msg.args['Position'] == Position(1235989454545, 45457878788878787))
        assert( msg.args['Remote-Address'] == Address('192.235.25.3', 5678) )
        assert( msg.args['Orientation'] == 10 )
        
if __name__ == "__main__":
    unittest.main()
    
