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

import sys
import math
import random
import time

from solipsis.util.utils import set
from solipsis.util.exception import *
from solipsis.util.position import Position
from solipsis.util.address import Address
from peer import Peer
import protocol
import states
from topology import Topology
from delayedcaller import DelayedCaller


class StateMachine(object):
    """
    Finite State Machine of the Solipsis protocol.
    This is where all the interesting stuff happens.
    """
    world_size = 2**128

    # It is safer not to set this greater than 1
    teleportation_flood = 1
    neighbour_tolerance = 0.3
    peer_neighbour_ratio = 1.8

    # Various retry delays
    scanning_period = 4.0
    connecting_period = 4.0
    early_connecting_period = 3.0
    gc_check_period = 4.0
    population_check_period = 5.0

    # Various timeouts
    gc_trials = 3
    locating_timeout = 5.0
    early_connecting_trials = 3
    locating_trials = 3
    scanning_trials = 3
    connecting_trials = 3

    # Hold time
    # With local nodes, we choose a very long timeout which enables us
    # to minimize the number of HEARTBEAT messages in a mass-hosting setup
    minimum_hold_time = 30
    local_hold_time = 1200
    remote_hold_time = 30
    
    # Various delays
    hello_dampening = 3.0
    meta_change_delay = 0.5

    # Time during which we request to send detects on a HELLO
    # after having moved
    move_duration = 3.0


    # These are all the message types accepted from other peers.
    # Some of them will only be accepted in certain states.
    # The motivation is twofold:
    # - we don't want to answer certain queries if our answer may be false
    # - we don't want to process answers to questions we didn't ask
    accepted_peer_messages = {
        'AROUND':       [states.Scanning, states.Connecting],
        'BEST':         [states.Locating, states.Scanning],
        'CONNECT':      [],
        'CLOSE':        [],
        'DETECT':       [],
        'FINDNEAREST':  [states.Scanning, states.Connecting, states.Idle, states.LostGlobalConnectivity],
        'FOUND':        [],
        'HEARTBEAT':    [],
        'HELLO':        [],
        'JUMPNEAR':     [],
        'META':         [],
        'NEAREST':      [states.Locating, states.Scanning],
        'QUERYAROUND':  [states.Connecting, states.Idle, states.LostGlobalConnectivity],
        'QUERYMETA':    [],
        'QUERYSERVICE': [],
        'SEARCH':       [states.Connecting, states.Idle, states.LostGlobalConnectivity],
        'SERVICEDATA':  [],
        'SERVICEINFO':  [],
        'SUGGEST':      [],
        'UPDATE':       [],
    }

    def __init__(self, reactor, params, node, logger):
        """
        Initialize the state machine.
        """
        self.reactor = reactor
        self.params = params
        self.node = node
        self.topology = Topology()
        self.logger = logger
        self.parser = protocol.Parser()

        # Expected number of neighbours (in awareness radius)
        self.expected_neighbours = params.expected_neighbours
        self.min_neighbours = int(round((1.0 - self.neighbour_tolerance) * self.expected_neighbours))
        self.max_neighbours = int(round((1.0 + self.neighbour_tolerance) * self.expected_neighbours))
        # Max number of connections (total)
        self.max_connections = int(self.expected_neighbours * self.peer_neighbour_ratio)

        self.caller = DelayedCaller(self.reactor)
        self.peer_sender = None
        # Dispatch tables
        self.peer_dispatch_cache = {}
        self.state_dispatch = {}

        # Statistics
        self.received_messages = {}
        self.sent_messages = {}

        self.Reset()

    def Reset(self):
        self.state = None
        self.peer_dispatch = {}

        self.moved = False
        # Id's of the peers encountered during a FINDNEAREST chain
        self.nearest_peers = set()
        # "Future" values used when executing a far jump (FINDNEAREST)
        self.future_topology = None
        self.future_position = None
        # BEST peer discovered at the end of a FINDNEAREST chain
        self.best_peer = None
        self.best_distance = 0.0
        # Address of peer we asked a JUMPNEAR
        self.jump_near_address = None

        # Delayed calls
        self.peer_timeouts = {}
        self.peer_updates = {}
        self.caller.Reset()
        
        # For each address, this is the timestamp of the last HELLO attempt
        self.last_hellos = {}

        self.topology.Reset(origin=self.node.position.GetXY())

    def Init(self, peer_sender, event_sender, bootup_addresses):
        """
        Initialize the state machine. This is mandatory.
        """
        self.peer_sender = peer_sender
        self.event_sender = event_sender
        self.bootup_addresses = bootup_addresses

    def Close(self):
        """
        Close all connections and finalize stuff.
        """
        self._CloseCurrentConnections()
        self.Reset()

    def SetState(self, state):
        """
        Change the current state of the state machine.
        The 'state' parameter must be an instance of one
        of the State subclasses.
        """
        old_state = self.state
        self.state = state
        _class = state.__class__
        try:
            self.peer_dispatch = self.peer_dispatch_cache[_class]
        except KeyError:
            # Here we build a cache for dispatching peer messages
            # according to the current state.
            d = {}
            # We restrict message types according both to:
            # 1. expected messages in the given state
            # 2. accepted states for the given message type
            try:
                messages = state.expected_peer_messages
            except AttributeError:
                messages = self.accepted_peer_messages.keys()
            for request in messages:
                l = self.accepted_peer_messages[request]
                if len(l) == 0 or _class in l:
                    d[request] = getattr(self, 'peer_' + request)
            self.peer_dispatch = d
            self.peer_dispatch_cache[_class] = d
        if _class != old_state.__class__:
            # Discard old timers
            self.caller.Reset()
            # Call state initialization function
            try:
                func = self.state_dispatch[_class]
            except KeyError:
                func = getattr(self, 'state_' + _class.__name__, None)
                self.state_dispatch[_class] = func
            if func is not None:
                func()
            # Notify controller(s)
            self.event_sender.event_StatusChanged(self.GetStatus())

    def InState(self, state_class):
        """
        Returns True if the current state is an instance of the given class.
        """
        return isinstance(self.state, state_class)

    def PeerMessageReceived(self, request, args):
        """
        Called by the network routines when a proper Solipsis message is received.
        """
        try:
            func = self.peer_dispatch[request]
        except KeyError:
            self.logger.info("Ignoring unexpected message '%s' in state '%s'" % (request, self.state.__class__.__name__))
        else:
            func(args)
            try:
                self.received_messages[request] += 1
            except KeyError:
                self.received_messages[request] = 1
            # Heartbeat handling
            try:
                id_ = args.id_
            except AttributeError:
                pass
            else:
                if id_ in self.peer_timeouts:
                    self.peer_timeouts[id_].RescheduleCall('msg_receive_timeout')

    def DumpStats(self):
        requests = self.sent_messages.keys()
        requests.extend([k for k in self.received_messages.keys() if k not in requests])
        requests.sort()
        self._Verbose("\n... Message statistics ...")
        for r in requests:
            self._Verbose("%s: %d sent, %d received" % (r, self.sent_messages.get(r, 0), self.received_messages.get(r, 0)))


    #
    # Methods called when a new state is entered
    #
    def state_NotConnected(self):
        self._Verbose("not connected")

    def state_Locating(self):
        self._Verbose("locating")

        self.best_peer = None

        def _restart():
            self.SetState(states.NotConnected())
            self.TryConnect()

        self.caller.CallLaterWithId('locating_timeout', self.locating_timeout, _restart)

    def state_Scanning(self):
        self._Verbose("scanning")

        def _restart():
            self._Jump(self.future_position)
        def _retry():
            # Resend a QUERYAROUND message to all future peers
            message = self._PeerMessage('QUERYAROUND', future=True)
            message.args.best_id = self.best_peer.id_
            message.args.best_distance = self.best_distance
            for p in self.future_topology.EnumeratePeers():
                self._SendToPeer(p, message)

        self.caller.CallPeriodically(self.scanning_period, _retry)
        self.caller.CallLater(self.scanning_period * self.scanning_trials, _restart)

    def state_EarlyConnecting(self):
        self._Verbose("early connecting")

        def _restart():
            self.SetState(states.NotConnected())
            self.TryConnect()

        def _check_gc():
            # Periodically check global connectivity
            if self.topology.HasGlobalConnectivity():
                self.SetState(states.Idle())
            else:
                self._Verbose("(still connecting)")

        self.caller.CallPeriodically(self.early_connecting_period, _check_gc)
        self.caller.CallPeriodically(self.early_connecting_period * self.early_connecting_trials, _restart)

    def state_Connecting(self):
        self._Verbose("connecting")

        def _restart():
            self._Jump(self.future_position)

        def _check():
            if self.topology.HasGlobalConnectivity():
                self.future_topology = None
                self.future_position = None
                self.best_peer = None
                self.best_distance = 0.0
                self.SetState(states.Idle())
        def _retry():
            # Resend a HELLO message to all future peers
            self._Verbose("(still connecting)")
            peers = self.topology.PeersSet()
            for p in self.future_topology.EnumeratePeers():
                if p not in peers:
                    self._SayHello(p.address)

        self.caller.CallPeriodically(1.0, _check)
        self.caller.CallPeriodically(self.connecting_period, _retry)
        self.caller.CallLater(self.connecting_period * self.connecting_trials, _restart)

    def state_Idle(self):
        self._Verbose("idle")

        def _check_gc():
            # Periodically check global connectivity
            if not self.topology.HasGlobalConnectivity():
                self.SetState(states.LostGlobalConnectivity())

        self.caller.CallPeriodically(self.gc_check_period, _check_gc)
        self._CheckNumberOfPeers()
        self.caller.CallPeriodically(self.population_check_period, self._CheckNumberOfPeers)

    def state_LostGlobalConnectivity(self):
        self._Verbose("lost global connectivity")

        def _restart():
            self._Jump()

        def _check_gc():
            # Periodically check global connectivity
            if self.topology.GetNumberOfPeers() == 0:
                self._Jump()

            pair = self.topology.GetBadGlobalConnectivityPeers()
            if not pair:
                self.SetState(states.Idle())
            else:
                # Send search message to each entity
                message1 = self._PeerMessage('SEARCH')
                message1.args.clockwise = False
                message2 = self._PeerMessage('SEARCH')
                message2.args.clockwise = True
                self._SendToPeer(pair[0], message1)
                self._SendToPeer(pair[1], message2)

        _check_gc()
        self.caller.CallPeriodically(self.gc_check_period, _check_gc)
        self.caller.CallLater(self.gc_check_period * self.gc_trials, _restart)


    #
    # Methods called when a message is received from a peer
    #
    def peer_HELLO(self, args):
        """
        A new peer is contacting us.
        """
        peer = self._Peer(args)
        peer.hold_time = args.hold_time
        topology = self.topology

        # Check if we want to accept peer as a neighbour
        if peer.hold_time < self.minimum_hold_time or not self._AcceptPeer(peer):
            # Refuse connection
            self._SendToPeer(peer, self._PeerMessage('CLOSE'))
        else:
            if topology.HasPeer(peer.id_):
                # If we are already connected, update characteristics
                self.logger.info("HELLO from '%s', but we are already connected" % peer.id_)
                if self._SayConnect(peer):
                    self._UpdatePeer(peer)
                else:
                    self._RemovePeer(peer.id_)
            elif self._SayConnect(peer):
                # If it's a new peer, add it and notify it of neighbours
                self._AddPeer(peer)
                if args.send_detects:
                    self._SendDetects(peer)

    def peer_CONNECT(self, args):
        """
        A peer accepts our connection proposal.
        """
        # TODO: check that we sent a HELLO message to this peer
        peer = self._Peer(args)
        peer.hold_time = args.hold_time
        topology = self.topology

        # The proposed hold time is too small
        if peer.hold_time < self.minimum_hold_time:
            # Refuse connection
            self._SendToPeer(peer, self._PeerMessage('CLOSE'))

        if not topology.HasPeer(peer.id_):
            self._AddPeer(peer)
        else:
            self.logger.info("reception of CONNECT but we are already connected to '%s'" % peer.id_)
        self._QueryMeta(peer)

    def peer_CLOSE(self, args):
        """
        A peer closes or refuses a connection.
        """
        id_ = args.id_
        topology = self.topology

        if not topology.HasPeer(id_):
            self.logger.info('CLOSE from %s, but we are not connected' % id_)
            return

        self._RemovePeer(id_)

    def peer_QUERYMETA(self, args):
        """
        A peer queries our metadata and sends its own.
        """
        id_ = args.id_
        if self.topology.HasPeer(id_):
            peer = self.topology.GetPeer(id_)
            self._UpdatePeerMeta(peer, args)
            self._SendMeta(peer)

    def peer_META(self, args):
        """
        A peer sends or updates its metadata.
        """
        id_ = args.id_
        if self.topology.HasPeer(id_):
            peer = self.topology.GetPeer(id_)
            self._UpdatePeerMeta(peer, args)
            self._SendServices(peer, 'QUERYSERVICE')

    def peer_QUERYSERVICE(self, args):
        """
        A peer queries information about a service and sends its own.
        """
        id_ = args.id_
        service_id = args.service_id
        if self.topology.HasPeer(id_):
            peer = self.topology.GetPeer(id_)
            self._UpdatePeerService(peer, args)
            # Find our own service and send info about it
            service = self.node.GetService(service_id)
            if service is not None:
                self._SendService(peer, service, 'SERVICEINFO')

    def peer_SERVICEINFO(self, args):
        """
        A peer sends or updates information about a service.
        """
        id_ = args.id_
        service_id = args.service_id
        if self.topology.HasPeer(id_):
            peer = self.topology.GetPeer(id_)
            self._UpdatePeerService(peer, args)

    def peer_SERVICEDATA(self, args):
        """
        A peer sends us some service-specific data.
        """
        id_ = args.id_
        service_id = args.service_id
        if self.node.GetService(service_id) is not None:
            self.event_sender.event_ServiceData(id_, service_id, args.payload)

    def peer_NEAREST(self, args):
        """
        A peer answers us a NEAREST message.
        """
        id_ = args.remote_id
        # Loop detection
        if id_ in self.nearest_peers:
            self.logger.warning("Already encountered peer '%s' in FINDNEAREST algorithm: %s"
                    % (str(id_), ", ".join(["'" + str(i) + "'" for i in self.nearest_peers])))
            return
        # Check we do not already have a better candidate
        if self.best_peer is not None:
            if id_ == self.best_peer.id_:
                self.logger.info("NEAREST received, but proposed is already our best")
                return
            elif (self.best_distance <= self.future_topology.RelativeDistance(args.remote_position.GetXY())):
                self.logger.info("NEAREST received, but proposed peer is farther than our current best")
                return

        self.nearest_peers.add(id_)
        address = args.remote_address
        self._SendToAddress(address, self._PeerMessage('FINDNEAREST', future=True))
        # We could come here from the Scanning procedure,
        # if a neighbour finds someone closer to us than our current BEST
        if self.InState(states.Scanning):
            self.SetState(states.Locating())
        # Endly, reinitialize timeout
        self.caller.RescheduleCall('locating_timeout')

    def peer_BEST(self, args):
        """
        A peer answers us a BEST message.
        """
        # Instantiate the best peer
        peer = self._Peer(args)
        assert self.future_topology is not None, "BEST received but we have no future topology!"
        distance = self.future_topology.RelativeDistance(peer.position.GetXY())

        # Store the best peer
        if self.best_peer is not None:
            if distance >= self.best_distance:
                self.logger.info("BEST received, but peer is farther than our current best")
                return

        self._Verbose("-> %d hops until BEST" % len(self.nearest_peers))
        self.best_peer = peer
        self.best_distance = distance
        self.nearest_peers.clear()
        self.future_topology.Reset()
        self.future_topology.AddPeer(peer)

        # Send a queryaround message
        message = self._PeerMessage('QUERYAROUND', future=True)
        message.args.best_id = peer.id_
        message.args.best_distance = distance
        self._SendToPeer(peer, message)

        #  We are now in the Scanning state
        self.SetState(states.Scanning())

    def peer_FINDNEAREST(self, args):
        """
        A peer sends us a FINDNEAREST query.
        """
        id_ = args.id_
        target = args.position.GetXY()
        address = args.address
        (nearest, nearest_distance) = self.topology.GetClosestPeer(target, id_)
        if nearest is None:
            return

        # Check whether I am closer to the target than nearestPeer
        our_distance = self.topology.RelativeDistance(target)
        if our_distance < nearest_distance:
            message = self._PeerMessage('BEST')
        # I'm closer : send a best message
        else:
            message = self._PeerMessage('NEAREST', remote_peer=nearest)

        # Send our answer
        self._SendToAddress(address, message)

    def peer_DETECT(self, args):
        """
        A peer signals another peer moving towards us.
        """
        peer = self._RemotePeer(args)
        id_ = peer.id_

        # Filter 1: don't connect with ourselves
        # (TODO: handle this case upstream)
        if id_ == self.node.id_:
            return
        # Filter 2: don't connect with someone too far from us
        distance = self.topology.RelativeDistance(peer.position.GetXY())
        if distance > self.node.awareness_radius:
            return

        # We are only interested by entities that are not yet in our peer list
        if not self.topology.HasPeer(id_):
            # Check we don't have too many peers, or have worse peers than this one
            if self._AcceptPeer(peer):
                # Connect to this peer
                self._SayHello(peer.address, send_detects=self.moved)

    def peer_AROUND(self, args):
        """
        A peer replies to us with an AROUND message.
        """
        peer = self._RemotePeer(args)
        assert self.future_topology is not None, "Processing an AROUND message but we have no future topology!"

        # Check whether we came back to our BEST peer
        already_best = (peer.id_ == self.best_peer.id_)
        if not already_best:
            if not self.future_topology.HasPeer(peer.id_):
                self.future_topology.AddPeer(peer)
            else:
                self.logger.info("The AROUND peer is already in the future topology, ignoring")
                return

        # Maybe we don't want to continue the Scanning algorithm
        if not self.InState(states.Scanning):
            return

        if self.future_topology.HasGlobalConnectivity():
            self._SwitchTopologies()
            self.SetState(states.Connecting())
            return

        if already_best:
            # Handled by timeouts
            self.logger.info("AROUND: we came back to our BEST but there is no global connectivity")
            return

        # Send this peer a queryaround message
        message = self._PeerMessage('QUERYAROUND', future=True)
        message.args.best_id = self.best_peer.id_
        message.args.best_distance = self.best_distance
        self._SendToPeer(peer, message)

    def peer_QUERYAROUND(self, args):
        """
        A peer sent us a QUERYAROUND message.
        """
        peer_id = args.id_
        best_id = args.best_id
        best_distance = args.best_distance
        target = args.position.GetXY()
        (nearest, nearest_distance) = self.topology.GetClosestPeer(target, peer_id)
        if nearest is None:
            return

        # Either:
        # 1. We have a peer closer to the target than the given Best
        if nearest.id_ != best_id and long(nearest_distance) < long(best_distance):
            self._Verbose("QUERYAROUND: ('%s', %f) is closer than best ('%s', %f)" % (nearest.id_, nearest_distance, best_id, best_distance))
            self._SendToAddress(args.address, self._PeerMessage('NEAREST', remote_peer=nearest))

        # 2. Or we find the closest peer around the target position and in the right half-plane
        else:
            # Search for a peer around target position
            around = self.topology.GetPeerAround(target, peer_id)
            if around is not None:
                self._SendToAddress(args.address, self._PeerMessage('AROUND', remote_peer=around))
            else:
                self.logger.info('QUERYAROUND received, but no peer around position: %s' % str(target))

    def peer_HEARTBEAT(self, args):
        """
        A peer reminds us it is alive.
        """
        pass

    def peer_UPDATE(self, args):
        """
        A peer notifies us it UPDATEs its characteristics.
        """
        peer = self._Peer(args)

        if not self.topology.HasPeer(peer.id_):
            self.logger.info('UPDATE from %s, but we are not connected' % peer.id_)
            return

        self._UpdatePeer(peer)

    def peer_FOUND(self, args):
        """
        A peer replies to us with a FOUND message.
        """
        id_ = args.remote_id
        address = args.remote_address

        # Verify that new entity is neither self neither an already known entity.
        if id_ == self.node.id_:
            self.logger.warning("FOUND message pointing to ourselves received")
        elif not self.topology.HasPeer(id_):
            self._SayHello(address)

    def peer_SEARCH(self, args):
        """
        A peer sends SEARCH queries around itself to restore its global connectivity.
        """
        id_ = args.id_
        clockwise = args.clockwise > 0

        try:
            peer = self.topology.GetPeer(id_)
        except UnknownIdError:
            self.logger.warning("Error, reception of SEARCH message from unknown peer '%s'" % str(id_))
            return

        around = self.topology.GetPeerAround(peer.position.GetXY(), id_, clockwise)

        # Send message if an entity has been found
        if around is not None:
            self._SendToPeer(peer, self._PeerMessage('FOUND', remote_peer=around))

    def peer_JUMPNEAR(self, args):
        """
        A peer asks a position suggestion around the node.
        """
        x, y = self.topology.SuggestPosition(self.node.awareness_radius)
        message = self._PeerMessage('SUGGEST')
        message.args.remote_position = Position((x, y, 0.0))
        self._SendToAddress(args.address, message)

    def peer_SUGGEST(self, args):
        """
        A peer answers a position suggestion in response to a JUMPNEAR message.
        """
        # Instantiate the target peer
        if self.jump_near_address is None or self.jump_near_address != args.address:
            self.logger.warning("Error, reception of unexpected SUGGEST message from peer '%s':\n%s != %s"
                % (str(args.id_), self.jump_near_address.ToString(), args.address.ToString()))
            return
        peer = self._Peer(args)
        self.jump_near_address = None

        # Really jump near the target peer
        self.future_topology = Topology()
        self.future_topology.SetOrigin(args.remote_position.GetXY())
        self.future_topology.AddPeer(peer)
        self.future_position = args.remote_position
        self._StartFindNearest(addresses=[args.address])


    #
    # Control events
    #
    def ChangeMeta(self, new_node):
        """
        Change our meta-information.
        """
        self.node.UpdateMeta(
            new_node.pseudo,
            new_node.languages,
            new_node.services.values())
        for peer in self.GetAllPeers():
            self._SendMeta(peer)

    def GetAllPeers(self):
        """
        Returns a list of all peers.
        """
        return self.topology.EnumeratePeers()

    def GetStatus(self):
        """
        Returns the connection status : READY, BUSY or UNAVAILABLE
        """
        if self.InState(states.Idle):
            return 'READY'
        elif self.InState(states.NotConnected):
            return 'UNAVAILABLE'
        else:
            return 'BUSY'

    def ImmediatelyConnect(self):
        """
        Immediately connect to bootup entities. This is only used
        for the first nodes when building the world.
        """
        self._CloseCurrentConnections()
        self.Reset()
        for host, port in self.bootup_addresses:
            self._SayHello(Address(host, port))
        self.SetState(states.EarlyConnecting())

    def TryConnect(self):
        """
        Try to connect to the world, picking some bootup entities
        at random and teleporting to our destination position.
        """
        self._CloseCurrentConnections()
        self.Reset()
        if len(self.bootup_addresses) > self.teleportation_flood:
            addresses = random.sample(self.bootup_addresses, self.teleportation_flood)
        else:
            addresses = self.bootup_addresses
        self._StartFindNearest([Address(host, port) for host, port in addresses])

    def MoveTo(self, (x, y, z)):
        """
        Move to a given absolute position in the world.
        """
        # Change position
        x %= self.world_size
        y %= self.world_size
        position = Position((x, y, z))
        old_position = self.node.position

        # Hackish: we first change the position to check the global connectivity,
        # then possibly set it back to its former value
        self.topology.SetOrigin((x, y))

        if self.topology.HasGlobalConnectivity():
            # We still have the global connectivity,
            # so we simply notify our peers of the position change
            self.node.position = position
            self.future_position = None
            # This handles the case when the user continues moving
            # while we are changing topologies
            if self.future_topology is not None:
                self.future_topology.SetOrigin((x, y))
            self._SendUpdates()
        else:
            # Otherwise, do a full-fledged teleport from the current position
            self.topology.SetOrigin(old_position.GetXY())
            self._Jump(position)

        # "self.moved" will be True during a few seconds
        self.moved = True
        def _finish():
            self.moved = False
        caller = DelayedCaller(self.reactor)
        caller.CallLater(self.move_duration, _finish)

    def JumpNear(self, address):
        """
        Try to jump near an existing entity.
        """
        message = self._PeerMessage('JUMPNEAR')
        self._SendToAddress(address, message)
        self.jump_near_address = address
    
    def SendServiceData(self, id_, service_id, data):
        """
        Send service-specific data to a peer.
        """
        if self.topology.HasPeer(id_):
            peer = self.topology.GetPeer(id_)
            message = self._PeerMessage('SERVICEDATA')
            message.args.service_id = service_id
            message.args.payload = data
            self._SendToPeer(peer, message)
    
    def DisableServices(self):
        self.node.DisableServices()
        for peer in self.GetAllPeers():
            self._SendMeta(peer)
    
    def EnableServices(self):
        self.node.EnableServices()
        for peer in self.GetAllPeers():
            self._SendMeta(peer)
    
    #
    # Private methods: add / remove peers
    #
    def _AddPeer(self, peer):
        """
        Add a peer and send the necessary notification messages.
        """
        if not self.topology.AddPeer(peer):
            self.logger.warning("sed peer '%s'" % peer.id_)
            return

        def msg_receive_timeout():
            self._Verbose("timeout (%s) => closing connection with '%s'" % (str(self.node.id_), str(peer.id_)))
            self._CloseConnection(peer)
        def msg_send_timeout():
            self._SendToPeer(peer, self._PeerMessage('HEARTBEAT'))

        # Notify remote control
        self.event_sender.event_NewPeer(peer)

        # Setup heartbeat handling callbacks
        caller = DelayedCaller(self.reactor)
        # Heuristic (a la BGP)
        keepalive = peer.hold_time / 3.0
        caller.CallPeriodicallyWithId('msg_receive_timeout', peer.hold_time, msg_receive_timeout)
        caller.CallPeriodicallyWithId('msg_send_timeout', keepalive, msg_send_timeout)
        self.peer_timeouts[peer.id_] = caller
        self.peer_updates[peer.id_] = DelayedCaller(self.reactor)

        self._CheckNumberOfPeers(check_ar=False)

    def _RemovePeer(self, id_):
        """
        Remove a peer and send the necessary notification messages.
        """
        self.peer_timeouts[id_].Reset()
        self.peer_updates[id_].Reset()
        del self.peer_timeouts[id_]
        del self.peer_updates[id_]
        self.topology.RemovePeer(id_)
        # Notify remote control
        self.event_sender.event_LostPeer(id_)

    def _AcceptPeer(self, peer):
        """
        True if peer is accepted as a potential neighbour.
        """
        if self.topology.GetNumberOfPeers() < self.max_connections:
            return True
        return not self.topology.IsWorstPeer(peer)

    def _CloseCurrentConnections(self, keep_peers=None):
        remove_ids = []
        for p in self.topology.EnumeratePeers():
            if keep_peers is None or p.id_ not in keep_peers:
                self._SendToPeer(p, self._PeerMessage('CLOSE'))
                remove_ids.append(p.id_)
        for id_ in remove_ids:
            self._RemovePeer(id_)

    def _CloseConnection(self, peer):
        self._SendToPeer(peer, self._PeerMessage('CLOSE'))
        self._RemovePeer(peer.id_)


    #
    # Teleportation algorithm
    #
    def _SwitchTopologies(self):
        """
        Called when finished teleporting.
        This function "commits" the future topology, notably by sending the
        necessary HELLO and CLOSE messages.
        """
        # Our awareness radius is the distance between us and our closest
        # neighbour, because we are "sure" to know all the entities between us
        # and the best.
        self.node.awareness_radius = self.best_distance
        self.node.position = self.future_position
        self.topology.SetOrigin(self.node.position.GetXY())

        new_peers = self.future_topology.PeersSet()
        old_peers = self.topology.PeersSet()

        #~ for p in self.future_topology.EnumeratePeers():
            #~ if p not in old_peers:
                #~ self._SayHello(p.address)

        # Close connections with peers that do not belong to the new topology
        self._CloseCurrentConnections(keep_peers=new_peers)
        
        # Notify remaining peers that our position has changed
        self._SendUpdates()

        # Try to connect with new peers
        for peer_id in new_peers - old_peers:
            self._SayHello(self.future_topology.GetPeer(peer_id).address)

        # Don't forget to notify our controller(s)
        #~ print self.node.position.GetXY()
        self.event_sender.event_Jumped(self.node.position)

    def _Jump(self, position=None):
        """
        Jump to the given position, or by default the node's current position.
        This triggers the recursive teleportation algorithm.
        """
        # Prefer future topology over current one
        topology = self.future_topology or self.topology
        addresses = [peer.address for peer in topology.GetNearestPeers(self.teleportation_flood)]
        if position is None:
            position = self.node.position
        self.future_position = position

        # Start teleportation algorithm
        if addresses:
            self._StartFindNearest(addresses)
        else:
            self.TryConnect()

    def _StartFindNearest(self, addresses):
        """
        Start the teleportation algorithm.
        """
        # Create future topology
        if self.future_position is None:
            self.future_position = self.node.position
        self.future_topology = Topology()
        self.future_topology.SetOrigin(self.future_position.GetXY())

        # Send FINDNEAREST to all selected addresses
        message = self._PeerMessage('FINDNEAREST', future=True)
        for address in addresses:
            self._SendToAddress(address, message)

        # Jump into the proper state
        self.SetState(states.Locating())


    #
    # Awareness radius management
    #
    def _UpdatePeer(self, new_peer):
        """
        Update a peer's characteristics.
        """
        topology = self.topology

        # Save old peer value and update
        peer = topology.GetPeer(new_peer.id_)

        old_pos = peer.position.GetXY()
        new_pos = new_peer.position.GetXY()
        old_ar = peer.awareness_radius
        new_ar = new_peer.awareness_radius

        # Update characteristics whilst keeping metadata
        peer.Update(new_peer)
        topology.UpdatePeer(peer)

        # Notify remote control
        self.event_sender.event_ChangedPeer(peer)

        # Peer position or awareness radius changed
        if new_pos != old_pos or new_ar != old_ar:
            # Verify entities that could be interested by the change
            for entity in topology.EnumeratePeers():
                if entity.id_ == peer.id_:
                    continue
                its_pos = entity.position.GetXY()
                its_ar = entity.awareness_radius

                our_dist = topology.RelativeDistance(its_pos)
                their_dist = topology.Distance(its_pos, new_pos)
                their_old_dist = topology.Distance(its_pos, old_pos)

                # Detection 1: the peer has entered an entity's awareness radius,
                # or it has become closer to the entity than us
                if their_dist <= its_ar < their_old_dist \
                    or their_dist <= our_dist < their_old_dist:
                    # The moving peer is signalled to the fixed entity
                    self._SendToPeer(entity, self._PeerMessage('DETECT', remote_peer=peer))

                # Detection 2: the entity has become part of the moving peer's awareness radius
                if old_ar < their_old_dist and new_ar >= their_dist:
                    # The entity is signalled to the moving peer
                    self._SendToPeer(peer, self._PeerMessage('DETECT', remote_peer=entity))


    def _SendUpdates(self):
        """
        Send updates to all peers.
        Called when some of our properties have changed (position, etc.).
        """
        message = self._PeerMessage('UPDATE')
        for peer in self.topology.EnumeratePeers():
            self._SendToPeer(peer, message)

    def _SendDetects(self, peer):
        """
        Send detect messages to a peer.
        This is called on the connection initialization.
        """
        # Hack to speed up world build
        position = peer.position.GetXY()
        radius = peer.awareness_radius
        for remote_peer in self.topology.GetPeersInCircle(position, radius):
            message = self._PeerMessage('DETECT', remote_peer=remote_peer)
            self._SendToPeer(peer, message)

    def _UpdateAwarenessRadius(self, ar):
        self.node.awareness_radius = ar
        self._SendUpdates()

    def _CheckNumberOfPeers(self, check_ar=True):
        """
        Check the current number of peers and optionally launch
        various actions so that it stays within the desired bounds.
        """
        topology = self.topology
        new_ar = ar = self.node.awareness_radius
        nb_peers = topology.GetNumberOfPeers()
        neighbours = topology.GetPeersWithinDistance(ar)
        nb_neighbours = len(neighbours)
        if nb_peers < 3:
            # This case is handled by the global connectivity check
            return

        if check_ar:
            # 1. Not enough neighbours in our awareness radius
            if nb_neighbours < self.min_neighbours:
                if nb_peers >= self.min_neighbours:
                    # +1% to avoid boundary/imprecision issues
                    new_ar = topology.GetEnclosingDistance(self.min_neighbours) * 1.01
                else:
                    # We assume areal density is roughly constant
                    d = topology.GetEnclosingDistance(nb_peers)
                    new_ar = max(d, ar) * math.sqrt(float(self.min_neighbours) / nb_peers)
                new_ar = min(new_ar, self.world_size)
            # 2. Too many neighbours in our awareness radius
            elif nb_neighbours > self.max_neighbours:
                new_ar = topology.GetEnclosingDistance(self.min_neighbours) * 1.01
        # 3. Too many connected peers outside of our awareness radius
        if nb_peers > self.max_connections:
            peers = self.topology.GetWorstPeers(nb_peers - self.max_neighbours, new_ar)
            for p in peers:
                self._CloseConnection(p)
        # Notify peers of our new awareness radius
        if new_ar != ar:
            self._UpdateAwarenessRadius(new_ar)

    def _NotifyPeerMeta(self, peer_id):
        """
        Notify peer metadata changes to the remote control.
        """
        def _notify():
            if self.topology.HasPeer(peer_id):
                peer = self.topology.GetPeer(peer_id)
                self.event_sender.event_ChangedPeer(peer)
        self.peer_updates[peer_id].Reset()
        self.peer_updates[peer_id].CallLater(self.meta_change_delay, _notify)

    def _UpdatePeerMeta(self, peer, args):
        """
        Update a peer's metadata from the incoming message's arguments.
        """
        peer.UpdateMeta(pseudo=args.pseudo,
            languages=args.accept_languages, 
            services=args.accept_services)
        # Notify remote control
        self._NotifyPeerMeta(peer.id_)

    def _UpdatePeerService(self, peer, args):
        """
        Update a service of a peer from the incoming message's arguments.
        """
        peer.UpdateServiceInfo(args.service_id, address=args.service_address)
        # Notify remote control
        self._NotifyPeerMeta(peer.id_)

    #
    # Protocol helpers
    #
    def _Peer(self, args):
        """
        Returns a Peer created from the given message arguments.
        """
        return Peer(
            address = args.address,
            awareness_radius = args.awareness_radius,
            id_ = args.id_,
            position = args.position,
            )

    def _RemotePeer(self, args):
        """
        Returns a Peer created from the given "Remote-*" message arguments.
        """
        return Peer(
            address = args.remote_address,
            awareness_radius = args.remote_awareness_radius,
            id_ = args.remote_id,
            position = args.remote_position,
            )

    def _PeerMessage(self, request, peer=None, remote_peer=None, future=False):
        """
        Builds a protocol message from the given peer(s).
        If 'future' is True, the future_position will be used instead of the current one.
        """
        if peer is None:
            peer = self.node
        message = protocol.Message(request)
        # Build message args from involved entities
        # TODO: rewrite this better
        a = message.args
        p = peer
        a.address = p.address
        a.awareness_radius = p.awareness_radius
        a.id_ = p.id_
        if future:
            a.position = self.future_position
        else:
            a.position = p.position
        if remote_peer:
            r = remote_peer
            a.remote_address = r.address
            a.remote_awareness_radius = r.awareness_radius
            a.remote_id = r.id_
            a.remote_position = r.position
        # Then remove unnecessary fields
        self.parser.StripMessage(message)
        return message

    def _FillMeta(self, message):
        a = message.args
        a.pseudo = self.node.pseudo
        a.accept_languages = self.node.GetLanguages()
        a.accept_services = self.node.GetServices()

    def _HoldTime(self, address):
        """
        Choose hold time depending on peer address.
        """
        if address.host == self.node.address.host:
            return self.local_hold_time
        else:
            return self.remote_hold_time

    def _SayHello(self, address, send_detects=False):
        """
        Say HELLO to a peer.
        """
        # TODO: manage repeted connection failures and
        # optionally cancel request (returning False)
        last = self.last_hellos.get(address, 0.0)
        now = time.time()
        if now - last > self.hello_dampening:
            self.last_hellos[address] = now
            #~ msg = self._PeerMessage('HELLO', future=self.future_position is not None)
            msg = self._PeerMessage('HELLO')
            msg.args.send_detects = send_detects
            msg.args.hold_time = self._HoldTime(address)
            self._SendToAddress(address, msg)
            return True
        return False

    def _SayConnect(self, peer):
        """
        Answer CONNECT to a peer.
        """
        # TODO: manage repeted connection failures and
        # optionally cancel request (sending CLOSE and
        # returning False)
        #~ msg = self._PeerMessage('CONNECT', future=self.future_position is not None)
        msg = self._PeerMessage('CONNECT')
        msg.args.hold_time = self._HoldTime(peer.address)
        self._SendToPeer(peer, msg)
        return True

    def _QueryMeta(self, peer):
        """
        Send our metadata to a peer.
        """
        msg = self._PeerMessage('QUERYMETA')
        self._FillMeta(msg)
        self._SendToPeer(peer, msg)
        return True

    def _SendMeta(self, peer):
        """
        Send our metadata to a peer.
        """
        msg = self._PeerMessage('META')
        self._FillMeta(msg)
        self._SendToPeer(peer, msg)
        return True

    def _SendService(self, peer, service, request='SERVICEINFO'):
        """
        Send service information to a peer.
        """
        message = self._PeerMessage(request)
        message.args.service_id = service.id_
        message.args.service_address = service.address
        self._SendToPeer(peer, message)

    def _SendServices(self, peer, request='SERVICEINFO'):
        """
        Send service information messages to a peer.
        The request can be either 'QUERYSERVICE' or 'SERVICEINFO'.
        """
        matched_services = self.node.MatchServices(peer)
        for service in matched_services:
            self._SendService(peer, service, request)

    def _SendToAddress(self, address, message):
        """
        Send a Solipsis message to a given address.
        """
        if self.peer_sender is None:
            self.logger.error("Attempting to send message but sender method is not initialized")
            return
        self.peer_sender(message=message, address=address)
        try:
            self.sent_messages[message.request] += 1
        except KeyError:
            self.sent_messages[message.request] = 1

    def _SendToPeer(self, peer, message):
        """
        Send a Solipsis message to a known peer.
        """
        if peer.id_ == self.node.id_:
            self.logger.error("we tried to send a message (%s) to ourselves" % message.request)
            return
        self._SendToAddress(peer.address, message)
        # Heartbeat handling
        try:
            id_ = message.args.id_
        except AttributeError:
            pass
        else:
            if id_ in self.peer_timeouts:
                self.peer_timeouts[id_].RescheduleCall('msg_send_timeout')

    #
    # Various stuff
    #
    def _Verbose(self, s):
        s += "\n"
        if not self.params.quiet:
            sys.stdout.write(s)
        self.logger.info(s)
