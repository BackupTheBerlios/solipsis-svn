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
import drawable
import images

# TODO: ask the avatar plugin to the app instead
from solipsis.services.avatar.repository import AvatarRepository


class World(object):
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
            # avatar hash
            #~ self.avatar_hash = ""
            # wx.Bitmaps
            #~ self.original_avatar = None
            #~ self.processed_avatar = None
    
    def __init__(self, viewport):
        self.charset = GetCharset()
        self.viewport = viewport
        self.repository = images.ImageRepository()
        self.avatars = AvatarRepository()
        self.Reset()

    def Reset(self):
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

    def _CreatePeerLabel(self, item):
        """
        Add the peer's pseudo to the viewport.
        """
        peer = item.peer
        d = drawable.Text(peer.pseudo)
        item.label_id = self.viewport.AddDrawable(peer.id_, d, (0, 20), 1)

    def _CreatePeerAvatar(self, item):
        """
        Add the peer'savatar to the viewport.
        """
        peer_id = item.peer.id_
        
        #~ # Load random PIL image or use existing one
        #~ try:
            #~ hash_ = item.avatar_hash
            #~ pil = self.pil_avatar_cache[hash_]
        #~ except KeyError:
            #~ pil = None
            #~ while pil is None:
                #~ data = self._GetRandomAvatarData()
                #~ print "** image load"
                #~ pil = self._PILFromData(data)
            #~ hash_ = self._HashAvatarData(data)
            #~ self.pil_avatar_cache[hash_] = pil

        #~ # Calculate wx.Bitmaps
        #~ item.avatar_hash = hash_
        #~ self._CalculatePeerAvatar(item)

        #~ d = drawable.Image(item.processed_avatar)
        bitmap = self.avatars.GetProcessedAvatarBitmap(peer_id)
        if bitmap is None:
            hash_ = self.avatars.GetRandomAvatarHash()
            self.avatars.BindHashToPeer(hash_, peer_id)
            bitmap = self.avatars.GetProcessedAvatarBitmap(peer_id)
        d = drawable.Image(bitmap)
        item.avatar_id = self.viewport.AddDrawable(peer_id, d, (0, 0), 0)
