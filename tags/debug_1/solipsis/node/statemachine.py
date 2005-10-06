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
import os

from solipsis.util.compat import set
from solipsis.util.exception import *
from solipsis.util.position import Position
from solipsis.util.address import Address
from peer import Peer
from parser import Parser
import protocol
import states
from topology import Topology
from delayedcaller import DelayedCaller
from entitycache import EntityCache


class StateMachine(object):
    """
    Finite State Machine of the Solipsis protocol.
    This is where all the interesting stuff happens.
    """
    world_size = 2**128

    teleportation_flood = 4
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

    # Various delays
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
        'MIDDLEMAN':    [],
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
        self.parser = Parser()
        self.node_connector = None

        # Expected number of neighbours (in awareness radius)
        self.expected_neighbours = params.expected_neighbours
        self.min_neighbours = int(round((1.0 - self.neighbour_tolerance) * self.expected_neighbours))
        self.max_neighbours = int(round((1.0 + self.neighbour_tolerance) * self.expected_neighbours))
        # Max number of connections (total)
        self.max_connections = int(self.expected_neighbours * self.peer_neighbour_ratio)

        # Dispatch tables
        self.peer_dispatch_cache = {}
        self.state_dispatch = {}

        # Delayed calls
        self.caller = DelayedCaller(self.reactor)
        self.state_caller = DelayedCaller(self.reactor)

        # Entity cache for bootstrap
        self.entity_cache_file = os.path.join(params.state_dir, params.entities_file)
        self.entity_cache = EntityCache()
        self._LoadEntityCache()
        self.entity_chooser = None

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
        # Address of peer whom we asked a JUMPNEAR
        self.jump_near_address = None
        self.jump_near_position = None
        self.jump_near_expected_id = None

        # Delayed calls
        self.dc_locating_timeout = None
        self.meta_notify_ids = set()
        self.dc_meta_notify = None
        self.caller.Reset()
        self.state_caller.Reset()

        self.topology.Reset(origin=self.node.position.GetXY())

    def Init(self, node_connector, event_sender, bootup_addresses):
        """
        Initialize the state machine. This is mandatory.
        """
        self.node_connector = node_connector
        self.event_sender = event_sender
        self.entity_cache.SetDefaultEntities(bootup_addresses)
        self.entity_chooser = None

    def Close(self):
        """
        Close all connections and finalize stuff.
        """
        self._CloseCurrentConnections()
        self._SaveEntityCache()
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
            self.state_caller.Reset()
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

        self.dc_locating_timeout = self.state_caller.CallLater(self.locating_timeout, _restart)

    def state_Scanning(self):
        self._Verbose("scanning")

        def _restart():
            self._JumpToPosition(self.future_position)
        def _retry():
            # Resend a QUERYAROUND message to all future peers
            message = self._PeerMessage('QUERYAROUND', future=True)
            message.args.best_id = self.best_peer.id_
            message.args.best_distance = self.best_distance
            for p in self.future_topology.EnumeratePeers():
                self._SendToPeer(p, message)

        self.state_caller.CallPeriodically(self.scanning_period, _retry)
        self.state_caller.CallLater(self.scanning_period * self.scanning_trials, _restart)

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

        self.state_caller.CallPeriodically(self.early_connecting_period, _check_gc)
        self.state_caller.CallPeriodically(self.early_connecting_period * self.early_connecting_trials, _restart)

    def state_Connecting(self):
        self._Verbose("connecting")

        def _restart():
            self._JumpToPosition(self.future_position)

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
                    self._SayHello(p)

        self.state_caller.CallPeriodically(1.0, _check)
        self.state_caller.CallPeriodically(self.connecting_period, _retry)
        self.state_caller.CallLater(self.connecting_period * self.connecting_trials, _restart)

    def state_Idle(self):
        self._Verbose("idle")

        def _check_gc():
            # Periodically check global connectivity
            if not self.topology.HasGlobalConnectivity():
                self.SetState(states.LostGlobalConnectivity())

        self.state_caller.CallPeriodically(self.gc_check_period, _check_gc)
        self._CheckNumberOfPeers()
        self.state_caller.CallPeriodically(self.population_check_period, self._CheckNumberOfPeers)

    def state_LostGlobalConnectivity(self):
        self._Verbose("lost global connectivity")

        def _restart():
            self._JumpToPosition()

        def _check_gc():
            # Periodically check global connectivity
            if self.topology.GetNumberOfPeers() == 0:
                self._JumpToPosition()

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
        self.state_caller.CallPeriodically(self.gc_check_period, _check_gc)
        self.state_caller.CallLater(self.gc_check_period * self.gc_trials, _restart)


    #
    # Methods called when a message is received from a peer
    #
    def peer_HELLO(self, args):
        """
        A new peer is contacting us.
        """
        peer = Peer.FromArgs(args)
        topology = self.topology

        # Check if we want to accept peer as a neighbour
        if not self.node_connector.AcceptHandshake(peer) or not self._AcceptPeer(peer):
            # Refuse connection
            self._SayClose(peer)
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
        peer = Peer.FromArgs(args)
        topology = self.topology

        # Check if we want to accept peer as a neighbour
        if not self.node_connector.AcceptHandshake(peer) or not self._AcceptPeer(peer):
            # Refuse connection
            self._SayClose(peer)

        if not topology.HasPeer(peer.id_):
            self._AddPeer(peer)
        else:
            self.logger.info("reception of CONNECT but we are already connected to '%s'" % peer.id_)
            self._UpdatePeer(peer)
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
        peer = Peer.FromRemoteArgs(args)
        self._SendToPeer(peer, self._PeerMessage('FINDNEAREST', future=True))
        # We could come here from the Scanning procedure,
        # if a neighbour finds someone closer to us than our current BEST
        if self.InState(states.Scanning):
            self.SetState(states.Locating())
        # Endly, reinitialize timeout
        self.dc_locating_timeout.Reschedule()

    def peer_BEST(self, args):
        """
        A peer answers us a BEST message.
        """
        # Instantiate the best peer
        peer = Peer.FromArgs(args)
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
        if not self.future_topology.AddPeer(peer):
            # If we fail adding the peer, we are too close to it:
            # we must ask for a surrounding position
            self._JumpNearPeer(self.best_peer.address)

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
        peer = Peer.FromRemoteArgs(args)
        id_ = peer.id_

        # Filter 1: don't connect with ourselves
        if id_ == self.node.id_:
            return
        # Filter 2: don't connect with someone too far from us
        distance = self.topology.RelativeDistance(peer.position.GetXY())
        if distance > self.node.awareness_radius:
            return

        # We are only interested by entities that are not yet in our peer list
        if not self.topology.HasPeer(id_):
            # 1. Check the peer isn't actually too close (this can happen)
            if self.topology.TooClose(peer.position.GetXY()):
                self._JumpNearPeer(peer.address)
            # 2. Check we either don't have too many peers, or have worse peers than this one
            elif self._AcceptPeer(peer):
                # Connect to this peer
                self._SayHello(peer, send_detects=self.moved)

    def peer_AROUND(self, args):
        """
        A peer replies to us with an AROUND message.
        """
        peer = Peer.FromRemoteArgs(args)
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
            if self.jump_near_position or self.future_topology.TooClose(self.best_peer.position.GetXY()):
                # If we are jumping near a position, ask target position to the best peer
                self._JumpNearPeer(self.best_peer.address)
            else:
                # Otherwise, just go on with the connecting procedure
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
            around = self.topology.GetPeerAround(target, peer_id, clockwise=True)
            if around is not None:
                self._SendToAddress(args.address, self._PeerMessage('AROUND', remote_peer=around))
            else:
                self.logger.info('QUERYAROUND received, but no peer around position: %s' % str(target))
            around = self.topology.GetPeerAround(target, peer_id, clockwise=False)
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
        peer = Peer.FromArgs(args)

        if not self.topology.HasPeer(peer.id_):
            self.logger.info('UPDATE from %s, but we are not connected' % peer.id_)
            return

        self._UpdatePeer(peer)

    def peer_FOUND(self, args):
        """
        A peer replies to us with a FOUND message.
        """
        peer = Peer.FromRemoteArgs(args)

        # Verify that new entity is neither self neither an already known entity.
        if peer.id_ == self.node.id_:
            self.logger.warning("FOUND message pointing to ourselves received")
        elif not self.topology.HasPeer(peer.id_):
            self._SayHello(peer)

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
        x, y = self.topology.SuggestPosition(self.node.awareness_radius / 2.0)
        message = self._PeerMessage('SUGGEST')
        message.args.remote_position = Position((x, y, 0.0))
        self._SendToAddress(args.address, message)

    def peer_SUGGEST(self, args):
        """
        A peer answers a position suggestion in response to a JUMPNEAR message.
        """
        # Instantiate the target peer
        if self.jump_near_address is None or self.jump_near_address != args.address:
            self.logger.warning("Error, reception of unexpected SUGGEST message from peer '%s' at address '%s'"
                % (str(args.id_), args.address.ToString()))
            return
        peer = Peer.FromArgs(args)
        # If the client asked for it, we check the peer has the expected id
        if self.jump_near_expected_id:
            if peer.id_ != self.jump_near_expected_id:
                self.event_sender.event_ChangedId(self.jump_near_expected_id, peer)
#                 print "WARNING: expected jump near id '%s', got '%s'" % (self.jump_near_expected_id, peer.id_)
#             else:
#                 print "OK: jump near id '%s'" % peer.id_
        self.jump_near_address = None
        self.jump_near_position = None
        self.jump_near_expected_id = None

        print "suggest received, jumping"
        # Really jump near the target peer
        self.future_topology = Topology()
        self.future_topology.SetOrigin(args.remote_position.GetXY())
        self.future_topology.AddPeer(peer)
        self.future_position = args.remote_position
        self._StartFindNearest(addresses=[args.address])

    def peer_MIDDLEMAN(self, args):
        """
        A peer asks us to relay a message to another peer.
        """
        self.node_connector.DoMiddleman(args.id_, args.remote_id, args.payload)

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
        for peer in self.entity_cache.IterChoose(loop=False):
            if peer.address != self.node.address:
                self._SayHello(peer)
        self.SetState(states.EarlyConnecting())

    def TryConnect(self):
        """
        Try to connect to the world, picking some bootup entities
        at random and teleporting to our destination position.
        """
        self._CloseCurrentConnections()
        self.Reset()
        # 'self.entity_chooser' will be reused in case the connection fails
        if not self.entity_chooser:
            self.entity_chooser = self.entity_cache.IterChoose()
        addresses = [peer.address
            for peer, i in zip(self.entity_chooser, xrange(self.teleportation_flood - 1))]
        self._StartFindNearest(addresses)

    def MoveTo(self, (x, y, z), jump_near=False):
        """
        Move to a given absolute position in the world.
        """
        # Change position
        x %= self.world_size
        y %= self.world_size
        position = Position((x, y, z))
        old_position = self.node.position
        self.jump_near_position = jump_near and position or None
        self.jump_near_expected_id = None

        # We first change the position to check whether:
        # 1. the position can be accepted (i.e. not too close to another peer)
        # 2. we still have the global connectivity
        if not jump_near and self.topology.SetOrigin((x, y)) and self.topology.HasGlobalConnectivity():
            # We still have the global connectivity,
            # so we simply notify our peers of the position change
            self.node.position = position
            # This handles the case when the user continues moving
            # while we are changing topologies
            if self.future_topology is not None:
                self.future_topology.SetOrigin((x, y))
            else:
                self.future_position = None
            self._SendUpdates()
            self.event_sender.event_Moved(self.node.position)
        else:
            # Otherwise, do a full-fledged teleport from the current position:
            # for this it is better to first restore the old position
            self.topology.SetOrigin(old_position.GetXY())
            self._JumpToPosition(position)

        # "self.moved" will be True during a few seconds
        self.moved = True
        def _finish():
            self.moved = False
        caller = DelayedCaller(self.reactor)
        caller.CallLater(self.move_duration, _finish)

    def JumpNear(self, address, peer_id=None):
        """
        Try to jump near an existing entity.
        """
        self.jump_near_expected_id = peer_id or None
        self._JumpNearPeer(address)

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
        if not self.topology.AddPeer(peer) or not self.node_connector.AddPeer(peer):
            self.logger.warning("ignoring peer '%s'" % peer.id_)
            return

        # Open history entry
        self.entity_cache.OnPeerConnected(peer)
        # Notify remote control
        self.event_sender.event_NewPeer(peer)
        # Check topology properties
        self._CheckNumberOfPeers(check_ar=False)

    def _RemovePeer(self, id_):
        """
        Remove a peer and send the necessary notification messages.
        """
        try:
            self.meta_notify_ids.remove(id_)
        except KeyError:
            pass
        self.topology.RemovePeer(id_)
        self.node_connector.RemovePeer(id_)
        # Close history entry
        self.entity_cache.OnPeerDisconnected(id_)
        # Notify remote control
        self.event_sender.event_LostPeer(id_)

    def _AcceptPeer(self, peer):
        """
        True if peer is accepted as a potential neighbour.
        """
        if peer.id_ == self.node.id_:
            return False
        if not self.node_connector.AcceptPeer(peer):
            return False
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

    def _SaveEntityCache(self):
        if not self.params.as_seed:
            self.entity_cache.SaveAtomic(self.entity_cache_file)

    def _LoadEntityCache(self):
        if not self.params.as_seed:
            self.entity_cache.Load(self.entity_cache_file)

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

        # Close connections with peers that do not belong to the new topology
        self._CloseCurrentConnections(keep_peers=new_peers)

        # Notify remaining peers that our position has changed
        self._SendUpdates()

        # Try to connect with new peers
        for peer_id in new_peers - old_peers:
            self._SayHello(self.future_topology.GetPeer(peer_id))

        # Don't forget to notify our controller(s)
        self.event_sender.event_Jumped(self.node.position)

    def _JumpNearPeer(self, address):
        """
        Jump near a peer known by its address.
        """
        message = self._PeerMessage('JUMPNEAR')
        self._SendToAddress(address, message)
        self.jump_near_address = address

    def _JumpToPosition(self, position=None):
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
            if address != self.node.address:
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
            self.dc_meta_notify = None
            for id_ in self.meta_notify_ids:
                peer = self.topology.GetPeer(id_)
                self.event_sender.event_ChangedPeer(peer)
        self.meta_notify_ids.add(peer_id)
        if not self.dc_meta_notify:
            self.dc_meta_notify = self.caller.CallLater(self.meta_change_delay, _notify)

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
    def _PeerMessage(self, request, peer=None, remote_peer=None, future=False):
        """
        Builds a protocol message using parameters from the given peer(s).
        If 'future' is True, the future_position will be used instead of the current one.
        """
        if peer is None:
            peer = self.node
        message = protocol.Message(request)
        # Build message args from involved entities
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
            a.remote_version = r.protocol_version
            a.remote_needs_middleman = r.needs_middleman
        return message

    def _SayHello(self, peer, send_detects=False):
        """
        Say HELLO to a peer.
        """
        msg = self._PeerMessage('HELLO')
        msg.args.send_detects = send_detects
        return self.node_connector.SendHandshake(peer, msg)

    def _SayConnect(self, peer):
        """
        Answer CONNECT to a peer.
        """
        msg = self._PeerMessage('CONNECT')
        # When sending a CONNECT message, we don't want negotiation
        # so we use the normal way of sending messages
        self.node_connector.FillHandshake(peer, msg)
        return self.node_connector.SendToPeer(peer, msg, can_ignore_middleman=True)

    def _SayClose(self, peer):
        """
        Say CLOSE to a peer.
        """
        msg = self._PeerMessage('CLOSE')
        return self.node_connector.SendToPeer(peer, msg, can_ignore_middleman=True)

    def _QueryMeta(self, peer):
        """
        Send our metadata to a peer.
        """
        msg = self._PeerMessage('QUERYMETA')
        self.node.FillMeta(msg)
        self._SendToPeer(peer, msg)
        return True

    def _SendMeta(self, peer):
        """
        Send our metadata to a peer.
        """
        msg = self._PeerMessage('META')
        self.node.FillMeta(msg)
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
        self.node_connector.SendToAddress(address, message)

    def _SendToPeer(self, peer, message):
        """
        Send a Solipsis message to a known peer.
        """
        self.node_connector.SendToPeer(peer, message)

    #
    # Various stuff
    #
    def _Verbose(self, s):
        s += "\n"
        if not self.params.quiet:
            sys.stdout.write(s)
        self.logger.info(s)
