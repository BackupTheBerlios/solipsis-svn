

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
        self.connect_id = None

    def Connect(self, host, port):
        control_url = 'http://%s:%d/RPC2' % (host, port)
        notif_url = 'http://%s:%d/RPC2' % (host, port + 1)
        xmlrpc_control = xmlrpc.Proxy(control_url)

        def _connected(connect_id):
            self.xmlrpc_control = xmlrpc_control
            self.connect_id = connect_id
            print "connect_id:", connect_id
        xmlrpc_control.callRemote('Connect').addCallback(_connected)

#         self.xmlrpc_notif = xmlrpc.Proxy(notif_url)
#         self._AskNotif()

    def Disconnect(self):
        self.CallControl('Disconnect')
        self.xmlrpc_control = None
        self.xmlrpc_notif = None
        self.connect_id = None

    def CallControl(self, method, *args):
        if self.xmlrpc_control is not None:
            d = self.xmlrpc_control.callRemote(method, self.connect_id, *args)
            d.addCallbacks(self.ControlResponse, self.ControlError)

    #
    # XML RPC callbacks
    #
    def ControlResponse(self, reply):
        """ Called on response to a control request. """

    def NotifResponse(self, reply):
        self._AskNotif()
        try:
            notifications = []
            for value in reply:
                request = value['request']
                items = [(k, v) for (k, v) in value.items() if k != 'request']
                notifications.append((request, items))
        except AttributeError:
            print "Bad notification:", str(reply)
        else:
            for (request, items) in notifications:
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
            d = self.xmlrpc_notif.callRemote('Get')
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
        self.node_connector.CallControl('Move', 500, 2000, 0)

    def DisconnectFromNode(self, *args, **kargs):
#         self.node_connector.CallControl('Die')
        self.node_connector.Disconnect(*args, **kargs)

    def MoveTo(self, (x, y)):
        x = str(long(x))
        y = str(long(y))
        self.node_connector.CallControl('Move', x, y, 0)

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

