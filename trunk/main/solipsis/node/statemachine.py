import logging

from solipsis.util.geometry import Geometry
from solipsis.util.exception import *

from peer import Peer
import protocol
import states


# Forward compatibility with built-in "set" types
try:
    set
except:
    from Sets import Set as set


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
        self.peers = self.node.getPeersManager()
        self.logger = logger or logging.getLogger("root")

        self.peer_dispatch_cache = {}
        self.peer_dispatch = None

        self.Reset()

    def Reset(self):
        self.state = None

        # Id's of the peers encountered during a FINDNEAREST chain
        self.nearest_peers = set()
        # Peers discovered during a QUERYAROUND chain
        self.scanned_neighbours = []
        # BEST peer discovered at the end of a FINDNEAREST chain
        self.best_peer = None


    def SetState(self, state):
        """
        Change the current state of the state machine.
        The 'state' parameter must be an instance of one
        of the State subclasses.
        """
        self.state = state
        try:
            self.peer_dispatch = self.peer_dispatch_cache[state.__class__]
        except KeyError:
            # Here we build a cache for dispatching peer messages
            # according to the current state.
            d = {}
            _class = state.__class__
            # We restrict message types according both to:
            # 1. expected messages in the given state
            # 2. accepted states for the given message type
            try:
                messages = state.expected_messages
            except AttributeError:
                messages = self.accepted_peer_messages.keys()
            for request in messages:
                l = self.accepted_peer_messages[request]
                if len(l) == 0 or _class in l:
                    d[request] = getattr(self.state_machine, 'peer_' + request)
            self.peer_dispatch = d
            self.peer_dispatch_cache[state.__class__] = d

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
            self.dispatch[request](args)
        except:
            self.logger.debug("Ignoring unexpected message '%s' in state '%s'" % (request, state.__class__.__name__))
        else:
            # TODO: properly handle heartbeat et al.
            try:
                id_ = args.id_
            except KeyError:
                pass
            else:
                manager = self.peers
                manager.heartbeat(id_)

    def _Peer(self, args):
        return Peer(
            address = args.address
            awareness_radius = args.awareness_radius,
            calibre = args.calibre,
            id_ = args.id_,
            orientation = args.orientation,
            position = args.position,
            pseudo = args.pseudo)

    def _RemotePeer(self, args):
        return Peer(
            address = args.remote_address
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
        if peer is None:
            peer = self.node
        message = protocol.Message()
        # Build message args from involved entities
        # This could be smarter...
        a = message.args
        a.address = entity.address
        a.awareness_radius = entity.awareness_radius
        a.calibre = entity.calibre
        a.id_ = entity.id_
        a.orientation = entity.orientation
        a.position = entity.position
        a.pseudo = entity.pseudo
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
        print "sending '%s' message to %s:" % (message.request, str(address))
        #print data

    def _SendToPeer(self, peer, message):
        data = self.parser.BuildMessage(message)
        self._SendToAddress(peer.address, message)

    #
    # Peer events
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
            if manager.hasPeer(peer.id_):
                manager.removePeer(peer.id_)
                self.logger.debug('HELLO from %s, but we are already connected',
                                  peer.getId())
            if self._SayConnect(peer):
                self._AddPeer(peer)

    def peer_CONNECT(self, args):
        """
        A peer accepts our connection proposal.
        """
        # TODO: check that we sent a HELLO message to this peer
        peer = self._Peer(args)
        manager = self.peers

        if not manager.hasPeer(peer.id_):
            self._AddPeer(peer)
            # TODO: exchange service info and other stuff
            # TODO: notify

        else:
            self.logger.debug('reception of CONNECT but we are already connected to'
                              + peer.getId())

    def peer_CLOSE(self, args):
        """
        A peer closes or refuses a connection.
        """
        id_ = args.id_
        manager = self.peers
        if not manager.hasPeer(id_):
            self.logger.debug('CLOSE from %s, but we are not connected' % id_)
            return

        self._RemovePeer(manager.getPeer(id_))
        # TODO: check global connectivity

        # check what is our state
#         if manager.hasTooFewPeers():
#             self.updateAwarenessRadius()
#
#             # we don't have enough peers but our Global Connectivity is OK
#             if manager.hasGlobalConnectivity():
#                 self.node.setState(NotEnoughPeers())
#             # not enough peers + GC is NOK
#             else:
#                 self.searchPeers()
#                 self.node.setState(NotEnoughPeersAndNoGlobalConnectivity())
#         # we still have enough peers
#         else:
#             # but we don't have our GC
#             if not manager.hasGlobalConnectivity():
#                 self.searchPeers()
#                 self.node.setState(NoGlobalConnectivity())

    def peer_NEAREST(self, args):
        """
        A peer answers us a NEAREST message.
        """
        # Create a find nearest event
        id_ = args.remote_id
        if id_ in self.nearest_peers:
            self.logger.warning("Infinite loop in FINDNEAREST algorithm: %s"
                    % ", ".join(["'" + str(i) + "'" for i in self.nearest_peers]))
        else:
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
        self.scanned.neighbours = [peer]
        self.SetState(states.Scanning())

    def peer_FINDNEAREST(self, args):
        """
        A peer sends us a FINDNEAREST query.
        """
        id_ = args.id_
        target = args.position
        address = args.address
        nearest = self.peers.getClosestPeer(target, id_)

        # Check if I am not closer than nearestPeer
        if nearest.isCloser(self.node, targetPosition):
            message = self._PeerMessage('NEAREST', remote_peer=nearest)
        # I'm closer : send a best message
        else:
            message = self._PeerMessage('BEST')

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
        dist = Geometry.distance(self.node.position, peer.position)
        if dist > self.node.awareness_radius:
            return

        # we are only interested by entities that are not yet in our peer list
        if not manager.hasPeer(id_):
            # Check we don't have too many peers, or have worse peers than this one
            if manager.isPeerAccepted(peer):
                # Connect to this peer
                self._SayHello(args.address)

    def peer_AROUND(self, args):
        """
        A peer replies to us with an AROUND message.
        """
        peer = self._RemotePeer(args)
        # Current number of neighbours
        nb_peers = len(self.scanned_neighbours)
        # Last neighbour found
        last = self.scanned_neighbours[nb_peers - 1]

        our_pos = self.node.position
        best_pos = self.best_peer.position
        peer_pos = Geometry.relativePosition(peer.position, our_pos)
        best_distance = Geometry.distance(best_pos, our_pos)

        # Check if turn ends : we have at least 3 neighbours and either we got back
        # to the first peer (=> turn completed) or our last neighbour was in the
        # left half plane and this peer is in the right half plane
        if nb_peers > 2 and (peer.id_ == self.best_peer.id_ or
            (Geometry.inHalfPlane(best_pos, our_pos, last.position) !=
            Geometry.inHalfPlane(best_pos, our_pos, peer.pos))):
#             (not Geometry.inHalfPlane(best_pos, our_pos, last.position)
#             and Geometry.inHalfPlane(bestPos, nodePos, peerPos))):

            # Our awareness radius is the distance between us and our closest
            # neighbour, because we are sure to know all the entities between us
            # and the best.
            self.node.setAwarenessRadius(best_distance)

            # Try to connect with those peers
            for p in self.scanned_neighbours:
                self._SayHello(p.address)

            self.scanned_neighbours.clear()
            self.best_peer = None
            self.node.setState(Connecting())
            return

        # Add this peer to our list of neighbours
        self.scanned_neighbours.append(peer)

        # Send this peer a queryaround message
        message = self._PeerMessage('QUERYAROUND')
        message.args.best_id = peer.id_
        message.args.best_distance = Geometry.distance(self.node.position, peer.position)
        self._SendToPeer(peer, message)

    def peer_QUERYAROUND(self, args):
        """
        A peer sent us a QUERYAROUND message.
        """
        peer_id = args.id_
        best_id = args.best_id
        best_distance = args.best_distance
        manager = self.peers
        target = args.position
        nearest = manager.getClosestPeer(target, best_id)

        # Either:
        # 1. We have a peer closer to the target than the given Best-Distance
        if Geometry.distance(nearest.position, target) < best_distance:
            self.SendToAddress(args.address, self._PeerMessage('NEAREST', remote_peer=nearest))

        # 2. Or we find the closest peer around the target position and in the right half-plane
        else:
            # Search for a peer around target position
            around = manager.getPeerAround(target, source_id)
            if around is not None:
                self.SendToAddress(args.address, self._PeerMessage('AROUND', remote_peer=around))
            else:
                self.logger.debug('QUERYAROUND received, but no peer around position: %s' % str(target))

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
            self.logger.debug('UPDATE from %s, but we are not connected' % peer.id_)
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
                if entity.id_ == id_:
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
        self.logger.debug("Received kill message")
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

        # TODO: notify navigator that we lost connection with a peer
#         factory = EventFactory.getInstance(ControlEvent.TYPE)
#         dead = factory.createDEAD(id_)
#         self.node.dispatch(dead)


    #
    # Old stuff
    # TODO: remove
    #
    def searchPeers(self):
        """ Our Global connectivity is NOT OK, we have to search for new peers"""
        manager = self.node.getPeersManager()
        factory = EventFactory.getInstance(PeerEvent.TYPE)

        if manager.getNumberOfPeers() == 0:
            self.logger.info("All peers lost, relaunching JUMP algorithm")
            self.jump()

        else:
            # send msg SEARCH
            pair = manager.getBadGlobalConnectivityPeers()

            if pair:
                # send message to each entity
                searchClockWise = factory.createSEARCH(True)
                searchCounterclockWise = factory.createSEARCH(False)
                searchClockWise.setRecipientAddress(pair[0].getAddress())
                searchCounterclockWise.setRecipientAddress(pair[1].getAddress())
                self.node.dispatch(searchClockWise)
                self.node.dispatch(searchCounterclockWise)

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

