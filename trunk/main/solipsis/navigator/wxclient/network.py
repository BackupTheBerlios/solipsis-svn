
import threading
import twisted.web.xmlrpc as xmlrpc

from proxy import UIProxy


class NotificationHandler(object):
    def __init__(self, reactor, ui):
        super(NotificationHandler, self).__init__()

        self.parsers = {
            'position': self._ParsePosition,
        }
        self.reactor = reactor
        self.ui = ui

    def Receive(self, request, properties):
        try:
            attr = getattr(self, request)
        except:
            print "Unhandled notification '%s'" % request
        else:
            self._ParseProperties(properties)
            attr(properties)

    #
    # Notification handlers
    #
    def NEW(self, properties):
        print "NEW", properties['id'], properties['position']
        self.ui.AddObject(properties['id'], None, position=properties['position'])

    def DEAD(self, properties):
        print "DEAD", properties['id']
        self.ui.RemoveObject(properties['id'])


    #
    # Private methods
    #
    def _ParseProperties(self, properties):
        for p, parser in self.parsers.items():
            if p in properties:
                try:
                    properties[p] = parser(properties[p])
                except:
                    print "Wrong syntax for '%s' in notification: %s" % (p, properties[p])

    def _ParsePosition(self, position):
        x, y, z = position.split(",")
        return (float(x), float(y), float(z))
        #return (float(x)/2**128, float(y)/2**128, float(z))


class XMLRPCConnector(object):
    """
    XMLRPCConnector builds the socket-based connection to the Solipsis node.
    It handles sending and receiving data from the node.
    """
    def __init__(self, reactor, notification_receiver):
        super(XMLRPCConnector, self).__init__()

        self.reactor = reactor
        self.notification_receiver = notification_receiver
        self.xmlrpc_control = None
        self.xmlrpc_notif = None

    def Connect(self, host, port):
        control_url = 'http://%s:%d/RPC2' % (host, port)
        notif_url = 'http://%s:%d/RPC2' % (host, port + 1)
        self.xmlrpc_control = xmlrpc.Proxy(control_url)
        self.xmlrpc_notif = xmlrpc.Proxy(notif_url)
        self._AskNotif()

    def Disconnect(self):
        self.xmlrpc_control = None
        self.xmlrpc_notif = None

    def CallControl(self, method, *args):
        if self.xmlrpc_control is not None:
            print method
            d = self.xmlrpc_control.callRemote(method, *args)
            d.addCallbacks(self.ControlResponse, self.ControlError)

    #
    # XML RPC callbacks
    #
    def ControlResponse(self, value):
        pass

    def NotifResponse(self, value):
        self._AskNotif()
        message = None
        try:
            request = value['request']
            items = [(k, v) for (k, v) in value.items() if k != 'request']
        except AttributeError:
            print "Bad notification:", str(value)
        else:
            self.notification_receiver(request, dict(items))

    def ControlError(self, failure):
        print "Control error:", str(failure)
        self.xmlrpc_control = None
        self.xmlrpc_notif = None
        raise failure

    def NotifError(self, failure):
        print "Notification error:", str(failure)
        self.xmlrpc_control = None
        self.xmlrpc_notif = None
        raise failure

    #
    # Private methods
    #
    def _AskNotif(self):
        if self.xmlrpc_notif is not None:
            d = self.xmlrpc_notif.callRemote('get')
            d.addCallbacks(self.NotifResponse, self.NotifError)


class NetworkLoop(threading.Thread):
    """
    NetworkLoop is an event loop running in its own thread.
    It manages socket-based communication with the Solipsis node
    and event-based communication with the User Interface (UI).
    """
    def __init__(self, reactor, wxEvtHandler):
        """ Builds a network loop from a Twisted reactor and a Wx event handler """

        super(NetworkLoop, self).__init__()
        self.repeat_hello = True
        self.repeat_count = 0
        self.ui = UIProxy(wxEvtHandler)
        self.reactor = reactor

        self.angle = 0.0
        self.notification_handler = NotificationHandler(reactor=self.reactor, ui=self.ui)
        self.node_connector = XMLRPCConnector(reactor=self.reactor, notification_receiver=self.notification_handler.Receive)

    def run(self):
        # Dummy demo stuff
        #self._AnimCircle(init=True)
        #self.reactor.callLater(3, self._HelloWorld)

        # Run reactor
        self.reactor.run(installSignalHandlers=0)


    #
    # Actions from the UI thread
    #

    def ConnectToNode(self, *args, **kargs):
        self.node_connector.Connect(*args, **kargs)
        self.node_connector.CallControl('move', 500, 2000, 0)

    def DisconnectFromNode(self, *args, **kargs):
        self.node_connector.CallControl('move', str(2**127+12), str(2**127+325), 0)
        #self.node_connector.Disconnect(*args, **kargs)


    #
    # Private methods
    #

    def _HelloWorld(self):
        from random import random

        class C(object): pass
        self.repeat_count += 1
        #self.ui.AddObject(str(random()), C(), (random(), random()))

        if self.repeat_hello:
            self.reactor.callLater(1, self._HelloWorld)

    def _AnimCircle(self, init=False):
        import math
        r = 0.5
        self.x = r * math.cos(self.angle)
        self.y = r * math.sin(self.angle)
        self.angle += 0.01
        if init:
            class C(object): pass
            self.ui.AddObject("toto", C(), (self.x, self.y))
        else:
            self.ui.MoveObject("toto", (self.x, self.y))
        self.reactor.callLater(0.05, self._AnimCircle)

