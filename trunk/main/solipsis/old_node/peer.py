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
from solipsis.node.entity import Entity
from solipsis.util.geometry import Geometry, Position
from solipsis.util.address import Address

from solipsis.util.exception import *
from solipsis.util.container import CcwList, DistList


class Peer(Entity):

    def __init__(self, id="", address=None, position=Position(0,0), orientation=0,
                 awarenessRadius=0, calibre=0, pseudo=""):
        """ Create a new Entity and keep information about it"""

        # call parent class constructor
        Entity.__init__(self, id, position, orientation, awarenessRadius, calibre,
                        pseudo, address)

        # last time when we saw this peer active
        self.activeTime = 0

        # local position is the position of this peer using a coordinate system
        # centered on the position of the node
        # this value is set-up by the peer manager
        #self.localPosition = position

        # set the ID of this peer
        #id = self.createId()
        #self.setId(id)

        # position and relative position
        #relative_position = Function.relativePosition(self.position,
        # globalvars.me.position)
        #self.local_position = [ relative_position[0] - globalvars.me.position[0],
        #relative_position[1] - globalvars.me.position[1] ]

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
        self.localPosition = Geometry.localPosition(self.getPosition(), nodePosition)

    def setActiveTime(self, t):
        self.activeTime = t


    def isCloser(self, peerB, targetPosition):
        """ Return True if this peer is closer than peerB to targetPosition
        """
        d1 = Geometry.distance(self.getPosition(), targetPosition)
        d2 = Geometry.distance(peerB.getPosition(), targetPosition)

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
        referencePosition = self.node.getPosition()
        p.setLocalPosition(referencePosition)

        id_ = p.getId()
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
        peers = self.enumeratePeers