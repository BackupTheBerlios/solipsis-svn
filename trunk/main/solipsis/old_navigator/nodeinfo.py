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

    
    
