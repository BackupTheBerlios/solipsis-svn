# pylint: disable-msg=C0103,C0101
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
"""base class for the world. Implements mechanism to manage peers and
includes callbacks to viewport (see viewport.py). DOES NOT INCLUDE
AVATARS."""

class Item(object):
    """
    An item points to a peer and contains information about how to draw it.
    """
    def __init__(self, peer):
        self.peer = peer
        self.Reset()
        
    def Reset(self):
        """Drawable ids in viewport"""
        self.label_id = None
        self.avatar_id = None

class BaseWorld:
    """
    This class represents the navigator's view of the world.
    It receives events from the remote connector and communicates
    with the viewport to display the world on screen.
    """
    
    def __init__(self, viewport):
        """
        Constructor.
        """
        # Solipsis ID of the node
        self.node_id = None
        self.node_item = None
        # Charset used for display
        self.charset = "utf-8"
        self.viewport = viewport
        # Cache of all encountered peers (useful for labels, avatars, etc.)
        self.item_cache = {}
        self.Reset()

    def Reset(self):
        """
        Reset the world (removing all peers).
        """
        # Dictionnary of peer ID -> world item
        self.items = {}
        self.viewport.Reset()
        if self.node_item:
            self.UpdateNode(self.node_item.peer)

    def AddPeer(self, peer):
        """
        Called when a new peer is discovered.
        """
        id_ = peer.id_
        try:
            item = self.item_cache[id_]
            item.peer = peer
        except KeyError:
            item = Item(peer)
        self.items[id_] = item
        x, y, z = peer.position.GetXYZ()
        self.viewport.AddObject(id_, None, position=(x, y))
        return item

    def RemovePeer(self, peer_id):
        """
        Called when a peer disappears.
        """
        try:
            item = self.items.pop(peer_id)
        except KeyError:
            return
        item.Reset()
        self.item_cache[peer_id] = item
        self.viewport.RemoveObject(peer_id)

    def _UpdateNode(self, node):
        """
        Update node's characteristics. This function is overridden by
        the specific navigators
        """
        # Reinitialize in case the node ID has changed
        if self.node_item is None:
            self._InitNode(node)
        elif self.node_id == node.id_:
            self.viewport.RemoveObject(self.node_id)
            self._InitNode(node)
        self.node_id = node.id_
        item = self.node_item
        item.peer = node
        return item

    def UpdateNode(self, node):
        """
        Called when the node's characteristics are updated. Updates
        node data and node position
        """
        self._UpdateNode(node)
        # Update node position
        self.UpdateNodePosition(node.position)

    def UpdateNodePosition(self, position, jump=False):
        """
        Called when the node's position is updated.
        """
        x, y = position.GetXY()
        if self.node_id is not None:
            self.viewport.MoveObject(self.node_id, position=(x, y))
        if jump:
            self.viewport.JumpTo((x, y))
        #~ else:
            #~ self.viewport.MoveTo((x, y))

    def UpdatePeer(self, peer):
        """
        Called when a peer has changed.
        """
        id_ = peer.id_
        try:
            item = self.items[id_]
        except KeyError:
            return
        old = item.peer
        item.peer = peer
        old_pos = old.position.GetXYZ()
        new_pos = peer.position.GetXYZ()
        if new_pos != old_pos:
            x, y, z = new_pos
            self.viewport.MoveObject(id_, position=(x, y))
        return (item, old)
            
    def GetNode(self):
        """
        Returns the node.
        """
        try:
            return self.node_item.peer
        except AttributeError:
            return None

    def GetPeer(self, peer_id):
        """
        Returns the peer with the given ID.
        """
        if peer_id == self.node_id:
            return self.node_item.peer
        elif peer_id in self.items:
            return self.items[peer_id].peer
        else:
            return None
    
    def GetAllPeers(self):
        """
        Returns a list of all peers.
        """
        return [item.peer for item in self.items.values()]

    def GetItemPseudo(self, id_):
        """
        Returns the pseudo corresponding to a specific item.
        """
        peer = self.GetPeer(id_)
        # TODO: properly handle the case when the hovered peer
        # has been removed from the viewport.
        if peer is not None:
            return peer.pseudo.encode(self.charset)
        return ""

    #
    # Private methods
    #
    
    def _InitNode(self, node):
        """
        Initialize the node and add it to the viewport.
        """
        self.node_item = Item(node)
        x, y = node.position.GetXY()
        self.viewport.AddObject(node.id_, None, position=(x, y))
        self.UpdateNodePosition(node.position, jump=True)

