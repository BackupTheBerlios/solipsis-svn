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
        def __init__(self, peer):
            self.peer = peer
            # drawable ids in viewport
            self.label_id = None
            self.avatar_id = None
    
    def __init__(self, viewport):
        """
        Constructor.
        """
        UIProxyReceiver.__init__(self)
        self.charset = GetCharset()
        self.viewport = viewport
        self.repository = images.ImageRepository()
        self.avatars = AvatarRepository()
        self.avatars.AskNotify(UIProxy(self).UpdateAvatar)
        self.Reset()

    def Reset(self):
        """
        Reset the world (removing all peers).
        """
        self.node_id = None
        self.items = {}
        self.item_cache = {}
        self.viewport.Reset()

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
        if peer_id in self.items:
            self.item_cache[peer_id] = self.items[peer_id]
            del self.items[peer_id]
            self.viewport.RemoveObject(peer_id)

    def UpdateNode(self, node):
        """
        Called when the node's characteristics are updated.
        """
        self.node_id = node.id_
        x, y, z = node.position.GetXYZ()
        self.viewport.JumpTo((x, y))

    def UpdateNodePosition(self, position):
        """
        Called when the node's position is updated.
        """
        x, y, z = position.GetXYZ()
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

    def UpdateAvatar(self, peer_id):
        """
        Called when a peer's avatar has changed.
        """
        try:
            item = self.items[peer_id]
        except KeyError:
            return
        if item.avatar_id:
            self.viewport.RemoveDrawable(peer_id, item.avatar_id)
            item.avatar_id = None
        self._CreatePeerAvatar(item)

    def GetPeer(self, peer_id):
        """
        Returns the peer with the given ID.
        """
        try:
            return self.items[peer_id].peer
        except KeyError:
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
