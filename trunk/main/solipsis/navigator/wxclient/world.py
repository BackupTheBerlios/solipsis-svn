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

from PIL import Image, ImageDraw

from solipsis.util.wxutils import GetCharset
import drawable
import images


class World(object):
    """
    This class represents the navigator's view of the world.
    It receives events from the remote connector and communicates
    with the viewport to display the world on screen.
    """

    repository = images.ImageRepository()
    avatar_size = 40

    class Item(object):
        def __init__(self, peer):
            self.peer = peer
            self.label_id = None
            self.avatar_id = None
            self.original_avatar = None
            self.processed_avatar = None
    
    def __init__(self, viewport):
        self.charset = GetCharset()
        self.viewport = viewport
        self.Reset()

        f = 'avatars/dauphin.jpg'
        source = Image.open(f)
        s = self.avatar_size
        # Resize to desired target size
        resized = source.resize((s, s), Image.BICUBIC)
        # Build mask to shape the avatar inside a circle
        transparent = (0,255,0,0)
        opaque = (255,0,0,255)
        background = (0,0,255,0)
        mask = Image.new('RGBA', (s, s), transparent)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, s - 1, s - 1), outline=opaque, fill=opaque)
        # Build the final result
        target = Image.new('RGBA', (s, s), background)
        target.paste(resized, None, mask)
        #~ target.show()
        # Convert to wxBitmap
        r, g, b, alpha = target.split()
        rgb_data = Image.merge('RGB', (r, g, b))
        image = wx.EmptyImage(s, s)
        print len(rgb_data.tostring()), len(alpha.tostring())
        image.SetData(rgb_data.tostring())
        image.SetAlphaData(alpha.tostring())
        self.avatar_bitmap = wx.BitmapFromImage(image)

    def Reset(self):
        self.items = {}
        self.viewport.Reset()

    def AddPeer(self, peer):
        """
        Called when a new peer is discovered.
        """
        item = self.Item(peer)
        id_ = peer.id_
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
            del self.items[peer_id]
            self.viewport.RemoveObject(peer_id)

    def UpdateNode(self, node):
        """
        Called when the node's characteristics are updated.
        """
        x, y, z = node.position.GetXYZ()
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
        peer = item.peer
        d = drawable.Text(peer.pseudo)
        item.label_id = self.viewport.AddDrawable(peer.id_, d, (0, 20), 1)

    def _CreatePeerAvatar(self, item):
        peer = item.peer
        bitmap = self.repository.GetBitmap(images.IMG_AVATAR)
        #~ d = drawable.Image(bitmap)
        d = drawable.Image(self.avatar_bitmap)
        item.avatar_id = self.viewport.AddDrawable(peer.id_, d, (0, 0), 0)
