

import threading
import twisted.web.xmlrpc as xmlrpc

from solipsis.util import marshal
from proxy import UIProxy


class NotificationHandler(object):
    def __init__(self, reactor, ui):
        super(NotificationHandler, self).__init__()

#         self.parsers = {
#             'position': self._ParsePosition,
#         }
        self.reactor = reactor
        self.ui = ui

    def Receive(self, request, payload):
        try:
            attr = getattr(self, request)
        except:
            print "Unrecognized notification '%s'" % request
        else:
            attr(payload)

    #
    # Notification handlers
    #
    def NEW(self, struct):
        peer_info = marshal.PeerInfo(struct)
        print "NEW", peer_info.id_
        self.ui.AddObject(peer_info.id_, None, position=peer_info.position)

    def LOST(self, peer_id):
        print "LOST", peer_id
        self.ui.RemoveObject(peer_id)


    #
    # Private methods
    #
#     def _ParseProperties(self, properties):
#         for p, parser in self.parsers.items():
#             if p in properties:
#                 try:
#                     properties[p] = parser(properties[p])
#                 except:
#                     print "Wrong syntax for '%s' in notification: %s" % (p, properties[p])
#
#     def _ParsePosition(self, position):
#         x, y, z = position.split(",")
#         return (float(x), float(y), float(z))


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
        self.connect_id = None

    def Connect(self, host, port):
        """
        Connect to the node.
        """
        control_url = 'http://%s:%d/RPC2' % (host, port)
        xmlrpc_control = xmlrpc.Proxy(control_url)

        def _success(connect_id):
            self.xmlrpc_control = xmlrpc_control
            self.connect_id = connect_id
            print "connect_id:", connect_id
            self._AskEvents()
        def _failure(error):
            print "connection failure:", str(error)
        xmlrpc_control.callRemote('Connect').addCallbacks(_success, _failure)

    def Disconnect(self):
        """
        Disconnect from the node.
        """
        self.Call('Disconnect')
        self.xmlrpc_control = None
        self.connect_id = None

    def Connected(self):
        """
        Returns True if connected.
        """
        return self.xmlrpc_control is not None

    def Call(self, method, *args):
        """
        Call a remote function on the node.
        """
        if self.xmlrpc_control is not None:
            d = self.xmlrpc_control.callRemote(method, self.connect_id, *args)
            _success = getattr(self, "success_" + method, self.success_default)
            _failure = getattr(self, "failure_" + method, self.failure_default)
            d.addCallbacks(_success, _failure)

    #
    # XML RPC callbacks
    #
    def success_default(self, reply):
        pass

    def failure_default(self, error):
        print "failure:", str(error)

    def success_GetEvents(self, reply):
        for notif in reply:
            t, request, payload = notif
            self.notification_receiver(request, payload)
        self._AskEvents()

    #
    # Private methods
    #
    def _AskEvents(self):
        self.Call('GetEvents')


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
        self.node_connector.Call('Move', 500, 2000, 0)

    def DisconnectFromNode(self, *args, **kargs):
        self.node_connector.Disconnect(*args, **kargs)

    def MoveTo(self, (x, y)):
        x = str(long(x))
        y = str(long(y))
        self.node_connector.Call('Move', x, y, 0)

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

