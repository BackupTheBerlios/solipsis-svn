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

import os
import sha
import random
import wx
from cStringIO import StringIO
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
    # hash -> PIL image
    pil_avatar_cache = {}
    # hash -> wx.Bitmap
    original_avatar_cache = {}
    # hash -> wx.Bitmap
    processed_avatar_cache = {}
    
    class Item(object):
        def __init__(self, peer):
            self.peer = peer
            # drawable ids in viewport
            self.label_id = None
            self.avatar_id = None
            # avatar hash
            self.avatar_hash = ""
            # wx.Bitmaps
            self.original_avatar = None
            self.processed_avatar = None
    
    def __init__(self, viewport):
        self.charset = GetCharset()
        self.viewport = viewport
        self.Reset()

        self.random_avatars = []
        avatar_dir = 'avatars'
        l = os.listdir(avatar_dir)
        for filename in l:
            if filename.startswith('.') or filename.startswith('_'):
                continue
            path = os.path.join(avatar_dir, filename)
            if not os.path.isfile(path):
                continue
            try:
                f = file(path, 'rb')
            except IOError, e:
                print str(e)
            else:
                self.random_avatars.append(f.read())
                f.close()


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
        peer_id = item.peer.id_
        #~ bitmap = self.repository.GetBitmap(images.IMG_AVATAR)
        
        # Load random PIL image or use existing one
        try:
            hash = item.avatar_hash
            pil = self.pil_avatar_cache[hash]
        except KeyError:
            pil = None
            while pil is None:
                data = self._GetRandomAvatarData()
                print "** image load"
                pil = self._PILFromData(data)
            hash = self._HashAvatarData(data)
            self.pil_avatar_cache[hash] = pil

        # Calculate wx.Bitmaps
        item.avatar_hash = hash
        self._CalculatePeerAvatar(item)
        
        d = drawable.Image(item.processed_avatar)
        item.avatar_id = self.viewport.AddDrawable(peer_id, d, (0, 0), 0)

    def _CalculatePeerAvatar(self, item):
        hash = item.avatar_hash
        try:
            original = self.original_avatar_cache[hash]
        except KeyError:
            pil = self.pil_avatar_cache[hash]
            print "** image convert 1"
            original = self._BitmapFromPIL(pil)
            self.original_avatar_cache[hash] = original
        try:
            processed = self.processed_avatar_cache[hash]
        except KeyError:
            pil = self.pil_avatar_cache[hash]
            print "** image convert 2"
            processed = self._BitmapFromPIL(self._ProcessAvatar(pil))
            self.processed_avatar_cache[hash] = processed
        item.original_avatar = original
        item.processed_avatar = processed

    def _PILFromData(self, data):
        """
        Converts raw image data (as JPEG, PNG, etc.) to PIL image.
        Returns None if conversion failed.
        """
        sio = StringIO()
        sio.write(data)
        sio.seek(0)
        try:
            im = Image.open(sio)
        except IOError, e:
            print str(e)
            im = None
        else:
            im.load()
        sio.close()
        return im

    def _BitmapFromPIL(self, im):
        bands = im.getbands()
        if bands != ('R', 'G', 'B', 'A'):
            im = im.convert('RGBA')
        r, g, b, alpha = im.split()
        rgb_data = Image.merge('RGB', (r, g, b))
        w, h = im.size
        wxim = wx.EmptyImage(w, h)
        #~ print len(rgb_data.tostring()), len(alpha.tostring())
        wxim.SetData(rgb_data.tostring())
        wxim.SetAlphaData(alpha.tostring())
        return wx.BitmapFromImage(wxim)

    def _HashAvatarData(self, data):
        return sha.new(data).digest()

    def _GetRandomAvatarData(self):
        return random.choice(self.random_avatars)

    def _ProcessAvatar(self, source):
        """
        Process the original avatar (as PIL image) and returns 
        its processed counterpart (as PIL image).
        """
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
        return target
