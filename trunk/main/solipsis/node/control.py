
import sha
import random
try:
    set
except:
    from sets import Set as set

from twisted.internet import defer

from solipsis.util.exception import *
from delayedcaller import DelayedCaller


class RemoteControl(object):
    def __init__(self, reactor, params, state_machine):
        self.reactor = reactor
        self.params = params
        self.state_machine = state_machine
        self.caller = DelayedCaller(self.reactor)
        self.connections = set()
#         self.notif_lists = {}
#         self.notif_count = 0
#
#         self.cnt = 0
#         def _fill():
#             self.cnt += 1
#             for l in self.notif_lists.itervalues():
#                 l.append(self.cnt)
#         self.caller.CallPeriodically(0.5, _fill)


    #
    # Remotely callable methods
    #
    def remote_Connect(self):
        connect_id = self._NewConnectId()
        self.connections.add(connect_id)
        return connect_id

    def remote_Disconnect(self, connect_id):
        self._CheckConnectId(connect_id)
        self.connections.remove(connect_id)
        return True

    def remote_Move(self, connect_id, x, y, z):
        self._CheckConnectId(connect_id)
        x = float(x)
        y = float(y)
        z = float(z)
        print "Move received", x, y, z
        self.state_machine.MoveTo((x, y, z))
        return True

    def remote_Die(self, connect_id):
        self._CheckConnectId(connect_id)
        print "Die received"
        self.notif_count += 1
        notif_id = self.notif_count
        d = defer.Deferred()

        def _get():
            result = self.notif_lists.pop(notif_id)
            print "-> die callback"
            d.callback(result)

        self.caller.CallLaterWithId(notif_id, 3.0, _get)
        self.notif_lists[notif_id] = []
        return True


    #
    # Private methods
    #
    def _CheckConnectId(self, connect_id):
        if connect_id not in self.connections:
            raise UnauthorizedRequest()

    def _NewConnectId(self):
        nbytes = 20
        r = random.getrandbits(nbytes * 8)
        s = ''
        for i in xrange(nbytes):
            s += chr(r & 0xFF)
            r >>= 8
        return sha.new(s).hexdigest()
