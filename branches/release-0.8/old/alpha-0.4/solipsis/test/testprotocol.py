import unittest

from solipsis.engine.node import Node
from solipsis.util.parameter import Parameters
from solipsis.engine.protocol import Message, MessageFactory

class MessageFactoryTestCase(unittest.TestCase):
    def setUp(self):
        configFileName = "conf/solipsis.conf"
        param = Parameters(configFileName)
        n = Node(param)            
        MessageFactory.init(n)

    def testBest(self):
        factory = MessageFactory.getInstance()
        best = factory.createBestMsg()
        print best

        myBest = Message(best.data())
        print myBest

    def msg1(self):
        line1 = "FINDNEAResT SOLIPSIS/1.0"
        line2 = "Position: 1235989454545 - 454578787888787876646"
        line3 = "Remote-Address: 192.235.25.3:5678"
        buffer = [line1, line2, line3]

        rawData = "\r\n".join(buffer)
        print rawData


if __name__ == "__main__":
  unittest.main()
