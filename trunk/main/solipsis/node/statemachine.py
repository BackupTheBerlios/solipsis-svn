
import logging
import math
import random

from solipsis.util.exception import *
from solipsis.util.geometry import Position
from peer import Peer
import protocol
import states
from topology import Topology
from delayedcaller import DelayedCaller


# Forward compatibility with built-in "set" types
try:
    set
except:
    from sets import Set as set


class StateMachine(object):
    """
    Finite State Machine of the Solipsis protocol.
    This is where all the interesting stuff happens.
    """
    world_size = 2**128

    teleportation_flood = 5
    peer_neighbour_ratio = 2.0

    scanning_period = 1.0
    connecting_period = 1.0
    early_connecting_period = 5.0
    gc_check_period = 2.0
    population_check_period = 4.0

    gc_trials = 3
    locating_timeout = 3.0
    locating_trials = 3
    scanning_trials = 3
    connecting_trials = 4

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
        'FINDNEAREST':  [states.Connecting, states.Idle],
        'FOUND':        [],
        'HEARTBEAT':    [],
        'HELLO':        [],
        'NEAREST':      [states.Locating, states.Scanning],
        'QUERYAROUND':  [states.Idle],
        'SEARCH':       [states.Idle],
        'UPDATE':       [],
    }

    def __init__(self, reactor, params, node, logger=None):
        """
        Initialize the state machine.
        """
        self.reactor = reactor
        self.node = node
        self.topology = Topology()
        self.logger = logger or logging.getLogger("root")
        self.parser = protocol.Parser()

        # Expected number of neighbours (in awareness radius)
        self.expected_neighbours = params.expected_neighbours
        self.min_neighbours = self.expected_neighbours
        self.max_neighbours = round(1.2 * self.expected_neighbours)
        # Max number of connections (total)
        self.max_connections = 2 * self.expected_neighbours

        self.peer_dispatch_cache = {}
        self.state_dispatch = {}
        self.caller = DelayedCaller(self.reactor)
        self.peer_sender = None

        self.Reset()

    def __del__(self):
        print "state machine finalized"
        self.Reset()

    def Reset(self):
        self.state = None
        self.peer_dispatch = {}

        # Id's of the peers encountered during a FINDNEAREST chain
        self.nearest_peers = set()
        # Peers discovered during a QUERYAROUND chain
        self.future_topology = None
        # BEST peer discovered at the end of a FINDNEAREST chain
        self.best_peer = None
        self.best_distance = 0.0

        # Delayed calls
        self.peer_timeouts = {}
        self.caller.Reset()

        self.topology.Reset(origin=self.node.position.getCoords())

    def Init(self, sender, bootup_addresses):
        """
        Initialize the state machine. This is mandatory.
        """
        self.peer_sender = sender
        self.bootup_addresses = bootup_addresses

    def ImmediatelyConnect(self):
        self.Reset()
        message = self._PeerMessage('HELLO')
        for address in self.bootup_addresses:
            self._SendToAddress(address, message)
        self.SetState(states.EarlyConnecting())

    def TryConnect(self):
        self.Reset()
        addresses = random.sample(self.bootup_addresses, self.teleportation_flood)
        self._StartFindNearest(addresses)

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
        # Call state initialization function
        if _class != old_state.__class__:
            self.caller.Reset()
            try:
                func = self.state_dispatch[_class]
            except:
                func = getattr(self, 'state_' + _class.__name__, None)
                self.state_dispatch[_class] = func
            if func is not None:
                func()

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
        except:
            self.logger.info("Ignoring unexpected message '%s' in state '%s'" % (request, self.state.__class__.__name__))
        else:
            func(args)
            try:
                id_ = args.id_
            except AttributeError:
                pass
            else:
                # Heartbeat handling
                if id_ in self.peer_timeouts:
                    self.peer_timeouts[id_].RescheduleCall('msg_receive_timeout')


    #
    # Methods called when a new state is entered
    #
    def state_NotConnected(self):
        print "not connected"

    def state_Locating(self):
        print "locating"

        def _restart():
            self.SetState(states.NotConnected())
            self.TryConnect()

        self.caller.CallLaterWithId('locating_timeout', self.locating_timeout, _restart)

    def state_Scanning(self):
        print "scanning"
        def _restart():
            self._Jump()
        def _retry():
            # Resend a QUERYAROUND message to all future peers
            message = self._PeerMessage('QUERYAROUND')
            message.args.best_id = self.best_peer.id_
            message.args.best_distance = self.best_distance
            peers = self.topology.PeersSet()
            for p in self.future_topology.EnumeratePeers():
                self._SendToPeer(p, message)

        self.caller.CallPeriodically(self.scanning_period, _retry)
        self.caller.CallLater(self.scanning_period * self.scanning_trials, _restart)

    def state_EarlyConnecting(self):
        print "early connecting"
        def _check_gc():
            # Periodically check global connectivity
            if self.topology.HasGlobalConnectivity():
                self.SetState(states.Idle())
            else:
                print "(still connecting)"

        self.caller.CallPeriodically(self.early_connecting_period, _check_gc)

    def state_Connecting(self):
        print "connecting"
        def _restart():
            self._Jump()

        def _check():
            if self.topology.HasGlobalConnectivity():
                self.future_topology = None
                self.best_peer = None
                self.best_distance = 0.0
                self.SetState(states.Idle())
            else:
                # Resend a HELLO message to all future peers
                print "(still connecting)"
                peers = self.topology.PeersSet()
                for p in self.future_topology.EnumeratePeers():
                    if p not in peers:
                        self._SayHello(p.address)

        self.caller.CallPeriodically(self.connecting_period, _check)
        self.caller.CallLater(self.connecting_period * self.connecting_trials, _restart)

    def state_Idle(self):
        print "idle"
        def _jump():
            x = random.random() * self.world_size
            y = random.random() * self.world_size
            self.node.position = Position(x, y, 0)
            print "jump to %f, %f" % (x, y)
            self._Jump()

#         self.caller.CallLater(3.0 * random.random(), _jump)

        def _check_gc():
            # Periodically check global connectivity
            if not self.topology.HasGlobalConnectivity():
                self.SetState(states.LostGlobalConnectivity())

        self.caller.CallPeriodically(self.gc_check_period, _check_gc)
        self._CheckNumberOfPeers()
        self.caller.CallPeriodically(self.population_check_period, self._CheckNumberOfPeers)

    def state_LostGlobalConnectivity(self):
        print "lost global connectivity"
        def _restart():
            self._Jump()

        def _check_gc():
            # Periodically check global connectivity
            if self.topology.GetNumberOfPeers() == 0:
                # TODO: implement this (we need some initial peer addresses...)
                self.logger.info("All peers lost, relaunching JUMP algorithm")
                return

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
        topology = self.topology

        # We have now too many peers and this is the worst one
        if not self._AcceptPeer(peer):
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
                self._SendDetects(peer)

    def peer_CONNECT(self, args):
        """
        A peer accepts our connection proposal.
        """
        # TODO: check that we sent a HELLO message to this peer
        peer = self._Peer(args)
        topology = self.topology

        if not topology.HasPeer(peer.id_):
            self._AddPeer(peer)
            # TODO: exchange service info and other stuff

        else:
            self.logger.info("reception of CONNECT but we are already connected to '%s'" % peer.id_)

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
            elif (self.best_distance <= self.topology.RelativeDistance(args.remote_position.getCoords())):
                self.logger.info("NEAREST received, but proposed peer is farther than our current best")
                return

        self.nearest_peers.add(id_)
        address = args.remote_address
        self._SendToAddress(address, self._PeerMessage('FINDNEAREST'))
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
        distance = self.future_topology.RelativeDistance(peer.position.getCoords())

        # Store the best peer
        if self.best_peer is not None:
            if distance >= self.best_distance:
                self.logger.info("BEST received, but peer is farther than our current best")
                return

        self.best_peer = peer
        self.best_distance = distance
        self.nearest_peers.clear()
        self.future_topology.Reset()
        self.future_topology.AddPeer(peer)

        # Send a queryaround message
        message = self._PeerMessage('QUERYAROUND')
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
        target = args.position.getCoords()
        address = args.address
        (nearest, nearest_distance) = self.topology.GetClosestPeer(target, id_)

        # Check whether I am closer to the target than nearestPeer
        if self.topology.RelativeDistance(target) < nearest_distance:
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
        distance = self.topology.RelativeDistance(peer.position.getCoords())
        if distance > self.node.awareness_radius:
            return

        # We are only interested by entities that are not yet in our peer list
        if not self.topology.HasPeer(id_):
            # Check we don't have too many peers, or have worse peers than this one
            if self._AcceptPeer(peer):
                # Connect to this peer
                self._SayHello(peer.address)

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
            # Our awareness radius is the distance between us and our closest
            # neighbour, because we are "sure" to know all the entities between us
            # and the best.
            self.node.awareness_radius = self.best_distance
            self._SwitchTopologies()
            self.SetState(states.Connecting())
            return

        if already_best:
            # Handled by timeouts
            self.logger.info("AROUND: we came back to our BEST but there is no global connectivity")
            return

        # Send this peer a queryaround message
        message = self._PeerMessage('QUERYAROUND')
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
        target = args.position.getCoords()
        (nearest, nearest_distance) = self.topology.GetClosestPeer(target, peer_id)

        # Either:
        # 1. We have a peer closer to the target than the given Best
        if nearest.id_ != best_id and nearest_distance < best_distance:
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

        around = self.topology.GetPeerAround(peer.position.getCoords(), id_, clockwise)

        # Send message if an entity has been found
        if around is not None:
            self._SendToPeer(peer, self._PeerMessage('FOUND', remote_peer=around))

    #
    # Control events
    # TODO: rewrite
    #
    def control_MOVE(self, event):
        """ MOVE control event. Move the node to a new position.
        event : Request = MOVE, args = {'Position'}
        """

        # Change position
        newPosition = event.getArg(protocol.ARG_POSITION)
        self.node.setPosition(newPosition)
        manager = self.node.getPeersManager()
        if manager.hasGlobalConnectivity():
            # We still have the global connectivity,
            # so we can simply notify peers of the position change
            self.sendUpdates()

        else:
            # We cannot keep our global connectivity,
            # so we do the JUMP algorithm to get the knowledge
            # of our new neighbourhood
            self.jump()

    def control_KILL(self, event):
        self.logger.info("Received kill message")
        self.node.exit()

    def control_ABORT(self, event):
        self.node.alive = False
        print "\nFatal error: " + event.getArg('Message') + "\nAborting"
        self.node.dispatch(event)

    def control_GETNODEINFO(self, event):
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        info = factory.createNODEINFO()
        self.node.dispatch(info)

    def control_SET(self, event):
        field = event.getArg('Name')
        value = event.getArg('Value')
        if field == 'Pseudo':
            self.node.setPseudo(value)
            self.sendUpdates()
        else:
            import exceptions
            raise NotImplementedError()

    #
    # Private methods: connection management
    #
    def _AddPeer(self, peer):
        """
        Add a peer and send the necessary notification messages.
        """
        peer.id_ = intern(peer.id_)
        if not self.topology.AddPeer(peer):
            print "topology refused peer '%s'" % peer.id_
            return

        def msg_receive_timeout():
            print "timeout (%s) => closing connection with '%s'" % (str(self.node.id_), str(peer.id_))
            self._CloseConnection(peer)
        def msg_send_timeout():
            self._SendToPeer(peer, self._PeerMessage('HEARTBEAT'))

        # Setup heartbeat handling callbacks
        caller = DelayedCaller(self.reactor)
        # Heuristic (a la BGP)
        keepalive = peer.hold_time / 3.0
        caller.CallPeriodicallyWithId('msg_receive_timeout', peer.hold_time, msg_receive_timeout)
        caller.CallPeriodicallyWithId('msg_send_timeout', keepalive, msg_send_timeout)
        self.peer_timeouts[peer.id_] = caller

        # TODO: notify navigator that we gained a new peer

    def _RemovePeer(self, id_):
        """
        Remove a peer and send the necessary notification messages.
        """
        del self.peer_timeouts[id_]
        self.topology.RemovePeer(id_)

        # TODO: notify navigator that we lost connection with a peer

    def _AcceptPeer(self, peer):
        """
        True if peer is accepted as a potential neighbour.
        """
        if self.topology.GetNumberOfPeers() < self.max_connections:
            return True
        return not self.topology.IsWorstPeer(peer)

    def _CloseCurrentConnections(self, keep_ids=None):
        remove_ids = []
        for p in self.topology.EnumeratePeers():
            if keep_ids is None or p.id_ not in keep_ids:
                self._SendToPeer(p, self._PeerMessage('CLOSE'))
                remove_ids.append(p.id_)
        for id_ in remove_ids:
            self._RemovePeer(id_)

    def _CloseConnection(self, peer):
        self._SendToPeer(peer, self._PeerMessage('CLOSE'))
        self._RemovePeer(peer.id_)

    def _SayHello(self, address):
        # TODO: manage repeted connection failures and
        # optionally cancel request (returning False)
        self._SendToAddress(address, self._PeerMessage('HELLO'))
        return True

    def _SayConnect(self, peer):
        # TODO: manage repeted connection failures and
        # optionally cancel request (sending CLOSE and
        # returning False)
        self._SendToPeer(peer, self._PeerMessage('CONNECT'))
        return True


    #
    # Teleportation algorithm
    #
    def _SwitchTopologies(self):
        new_peers = self.future_topology.PeersSet()
        old_peers = self.topology.PeersSet()

        # Close our current connections, except with peers that
        # are in our future topology.
        self._CloseCurrentConnections(new_peers)

        # Try to connect with future peers
        for p in self.future_topology.EnumeratePeers():
            if p not in old_peers:
                self._SayHello(p.address)

    def _Jump(self, topology=None):
        """
        Jump to the node's current position. This triggers
        the recursive teleportation algorithm.
        """
        # If nothing asked, prefer future topology over current one
        if topology is None:
            topology = self.future_topology or self.topology
        addresses = [peer.address for peer in topology.GetNearestPeers(self.teleportation_flood)]

        # Start teleportation algorithm
        self._StartFindNearest(addresses)

    def _StartFindNearest(self, addresses):
        # Send FINDNEAREST to all selected addresses
        message = self._PeerMessage('FINDNEAREST')
        for address in addresses:
            self._SendToAddress(address, message)

        # Create future topology and jump into state "locating"
        self.future_topology = Topology()
        self.future_topology.SetOrigin(self.node.position.getCoords())
        self.SetState(states.Locating())


    #
    # Awareness radius management
    #
    def _UpdatePeer(self, peer):
        """
        Update a peer's characteristics.
        """
        topology = self.topology

        # Save old peer value and update
        old = topology.GetPeer(peer.id_)
        topology.UpdatePeer(peer)

        # TODO: Notify the controller that a peer has changed
#         ctlFact = EventFactory.getInstance(ControlEvent.TYPE)
#         upd = ctlFact.createUPDATE(peer)
#         self.node.dispatch(upd)

        old_pos = old.position.getCoords()
        new_pos = peer.position.getCoords()
        our_pos = self.node.position

        old_ar = old.awareness_radius
        new_ar = peer.awareness_radius

        # Peer position or awareness radius changed
        if new_pos != old_pos or new_ar != old_ar:
            # Verify entities that could be interested by the change
            for entity in topology.EnumeratePeers():
                if entity.id_ == peer.id_:
                    continue
                its_pos = entity.position.getCoords()
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
        if self.InState(states.EarlyConnecting):
            return
        position = peer.position.getCoords()
        radius = peer.awareness_radius
        for remote_peer in self.topology.GetPeersInCircle(position, radius):
            message = self._PeerMessage('DETECT', remote_peer=remote_peer)
            self._SendToPeer(peer, message)

    def _UpdateAwarenessRadius(self, ar):
        self.node.awareness_radius = ar
        self._SendUpdates()

    def _CheckNumberOfPeers(self):
        """
        Check the current number of peers and optionally launch
        various actions so that it stays within the desired bounds.
        """
        topology = self.topology
        ar = self.node.awareness_radius
        nb_peers = topology.GetNumberOfPeers()
        neighbours = topology.GetPeersWithinDistance(ar)
        nb_neighbours = len(neighbours)
        if nb_peers < 3:
            # This case is handled by the global connectivity check
            return

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
            if new_ar != ar:
                self._UpdateAwarenessRadius(new_ar)
        # 2. Too many neighbours in our awareness radius
        elif nb_neighbours > self.max_neighbours:
            new_ar = topology.GetEnclosingDistance(self.min_neighbours) * 1.01
            # Sometimes several peers are exactly at the same distance, so the AR doesn't change...
            if new_ar != ar:
                self._UpdateAwarenessRadius(new_ar)
        # 3. Too many connected peers outside of our awareness radius
        elif nb_peers > self.max_connections:
            peers = self.topology.GetWorstPeers(self.max_connections - self.max_neighbours, ar)
            for p in peers:
                self._CloseConnection(p)
        else:
            return
#         print "ar=%6f, peers=%d, neighbours=%d (min=%d, max=%d)" % (ar, nb_peers, nb_neighbours, self.min_neighbours, self.max_neighbours)


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
            calibre = args.calibre,
            id_ = args.id_,
            orientation = args.orientation,
            position = args.position,
            pseudo = args.pseudo)

    def _RemotePeer(self, args):
        """
        Returns a Peer created from the given "Remote-*" message arguments.
        """
        return Peer(
            address = args.remote_address,
            awareness_radius = args.remote_awareness_radius,
            calibre = args.remote_calibre,
            id_ = args.remote_id,
            orientation = args.remote_orientation,
            position = args.remote_position,
            pseudo = args.remote_pseudo)

    def _PeerMessage(self, request, peer=None, remote_peer=None):
        if peer is None:
            peer = self.node
        message = protocol.Message(request)
        # Build message args from involved entities
        # TODO: rewrite this better
        a = message.args
        p = peer
        a.address = p.address
        a.awareness_radius = p.awareness_radius
        a.calibre = p.calibre
        a.id_ = p.id_
        a.orientation = p.orientation
        a.position = p.position
        a.pseudo = p.pseudo
        if remote_peer:
            r = remote_peer
            a.remote_address = r.address
            a.remote_awareness_radius = r.awareness_radius
            a.remote_calibre = r.calibre
            a.remote_id = r.id_
            a.remote_orientation = r.orientation
            a.remote_position = r.position
            a.remote_pseudo = r.pseudo
        # Then remove unnecessary fields
        self.parser.StripMessage(message)
        return message

    def _SendToAddress(self, address, message):
        if self.peer_sender is not None:
            self.peer_sender(message=message, address=address)
        else:
            self.logger.warning("Attempting to send message but sender method is not initialized")

    def _SendToPeer(self, peer, message):
        if peer.id_ == self.node.id_:
            self.logger.error("we tried to send a message (%s) to ourselves" % message.request)
            return
        data = self.parser.BuildMessage(message)
        self._SendToAddress(peer.address, message)

