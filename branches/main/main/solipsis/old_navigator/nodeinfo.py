from solipsis.engine.entity import Entity, Position
from solipsis.util.exception import SolipsisInternalError

class NodeInfo(Entity):
    """ NodeInfo contains all the informations related to the node
    * its characteristics : position, awareness radius, etc..
    * its peers
    * the services available for this node    
    """
    def __init__(self):
        Entity.__init__(self)
        self._isConnected = False
        self._peers = {}
        
    def isConnected(self):
        return self._isConnected

    def addPeerInfo(self, peerInfo):
        """ Add information on a new peer
        peerInfo : a EntityInfo object
        """
        id = peerInfo.getId()
        assert( id <> '' )
        if not self._peers.has_key(id):
            self._peers[id] = peerInfo
        else:
            msg = 'Error - duplicate ID. Cannot add peer with id:' + id
            raise SolipsisInternalError(msg)

    
    
