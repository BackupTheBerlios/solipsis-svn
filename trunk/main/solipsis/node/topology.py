
import logging
import math
import bisect

from solipsis.util.exception import *


class Topology(object):
    """
    Manage all the neighbours of a node.
    """

    world_size = 2**128

    def __init__(self, params):
        """
        Initialize topology object.
        """
        self.logger = logging.getLogger("root")
        self.normalize = (lambda x, lim=float(self.world_size) / 2: (x + lim) % (lim + lim) - lim)

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

    def _InsertPeer(self, p):
        assert self.origin is not None, "topology origin is not set"
        xc, yc = self.origin
        id_ = p.id_

        # Relative position
        x = self.normalize(p.position.getPosX() - xc)
        y = self.normalize(p.position.getPosY() - yc)

        # Distance
        d = math.sqrt(x**2 + y**2)
        if d == 0.0:
            self.logger.warning("Null distance for peer '%s', cannot insert" % str(id_))
            return False

        # Angle relatively to the [Ox) oriented axis
        # The result is between -pi and +pi
        if abs(x) > abs(y):
            angle = math.acos(x / d)
            if y < 0:
                angle = -angle
        else:
            angle = math.asin(y / d)
            if x < 0:
                angle = math.pi - angle

        self.relative_positions[id_] = (x, y)
        self.distances[id_] = d
        self.angles[id_] = angle
        bisect.insort(self.distance_peers, (d, id_))
        bisect.insort(self.angle_peers, (angle, id_))
        return True

    def _ExtractPeer(self, id_):
        d = self.distances.pop(id_)
        angle = self.angles.pop(id_)
        self.distance_peers.remove((d, id_))
        self.angle_peers.remove((angle, id_))
        del self.relative_positions[id_]

    def _Recalculate(self):
        """
        Recalculate topology information. This function
        is called when the origin has changed.
        """
        self.relative_positions = {}
        self.distances = {}
        self.angles = {}
        self.angle_peers = []
        self.distance.peers = []
        for p in self.peers.values():
            self._InsertPeer(p)

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
        self._ExtractPeer(p.id_)
        self._InsertPeer(p)

    def GetPeer(self, id_):
        """
        Returns a peer according to its id.
        """
        try:
            p = self.peers[id_]
            return p
        except KeyError:
            raise UnknownIdError(peerid)

    def GetClosestPeer(self, target, exclude_id=None):
        """
        Returns the peer that is the closest to a target position.
        """
        closest_id = None
        closest_distance = 0.0
        xc, yc = self.origin
        xt, yt = target
        _norm = self.normalize
        l = [(_norm(x + xc - xt) ** 2 + _norm(y + yc - yt) ** 2, id_)
                for id_, (x, y) in self.relative_positions.iteritems()
                if id_ != exclude_id]
        closest_distance, closest_id = min(l)
        return closest_id and self.peers[closest_id] or None

    def GetNumberOfPeers(self):
        """
        Returns the current number of peers.
        """
        return len(self.peers)

    def EnumeratePeers(self):
        """
        Return as list with all peers.
        """
        return self.peers.itervalues()

    def NecessaryPeers(self, max_angle=None):
        """
        Returns id's of peers that are necessary for our global connectivity.
        """
        if len(self.peers) < 3:
            return self.peers.keys()
        if max_angle is None:
            max_angle = math.pi
        _angles = self.angle_peers
        pi2 = 2.0 * math.pi

        result = []
        prev_angle, prev_id = _angles[-2]
        angle, id_ = _angles[-1]
        # For each peer, we check the angle between the predecessor and
        # the successor. If the angle is greater than the desired max angle,
        # then this peer is necessary.
        for next_angle, next_id in _angles:
            if (next_angle - prev_angle) % pi2 >= max_angle:
                result.append(id_)
            prev_angle, prev_id = angle, id_
            angle, id_ = next_angle, next_id

        return result

    def HasGlobalConnectivity(self, max_angle=None):
        """
        Checks whether we currently have the global connectivity.
        """
        if len(self.peers) < 3:
            return False
        if max_angle is None:
            max_angle = math.pi
        _angles = self.angle_peers
        pi2 = 2.0 * math.pi
        prev_angle, id_ = _angles[-1]
        for angle, id_ in _angles:
            if (angle - prev_angle) % pi2 >= max_angle:
                return False
            prev_angle = angle
        return True


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

