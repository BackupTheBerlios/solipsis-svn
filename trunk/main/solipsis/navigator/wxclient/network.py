
import threading

from proxy import UIProxy


class C:
    pass


class NetworkLoop(threading.Thread):
    def __init__(self, reactor, wxEvtHandler):
        super(NetworkLoop, self).__init__()
        self.repeat_hello = True
        self.repeat_count = 0
        self.ui = UIProxy(wxEvtHandler)
        self.reactor = reactor

        self.angle = 0.0
        self.AnimCircle(init=True)

    def run(self):
        # Dummy demo stuff
        self.reactor.callLater(3, self.HelloWorld)
        self.reactor.callLater(1, self.AnimCircle)

        # Run reactor
        self.reactor.run(installSignalHandlers=0)

    def HelloWorld(self):
        from random import random

        self.repeat_count += 1
        self.ui.AddObject(str(random()), C(), (random(), random()))

        if self.repeat_hello:
            self.reactor.callLater(1, self.HelloWorld)

    def UI_dump(self, s):
        print s

    def SetRepeat(self, value):
        if not self.repeat_hello and value:
            self.reactor.callLater(1, self.HelloWorld)
        self.repeat_hello = value

    def AnimCircle(self, init=False):
        import math
        r = 0.5
        self.x = r * math.cos(self.angle)
        self.y = r * math.sin(self.angle)
        self.angle += 0.01
        if init:
            self.ui.AddObject("toto", C(), (self.x, self.y))
        else:
            self.ui.MoveObject("toto", (self.x, self.y))
        self.reactor.callLater(0.05, self.AnimCircle)
