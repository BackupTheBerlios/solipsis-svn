## SOLIPSIS Copyright (C) France Telecom

## This file is part of SOLIPSIS.

##    SOLIPSIS is free software; you can redistribute it and/or modify
##    it under the terms of the GNU Lesser General Public License as published by
##    the Free Software Foundation; either version 2.1 of the License, or
##    (at your option) any later version.

##    SOLIPSIS is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU Lesser General Public License for more details.

##    You should have received a copy of the GNU Lesser General Public License
##    along with SOLIPSIS; if not, write to the Free Software
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

## ------------------------------------------------------------------------------
## -----                           Peer.py                                -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module defines the class for a neighbor.
##   A neighbor is an entity with which we are able to communicate.
##   This module provides all methods for the modifications of any variable
##   characteristic of an entity.
##   These modifications are capted by the Network module.
##
## ******************************************************************************

import random, string, time, logging, math

from solipsis.util.geometry import Geometry, Position
from solipsis.util.address import Address
from solipsis.util.exception import *
from solipsis.util.container import CcwList, DistList

from entity import Entity


class Peer(Entity):

    def __init__(self, *args, **kargs):
        """ Create a new Entity and keep information about it"""

        # call parent class constructor
        super(Peer, self).__init__(*args, **kargs)

        # last time when we saw this peer active
        self.activeTime = 0

        # two boolean variables indicating that
        # we received a message from this entity
        self.message_received = 1
        # we sent a message to this entity
        self.message_sent = 0

        # services provided by entity
        # {id_service: [desc_service, host, port], ...}
        self.services = {}

        # boolean confirmation of the accuracy of informations
        self.ok = 0

    def setLocalPosition(self, nodePosition):
        """ Set the local position in the coordinate system with origin nodePosition
        nodePosition: position of the node, e.g. [12,56]
        """
        self.localPosition = Geometry.localPosition(self.position, nodePosition)

    def setActiveTime(self, t):
        self.activeTime = t


    def isCloser(self, peerB, targetPosition):
        """ Return True if this peer is closer than peerB to targetPosition
        """
        d1 = Geometry.distance(self.position, targetPosition)
        d2 = Geometry.distance(peerB.position, targetPosition)

        return d1 < d2

class PeersManager(object):
    """ Manage all the neighbours of a node """

    # the number of neigbours should be inside a range of value
    # if exp =10 and percentage = 0.2, then we should have between 8 and 12 neighbours
    PERCENTAGE_VARIATION_EXPECTED_NEIGHBOURS = 0.2

    def __init__(self, node, params):
        """ Constructor
        node : node using this manager
        peersParams : initialization parameters of the peer manager, a list
        [entitiesFileName, maxPeers, logger]
        """
        self.node = node
        self.entitiesFileName = params.entities_file
        self.setExpectedPeers(params.expected_neighbours)

        self.logger = logging.getLogger("root")
        self.reset()

    def reset(self):
        # hash table of peers indexed by ID
        self.peers     = {}
        # clountercloclwise ordered list of peers
        self.ccwPeers  = CcwList()
        # distance ordered list of peers
        self.distPeers = DistList()

    def setExpectedPeers(self, nbPeers):
        maxCoeff = 1 + PeersManager.PERCENTAGE_VARIATION_EXPECTED_NEIGHBOURS
        minCoeff = 1 - PeersManager.PERCENTAGE_VARIATION_EXPECTED_NEIGHBOURS
        self.expectedPeers = nbPeers
        self.maxPeers = int(self.expectedPeers * maxCoeff)
        self.minPeers = int(self.expectedPeers * minCoeff)

    def getExpectedPeers(self):
        return self.expectedPeers

    def getRandomPeer(self):
        """ Return a peer randomly chosen from a file
        Read the entities file and return a random peer
        """
        lines = []
        try:
            f = file(self.entitiesFileName, 'r')
            # read file
            lines = f.readlines()
            f.close()

        except:
            self.logger.critical("Cannot read file " + self.entitiesFileName)
            raise

        # retrieve peer
        peer = ''
        # ignore blank lines in file
        while peer == '':
            peer = random.choice(lines).strip()

        host, stringPort = string.splitfields(peer)
        port = int(stringPort)
        addr = Address(host, port)
        p = Peer(address=addr)
        return p

    def hasPeer(self, id_):
        """ Check if the manager knwos this peer
        id : ID of the peer
        Returns True if the manager knows this peer"""
        return self.peers.has_key(id_)

    def addPeer(self, p):
        """ add a new peer
        p : a peer object
        Raises : DuplicateIdError, if a peer with the same id already exists
        EmptyIdError, if the ID of the peer is empty
        """
        referencePosition = self.node.position
        p.setLocalPosition(referencePosition)

        id_ = p.id_
        if not id_:
            raise EmptyIdError()

        if self.peers.has_key(id_):
            raise DuplicateIdError(id_)

        self.peers[id_] = p

        self.ccwPeers.insert(p)
        self.distPeers.insert(p)

    def removePeer(self, id_):
        """ remove a peer
        id : ID of the peer to remove
        Raises : UnknownIdError if the manager has no peer with this ID
        """

        p = self.getPeer(id_)
        del self.peers[id_]
        self.ccwPeers.delete(p)
        self.distPeers.delete(p)

    def recalculate(self):
        """ Recalculate topology information. This functions must be
        called when the node position has changed. """
        peers = self.enumeratePeers()
        self.reset()
        for p in peers:
            self.addPeer(p)

    def updatePeer(self, p):
        """ update information on a peer. """
        self.removePeer(p.id_)
        self.addPeer(p)

    def getPeer(self, peerid):
        """ Return the peer associated with this ID
        Raises : UnknownIdError if the manager has no peer with this ID
        """
        try:
            p = self.peers[peerid]
            return p
        except KeyError:
            raise UnknownIdError(peerid)

    def heartbeat(self, id_):
        """ Update status of a peer
        id : id of the peer that sent us a HEARTBEAT message
        """
        try:
            peer = self.peers[id_]
        except KeyError:
            pass
        else:
            peer.setActiveTime(time.time())

    def getPeerFromAddress(self, address):
        """ Get the peer with address 'address'
        address: address of the peer we are looking for - Address object
        Return : a peer, or None if no such peer was found
        """
        # Iterate through list of peers
        ids = self.peers.keys()
        for id_ in ids:
            p = self.peers[id_]
            if p.address.toString() == address.toString():
                return p

        # no peer with this address was found
        return None


    def getClosestPeer(self, target, emitter_id = None):
        """ Return the peer that is the closest to a target position
        target : a Position object
        """
        closestPeer = None
        for p in self.peers.values():
            if p.id_ == emitter_id:
                continue
            if closestPeer is None or p.isCloser(closestPeer, target):
                closestPeer = p

        return closestPeer


    def getPeerAround(self, targetPosition, emitter_id, isClockWise=True):
        """ Return the peer that is the closest to a target position and that
        is in the right half plane.
        targetPosition : target position which we are looking around
        isClockWise : boolean indicating if we we searching in the right or the
        left half-plane - optional
        Return : a peer or None if there is no peer in the half plane
        """
        found = False
        around = None
        distClosest = 0
        nodePosition = self.node.position
        for p in self.peers.values():
            if p.id_ == emitter_id:
                continue
            if Geometry.inHalfPlane(nodePosition, targetPosition,
                                    p.position) == isClockWise:
                # first entity in right half-plane
                if not found:
                    found = True
                    around = p
                    distClosest = Geometry.distance(targetPosition, p.position)
                else:
                    dist = Geometry.distance(targetPosition, p.position)
                    # this peer is closer
                    if dist < distClosest:
                        around = p
                        distClosest = dist

        return around

    def getMedianAwarenessRadius(self):
        """ Return the median value of the awareness radius of all our peers.

        This is needed during the connection phasis when we to guess a reasonnable
        value for our AR
        """
        arList = []
        for p in self.enumeratePeers():
            arList.append(p.awareness_radius)
        arList.sort()
        return arList[len(arList)//2]

    def getNumberOfPeers(self):
        return len(self.peers)

    def hasTooFewPeers(self):
        """ Check if we have too few neighbours
        Return True if we have too few peers"""
        return self.getNumberOfPeers() < self.minPeers

    def hasTooManyPeers(self):
        """ Check if we have too many neighbours
        Return True if we have too many peers"""
        return self.getNumberOfPeers() > self.maxPeers

    def isPeerAccepted(self, peer):
        """ Check, if a peer is the worst peer.

        """
        if not self.hasTooManyPeers():
            return True

        if self.hasPeer(peer.id_):
            worst = self.getWorstPeer()
        else:
            self.addPeer(peer)
            worst = self.getWorstPeer()
            self.removePeer(peer.id_)

        return worst is not peer

    def getWorstPeer(self):
        """ Choose a peer for removal. Removing this must NOT break the global
        connectivity rule.
        Return the worst or None if we cannot remove a peer
        """

        filter_list = self.necessaryPeers()
        i = len(self.distPeers) - 1
        while i >= 0:
            peer = self.distPeers.ll[i]
            if peer not in filter_list:
                return peer
            i -= 1
        return None

    def necessaryPeers(self):
        """ Returns the list of peers that are necessary for our global connectivity. """

        n = len(self.ccwPeers)
        if n < 4:
            return self.enumeratePeers()
        result = []
        for i in xrange(n):
            pred_pos = self.ccwPeers.ll[i - 2].position
            pos = self.node.getPosition()
            succ_pos = self.ccwPeers.ll[i].position
            if not Geometry.inHalfPlane(pred_pos, pos, succ_pos):
                result.append(self.ccwPeers.ll[i - 1])

        return result

    def enumeratePeers(self):
        """ return a list with all peers """
        return self.peers.values()

    def getBadGlobalConnectivityPeers(self):
        """ Check if global connectivity is ensured

        Return a pair of entities not respecting property or an empty set.
        First entity should be used to search clockwise and the second one ccw"""
        result = []

        nodePos = self.node.position
        length = self.getNumberOfPeers()

        if length == 0:
            return []

        if length == 1:
            (peer,) = self.peers.values()
            return [peer, peer]

        for index in range(length):
            ent = self.ccwPeers.ll[index]
            nextEnt = self.ccwPeers.ll[ (index+1) % length ]
            entPos = ent.position
            nextEntPos = nextEnt.position
            if not Geometry.inHalfPlane(entPos, nodePos, nextEntPos):
                return [ent, nextEnt]
        return []

    def hasGlobalConnectivity(self):
        """ Return True if Global connectivity rule is respected"""
        return self.getNumberOfPeers() > 0 and self.getBadGlobalConnectivityPeers() == []

    def computeAwarenessRadius(self):
        """ Based on curent the repartition of our peers (number, position),
        compute what should be our awareness radius
        Return an awareness radius (integer)
        """
        if self.hasTooManyPeers():
            offset = self.getNumberOfPeers() - self.maxPeers
            index = len(self.distPeers) - offset - 1
            # Get the average between the max inside distance and the min outside distance
            pos_outside = self.distPeers.ll[index].position
            pos_inside = self.distPeers.ll[index - 1].position
            dist_outside = Geometry.distance(self.node.position, pos_outside)
            dist_inside = Geometry.distance(self.node.position, pos_inside)
            return (dist_outside + dist_inside) // 2
        if self.hasTooFewPeers():
            fartherPeerPos = self.distPeers.ll[len(self.distPeers) - 1].position
            maxDist = Geometry.distance(self.node.position, fartherPeerPos)
            # Areal density
            return maxDist * math.sqrt(self.expectedPeers / self.getNumberOfPeers())
        else:
            fartherPeerPos = self.distPeers.ll[len(self.distPeers) - 1].position
            return Geometry.distance(self.node.position, fartherPeerPos)

