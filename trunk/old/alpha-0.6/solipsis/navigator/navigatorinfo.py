import math

from solipsis.core.entity import Entity, Position
from solipsis.util.exception import InternalError
from solipsis.util.util import Geometry

class NavigatorInfo(object):
    """ NavigatorInfo contains all the informations related to the node
    * its characteristics : position, awareness radius, etc..
    * its peers
    * the services available for this node
    and the navigator state
    * what are the options : display avatar and/or display pseudo
    """
    def __init__(self, params):
        self._node = Entity()
        self._isConnected = False
        self._peers = {}
        self._options = {}
        self._params = params

        # get navigator specific parameters
        #self._options['dist_max'] = dist_max
        self._options['scale'] = params.scale
        self._options['coeff_zoom'] = params.zoom
        self._options['pseudo'] = params.pseudo
        self._options['display_pseudos'] = params.display_pseudos
        self._options['display_avatars'] = params.display_avatars


    def isConnected(self):
        return self._isConnected

    def addPeerInfo(self, peerInfo):
        """ Add information on a new peer
        peerInfo : a EntityInfo object
        """
        id = peerInfo.getId()
        relPos = Geometry.relativePosition(peerInfo.getPosition(),
                                           self._node.getPosition())
        peerInfo.setRelativePosition(relPos)
        assert( id <> '' )
        if not self._peers.has_key(id):
            self._peers[id] = peerInfo
        else:
            msg = 'Error - duplicate ID. Cannot add peer with id:' + id
            raise InternalError(msg)

    def updateNodeInfo(self, nodeinfo):
        self._node = nodeinfo
        self._node.setRelativePosition(Position(0,0))


    def getOption(self, optionName):
        return self._options[optionName]

    def arePseudosDisplayed(self):
        return self.getOption('display_pseudos')

    def areAvatarsDisplayed(self):
        return self.getOption('display_avatars')

    def setOption(self, section, option, value):

        self._options[option] = value
        self.params.setOption(section, option, value)

    def getMaxPosX(self):
        """ Return the X coordinate of the peer that is the farthest
        on the X axis.
        Return: a number >=0 """
        max = 0
        for p in self.enumeratePeers():
            absPosX = math.fabs(p.getRelativePosition().getPosX())
            if absPosX > max:
                max = absPosX

        return max

    def getMaxPosY(self):
        """ Return the Y coordinate of the peer that is the farthest
        on the Y axis.
        Return: a number >=0 """
        max = 0
        for p in self.enumeratePeers():
            absPosY = math.fabs(p.getRelativePosition().getPosY())
            if absPosY > max:
                max = absPosY

        return max

    def enumeratePeers(self):
        return self._peers.values()

    def getNode(self):
        return self._node
