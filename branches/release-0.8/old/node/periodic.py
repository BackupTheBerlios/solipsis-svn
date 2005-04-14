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
import threading
import time
import logging

from event import EventFactory
from peerevent import PeerEvent
from solipsis.util.memdebug import MemSizer

class PeriodicExecutor(threading.Thread):
    def __init__(self, interval, func, params):
        """ execute func(params) every 'interval' seconds """
        self.isCancelled = False
        self.func = func
        self.params = params
        self.interval = interval
        threading.Thread.__init__(self, name = "PeriodicExecutor")
        self.setDaemon(1)

    def run(self):
        while not self.isCancelled:
            time.sleep(self.interval)
            apply(self.func, self.params)

    def cancel(self):
        self.isCancelled = True


class Heartbeat(PeriodicExecutor):
    # heartbeat timeout
    Timeout = 100

    def __init__(self, node):
        super(Heartbeat, self).__init__(Heartbeat.Timeout, self.OnHeartbeat, [node])

    def OnHeartbeat(self, node):
        """ Heartbeat function : send an heartbeat to all peers

        node : the node that is going to send heartbeat
        """
        factory = EventFactory.getInstance(PeerEvent.TYPE)
        hb = factory.createHEARTBEAT()

        # send heartbeat to all our peers
        for p in node.getPeersManager().enumeratePeers():
            hb.setRecipientAddress(p.getAddress())
            node.dispatch(hb)


class Memdump(PeriodicExecutor):
    # memdump timeout
    Timeout = 30

    def __init__(self):
        super(Memdump, self).__init__(self.Timeout, self.OnMemdump, [])
        self.sizer = MemSizer()
        self.sizer.sizeall()

    def OnMemdump(self):
        self.sizer.sizeall()
#         print "\n... Memstat ...\n"
#         print "\n".join(self.sizer.get_sizes()) + "\n"
        print "... Memdiff ..."
        print "\n".join(self.sizer.get_deltas()) + "\n"
        import gc
        print "... Summary ..."
        print "%d objects managed by the GC\n" % len(gc.get_objects())

