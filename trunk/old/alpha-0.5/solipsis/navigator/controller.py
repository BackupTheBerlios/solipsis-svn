import xmlrpclib, os, new, threading
from solipsis.engine.event import Event
from solipsis.util.exception import SolipsisAbstractMethodError

class Controller:
    """ Abstract Controller class. Defines the method that a concrete
    Controller must implement """
    def __init__(self):
        raise SolipsisAbstractMethodError()
    
    def setSubscriber(self, subscriber):
        """ Bind a listener object to this controller. This listener will be
        notified, when new events are fired by the node """
        self._subscriber = subscriber

    def getSubscriber(self):
        return self._subscriber

    def createNode(self):
        """ Abstract method : this method must be implemented by a sub-class
        Create and start a new node """
        raise SolipsisAbstractMethodError()
   
    def connect(self):
        """ Abstract method : this method must be implemented by a sub-class
        Connect to an existing node
        """
        raise SolipsisAbstractMethodError()

    def kill(self):
        """ Abstract method : this method must be implemented by a sub-class
        Kill the node that is controlled by this oject
        """
        raise SolipsisAbstractMethodError()

    def jump(self, position):
        """ Abstract method : this method must be implemented by a sub-class
        Teleport the node to a target position. This method is used when we
        want to go a distant position on the Solipsis world, whereas move
        is used when we are moving around our current position.
        position : a Position object - our target position
        """
        raise SolipsisAbstractMethodError()

    def move(self, position):
        """ Abstract method : this method must be implemented by a sub-class
        Move to a target position. The target position is a Position located
        inside our awareness radius (close to our current position)
        position : a Position object - our target position
        """
        raise SolipsisAbstractMethodError()

    def addService(self, service):
        """ Abstract method : this method must be implemented by a sub-class
        Add a new Service.
        service : a Service object - the new service added to the node
        """
        raise SolipsisAbstractMethodError()

    def removeService(self, serviceId):
        """ Abstract method : this method must be implemented by a sub-class
        Remove a service.
        serviceId : a string representing a ServiceId
        """
        raise SolipsisAbstractMethodError()

    def getNodeInfo(self):
        """ Abstract method : this method must be implemented by a sub-class
        Get all the characteristics of the node: position, caliber, etc ...   
        """
        raise SolipsisAbstractMethodError()

    def getPeerInfo(self, peerId):
        """ Abstract method : this method must be implemented by a sub-class
        Get all the characteristics of a peer: position, caliber, etc ...
        peerId : ID of the peer
        """
        raise SolipsisAbstractMethodError()

    def getAllPeer(self):
        """ Abstract method : this method must be implemented by a sub-class
        Get information on all the peers of our node
        """
        raise SolipsisAbstractMethodError()
    
class XMLRPCController(Controller):
    def __init__(self, subscriber, params):
        """ Constructor. Create a new XML-RPC controller object
        subscriber : the listener object that registers for node notification 
        params : initialization parameters. a list [host, port, logger]
                 host= ip address of the node to control
                 port= port number for the control service in the node
                 logger= a logger object used for debugging purpose"""
        self._subscriber = subscriber
        [self.host, self.port, self.notifPort, self.logger] = params
        self.connected = False
        self.id = 51
        
    def createNode(self):
        """ Create and start a new node """
        # we create a new process 'python solipsis/engine/startup.py'
        # os.P_NOWAIT : do not wait for this process to finish
        # os.environ : needed to inherit the PYTHONPATH variable
        args = 'solipsis/engine/startup.py -h ' + self.host + ' -p '
        args = args + self.port + ' -n ' + self.notifPort
        self.nodePID = os.spawnlpe(os.P_NOWAIT, 'python', 'python',
                                   args, os.environ)
    
    def connect(self):
        self.server = xmlrpclib.ServerProxy("http://"+ self.host + ":" +
                                            str(self.port),None, None,0,1)
        self.notification = NodeNotification(self._subscriber, self.host,
                                             self.notifPort, self.logger)
        # start the notification thread
        self.notification.start()
        self.connected = True

    def kill(self):
        """ Kill the node created with this controller"""
        self.server.kill(self.id)
        #os.waitpid(self.nodePID, os.WNOHANG)
        # the node process was created with os.P_NOWAIT parameter so we need
        # to wait for this process in order to avoid a zombie process
        os.wait()

    def getNodeInfo(self):
        self.logger.debug("controller.getnodeinfo")
        self.server.getNodeInfo(self.id)

class NodeNotification(threading.Thread):

    def __init__(self, subscriber, host, notifPort, logger):
        self._subscriber = subscriber
        self.host = host
        self.port = notifPort
        self.logger = logger
        url = "http://" + self.host + ":" + str(self.port)
        self.server = xmlrpclib.ServerProxy(url, None, None,0,1)
        self.stopThread = False
        
    def run(self):
        while not self.stopThread:
            response = self.server.get()
            # with XMLRPC complex type like objects are marshalled to
            # dictionnaries.
            # The module new allows us to convert this dictionary to a 'real'
            # object of the class Event
            event = new.instance(Event, response)

            # get request name
            request = event.getRequest()
            # build the statement that will be evaluated,
            # e.g. 'self.subscriber.NEW(event)' 
            stmt = 'self.subscriber.' + request + '(event)'
            # call the corresponding method on the subscriber
            eval(stmt)

    def stop(self):
        self.stopThread = True
            

class DummyController(Controller):
    """ Dummy controller object only used to test the Controller class """
    def __init__(self, subscriber):
        self.setSubscriber(subscriber)

    def connect(self):
        """ Generate a NEW peer event """
        import solipsis.engine.event
        import solipsis.engine.entity
        nodeinfo = solipsis.engine.event.ControlEvent('NODEINFO')
        nodeinfo.addArg('Id', 'slp:node_dummycontroller')
        nodeinfo.addArg('Position', solipsis.engine.entity.Position(12,16))
        nodeinfo.addArg('Awarness-Radius', 10)
        nodeinfo.addArg('Pseudo', 'myNode')
        nodeinfo.addArg('Caliber', 2)
        self.getSubscriber().NODEINFO(nodeinfo)
        
        newEvent = solipsis.engine.event.ControlEvent('NEW')
        newEvent.addArg('Id', 'slp:dummycontroller')
        newEvent.addArg('Position', solipsis.engine.entity.Position(88,36))
        newEvent.addArg('Awarness-Radius', 10)
        newEvent.addArg('Pseudo', 'p1')
        self.getSubscriber().NEW(newEvent)

        threading.Timer(10.0, self.OnTimer).start()

    def OnTimer(self):
        import solipsis.engine.event
        import solipsis.engine.entity
        newEvent = solipsis.engine.event.ControlEvent('NEW')
        newEvent.addArg('Id', 'slp:peerTimer')
        newEvent.addArg('Position', solipsis.engine.entity.Position(-20,126))
        newEvent.addArg('Awarness-Radius', 10)
        newEvent.addArg('Pseudo', 'p2')
        self.getSubscriber().NEW(newEvent)
