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

import wx

from solipsis.util.wxutils import GetCharset
from solipsis.util.uiproxy import UIProxy, UIProxyReceiver
import drawable
import images

# This is ugly, but hey, we need it :(
from solipsis.services.avatar.repository import AvatarRepository


class World(UIProxyReceiver):
    """
    This class represents the navigator's view of the world.
    It receives events from the remote connector and communicates
    with the viewport to display the world on screen.
    """

    class Item(object):
        """
        An item points to a peer and contains information about how to draw it.
        """
        def __init__(self, peer):
            self.peer = peer
            self.Reset()
        
        def Reset(self):
            # Drawable ids in viewport
            self.label_id = None
            self.avatar_id = None
    
    def __init__(self, viewport):
        """
        Constructor.
        """
        UIProxyReceiver.__init__(self)
        # Solipsis ID of the node
        self.node_id = None
        self.node_item = None
        # Charset used for display
        self.charset = GetCharset()
        self.viewport = viewport
        self.repository = images.ImageRepository()
        self.avatars = AvatarRepository()
        self.avatars.AskNotify(UIProxy(self).UpdateAvatars)
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
            item = self.Item(peer)
        self.items[id_] = item
        x, y, z = peer.position.GetXYZ()
        self.viewport.AddObject(id_, None, position=(x, y))
        self._CreatePeerLabel(item)
        self._CreatePeerAvatar(item)

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

    def UpdateNode(self, node):
        """
        Called when the node's characteristics are updated.
        """
        print "node update: ", node.pseudo
        # Reinitialize in case the node ID has changed
        if self.node_id == node.id_:
            self.viewport.RemoveObject(self.node_id)
            self._InitNode(node)
        elif self.node_item is None:
            self._InitNode(node)
        self.node_id = node.id_
        item = self.node_item
        item.peer = node
        # Update node pseudo
        if item.label_id:
            self.viewport.RemoveDrawable(node.id_, item.label_id)
            item.label_id = None
        self._CreatePeerLabel(item)
        # Create avatar if necessary
        if item.avatar_id:
            self.viewport.RemoveDrawable(peer_id, item.avatar_id)
            item.avatar_id = None
        self._CreatePeerAvatar(item)
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
        if peer.pseudo != old.pseudo:
            self.viewport.RemoveDrawable(id_, item.label_id)
            self._CreatePeerLabel(item)

    def UpdateAvatars(self, peer_list):
        """
        Called when some peers' avatars have changed.
        This function also handles the special case of the node itself.
        """
        for peer_id in peer_list:
            if peer_id == self.node_id:
                item = self.node_item
            elif peer_id in self.items:
                item = self.items[peer_id]
            else:
                continue
            if item.avatar_id:
                self.viewport.RemoveDrawable(peer_id, item.avatar_id)
                item.avatar_id = None
            self._CreatePeerAvatar(item)

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
        self.node_item = self.Item(node)
        x, y = node.position.GetXY()
        print "node index = ", self.viewport.AddObject(node.id_, None, position=(x, y))
        self.UpdateNodePosition(node.position, jump=True)

    def _CreatePeerLabel(self, item):
        """
        Add the peer's pseudo to the viewport.
        """
        peer = item.peer
        d = drawable.Text(peer.pseudo)
        item.label_id = self.viewport.AddDrawable(peer.id_, d, (0, 20), 1)

    def _CreatePeerAvatar(self, item):
        """
        Add the peer's avatar to the viewport.
        """
        peer_id = item.peer.id_
        # Try to get an existing bitmap for the peer
        bitmap = self.avatars.GetProcessedAvatarBitmap(peer_id)
        if bitmap is None:
            if 0:
                # Test code: choose random avatar if no other is available
                hash_ = self.avatars.GetRandomAvatarHash()
                self.avatars.BindHashToPeer(hash_, peer_id)
                bitmap = self.avatars.GetProcessedAvatarBitmap(peer_id)
            else:
                bitmap = self.repository.GetBitmap(images.IMG_AVATAR_GREY)
        d = drawable.Image(bitmap)
        item.avatar_id = self.viewport.AddDrawable(peer_id, d, (0, 0), 0)
