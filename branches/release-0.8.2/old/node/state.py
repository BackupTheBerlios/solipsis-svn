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

"""
This module contains the Finite State Machine (FSM)
that implements the Solipsis protocol.

There is a base class for every state called State,
and each distinct state is represented by a class derived
from State:

    - class Locating (State)
    - class NotConnected (State)
    - etc.
"""

from threading import Timer

from event import EventFactory
from peerevent import PeerEvent
from controlevent import ControlEvent
from peer import Peer
from solipsis.util.geometry import Geometry
from solipsis.util.exception import *

import protocol


class State(object):

    TIMEOUT = 2

    def __init__(self, node, logger):
        self.node = node
        self.logger = logger
        self.expectedMessages = {}

    def setNode(self, node):
        self.node = node

    def setLogger(self, logger):
        self.logger = logger

    def isExpected(self, msgName):
        return msgName in self.expectedMessages

    def activate(self):
        """ method called by the Node.setState. Sub-classes can override this
        method to do some initialization stuff.
        """
        pass

    def OnTimeOut(self):
        """ The timer expired, add a TIMER event to the event Queue.
        This method is called from a timer thread, queing a new event will ensure
        that the timer procedure will be executed from the main thread
        """
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        timerEvt = factory.createTIMER()
        # this event is directly added to the event queue (and not using the
        # node.dispatch() method) because we don't want this event to be processed
        # by the controller connector but by the node itself
        self.node.events.put(timerEvt)

    #
    # Peer events
    #

    def HELLO(self, event):
        """ A new peer is contacting us """
        peer = event.createPeer()
        manager = self.node.getPeersManager()

        factory = EventFactory.getInstance(PeerEvent.TYPE)

        # We have now too many peers and this is the worst one
        if not manager.isPeerAccepted(peer):
            # refuse connection
            close = factory.createCLOSE()
            close.setRecipientAddress(peer.getAddress())
            self.node.dispatch(close)
        else:
            # check if we have not already connected to this peer
            id_ = peer.getId()
            if manager.hasPeer(id_):
                manager.removePeer(id_)
                self.logger.debug('HELLO from %s, but we are already connected',
                                  peer.getId())
            self.addPeer(peer)
            connect = factory.createCONNECT()
            connect.setRecipientAddress(peer.getAddress())
            self.node.dispatch(connect)

    def CONNECT(self, event):
        """ reception of a connect message """
        # TODO :check that we sent a HELLO message to this peer
        peer = event.createPeer()
        mng = self.node.getPeersManager()
        if not mng.hasPeer(peer.getId()):
            self.addPeer(peer)

            # Give the list of our services to the peer
            for s in self.node.enumerateServices():
                factory = EventFactory.getInstance(PeerEvent.TYPE)
                srvEvt = factory.createADDSERVICE(s.getId())
                srvEvt.setRecipientAddress(event.getSenderAddress())
                self.node.dispatch(srvEvt)
        else:
            self.logger.debug('reception of CONNECT but we are already connected to'
                              + peer.getId())

    def CLOSE(self, event):
        """ Connection closed with one of our peers."""
        id_ = event.getArg(protocol.ARG_ID)
        manager = self.node.getPeersManager()
        if not manager.hasPeer(id_):
            self.logger.debug('CLOSE from %s, but we are not connected' % id_)
            return

        self.removePeer(manager.getPeer(id_))
        # check what is our state
        if manager.hasTooFewPeers():
            self.updateAwarenessRadius()

            # we don't have enough peers but our Global Connectivity is OK
            if manager.hasGlobalConnectivity():
                self.node.setState(NotEnoughPeers())
            # not enough peers + GC is NOK
            else:
                self.searchPeers()
                self.node.setState(NotEnoughPeersAndNoGlobalConnectivity())
        # we still have enough peers
        else:
            # but we don't have our GC
            if not manager.hasGlobalConnectivity():
                self.searchPeers()
                self.node.setState(NoGlobalConnectivity())

    def GETNODEINFO(self, event):
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        info = factory.createNODEINFO()
        self.node.dispatch(info)

    def NEAREST(self, event):
        """ A peer sent us a NEAREST message
        """
        # unexpected message, do not process it
        msg = 'NEAREST'
        if not self.isExpected(msg):
            self.logger.debug('Error, reception of a ' + msg + 'message in state '
                              + str(self.__class__))
            return

        if self.timer is not None:
            # cancel timer
            self.timer.cancel()

        # create a find nearest event
        address = event.getArg(protocol.ARG_REMOTE_ADDRESS)
        self.sendFindNearest(address)

    def FINDNEAREST(self, event):
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

    def DETECT(self, event):
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

    def QUERYAROUND(self, event):
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

    def HEARTBEAT(self, event):
        """ reception of a message: HEARTBEAT, id"""
        self.node.getPeersManager().heartbeat(event.getArg(protocol.ARG_ID))

    def UPDATE(self, event):
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

    def ADDSERVICE(self, event):
        """ A peer sent us a ADDSERVICE message """
        # get service information
        srvId = event.getArg(protocol.ARG_SERVICE_ID)
        srvDesc =event.getArg(protocol.ARG_SERVICE_DESC)
        srvAddress = event.getArg(protocol.ARG_SERVICE_ADDRESS)
        # See solipsis.navigator.service
        srv = Service(srvId, srvDesc, srvAddress)

        # update the corresponding peer
        id_ = event.getArg(protocol.ARG_ID)
        peer = self.node.getPeersManager().getPeer(id_)
        peer.addService(srv)

        # notify the controller that this peer has a new service available
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        addsrv = factory.createADDSERVICE(id_, srvId, srvDesc, srvAddress)
        self.node.dispatch(addsrv)

    def DELSERVICE(self, event):
        """ A peer sent us a DELSERVICE message.
        The described service is longer available for this peer
        """
        # get service ID
        srvId = event.getArg(protocol.ARG_SERVICE_ID)
        # update the corresponding peer
        id_ = event.getArg(protocol.ARG_ID)
        peer = self.node.getPeersManager().getPeer(id_)
        peer.delService(srvId)
        # notify the controller that this peer deleted a service
        factory = EventFactory.getInstance(ControlEvent.TYPE)
        delsrv = factory.createDELSERVICE(id_, srvId)
        self.node.dispatch(delsrv)

    def SEARCH(self, event):
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

    def MOVE(self, event):
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

    def KILL(self, event):
        self.logger.debug("Received kill message")
        self.node.exit()

    def ABORT(self, event):
        self.node.alive = False
        print "\nFatal error: " + event.getArg('Message') + "\nAborting"
        self.node.dispatch(event)


    def SET(self, event):
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

    def addPeer(self, peer):
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

    def sendFindNearest(self, peerAddress):
        """ Send a FINNEAREST event and return the timer object assocoiated
        with this request
        peerAddress : network address of the peer who will receive this request
        """
        # create a findnearest event
        factory = EventFactory.getInstance(PeerEvent.TYPE)
        findnearest = factory.createFINDNEAREST()
        findnearest.setRecipientAddress(peerAddress)
        self.node.dispatch(findnearest)

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


class NotConnected(State):
    """ NOT CONNECTED: Initial state of the node.

    The node is not connected to any entity.
    The only allowed action is to JUMP to an absolute position in the world.
    The JUMP action will trigger a Solipsis connection to a first peer, and
    then the find-nearest-neighbour algorithm so as to connect to the right peers
    according to the desired JUMP position.
    """

    def __init__(self):
        self.expectedMessages = [ 'MOVE', 'KILL', 'SET']

    def activate(self):
        pass


class Locating(State):
    """ TRACKING: The node has attempted a first connection to the world and
    is now running the find-nearest-neighbour algorithm.

    This means the node is expecting a BEST message from its latest peer.
    """

    # maximum number of times we will try to connect
    MAX_CONNECTIONS_ATTEMPTS = 5

    def __init__(self):
        self.expectedMessages = ['NEAREST', 'BEST', 'TIMER', 'KILL', 'MOVE', 'SET']
        self.connectionAttempts = 0
        # timer object associated with the curent findnearest request - needed
        # to cancel the timer when we receive a response
        self.startTimer()

    def activate(self):
        pass

    def NEAREST(self, event):
        super(Locating, self).NEAREST(event)
        self.startTimer()

    def BEST(self, event):
        """ A peer sent us a BEST message
        This is the default behaviour
        """
        # unexpected message, do not process it
        msg = 'BEST'
        if not self.isExpected(msg):
            self.logger.debug('Error, reception of a ' + msg + 'message in state '
                              + str(self.__class__))
            return

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

    def TIMER(self, event):
        """ Timeout while waiting for an answer for a FINDNEAREST request """
        self.connectionAttempts += 1

        # connection failed
        if self.connectionAttempts > self.MAX_CONNECTIONS_ATTEMPTS:
            self.connectionError()

        # retry connecting
        manager = self.node.getPeersManager()
        peer = manager.getRandomPeer()
        self.sendFindNearest(peer.getAddress())
        self.startTimer()

class Scanning(State):
    """ SCANNING: The node has found its place in the world. It is asking its
    neighbours to notify it of other neighbours so as to have a complete
    knowledge of its the local neighborhood.
    """

    def __init__(self):
        self.expectedMessages = ['AROUND', 'NEAREST', 'KILL', 'MOVE', 'SET']
        self.best = None
        self.neighbours = []
        self.startTimer()

    def activate(self):
        self.logger.debug('Scanning')

    def setBestPeer(self, peer):
        """ Store information on who we currently think is the closest peer to
        our target position.

        peer : the best peer (the closest to our target position)"""
        # store this peer
        self.best = peer
        # add this peer to the list of the peers around our target position
        self.addPeerAround(peer)

    def addPeerAround(self, peer):
        self.neighbours.append(peer)

    def AROUND(self, event):
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

    def NEAREST(self, event):
        """ While scanning around our target a position, a peer informs us that
        there exists a peer that is closer than our current best.
        """
        peerPos = event.getArg(protocol.ARG_REMOTE_POSITION)

        # check if this peer is closer than our current best
        currentBestDistance = Geometry.distance(self.best.getPosition(),
                                                self.node.getPosition())
        newDist = Geometry.distance(peerPos, self.node.getPosition())
        if newDist < currentBestDistance:
            super(Scanning,self).NEAREST(event)
            self.node.setState(Locating())

    def TIMER(self, event):
        """ We have a timeout for our last queryaround message """
        # retry going around from our current best peer
        import exceptions
        raise exceptions.NotImplementedError()

class Connecting(State):
    """ CONNECTING: The node has found all the neigbours around its position.
    It is now attempting to connect to these peers.
    """

    # in the connecting state we increase our awareness radius in a linear way
    PERCENTAGE_AR_INCREASE = 0.3
    # maximum number of times we will try to incerease our awareness radius
    MAX_AR_INCREASE_ATTEMPTS = 10

    def __init__(self):
        self.expectedMessages = ['CONNECT', 'SERVICE', 'TIMER']
        self.nbArIncrease = 0
        self.startTimer()

    def activate(self):
        pass

    def CONNECT(self, event):
        super(Connecting, self).CONNECT(event)
        mng = self.node.getPeersManager()

        # we have now reached our number of expected neighbours
        if not mng.hasTooFewPeers():
            self.timer.cancel()
            if not mng.hasGlobalConnectivity():
                self.searchPeers()
                self.node.setState(NoGlobalConnectivity())
            else:
                # start periodic tasks and go to Idle state
                self.node.startPeriodicTasks()
                self.node.setState(Idle())

    def TIMER(self, event):
        """ The timer expired."""
        mng = self.node.getPeersManager()
        # we got 0 responses: we have a big problem !
        if mng.getNumberOfPeers() == 0:
            self.connectionError()
        elif self.nbArIncrease < Connecting.MAX_AR_INCREASE_ATTEMPTS:
            # first time we increase our AR, try to guess a good value
            if self.nbArIncrease == 0:
                self.node.setAwarenessRadius(mng.getMedianAwarenessRadius())
            else:
                # increase awareness radius
                ar = self.node.getAwarenessRadius()
                factor = 1 + Connecting.PERCENTAGE_AR_INCREASE
                self.node.setAwarenessRadius(int(ar*factor))

            # notify our peers
            self.sendUpdates()
            # relaunch a timer
            self.startTimer()
            self.nbArIncrease = self.nbArIncrease + 1
        else:
            self.connectionError()

class Idle(State):
    """ IDLE: the node has a stable position and is fully connected to its local neighborhood.
    """

    def __init__(self):
        self.expectedMessages = ['HELLO', 'DETECT', 'ADDSERVICE', 'FINDNEAREST'
                                 'QUERYAROUND', 'DELSERVICE']

    def activate(self):
        pass


class NoGlobalConnectivity(State):
    """ Our global connectivity rule is not satisfied """
    def __init__(self):
        self.expectedMessages = ['FOUND', 'HELLO', 'DETECT', 'ADDSERVICE', 'FINDNEAREST'
                                 'QUERYAROUND', 'DELSERVICE']
        self.startTimer()

    def activate(self):
        pass

    def FOUND(self, event):
        """ an entity detected in an empty sector
        reception of message: FOUND"""
        peer = event.createRemotePeer()
        manager = self.node.getPeersManager()
        id_ = peer.getId()
        factory = EventFactory.getInstance(PeerEvent.TYPE)

        # verify that new entity is neither self neither an already known entity.
        if id_ != self.node.getId() and not manager.hasPeer(id_):
            hello = factory.createHELLO()
            hello.setRecipientAddress(peer.getAddress())
            self.node.dispatch(hello)

    def CONNECT(self, event):
        self.timer.cancel()
        super(NoGlobalConnectivity, self).CONNECT(event)
        mng = self.node.getPeersManager()

        # check whether we now have our global connectivity
        if not mng.hasGlobalConnectivity():
            self.startTimer()
            self.searchPeers()
        else:
            self.node.setState(Idle())

    def HELLO(self, event):
        self.timer.cancel()
        super(NoGlobalConnectivity, self).HELLO(event)
        mng = self.node.getPeersManager()

        # check whether we now have our global connectivity
        if not mng.hasGlobalConnectivity():
            self.startTimer()
            self.searchPeers()
        else:
            self.node.setState(Idle())

    def TIMER(self, event):
        """ Timeout : we still don't have our GC"""
        # restart the timer
        self.startTimer()
        # search peers
        self.searchPeers()


class NotEnoughPeers(State):
    """ We do NOT have enough peers."""
    def __init__(self):
        self.expectedMessages = ['FOUND', 'HELLO', 'DETECT', 'ADDSERVICE', 'FINDNEAREST'
                                 'QUERYAROUND', 'DELSERVICE']
        self.startTimer()

    def activate(self):
        pass

    def CONNECT(self, event):
        super(NotEnoughPeers, self).CONNECT(event)
        mng = self.node.getPeersManager()

        # we have now reached our number of expected neighbours
        if not mng.hasTooFewPeers():
            self.timer.cancel()
            self.node.setState(Idle())

    def HELLO(self, event):
        super(NotEnoughPeers, self).HELLO(event)
        mng = self.node.getPeersManager()

        # we have now reached our number of expected neighbours
        if not mng.hasTooFewPeers():
            self.timer.cancel()
            self.node.setState(Idle())

    def TIMER(self, event):
        """ Timeout : we still don't have enough peers"""
        self.startTimer()
        self.updateAwarenessRadius()



class NotEnoughPeersAndNoGlobalConnectivity(State):
    """ We don't have enough peers and the Global connectivity rule is
    not satisfied"""
    def __init__(self):
        self.expectedMessages = ['FOUND', 'HELLO', 'DETECT', 'ADDSERVICE', 'FINDNEAREST'
                                 'QUERYAROUND', 'DELSERVICE']
        self.startTimer()

    def activate(self):
        self.logger.debug('NotEnoughPeersAndNoGlobalConnectivity')

    def CONNECT(self, event):
        super(NotEnoughPeersAndNoGlobalConnectivity, self).CONNECT(event)
        mng = self.node.getPeersManager()

        # we have now reached our number of expected neighbours
        if not mng.hasTooFewPeers():
            self.timer.cancel()
            # our GC is also OK go to Idle state
            if mng.hasGlobalConnectivity():
                self.node.setState(Idle())
            # GC is still NOK : go to NoGlobalConnectivity state
            else:
                self.searchPeers()
                self.node.setState(NoGlobalConnectivity())
        # we still don't have enough peers
        else:
            # but now our GC is OK : go to state NotEnoughPeers
            if mng.hasGlobalConnectivity():
                self.timer.cancel()
                self.updateAwarenessRadius()
                self.node.setState(NotEnoughPeers())

    def HELLO(self, event):
        super(NotEnoughPeersAndNoGlobalConnectivity, self).HELLO(event)
        mng = self.node.getPeersManager()

        # we have now reached our number of expected neighbours
        if not mng.hasTooFewPeers():
            self.timer.cancel()
            # our GC is also OK go to Idle state
            if mng.hasGlobalConnectivity():
                self.node.setState(Idle())
            # GC is still NOK : go to NoGlobalConnectivity state
            else:
                self.searchPeers()
                self.node.setState(NoGlobalConnectivity())
        # we still don't have enough peers
        else:
            # but now our GC is OK : go to state NotEnoughPeers
            if mng.hasGlobalConnectivity():
                self.timer.cancel()
                self.updateAwarenessRadius()
                self.node.setState(NotEnoughPeers())

    def TIMER(self, event):
        """ Timeout : we still don't have enough peers"""
        self.startTimer()
        self.updateAwarenessRadius()
        self.searchPeers()

class TooManyPeers(State):
    """ We have too many peers """
    def __init__(self):
        self.expectedMessages = ['FOUND', 'HELLO', 'DETECT', 'ADDSERVICE', 'FINDNEAREST'
                                 'QUERYAROUND', 'DELSERVICE']
        self.startTimer()

    def TIMER(self, event):
        """ Timeout : check if we still have too many peers peers"""
        manager = self.node.getPeersManager()
        factory = EventFactory.getInstance(PeerEvent.TYPE)

        while manager.getNumberOfPeers() > manager.getExpectedPeers():
            peer = manager.getWorstPeer()
            close = factory.createCLOSE()
            close.setRecipientAddress(peer.getAddress())
            self.node.dispatch(close)
            self.removePeer(peer)

        self.updateAwarenessRadius()
        self.node.setState(Idle())

