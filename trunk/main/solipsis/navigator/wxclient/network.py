
import threading
import twisted.web.xmlrpc as xmlrpc

from proxy import UIProxy


class XMLRPCConnector(object):
    def __init__(self, reactor):
        super(XMLRPCConnector, self).__init__()

        self.reactor = reactor
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

    def ControlResponse(self, value):
        print value

    def NotifResponse(self, value):
        print value
        self._AskNotif()

    def ControlError(self, error):
        print "Control error:", error
        self.xmlrpc_control = None
        self.xmlrpc_notif = None

    def NotifError(self, error):
        print "Notification error:", error
        self.xmlrpc_control = None
        self.xmlrpc_notif = None

    def _AskNotif(self):
        if self.xmlrpc_notif is not None:
            print 'Get'
            d = self.xmlrpc_notif.callRemote('get')
            d.addCallbacks(self.NotifResponse, self.NotifError)



class NetworkLoop(threading.Thread):
    def __init__(self, reactor, wxEvtHandler):
        """ Builds a network loop from a Twisted reactor and a Wx event handler """

        super(NetworkLoop, self).__init__()
        self.repeat_hello = True
        self.repeat_count = 0
        self.ui = UIProxy(wxEvtHandler)
        self.reactor = reactor

        self.angle = 0.0
        self._AnimCircle(init=True)
        self.node_connector = XMLRPCConnector(self.reactor)

    def run(self):
        # Dummy demo stuff
        self.reactor.callLater(3, self._HelloWorld)
        self.reactor.callLater(1, self._AnimCircle)

        # Run reactor
        self.reactor.run(installSignalHandlers=0)

    def UI_dump(self, s):
        print s

    def SetRepeat(self, value):
        if not self.repeat_hello and value:
            self.reactor.callLater(1, self._HelloWorld)
        self.repeat_hello = value


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

