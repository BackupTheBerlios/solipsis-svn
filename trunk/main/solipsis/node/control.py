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

import sha
import random
import time
try:
    set
except:
    from sets import Set as set

from twisted.internet import defer

from solipsis.util.exception import *
from solipsis.util.entity import Entity, Service, ServiceData
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

    min_notif_delay = 0.050
    max_notif_delay = 4.0
    connection_timeout = 60.0

    def __init__(self, reactor, params, state_machine):
        self.reactor = reactor
        self.params = params
        self.state_machine = state_machine
        self.caller = DelayedCaller(self.reactor)

        # (connect_id -> Connection) dictionnary
        self.connections = {}
        # (connect_id -> Deferred) dictionnary
        self.pending_notifs = {}


    #
    # Remotely callable methods
    #
    def remote_Connect(self):
        """
        Connect to the node. Returns a connect ID.
        """
        connect_id = self._CreateConnection()
        return connect_id

    def remote_Disconnect(self, connect_id):
        """
        Disconnect from the node. Invalidates the connect ID.
        """
        self._CheckConnectId(connect_id)
        self._CloseConnection(connect_id)
        return True

    def remote_Quit(self, connect_id):
        """
        Kills the node and quits the main program.
        Allowed only if the process hosts a single node.
        """
        self._CheckConnectId(connect_id)
        self._CloseConnection(connect_id)
        if self.params.pool:
            return False

        # We cannot call self.reactor.stop synchronously,
        # since we must first return the method result over the network.
        def _shutdown():
            self.reactor.stop()
        self.reactor.callLater(1.0, _shutdown)
        return True

    def remote_GetEvents(self, connect_id):
        """
        Get a list of events since last call (or since the beginning of
        the connection if this is the first call).
        This function takes a variable time to send its result,
        as it tries to minimize the number of round-trips.
        """
        self._CheckConnectId(connect_id)
        c = self.connections[connect_id]
        d = defer.Deferred()

        def _register():
            self.pending_notifs[connect_id] = d
            self._SendNotifs(connect_id)
        def _timeout():
            self._SendNotifs(connect_id, force=True)

        c.caller.CallLater(self.min_notif_delay, _register)
        c.caller.CallLater(self.max_notif_delay, _timeout)
        return d

    def remote_GetAllPeers(self, connect_id):
        """
        Get a list of all our peers.
        """
        self._CheckConnectId(connect_id)
        peers = self.state_machine.GetAllPeers()
        return [p.ToStruct() for p in peers]

    def remote_GetNodeInfo(self, connect_id):
        """
        Get information about the node.
        """
        self._CheckConnectId(connect_id)
        node = self.state_machine.node
        return node.ToStruct()

    def remote_GetStatus(self, connect_id):
        """
        Get current connection status.
        """
        self._CheckConnectId(connect_id)
        return self.state_machine.GetStatus()

    def remote_Move(self, connect_id, x, y, z):
        """
        Move to another position in the world.
        """
        self._CheckConnectId(connect_id)
        x = float(x)
        y = float(y)
        z = float(z)
        self.state_machine.MoveTo((x, y, z))
        return True

    def remote_SetNodeInfo(self, connect_id, node_info):
        """
        Change node information (only for metadata, the rest is ignored).
        """
        self._CheckConnectId(connect_id)
        node = Entity.FromStruct(node_info)
        self.state_machine.ChangeMeta(node)
        return True

    def remote_SendServiceData(self, connect_id, struct_):
        """
        Send service data to another peer.
        """
        self._CheckConnectId(connect_id)
        d = ServiceData.FromStruct(struct_)
        self.state_machine.SendServiceData(d.peer_id, d.service_id, d.data)
        return True

    #
    # Events
    #
    def event_ChangedPeer(self, peer):
        self._AddNotif("CHANGED", peer.ToStruct())

    def event_NewPeer(self, peer):
        self._AddNotif("NEW", peer.ToStruct())

    def event_LostPeer(self, peer_id):
        self._AddNotif("LOST", peer_id)

    def event_StatusChanged(self, status):
        self._AddNotif("STATUS", status)

    def event_ServiceData(self, peer_id, service_id, data):
        service_data = ServiceData(peer_id, service_id, data)
        self._AddNotif("SERVICEDATA", service_data.ToStruct())

    #
    # Private methods
    #
    def _CreateConnection(self):
        """
        Creates a connection to a controller.
        """
        connect_id = self._NewConnectId()
        self.connections[connect_id] = Connection(self.reactor)
        def _timeout():
            print "RemoteControl: connection timeout", connect_id
            self._CloseConnection(connect_id)
        self.caller.CallLaterWithId('timeout_' + connect_id, self.connection_timeout, _timeout)
        self.state_machine.EnableServices()
        return connect_id

    def _CloseConnection(self, connect_id):
        """
        Closes the connection to a controller.
        """
        self.caller.CancelCall('timeout_' + connect_id)
        if connect_id in self.pending_notifs:
            self._SendNotifs(connect_id, force=True)
        self.connections[connect_id].Reset()
        del self.connections[connect_id]
        if not len(self.connections):
            self.state_machine.DisableServices()

    def _CheckConnectId(self, connect_id):
        """
        Checks whether the connect_id is a valid one.
        """
        if connect_id not in self.connections:
            raise UnauthorizedRequest()
        self.caller.RescheduleCall('timeout_' + connect_id)

    def _NewConnectId(self):
        """
        Creates a new connection ID.
        """
        nbytes = 20
        try:
            r = random.getrandbits(nbytes * 8)
        except AttributeError:
            # Alternate method for Python < 2.4
            r = random.randrange(2 ** (nbytes * 8))
        s = ''
        for i in xrange(nbytes):
            s += chr(r & 0xFF)
            r >>= 8
        return sha.new(s).hexdigest()

    def _AddNotif(self, request, payload):
        """
        Adds a notification to all event queues.
        """
        t = time.time()
        for c in self.connections.itervalues():
            c.notifs.append((t, request, payload))
        # Send notifications
        for connect_id in self.pending_notifs.keys():
            self._SendNotifs(connect_id)

    def _SendNotifs(self, connect_id, force=False):
        """
        Sends all pending notifications to a peer.
        """
        c = self.connections[connect_id]
        if force or len(c.notifs):
            d = self.pending_notifs[connect_id]
            notifs, c.notifs = c.notifs, []
            del self.pending_notifs[connect_id]
            c.caller.Reset()
            d.callback(notifs)
