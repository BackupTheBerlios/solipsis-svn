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
        idNearest = 