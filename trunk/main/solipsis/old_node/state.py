
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
from internalevent import InternalEvent
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

    def HELLO(self, event):
        """ A new peer is contacting us """
        peer = event.createPeer()
        manager = self.node.getPeersManager()

        factory = EventFactory.getInstance(PeerEvent.TYPE)

        # We have now too many peers and this is the worst one
        if manager.isWorstPeer(peer):
            # refuse connection
            close = factory.createCLOSE()
            close.setRecipientAddress(peer.getAddress())
            self.node.dispatch(close)
        else:
            # check if we have not already connected to this peer
            if not manager.hasPeer(peer.getId()):
                manager.addPeer(peer)
                connect = factory.createCONNECT()
                connect.setRecipientAddress(peer.getAddress())
                self.node.dispatch(connect)
            else:
                self.logger.debug('HELLO from %s, but we are already connected',
                                  peer.getId())

    def CONNECT(self, event):
        """ reception of a connect message """
        # TODO :check that we sent a HELLO message to this peer
        peer = event.createPeer()
        mng = self.node.getPeersManager()
        if  not mng.hasPeer(peer.getId()):
            mng.addPeer(peer)
            factory = EventFactory.getInstance(ControlEvent.TYPE)
            newPeerEvent = factory.createNEW(peer)
            self.node.dispatch(newPeerEvent)

            # Give the list of our services to the peer
            for s in self.node.enumerateServices():
                factory = EventFactory.getInstance(PeerEvent.TYPE)
                srvEvt = factory.createADDSERVICE(s.getId())
                srvEvt.setRecipientAddress(event.getSenderAddress())
                self.node.dispatch(srvEvt)

    def DETECT(self, event):
        """ Notification that a peer is moving towards us"""
        peer = event.createRemotePeer()
        manager = self.node.getPeersManager()
        # we are only interested by entities that are not yet in our peer list
        if not manager.hasPeer(peer.getId()):

            # with this new peer, we now have too many peers
            # and the newly added peer is in fact our worst neighbour
            # so we remove this peer, and we don't contact this peer
            if manager.isWorstPeer(peer): pass
            else:
                # Connect to this peer
                factory = EventFactory.getInstance(PeerEvent.TYPE)
                hello = factory.createHELLO()
                hello.setRecipientAddress(peer.getAddress())
                self.node.dispatch(hello)

    def UPDATE(self, event):
        """ A peer sent us an UPDATE message."""
        # extract the peer from the event
        peer = event.createPeer()

        manager = self.node.getPeersManager()
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

                elif theirDist < newAR and oldAR < theirOldDist:
                    # The entity is notified to the moving peer
                    detect = peerFct.createDETECT(ent)
                    detect.setRecipientAddress(peer.getAddress())
                    self.node.dispatch(detect)

        # peer awareness radius changed
        if not oldAR == newAR:
            self.logger.debug('AR updated')
            # verify entities that could be interested by the modified entity.
            for ent in manager.enumeratePeers():
                # get distance between ent and modified entity
                theirDist = Geometry.distance(ent.getPosition(), newPosition)
                theirOldDist = Geometry.distance(ent.getPosition(), oldPosition)

                if oldAR < theirOldDist and newAR > theirDist:
                    # ent enter in Awareness Area of modified entity.
                    # DETECT message sent to modified entity.
                    detect = peerFct.createDETECT(ent)
                    detect.setRecipientAddress(peer.getAddress())
                    self.node.dispatch(de