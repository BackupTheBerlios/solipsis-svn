from optparse import OptionParser
import logging
# Solipsis Packages
from solipsis.util.parameter import Parameters
from solipsis.navigator.controller import XMLRPCController
from solipsis.navigator.subscriber import AbstractSubscriber

class PrinterNavigator(AbstractSubscriber):
    def __init__(self):
        self.params = self.getParams()
        self.controller = XMLRPCController(self, self.params)
        self.logger = logging.getLogger('root')
        
    def getParams(self):
        """ return the parameters for this navigator """
        try:
            config_file = "conf/solipsis.conf"
            usage = "usage: %prog [-db] [-p <port>] [-x ... -y ...] [-e ...] [-c <port>] [-n <port>] [firstpeer:port]"
            parser = OptionParser(usage)

            parser.add_option("-p", "--port", type="int", dest="port",
                                help="port number for all Solipsis connections")
            parser.add_option("-b", "--robot", action="store_true", dest="bot", default=False,
                                help="bot mode (don't listen for navigator)")
            parser.add_option("-d", "--detach", action="store_true", dest="detach", default=False,
                                help="run in the background")
            parser.add_option("-x", type="long", dest="pos_x",
                                help="X start value")
            parser.add_option("-y", type="long", dest="pos_y",
                                help="Y start value")
            parser.add_option("-e", type="int", dest="expected_neighbours",
                                help="number of expected neighbours")
            parser.add_option("-c", "--control_port", type="int", dest="control_port",
                                help="control port for navigator")
            parser.add_option("-n", "--notification_port", type="int", dest="notif_port",
                                help="notification port for navigator")
            parser.add_option("-f", "--file", dest="config_file", default=config_file,
                              help="configuration file" )
            params = Parameters(parser, config_file=config_file)

            return params
            
        except: raise

    def NEW(self, peer):
        """ Abstract method : this method must be implemented by a sub-class
        We have discovered a new Peer.
        peer : a Peer Object
        """
        self.logger.info('reception of NEW:\n' + str(peer))

    def NODEINFO(self, node):
        """ Abstract method : this method must be implemented by a sub-class

        nodeinfo: a NodeInfo object
        """
        self.logger.info( 'reception of NODEINFO:\n' + str(node))

    def UPDATE(self, entityId, entityFieldName, newFieldValue):
        """ Abstract method : this method must be implemented by a sub-class

        'entityId' : Id of the entity to update
        'entityFieldName' : what is the characteristic to update
        'newFieldValue' : the new value
        """
        self.logger.info( 'reception of UPDATE\n')

    def OnNodeCreationFailure(self, reason):
        """ Abstract method : this method must be implemented by a sub-class
        Failure of the node creation operation
        reason : reason why the node couldn' be created
        """
        self.logger.info( 'OnNodeCreationFailure:' + reason)


    def OnNodeCreationSuccess(self):
        """ Abstract method : this method must be implemented by a sub-class
        The node was successfully created """
        self.logger.info( 'OnNodeCreationSuccess: connecting to node')
        self.controller.connect()
        
        
    
