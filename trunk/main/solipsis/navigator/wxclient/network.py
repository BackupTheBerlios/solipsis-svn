
import threading

from proxy import UIProxy
from remote import RemoteConnector


class NetworkLoop(threading.Thread):
    """
    NetworkLoop is an event loop running in its own thread.
    It manages socket-based communication with the Solipsis node
    and event-based communication with the User Interface (UI).
    """
    def __init__(self, reactor, wxEvtHandler):
        """
        Builds a network loop from a Twisted reactor and a Wx event handler.
        """

        super(NetworkLoop, self).__init__()
        self.repeat_hello = True
        self.repeat_count = 0
        self.ui = UIProxy(wxEvtHandler)
        self.reactor = reactor

        self.angle = 0.0
        self.remote_connector = RemoteConnector(self.reactor, self.ui)

    def run(self):
        # Dummy demo stuff
        #self._AnimCircle(init=True)

        # Run reactor
        self.reactor.run(installSignalHandlers=0)


    #
    # Actions from the UI thread
    #
    def ConnectToNode(self, *args, **kargs):
        self.remote_connector.Connect(*args, **kargs)

    def DisconnectFromNode(self, *args, **kargs):
        self.remote_connector.Disconnect(*args, **kargs)

    def MoveTo(self, (x, y)):
        x = str(long(x))
        y = str(long(y))
        self.remote_connector.Call('Move', x, y, 0)

    #
    # Private methods
    #
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

