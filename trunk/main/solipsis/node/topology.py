
import logging
import math
import bisect
try:
    set
except:
    from sets import Set as set

from solipsis.util.exception import *


# class MockTopology(object):
#     def __init__(self, topology, manager):
#         self.topology = topology
#         self.manager = manager
#
#     def addPeer(self, peer)

class Topology(object):
    """
    Manage all the neighbours of a node.
    """

    world_size = 2**128

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
        self.normalize = (lambda x, lim=self.world_size // 2: (x + lim) % (lim + lim) - lim)
        self.max_angle = math.pi

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
            raise UnknownIdError(peerid)

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
        return not self.GetBadGlobalConnectivityPeers()

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
            self._InsertPeer(peer)

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
            if id_ not in excluded_peers and d >= min_distance:
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
        Returns the peers within a given distance (in distance order).
        """
        last = bisect.bisect(self.distance_peers, (distance, None))
        return [self.peers[id_] for (distance, id_) in self.distance_peers[:n]]

    def GetEnclosingDistance(self, n):
        """
        Get the best distance enclosing the N first peers and excluding the others.
        """
        dist_in = self.distance_peers[n][0]
        dist_out = self.distance_peers[n+1][0]
        return math.sqrt(dist_in * dist_out)

    #
    # Methods depending on a "target" position
    #

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
        return closest_id and (self.peers[closest_id], closest_distance) or None

    def GetPeerAround(self, target, emitter_id, clockwise=True, max_angle=None):
        """
        Return the peer that is the closest to a target position
        in the given angle from the origin.
        """
        sgn = clockwise and -1.0 or 1.0
        # We work in relative positions to the origin, which simplifies
        # calculations a bit since the origin is part of the vector product.
        xc, yc = self.origin
        _norm = self.normalize
        # xt, yt = vector(origin -> target)
        xt = _norm(target[0] - xc)
        yt = _norm(target[1] - yc)
        # dt = distance(origin, target)
        dt = math.sqrt(xt ** 2 + yt ** 2)
        if dt == 0.0:
            self.logger.warning("Asked for a peer around our own position")
        if max_angle is None:
            max_angle = self.max_angle
        # Minimum accepted cosine for angle between (origin -> target) and (peer -> target)
        min_cos = math.cos(max_angle)
        closest_id = None
        closest_distance = 0.0

        for id_, (x, y) in self.relative_positions:
            if p.id_ == emitter_id:
                continue
            # x, y = vector(origin -> peer), so:
            # xv, yv = vector(peer -> target)
            xv, yv = _norm(xt - x), _norm(yt - y)
            # Discard peers that are in the wrong half-plane
            if (xt * yv - xv * yt) * sgn <= 0.0:
                continue
            # dv = distance(peer, target)
            dv = math.sqrt(xv ** 2 + yv **2)
            # The dot product helps us calculate the cosine,
            # which is monotonous between 0 and PI
            dot_product = xt * yt + xv * yv
            # Check whether the angle is lower than max_angle
            if dot_product > dv * dt * min_cos:
                if closest_id is None or dv < closest_distance:
                    closest_id = id_
                    closest_distance = dv

        return closest_id and self.peers[closest_id] or None


    #
    # Private methods
    #
    def _InsertPeer(self, p):
        assert self.origin is not None, "topology origin is not set"
        xc, yc = self.origin
        id_ = p.id_

        # Relative position
        x, y = p.position.getCoords()
        x = self.normalize(x - xc)
        y = self.normalize(y - yc)

        # Distance
        d = math.sqrt(x**2 + y**2)
        if d == 0.0:
            self.logger.warning("Null distance for peer '%s', cannot insert" % str(id_))
            return False

        # Angle relatively to the [Ox) oriented axis
        # The result is between 0 and 2*PI
        if abs(x) > abs(y):
            angle = math.acos(x / d)
            if y < 0:
                angle = 2.0 * math.pi - angle
        else:
            angle = math.asin(y / d)
            if x < 0:
                angle = math.pi - angle

        self.relative_positions[id_] = (x, y)
        self.distances[id_] = d
        self.angles[id_] = angle
        bisect.insort(self.distance_peers, (d, id_))
        bisect.insort(self.angle_peers, (angle, id_))
        print self.distance_peers
        print self.angle_peers
        print
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
        self.distance_peers = []
        for p in self.peers.values():
            self._InsertPeer(p)

    def _NecessaryPeers(self, max_angle=None):
        """
        Returns id's of peers that are necessary for our global connectivity.
        """
        if len(self.peers) < 3:
            return self.peers.keys()
        if max_angle is None:
            max_angle = self.max_angle
        _angles = self.angle_peers
        pi2 = 2.0 * math.pi

        result = set()
        prev_angle, prev_id = _angles[-2]
        angle, id_ = _angles[-1]
        # For each peer, we check the angle between the predecessor and
        # the successor. If the angle is greater than the desired max angle,
        # then this peer is necessary.
        for next_angle, next_id in _angles:
            if (next_angle - prev_angle) % pi2 >= max_angle:
                result.add(id_)
            prev_angle, prev_id = angle, id_
            angle, id_ = next_angle, next_id

        return result

    #
    # Obsolete ??
    #
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

