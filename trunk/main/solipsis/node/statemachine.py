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

    all_peer_messages = [
        'AROUND',
        'BEST',
        'CONNECT',
        'CLOSE',
        'DETECT',
        'FINDNEAREST',
        'FOUND',
        'HEARTBEAT',
        'HELLO',
        'NEAREST',
        'QUERYAROUND',
        'SEARCH',
        'UPDATE',
    ]

    def __init__(self, reactor, node, logger=None):
        self.reactor = reactor
        self.node = node
        self.peers = self.node.getPeersManager()
        self.logger = logger or logging.getLogger("root")

        self.peer_dispatch_cache = {}
        self.peer_dispatch = None
        self.state = None

        self.nearest_peers = set()
        self.best_peer = None

    def SetState(self, state):
        self.state = state
        try:
            self.peer_dispatch = self.peer_dispatch_cache[state.__class__]
        except KeyError:
            d = {}
            try:
                messages = state.expected_messages
            except AttributeError:
                messages = self.all_peer_messages
            for request in state.expected_peer_messages:
                d[request] = getattr(self.state_machine, 'peer_' + request)
            self.peer_dispatch = d
            self.peer_dispatch_cache[state.__class__] = d

    def PeerMessageReceived(self, request, args):
        try:
            self.dispatch[request](args)
        except:
            self.logger.debug("Ignoring unexpected message '%s' in state '%s'" % (request, state.__class__.__name__))

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
            self._AddPeer(peer)
            self._SendToPeer(peer, self._PeerMessage('CONNECT'))

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

        self.removePeer(manager.getPeer(id_))
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
        A peer sent us a NEAREST message.
        """
        # Create a find nearest event
        id_ = args.remote_id
        if id_ in self.nearest_peers:
            self.logger.warning("Infinite loop in FINDNEAREST algorithm: %s"
                    % ", ".join(["'" + str(i) + "'" for i in self.nearest_peers]))
        else:
            address = args.remote_address
            self._SendMessage(address, self._PeerMessage('FINDNEAREST'))

    def peer_BEST(self, args):
        """
        A peer sent us a BEST message
        This is the default behaviour
        """
        self.timer.cancel()

        # Get the ID and the position of the BEST peer
        bestId = event.getArg(protocol.ARG_ID)
        bestPos = event.getArg(protocol.ARG_POSITION)
        bestAddress = event.getSenderAddress()

        # send a queryaround message
        bestDistance = Geometry.distance(self.node.getPosition(), bestPos)
        factory = EventFactory.getInstance(PeerEvent.TYPE)
        queryaround = factory.createQUERYAROUND(bestId, bestDistance)
        queryaround.setRecipientAddress(bestAddress)
        self.node.dispatch(queryaround)

        # Create a turning state and store the Best peer
        bestPeer = Peer(id=bestId, address=event.getSenderAddress(),
                        position=bestPos)
        scanning = Scanning()
        scanning.setBestPeer(bestPeer)

        # go to the Scanning state
        self.node.setState(scanning)

    def peer_FINDNEAREST(self, args):
        """ A peer sent us a FINDNEAREST message """
        source_id = event.getArg(protocol.ARG_ID)
        targetPosition = event.getArg(protocol.ARG_POSITION)
        nearestPeer = self.node.getPeersManager().getClosestPeer(targetPosition, source_id)

        factory = EventFactory.getInstance(PeerEvent.TYPE)

        # check if I am not closer than nearestPeer
        if (nearestPeer.isCloser(self.node, targetPosition)):
            response = factory.createNEAREST(nearestPeer)
        # I'm closer : send a best message
        else:
            response = factory.createBEST()

        response.setRecipientAddress(event.getSenderAddress())

        # send reply to remote peer
        self.node.dispatch(response)

    def peer_DETECT(self, args):
        """ Notification that a peer is moving towards us"""
        peer = event.createRemotePeer()
        id_ = peer.getId()
        manager = self.node.getPeersManager()
        # Sanity check 1: don't connect with ourselves
        if id_ == self.node.getId():
            return
        # Sanity check 2: don't connect with someone too far from us
        dist = Geometry.distance(self.node.getPosition(), peer.getPosition())
        ar = self.node.getAwarenessRadius()
        if dist > ar:
            return

        # we are only interested by entities that are not yet in our peer list
        if not manager.hasPeer(id_):
            # Check we don't have too many peers, or have worse peers than this one
            if manager.isPeerAccepted(peer):
                # Connect to this peer
                factory = EventFactory.getInstance(PeerEvent.TYPE)
                hello = factory.createHELLO()
                hello.setRecipientAddress(peer.getAddress())
                self.node.dispatch(hello)

    def peer_AROUND(self, args):
        """ A peer sent us an AROUND message """
        # cancel timer since we got our response
        self.timer.cancel()

        peer = event.createRemotePeer()
        # current number of neighbours
        nbNeighbours = len(self.neighbours)
        # last neighbour found
        last = self.neighbours[nbNeighbours-1]

        nodePos = self.node.getPosition() # our position
        bestPos = self.best.getPosition() # position of best node

        peerPos = Geometry.relativePosition(peer.getPosition(),
                                                 self.node.getPosition())

        # check if turn ends : we have at least 3 neighbours and either we got back
        # to the first peer (=> turn completed) or our last neighbour was in the
        # left half plane and this peer is in the right half plane
        if ( nbNeighbours > 2 ) and (peer.getId() == self.best.getId()) or (
            not Geometry.inHalfPlane(bestPos, nodePos, last.getPosition())
            and Geometry.inHalfPlane(bestPos, nodePos, peerPos) ):

            # Our awarenesse radius is the distance between us and our closest
            # neighbour, because we are sure to know all the entities between us
            # and the best.
            bestRelativePos = Geometry.relativePosition(bestPos, nodePos)
            minDistance = Geometry.distance(bestRelativePos, nodePos)
            self.node.setAwarenessRadius(minDistance)

            # register these peers with the peerManager and connect !
            manager = self.node.getPeersManager()
            for p in self.neighbours:
                factory = EventFactory.getInstance(PeerEvent.TYPE)
                hello = factory.createHELLO()
                hello.setRecipientAddress(p.getAddress())
                self.node.dispatch(hello)

            self.node.setState(Connecting())
        else:
            # add this peer to our list of neighbours
            self.addPeerAround(peer)

            # send this peer a queryaround message
            bestDist = Geometry.distance(bestPos, nodePos)
            factory = EventFactory.getInstance(PeerEvent.TYPE)
            queryaround = factory.createQUERYAROUND(self.best.getId(), bestDist)
            queryaround.setRecipientAddress(peer.getAddress())
            self.node.dispatch(queryaround)
            self.startTimer()

    def peer_QUERYAROUND(self, args):
        """ A peer sent us a QUERYAROUND message """
        #peer, idNearest, distNearest:
        source_id = event.getArg(protocol.ARG_ID)
        idNearest = event.getArg(protocol.ARG_BEST_ID)
        distNearest = event.getArg(protocol.ARG_BEST_DISTANCE)
        manager = self.node.getPeersManager()
        target = event.getArg(protocol.ARG_POSITION)
        closest = manager.getClosestPeer(target, source_id)

        factory = EventFactory.getInstance(PeerEvent.TYPE)
        # found a closest peer and this peer is a new one (it isn't idNearest moving
        # toward target position).
        if ( (Geometry.distance(closest.getPosition(), target) < distNearest) and
             closest.getId() <> idNearest ):
            # send a nearest message
            nearestEvent = factory.createNEAREST(closest)
            nearestEvent.setRecipientAddress(event.getSenderAddress())
            self.node.dispatch(nearestEvent)

        else:
            # search for a peer around target position
            around = manager.getPeerAround(target, source_id)
            if around is not None:
                aroundEvt = factory.createAROUND(around)
                aroundEvt.setRecipientAddress(event.getSenderAddress())
                self.node.dispatch(aroundEvt)
            else:
                self.logger.debug('no peer around position: ' + str(target))

    def peer_HEARTBEAT(self, args):
        """ reception of a message: HEARTBEAT, id"""
        self.node.getPeersManager().heartbeat(event.getArg(protocol.ARG_ID))

    def peer_UPDATE(self, args):
        """ A peer sent us an UPDATE message."""
        # extract the peer from the event
        peer = event.createPeer()
        id_ = peer.getId()

        manager = self.node.getPeersManager()
        if not manager.hasPeer(id_):
            self.logger.debug('UPDATE from %s, but we are not connected' % peer.getId())
            return

        # save peer old value
        oldPeer = manager.getPeer(event.getArg(protocol.ARG_ID))

        # update peer
        manager.updatePeer(peer)

        # notify the controller that a peer has changed
        ctlFact = EventFactory.getInstance(ControlEvent.TYPE)
        upd = ctlFact.createUPDATE(peer)
        self.node.dispatch(upd)

        oldPosition = oldPeer.getPosition()
        newPosition = peer.getPosition()
        nodePosition = self.node.getPosition()

        oldAR = oldPeer.getAwarenessRadius()
        newAR = peer.getAwarenessRadius()

        peerFct = EventFactory.getInstance(PeerEvent.TYPE)

        # peer position changed
        if not oldPosition == newPosition:
            # verify entities that could be interested by the entity id
            for ent in manager.enumeratePeers():
                if ent.getId() == id_:
                    continue
                itsAR = ent.getAwarenessRadius()

                # get distance between self and ent
                ourDist = Geometry.distance(nodePosition, ent.getPosition())

                # get distance between ent and entity id
                theirDist = Geometry.distance(ent.getPosition(), newPosition)

                # get old distance between ent and entity id
                theirOldDist = Geometry.distance(ent.getPosition(), oldPosition)

                if (theirDist < itsAR < theirOldDist) or \
                       (theirDist < ourDist < theirOldDist):
                    # modified entity enters in Awareness Area of ent
                    # OR moving entity is now closer than us to ent

                    # The moving peer is notified to a fixed entity
                    detect = peerFct.createDETECT(peer)
                    detect.setRecipientAddress(ent.getAddress())
                    self.node.dispatch(detect)

                elif oldAR < theirOldDist and newAR >= theirDist:
                    # The entity is notified to the moving peer
                    detect = peerFct.createDETECT(ent)
                    detect.setRecipientAddress(peer.getAddress())
                    self.node.dispatch(detect)

        # peer awareness radius changed
        if not oldAR == newAR:
            self.logger.debug('AR updated %d -> %d' % (oldAR, newAR))
            # verify entities that could be interested by the modified entity.
            for ent in manager.enumeratePeers():
                if ent.getId() == id_:
                    continue
                # get distance between ent and modified entity
                position = ent.getPosition()
                theirDist = Geometry.distance(position, newPosition)
                theirOldDist = Geometry.distance(position, oldPosition)
                self.logger.debug('peer %s: position (%s), old dist %d, new dist %d' %
                    (ent.getId(), str(position), theirDist, theirOldDist))

                if oldAR < theirOldDist and newAR >= theirDist:
                    # ent enter in Awareness Area of modified entity.
                    # DETECT message sent to modified entity.
                    detect = peerFct.createDETECT(ent)
                    detect.setRecipientAddress(peer.getAddress())
                    self.node.dispatch(detect)

    def peer_SEARCH(self, args):
        """ search an entity to restore the global connectivity of an other node
        reception of message: SEARCH, id, wise = 1 if counterclockwise"""
        id_ = event.getArg(protocol.ARG_ID)
        wise = event.getArg(protocol.ARG_CLOCKWISE)
        manager = self.node.getPeersManager()
        queryEnt = None

        try:
            # queryEnt is the querying entity
            queryEnt = manager.getPeer(id_)
        except UnknownIdError:
            self.logger.debug('Error, reception of SEARCH message with unknown ' +
                               'peer ID: ' + id_)
            return

        # update the status of querying entity
        manager.heartbeat(id_)

        around = manager.getPeerAround(queryEnt.getPosition(), id_, wise)

        # send message if an entity has been found.
        if around is not None:
            factory = EventFactory.getInstance(PeerEvent.TYPE)
            aroundEvt = factory.createFOUND(around)
            aroundEvt.setRecipientAddress(event.getSenderAddress())
            self.node.dispatch(aroundEvt)

    #
    # Control events
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
        """ Add a peer and send the necessary notification messages. """
        manager = self.node.getPeersManager()
        manager.addPeer(peer)
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        newPeerEvent = factory.createNEW(peer)
        self.node.dispatch(newPeerEvent)
        if type(self) == Idle:
            if manager.hasTooManyPeers():
                self.node.setState(TooManyPeers())

    def removePeer(self, peer):
        """ Remove a peer and send the necessary notification messages. """
        manager = self.node.getPeersManager()
        id_ = peer.getId()
        manager.removePeer(id_)

        # notify controler that we lost connection with a peer
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        dead = factory.createDEAD(id_)
        self.node.dispatch(dead)

    def sendUpdates(self):
        """ Send an UPDATE message to all our peers"""
        mng = self.node.getPeersManager()
        update = EventFactory.getInstance(PeerEvent.TYPE).createUPDATE()
        for p in mng.enumeratePeers():
            update.setRecipientAddress(p.getAddress())
            self.node.dispatch(update)

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

    def startTimer(self, timeout=None):
        if timeout is None:
            timeout=State.TIMEOUT
        self.timer = Timer(timeout, self.OnTimeOut)
        self.timer.start()

    def connectionError(self):
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        error = factory.createERROR('Error: cannot connect to Solipsis')
        self.node.setState(NotConnected())
        self.node.dispatch(error)

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

