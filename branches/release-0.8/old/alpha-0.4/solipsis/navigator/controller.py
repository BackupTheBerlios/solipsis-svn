import xmlrpclib
import os

class Controller:
    def __init__(self, params):
        """ Constructor. Create a new controller object
        params : initialization parameters. a list [host, port, logger]
                 host= ip address of the node to control
                 port= port number for the control service in the node
                 logger= a logger object used for debugging purpose"""
        [self.host, self.port, self.logger] = params
        self.connected = False
        self.id = 51
        
    def createNode(self):
        """ Create and start a new node """
        # we create a new process 'python solipsis/engine/startup.py'
        # os.P_NOWAIT : do not wait for this process to finish
        # os.environ : neede to inherit the PYTHONPATH variable
        self.nodePID = os.spawnlpe(os.P_NOWAIT, 'python', 'python',
                                   'solipsis/engine/startup.py',os.environ)
                
    def connect(self):
        self.server = xmlrpclib.ServerProxy("http://"+ self.host + ":" +
                                            str(self.port),None, None,0,1)
        self.connected = True

    def kill(self):
        """ Kill the node created with this controller"""
        self.server.kill(self.id)
        #os.waitpid(self.nodePID, os.WNOHANG)
        # the node process was created with os.P_NOWAIT parameter so we need
        # to wait for this process in order to avoid a zombie process
        os.wait()

    def getNodeInfo(self):
        info = self.server.getNodeInfo(self.id)
        self.logger.debug("controller.getnodeinfo")
        self.logger.debug(info)
        return info
        
