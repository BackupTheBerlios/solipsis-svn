import xmlrpclib, os, new, threading, time
from solipsis.core.event import Event, Notification

from solipsis.util.exception import AbstractMethodError

class Controller(object):
    """ Abstract Controller class. Defines the method that a concrete
    Controller must implement """
    def __init__(self):
        raise AbstractMethodError()

    def setSubscriber(self, subscriber):
        """ Bind a listener object to this controller. This listener will be
        notified, when new events are fired by the node """
        self._subscriber = subscriber

    def getSubscriber(self):
        return self._subscriber

    def createNode(self):
        """ Abstract method : this method must be implemented by a sub-class
        Create and start a new node """
        raise AbstractMethodError()

    def connect(self):
        """ Abstract method : this method must be implemented by a sub-class
        Connect to an existing node
        """
        raise AbstractMethodError()

    def kill(self):
        """ Abstract method : this method must be implemented by a sub-class
        Kill the node that is controlled by this oject
        """
        raise AbstractMethodError()

    def jump(self, x, y, z):
        """ Abstract method : this method must be implemented by a sub-class
        Teleport the node to a target position. This method is used when we
        want to go a distant position on the Solipsis world, whereas move
        is used when we are moving around our current position.

        """
        raise AbstractMethodError()

    def move(self, position):
        """ Abstract method : this method must be implemented by a sub-class
        Move to a target position. The target position is a Position located
        inside our awareness radius (close to our current position)
        position : a Position object - our target position
        """
        raise AbstractMethodError()

    def addService(self, service):
        """ Abstract method : this method must be implemented by a sub-class
        Add a new Service.
        service : a Service object - the new service added to the node
        """
        raise AbstractMethodError()

    def removeService(self, serviceId):
        """ Abstract method : this method must be implemented by a sub-class
        Remove a service.
        serviceId : a string representing a ServiceId
        """
        raise AbstractMethodError()

    def getNodeInfo(self):
        """ Abstract method : this method must be implemented by a sub-class
        Get all the characteristics of the node: position, caliber, etc ...
        """
        raise AbstractMethodError()

    def getPeerInfo(self, peerId):
        """ Abstract method : this method must be implemented by a sub-class
        Get all the characteristics of a peer: position, caliber, etc ...
        peerId : ID of the peer
        """
        raise AbstractMethodError()

    def getAllPeer(self):
        """ Abstract method : this method must be implemented by a sub-class
        Get information on all the peers of our node
        """
        raise AbstractMethodError()

class XMLRPCController(Controller):
    def __init__(self, subscriber, params):
        """ Constructor. Create a new XML-RPC controller object
        subscriber : the listener object that registers for node notification
        params : initialization parameters. a list [host, port]
                 host= ip address of the node to control
                 port= port number for the control service in the node
                 """
        self.setSubscriber(subscriber)
        self.host = 'localhost'
        self.port = params.control_port
        self.notifPort = params.notif_port
        self.connected = False
        self.server = None

    def createNode(self, pseudo=''):
        """ Create and start a new node
        pseudo : optional parameter, the pseudo of this Node
        """
        # we create a new process 'python solipsis/engine/startup.py'
        # os.P_NOWAIT : do not wait for this process to finish
        # os.environ : needed to inherit the PYTHONPATH variable
        args = ['python', 'solipsis/core/main.py']
        args +=  ['-c', str(self.port), '-n', str(self.notifPort)]

        print args
        self.nodePID = os.spawnvpe(os.P_NOWAIT, 'python', args, os.environ)
        CheckCreationThread(self).start()

    def OnNodeCreationTimeout(self):
        """ Node creation failed."""
        self.getSubscriber().OnNodeCreationFailure('Timeout')

    def OnNodeCreationSuccess(self):
        print 'XMLRPCController OnNodeCreationSuccess'
        self.getSubscriber().OnNodeCreationSuccess()

    def isNodeAlive(self):
        try:
            if self.server is None:
                self.server = xmlrpclib.ServerProxy("http://"+ self.host + ":" +
                                                    str(self.port),None, None,0,1)

            self.server.isAlive()
            return True
        except:
            return False

    def connect(self):
        self.server = xmlrpclib.ServerProxy("http://"+ self.host + ":" +
                                            str(self.port),None, None,0,1)
        self.notification = NodeNotification(self._subscriber, self.host,
                                             self.notifPort )
        # start the notification thread
        self.notification.start()
        self.connected = True

    def kill(self):
        """ Kill the node created with this controller"""
        self.server.kill()
        # os.waitpid(self.nodePID, os.WNOHANG)
        # the node process was created with os.P_NOWAIT parameter so we need
        # to wait for this process in order to avoid a zombie process
        os.wait()

    def getNodeInfo(self):
        self.server.getNodeInfo()

    def jump(self, x, y, z):
        self.server.jump(x, y, z)


class NodeNotification(threading.Thread):

    def __init__(self, subscriber, host, notifPort):
        super(NodeNotification, self).__init__()
        self.subscriber = subscriber
        self.host = host
        self.port = notifPort
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
            notification = new.instance(Notification, response)
            event = notification.createEvent()
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
        from solipsis.core.controlevent import ControlEvent
        import solipsis.core.entity
        nodeinfo = ControlEvent('NODEINFO')
        nodeinfo.addArg('Id', 'slp:node_dummycontroller')
        nodeinfo.addArg('Position', solipsis.core.entity.Position(12,16))
        nodeinfo.addArg('Awareness-Radius', 10)
        nodeinfo.addArg('Pseudo', 'myNode')
        nodeinfo.addArg('Calibre', 2)
        self.getSubscriber().NODEINFO(nodeinfo)

        newEvent = ControlEvent('NEW')
        newEvent.addArg('Id', 'slp:dummycontroller')
        newEvent.addArg('Position', solipsis.core.entity.Position(88,36))
        newEvent.addArg('Awareness-Radius', 10)
        newEvent.addArg('Pseudo', 'p1')
        self.getSubscriber().NEW(newEvent)

        threading.Timer(10.0, self.OnTimer).start()

    def OnTimer(self):
        from solipsis.core.controlevent import ControlEvent
        import solipsis.core.entity
        newEvent = ControlEvent('NEW')
        newEvent.addArg('Id', 'slp:peerTimer')
        newEvent.addArg('Position', solipsis.core.entity.Position(-20,126))
        newEvent.addArg('Awareness-Radius', 10)
        newEvent.addArg('Pseudo', 'p2')
        self.getSubscriber().NEW(newEvent)

    def createNode(self, pseudo):
        f = file('nodes/nodes.txt', 'w')
        f.write('dummy;127.0.0.1;1247;8088;7000;567687876787654;5668798798\n')
        f.close()
        self.getSubscriber()._OnNodeCreationSuccess()

class CheckCreationThread(threading.Thread):
    CREATION_TIMEOUT = 5
    SLEEP_TIME = 0.5
    def __init__(self, controller):
        self.controller = controller
        super(CheckCreationThread, self).__init__()

    def run(self):
        self.startTime = time.time()

        while time.time() < self.startTime + CheckCreationThread.CREATION_TIMEOUT:
            if not self.controller.isNodeAlive():
                print 'CheckCreationThread sleeping'
                time.sleep(CheckCreationThread.SLEEP_TIME)
            else:
                print 'CheckCreationThread success'
                self.controller.OnNodeCreationSuccess()
                return

        # timeout expired
        self.controller.OnNodeCreationTimeout()

