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

import logging
import math
import bisect

# Python 2.3 compatibility
try:
    set
except:
    from sets import Set as set

from solipsis.util.exception import *



class Topology(object):
    """
    Manage all the neighbours of a node.
    """

    world_size = 2 ** 128
    epsilon = 2.0 ** -50

    def __init__(self):
        """
        Initialize topology object.
        """
        self.logger = logging.getLogger("root")
        # Annoying precision warts that we should eliminate by changing
        # all coordinates to float
        if isinstance(self.world_size, long):
            self.half_world_size = self.world_size // 2
        else:
            self.half_world_size = self.world_size / 2.0
        self.normalize = (lambda x, lim=self.half_world_size: (x + lim) % (lim + lim) - lim)
        self.max_angle = math.pi
        self.origin = None

        self.Reset()

    def Reset(self, origin=None):
        # Hash table of peers (indexed by peer id)
        self.peers = {}
        # Relative positions (indexed by peer id)
        self.relative_positions = {}
        self.distances = {}
        self.angles = {}
        # Ordered list of (angle, peer id) tuples
        self.angle_peers  = []
        # Ordered list of (angle, peer id) tuples
        self.distance_peers = []

        if origin is not None:
            self.origin = origin

    def SetOrigin(self, (x, y)):
        """
        Sets (X, Y) coordinates of the origin. All calculations
        are relative to this reference point.
        """
        if self.origin != (x, y):
            self.origin = (x, y)
            self._Recalculate()

    def HasPeer(self, id_):
        """
        Checks whether the manager knows a peer.
        """
        return id_ in self.peers

    def RelativeDistance(self, (x, y)):
        """
        Relative distance from the given (x, y) to the origin.
        """
        xc, yc = self.origin
        x = self.normalize(x - xc)
        y = self.normalize(y - yc)
        return math.sqrt(x ** 2 + y ** 2)

    def Distance(self, (xa, ya), (xb, yb)):
        """
        Relative distance between two points.
        """
        x = self.normalize(xa - xb)
        y = self.normalize(ya - yb)
        return math.sqrt(x ** 2 + y ** 2)

    def AddPeer(self, p):
        """
        Adds a new peer.
        Returns True if the peer could be inserted, False otherwise.
        Currently, one reason that a peer cannot be inserted is that
        it has exactly the same position as the node.
        """
        id_ = p.id_
        if self.peers.has_key(id_):
            raise DuplicateIdError(id_)

        if not self._InsertPeer(p):
            return False

        self.peers[id_] = p
        return True

    def RemovePeer(self, id_):
        """
        Removes a peer.
        """
        if id_ in self.peers:
            self._ExtractPeer(id_)
            del self.peers[id_]
            return True
        else:
            return False

    def UpdatePeer(self, p):
        """
        Updates information about a peer.
        """
        self.RemovePeer(p.id_)
        self.AddPeer(p)

    def GetPeer(self, id_):
        """
        Returns a peer according to its id.
        """
        try:
            p = self.peers[id_]
            return p
        except KeyError:
            raise UnknownIdError(id_)

    def GetNumberOfPeers(self):
        """
        Returns the current number of peers.
        """
        return len(self.peers)

    def EnumeratePeers(self):
        """
        Return a list with all peers.
        """
        return self.peers.itervalues()

    def PeersSet(self):
        """
        Returns a set of all peer ids.
        """
        return set(self.peers.iterkeys())

    def HasGlobalConnectivity(self, max_angle=None):
        """
        Checks whether we currently have the global connectivity.
        """
        if len(self.peers) < 3:
            return False
        return not self.GetBadGlobalConnectivityPeers(max_angle)

    def GetBadGlobalConnectivityPeers(self, max_angle=None):
        """
        Checks whether global connectivity is ensured.

        Return a pair of entities not respecting property or None.
        First entity should be used to search counter-clockwise and the second one clockwise.
        """
        n = len(self.peers)
        if n == 0:
            return []
        if n == 1:
            (peer,) = self.peers.values()
            return [peer, peer]

        if max_angle is None:
            max_angle = self.max_angle

        _angles = self.angle_peers
        pi2 = 2.0 * math.pi
        prev_angle, prev_id = _angles[-1]
        for angle, id_ in _angles:
            if (angle - prev_angle) % pi2 >= max_angle:
                return [self.peers[prev_id], self.peers[id_]]
            prev_angle, prev_id = angle, id_
        return []

    def IsWorstPeer(self, peer):
        """
        Checks whether the given peer is the "worst" of all, that is:
        it would be the first to be removed if necessary.
        """
        id_ = peer.id_
        foreign_peer = id_ not in self.peers
        if foreign_peer:
            if not self._InsertPeer(peer):
                return True

        excluded_peers = self._NecessaryPeers()
        _distances = self.distance_peers
        worst_id = None
        # Find the farthest peer that can be removed
        for i in xrange(len(_distances) - 1, -1, -1):
            worst_id = _distances[i][1]
            if worst_id not in excluded_peers:
                break

        if foreign_peer:
            self._ExtractPeer(id_)
        return worst_id == id_

    def GetWorstPeers(self, n, min_distance=0.0):
        """
        Gets the N worst peers that are farther than a given distance.
        """
        excluded_peers = self._NecessaryPeers()
        _distances = self.distance_peers
        worst = []
        # Find the farthest peer that can be removed
        for i in xrange(len(_distances) - 1, -1, -1):
            d, id_ = _distances[i]
            if d < min_distance:
                break
            if id_ not in excluded_peers:
                worst.append(self.peers[id_])
                if len(worst) == n:
                    break
        return worst

    def GetNearestPeers(self, n):
        """
        Returns the N nearest peers to the origin (in distance order).
        """
        n = min(n, len(self.peers))
        return [self.peers[id_] for (distance, id_) in self.distance_peers[:n]]

    def GetPeersWithinDistance(self, distance):
        """
        Returns the peers within a given distance (in distance order if position is None).
        """
        last = bisect.bisect(self.distance_peers, (distance * (1.0 + self.epsilon), None))
        return [self.peers[id_] for (distance, id_) in self.distance_peers[:last]]

    def GetEnclosingDistance(self, n):
        """
        Get the best distance enclosing the N first peers and excluding the others.
        """
        dist_in = self.distance_peers[n-1][0]
        if n == len(self.distance_peers):
            return dist_in
        dist_out = self.distance_peers[n][0]
        return math.sqrt(dist_in * dist_out) * (1.0 + self.epsilon)


    #
    # Methods depending on a "target" position
    #

    def GetPeersInCircle(self, position, ra