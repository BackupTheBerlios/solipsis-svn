# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>

import random
import math

from solipsis.util.entity import Entity
from solipsis.util.timer import AutoTimer
from delayedcaller import DelayedCaller


class Controller(object):
    """
    walker.Controller is a special controller that periodically moves the
    node in the world by a random amount.
    """
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
        """
        Start behaviour.
        """
        self.alive = True
        self.timer = AutoTimer()
        self.connect_id = self.remote_control.remote_Connect()
        self._AskEvents()
        self._Decide()
        period = self.update_period * (1.0 + random.normalvariate(0.0, 0.2))
        self.caller.CallPeriodically(period, self._Update)

    def Stop(self):
        """
        Stop behaviour.
        """
        self.alive = False
        self.caller.Reset()
#         self.remote_control.remote_Disconnect(self.connect_id)

    def _Decide(self):
        if self.ready:
            speed = random.expovariate(3.0)
            angle = random.uniform(0.0, 2.0 * math.pi)
            self.speed = (speed * math.cos(angle), speed * math.sin(angle))
        if self.alive:
            duration = abs(random.normalvariate(self.decide_period_avg, self.decide_period_avg / 2.0))
            self.caller.CallLater(duration, self._Decide)

    def _Update(self):
        """
        Update the node's position.
        We only move if the node is in a stable state.
        """
        if self.ready:
            node = Entity.FromStruct(self.remote_control.remote_GetNodeInfo(self.connect_id))
            ar = node.awareness_radius
            (x, y, z) = node.position.GetXYZ()
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
