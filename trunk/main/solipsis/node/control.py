
import sha
import random
import time
try:
    set
except:
    from sets import Set as set

from twisted.internet import defer

from solipsis.util.exception import *
from solipsis.util import marshal
from delayedcaller import DelayedCaller


class Connection(object):
    def __init__(self, reactor):
        self.caller = DelayedCaller(reactor)
        self.notifs = []

    def Reset(self):
        self.caller.Reset()


class RemoteControl(object):
    """
    The RemoteControl is the object normally used to control the node.
    Its "remote_Foo" methods can be called by an XML-RPC listener, a
    SOAP listener, a local behaviour automaton, or anything else.
    """

    # TODO: handle timeouts

    min_notif_delay = 0.050
    max_notif_delay = 4.0

    def __init__(self, reactor, params, state_machine):
        self.reactor = reactor
        self.params = params
        self.state_machine = state_machine
        self.caller = DelayedCaller(self.reactor)

        # (connect_id -> Connection) dictionnary
        self.connections = {}
        # (connect_id -> Deferred) dictionnary
        self.pending_notifs = {}

#         self.cnt = 0
#         def _fill():
#             self.cnt += 1
#             self._AddNotif('PING', self.cnt)
#         self.caller.CallPeriodically(1.0, _fill)
#
#         connect_id = self.remote_Connect()
#         def _test_notif(f):
#             print "asked notif"
#             defer.maybeDeferred(self.remote_GetEvents, connect_id).addCallback(f)
#         def _test_result(notif):
#             print "\n".join([str(n) for n in notif])
#             self.caller.CallLater(random.random() * 2.5, _test_notif, _test_result)
#         self.caller.CallLater(2.0, _test_notif, _test_result)

    #
    # Remotely callable methods
    #
    def remote_Connect(self):
        """
        Connect to the node. Returns a connect ID.
        """
        connect_id = self._NewConnectId()
        self.connections[connect_id] = Connection(self.reactor)
        return connect_id

    def remote_Disconnect(self, connect_id):
        """
        Disconnect from the node. Invalidates the connect ID.
        """
        self._CheckConnectId(connect_id)
        if connect_id in self.pending_notifs:
            self._SendNotifs(connect_id, force=True)
        self.connections[connect_id].Reset()
        del self.connections[connect_id]
        return True

    def remote_GetEvents(self, connect_id):
        """
        Get a list of events since last call (or since the beginning of
        the connection if this is the first call).
        This function takes a variable time to send its result,
        as we try to minimize the number of round-trips.
        """
        self._CheckConnectId(connect_id)
        c = self.connections[connect_id]
        d = defer.Deferred()
        print "GetEvents", connect_id

        def _register():
            self.pending_notifs[connect_id] = d
            self._SendNotifs(connect_id)
        def _timeout():
            self._SendNotifs(connect_id, force=True)

        c.caller.CallLater(self.min_notif_delay, _register)
        c.caller.CallLater(self.max_notif_delay, _timeout)
        return d

    def remote_Move(self, connect_id, x, y, z):
        """
        Move to another position in the world.
        """
        self._CheckConnectId(connect_id)
        x = float(x)
        y = float(y)
        z = float(z)
        print "Move received", x, y, z
        self.state_machine.MoveTo((x, y, z))
        return True

    #
    # Events
    #
    def event_NewPeer(self, peer):
        peer_info = marshal.PeerInfo()
        peer_info.FromPeer(peer)
        self._AddNotif("NEW", peer_info.ToStruct())

    def event_LostPeer(self, peer_id):
        self._AddNotif("LOST", peer_id)


    #
    # Private methods
    #
    def _AddNotif(self, request, payload):
        """
        Add a notification.
        """
        t = time.time()
        for c in self.connections.itervalues():
            c.notifs.append((t, request, payload))
        # Send notifications
        for connect_id in self.pending_notifs.keys():
            self._SendNotifs(connect_id)

    def _CheckConnectId(self, connect_id):
        """
        Check whether the connect_id is a valid one.
        """
        if connect_id not in self.connections:
            raise UnauthorizedRequest()

    def _NewConnectId(self):
        """
        Create a new connection ID.
        """
        nbytes = 20
        r = random.getrandbits(nbytes * 8)
        s = ''
        for i in xrange(nbytes):
            s += chr(r & 0xFF)
            r >>= 8
        return sha.new(s).hexdigest()

    def _SendNotifs(self, connect_id, force=False):
        """
        Send all pending notifications to a peer.
        """
        c = self.connections[connect_id]
        if force or len(c.notifs):
            d = self.pending_notifs[connect_id]
            notifs, c.notifs = c.notifs, []
            del self.pending_notifs[connect_id]
            c.caller.Reset()
            d.callback(notifs)
