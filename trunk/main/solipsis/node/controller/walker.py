
import random
import math

from solipsis.util.timer import AutoTimer
from delayedcaller import DelayedCaller


class Controller(object):
    update_period = 60.0
    decide_period_avg = 60.0

    def __init__(self, reactor, params, remote_control):
        self.reactor = reactor
        self.params = params
        self.remote_control = remote_control
        self.caller = DelayedCaller(self.reactor)
        self.ready = False
        self.alive = False
        self.speed = (0.0, 0.0)

    def Start(self, pool_num):
        self.alive = True
        self.timer = AutoTimer()
        self.connect_id = self.remote_control.remote_Connect()
        self._AskEvents()
        self._Decide()
        self.caller.CallPeriodically(self.update_period, self._Update)

    def Stop(self):
        self.alive = False
        self.caller.Reset()
#         self.remote_control.remote_Disconnect(self.connect_id)

    def _Decide(self):
        if self.ready:
            node_info = self.remote_control.remote_GetNodeInfo(self.connect_id)
            speed = random.expovariate(3.0)
            angle = random.uniform(0.0, 2.0 * math.pi)
            self.speed = (speed * math.cos(angle), speed * math.sin(angle))
#             print "decide speed=%f angle=%f" % (speed, angle)
        if self.alive:
            duration = abs(random.normalvariate(self.decide_period_avg, self.decide_period_avg / 2.0))
            self.caller.CallLater(duration, self._Decide)

    def _Update(self):
        if self.ready:
            node_info = self.remote_control.remote_GetNodeInfo(self.connect_id)
            ar = node_info.awareness_radius
            (x, y, z) = node_info.position
            (vx, vy) = self.speed
            (tick, elapsed) = self.timer.Read()
            x += vx * ar
            y += vy * ar
            self.remote_control.remote_Move(self.connect_id, x, y, z)

    def _OnEvents(self, events):
        for t, request, args in events:
            if request == 'STATUS':
                self.ready = (args == 'READY')
                self.timer.Reset()
        if self.alive:
            self._AskEvents()

    def _AskEvents(self):
        d = self.remote_control.remote_GetEvents(self.connect_id)
        d.addCallback(self._OnEvents)
