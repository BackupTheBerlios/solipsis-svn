import logging

from solipsis.util.geometry import Geometry
from solipsis.util.exception import *

from peer import Peer
import protocol
import states
from topology import Topology


# Forward compatibility with built-in "set" types
try:
    set
except:
    from sets import Set as set


class StateMachine(object):
    timeout = 2

    # These are all the message types accepted from other peers.
    # Some of them will only be accepted in certain states.
    # The motivation is twofold:
    # - we don't want to answer certain queries if our answer may be false
    # - we don't want to process answers to questions we didn't ask
    accepted_peer_messages = {
        'AROUND':       [states.Scanning],
        'BEST':         [],
        'CONNECT':      [],
        'CLOSE':        [],
        'DETECT':       [],
        'FINDNEAREST':  [states.Idle],
        'FOUND':        [],
        'HEARTBEAT':    [],
        'HELLO':        [],
        'NEAREST':      [states.Locating, states.Scanning],
        'QUERYAROUND':  [states.Idle],
        'SEARCH':       [states.Idle],
        'UPDATE':       [],
    }

    def __init__(self, reactor, node, logger=None):
        """
        Initialize the state machine.
        """
        self.reactor = reactor
        self.node = node
        self.peers = self.node.peersManager
        self.topology = Topology()
        self.logger = logger or logging.getLogger("root")
        self.parser = protocol.Parser()

        self.peer_dispatch_cache = {}
        self.state_dispatch = {}
        self.delayed_calls = []

        self.Reset()

    def Reset(self):
        self.state = None
        self.sender = None
        self.peer_dispatch = {}

        # Id's of the peers encountered during a FINDNEAREST chain
        self.nearest_peers = set()
        # Peers discovered during a QUERYAROUND chain
        #self.scanned_neighbours = []
        self.future_topology = None
        # BEST peer discovered at the end of a FINDNEAREST chain
        self.best_peer = None

        self.topology.SetOrigin(self.node.position.getCoords())
        self._CancelDelayedCalls()

    def ConnectWithEntities(self, sender, addresses):
        self.Reset()
        self.sender = sender

        message = self._PeerMessage('FINDNEAREST')
        for address in addresses:
            self._SendToAddress(address, message)
        self.SetState(states.Locating())

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
            self._CancelDelayedCalls()
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
            # TODO: properly handle heartbeat et al.
            try:
                id_ = args.id_
            except AttributeError:
                pass
            else:
                manager = self.peers
                #manager.heartbeat(id_)

    def _CancelDelayedCalls(self):
        """
        Cancel all pending delayed calls.
        Called on a state change.
        """
        for delayed in self.delayed_calls:
            try:
                delayed[1].cancel()
            except Exception, e:
                print str(e)
        # Important: we must not create a new list
        # (see _CallLater below)
        self.delayed_calls[:] = []

    def _CallLater(self, _delay, _function, *args, **kargs):
        """
        Call a function later in the current state.
        The call will be cancelled if we enter another state.
        """
        # This class defines a callable that will remove itself
        # from the list of delayed calls
        class Fun:
            def __call__(self):
                self.delayed_calls.remove(self.delayed)
                _function(*args, **kargs)
        # We first register the callable, then give it the
        # necessary parameters to remove itself...
        fun = Fun()
        delayed = (_delay, self.reactor.callLater(_delay, fun))
        self.delayed_calls.append(delayed)
        fun.delayed = delayed
        fun.delayed_calls = self.delayed_calls

    def _CallPeriodically(self, _period, _function, *args, **kargs):
        """
        Call a function once in a while in the current state.
        The calls will be cancelled if we enter another state.
        """
        def fun():
            self._CallLater(_period, fun)
            _function(*args, **kargs)
        self._CallLater(_period, fun)

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

    def _PeerMessage(self, request, entity=None, remote_entity=None):
        if entity is None:
            entity = self.node
        message = protocol.Message(request)
        # Build message args from involved entities
        # This could be smarter...
        a = message.args
        e = entity
        a.address = e.address
        a.awareness_radius = e.awareness_radius
        a.calibre = e.calibre
        a.id_ = e.id_
        a.orientation = e.orientation
        a.position = e.position
        a.pseudo = e.pseudo
        if remote_entity:
            r = remote_entity
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
        if self.sender is not None:
            self.sender(message=message, address=address)
        else:
            self.logger.warning("Attempting to send message but sender method is not initialized")

    def _SendToPeer(self, peer, message):
        if peer.id_ == self.node.id_:
            self.logger.error("we tried to send a message (%s) to ourselves" % message.request)
            return
        data = self.parser.BuildMessage(message)
        self._SendToAddress(peer.address, message)

    #
    # Methods called when a new state is entered
    #
    def state_NotConnected(self):
        print "not connected"

    def state_Locating(self):
        print "locating"

    def state_Scanning(self):
        print "scanning"

    def state_Connecting(self):
        print "connecting"

        def check_gc():
            # Periodically check global connectivity
            manager = self.peers
            gc1 = manager.hasGlobalConnectivity()
            gc2 = self.topology.HasGlobalConnectivity()
            if gc1 ^ gc2:
                self.logger.error("Manager and topology disagree on global connectivity (%d, %d)" % (gc1, gc2))
            elif gc2:
                self.SetState(states.Idle())
        self._CallPeriodically(1, check_gc)

    def state_Idle(self):
        print "idle"
        # TODO: add periodic handler for increasing / decreasing the number of peers

        def count(i=[0]):
            i[0] += 1
            if i[0] % 50 == 0:
                print i[0]
        def check_gc():
            # Periodically check global connectivity
            manager = self.peers
            gc1 = manager.hasGlobalConnectivity()
            gc2 = self.topology.HasGlobalConnectivity()
            if gc1 ^ gc2:
                self.logger.error("Manager and topology disagree on global connectivity (%d, %d)" % (gc1, gc2))
            elif not gc2:
                self.SetState(states.LostGlobalConnectivity())
        self._CallPeriodically(2, check_gc)
        #self._CallPeriodically(0, count)

    def state_LostGlobalConnectivity(self):
        print "lost global connectivity"

        def check_gc():
            # Periodically check global connectivity
            manager = self.peers
#             if manager.getNumberOfPeers() == 0:
            if self.topology.getNumberOfPeers():
                # TODO: implement this
                self.logger.info("All peers lost, relaunching JUMP algorithm")
                return

            pair1 = manager.getBadGlobalConnectivityPeers()
            pair1.reverse()
            pair2 = self.topology.getBadGlobalConnectivityPeers()
            if pair1 != pair2:
                self.logger.error("Manager and topology disagree on global connectivity peers (%s, %s) <-> (%s, %s)"
                    % (pair1[0].id_, pair1[1].id_, pair2[0].id_, pair2[1].id_))
            elif not pair2:
                self.SetState(states.Idle())
            else:
                # Send search message to each entity
                message1 = self._PeerMessage('SEARCH')
                message1.clockwise = False
                message2 = self._PeerMessage('SEARCH')
                message2.clockwise = True
                self._SendToPeer(pair2[0], message1)
                self._SendToPeer(pair2[1], message2)

        check_gc()
        self._CallPeriodically(2, check_gc)


    #
    # Methods called when a message is received from a peer
    #
    def peer_HELLO(self, args):
        """
        A new peer is contacting us.
        """
        peer = self._Peer(args)
        manager = self.peers

        # We have now too many peers and this is the worst one
        if not manager.isPeerAccepted(peer):
            # refuse connection
            self._SendToPeer(peer, self._PeerMessage('CLOSE'))
        else:
            # check if we have not already connected to this peer
            if self.topology.HasPeer(peer.id_):
                manager.removePeer(peer.id_)
                self.topology.RemovePeer(peer.id_)
                self.logger.info("HELLO from '%s', but we are already connected" % peer.id_)
            if self._SayConnect(peer):
                self._AddPeer(peer)

    def peer_CONNECT(self, args):
        """
        A peer accepts our connection proposal.
        """
        # TODO: check that we sent a HELLO message to this peer
        peer = self._Peer(args)
        manager = self.peers

        if not self.topology.HasPeer(peer.id_):
            self._AddPeer(peer)
            # TODO: exchange service info and other stuff
            # TODO: notify

        else:
            self.logger.info("reception of CONNECT but we are already connected to '%s'" % peer.id_)

    def peer_CLOSE(self, args):
        """
        A peer closes or refuses a connection.
        """
        id_ = args.id_
        manager = self.peers
        if not self.topology.HasPeer(id_):
            self.logger.info('CLOSE from %s, but we are not connected' % id_)
            return

        self._RemovePeer(self.topology.GetPeer(id_))

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
            elif (Geometry.distance(self.node.position, self.best_peer.position) <=
                Geometry.distance(self.node.position, args.remote_position)):
                self.logger.info("NEAREST received, but proposed peer is farther than our current best")
                return

        self.nearest_peers.add(id_)
        address = args.remote_address
        self._SendToAddress(address, self._PeerMessage('FINDNEAREST'))
        # We could come here from the Scanning procedure,
        # if a neighbour finds someone closer to us than our current BEST
        if self.InState(states.Scanning):
            self.SetState(states.Locating())

    def peer_BEST(self, args):
        """
        A peer answers us a BEST message.
        """
        # Instantiate the best peer
        peer = self._Peer(args)

        # Send a queryaround message
        message = self._PeerMessage('QUERYAROUND')
        message.args.best_id = peer.id_
        message.args.best_distance = Geometry.distance(self.node.position, peer.position)
        self._SendToPeer(peer, message)

        # Store the best peer and launch the scanning procedure
        self.best_peer = peer
        self.nearest_peers.clear()
        self.future_topology = Topology()
        self.future_topology.SetOrigin(self.node.position.getCoords())
        self.future_topology.AddPeer(peer)
#         self.scanned_neighbours = [peer]
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
        manager = self.peers

        # Sanity check 1: don't connect with ourselves
        if id_ == self.node.id_:
            return
        # Sanity check 2: don't connect with someone too far from us
        distance = self.topology.RelativeDistance(peer.position.getCoords())
        if distance > self.node.awareness_radius:
            return

        # We are only interested by entities that are not yet in our peer list
        if not self.topology.HasPeer(id_):
            # Check we don't have too many peers, or have worse peers than this one
            if manager.isPeerAccepted(peer):
                # Connect to this peer
                self._SayHello(args.address)

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

        best_pos = self.best_peer.position.getCoords()
        best_distance = self.future_topology.RelativeDistance(best_pos)

        if self.future_topology.HasGlobalConnectivity():
            # Our awareness radius is the distance between us and our closest
            # neighbour, because we are sure to know all the entities between us
            # and the best.
            self.node.awareness_radius = best_distance
            self._SwitchTopologies()
            self.SetState(states.Connecting())
            return

        elif already_best:
            # TODO: handle this case (hmmm...)
            self.logger.warning("We came back to our BEST but there is no global connectivity: we have a problem!")

        # Send this peer a queryaround message
        message = self._PeerMessage('QUERYAROUND')
        message.args.best_id = self.best_peer.id_
        message.args.best_distance = best_distance
        self._SendToPeer(peer, message)

    def peer_QUERYAROUND(self, args):
        """
        A peer sent us a QUERYAROUND message.
        """
        peer_id = args.id_
        best_id = args.best_id
        best_distance = args.best_distance
        manager = self.peers
        target = args.position.getCoords()
        (nearest, nearest_distance) = self.topology.GetClosestPeer(target, best_id)

        # Either:
        # 1. We have a peer closer to the target than the given Best-Distance
        if nearest_distance < best_distance:
            self.SendToAddress(args.address, self._PeerMessage('NEAREST', remote_peer=nearest))

        # 2. Or we find the closest peer around the target position and in the right half-plane
        else:
            # Search for a peer around target position
            around = self.topology.GetPeerAround(target, source_id)
            if around is not None:
                self.SendToAddress(args.address, self._PeerMessage('AROUND', remote_peer=around))
            else:
                self.logger.info('QUERYAROUND received, but no peer around position: %s' % str(target))

    def peer_HEARTBEAT(self, args):
        """
        A peer reminds us it is alive.
        """
        # TODO: properly manage HEARTBEAT intervals and retries...
        manager = self.peers
        manager.heartbeat(args.id_)

    def peer_UPDATE(self, args):
        """
        A peer notifies us it UPDATEs its characteristics.
        """
        peer = self._Peer(args)

        manager = self.peers
        if not manager.hasPeer(peer.id_):
            self.logger.info('UPDATE from %s, but we are not connected' % peer.id_)
            return

        # Save old peer value
        old = manager.getPeer(peer.id_)

        # Update peer
        manager.updatePeer(peer)

        # TODO: Notify the controller that a peer has changed
#         ctlFact = EventFactory.getInstance(ControlEvent.TYPE)
#         upd = ctlFact.createUPDATE(peer)
#         self.node.dispatch(upd)

        old_pos = old.position
        new_pos = peer.position
        our_pos = self.node.position

        old_ar = old.awareness_radius
        new_ar = peer.awareness_radius

        # Peer position or awareness radius changed
        if new_pos != old_pos or new_ar != old_ar:
            # Verify entities that could be interested by the change
            for entity in manager.enumeratePeers():
                if entity.id_ == peer.id_:
                    continue
                its_ar = entity.awareness_radius

                our_dist = Geometry.distance(our_pos, entity.position)
                their_dist = Geometry.distance(entity.position, new_pos)
                their_old_dist = Geometry.distance(entity.position, old_pos)

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


    def peer_FOUND(self, args):
        """
        A peer replies to us with a FOUND message.
        """
        peer = self._RemotePeer(args)
        id_ = peer.id_
        manager = self.peers

        # Verify that new entity is neither self neither an already known entity.
        if id_ == self.node.id_:
            self.logger.warning("FOUND message pointing to ourselves received")
        elif not manager.hasPeer(id_):
            self._SayHello(peer.address)


    def peer_SEARCH(self, args):
        """
        A peer sends SEARCH queries around itself to restore its global connectivity.
        """
        id_ = args.id_
        clockwise = args.clockwise > 0
        manager = self.peers

        try:
            peer = manager.getPeer(id_)
        except UnknownIdError:
            self.logger.warning("Error, reception of SEARCH message from unknown peer '%s'" % str(id_))
            return

        around = manager.getPeerAround(peer.position, id_, clockwise)

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
    # Private methods
    #
    def _AddPeer(self, peer):
        """
        Add a peer and send the necessary notification messages.
        """
        manager = self.peers
        manager.addPeer(peer)
        self.topology.AddPeer(peer)

        # TODO: notify navigator that we gained a new peer
#         factory = EventFactory.getInstance(ControlEvent.TYPE)
#         newPeerEvent = factory.createNEW(peer)
#         self.node.dispatch(newPeerEvent)
#         if type(self) == Idle:
#             if manager.hasTooManyPeers():
#                 self.node.setState(TooManyPeers())

    def _RemovePeer(self, peer):
        """
        Remove a peer and send the necessary notification messages.
        """
        manager = self.peers
        manager.removePeer(peer.id_)
        self.topology.RemovePeer(peer.id_)

        # TODO: notify navigator that we lost connection with a peer
#         factory = EventFactory.getInstance(ControlEvent.TYPE)
#         dead = factory.createDEAD(id_)
#         self.node.dispatch(dead)

    def _SwitchTopologies(self):
        # Try to connect with future peers
        for p in self.future_topology.EnumeratePeers():
            self._SayHello(p.address)

        self.topology = Topology()
        self.topology.SetOrigin(self.node.position.getCoords())
        self.future_topology = None
        self.best_peer = None

    #
    # Old stuff
    # TODO: remove
    #

    def updateAwarenessRadius(self):
        """ compute our new awareness radius and notify peers of this update"""
        manager = self.node.getPeersManager()
        ar = manager.computeAwarenessRadius()
        self.node.setAwarenessRadius(ar)
        self.sendUpdates()

    def jump(self):
        """ Jump to the node's current position. This involves
        the recursive teleportation algorithm. """
        manager = self.node.getPeersManager()
        peer = manager.getRandomPeer()
        self.sendFindNearest(peer.getAddress())

        # Disconnect from our current peers
        peerFct = EventFactory.getInstance(PeerEvent.TYPE)
        for peer in manager.enumeratePeers():
            evt = peerFct.createCLOSE()
            evt.setRecipientAddress(peer.getAddress())
            self.node.dispatch(evt)
            self.removePeer(peer)

        # Go to the tracking state
        self.node.setState(Locating())

