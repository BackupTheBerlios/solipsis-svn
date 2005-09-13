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
from cStringIO import StringIO

import wx
from PIL import Image, ImageDraw

from solipsis.util.singleton import Singleton


class _AvatarRepository(object):
    """
    This class stores avatars, binds them to an arbitrary number of peer IDs,
    and caches processed versions of the avatars (wx.Bitmaps)
    """

    def __init__(self):
        """
        Create avatar repository.
        """
        # Size of processed avatars
        self.processed_avatar_size = 40

        # peer ID -> avatar hash
        self.peer_avatar_hashes = {}

        # hash -> PIL image
        self.pil_avatar_cache = {}
        # hash -> wx.Bitmap
        self.original_avatar_cache = {}
        # hash -> wx.Bitmap
        self.processed_avatar_cache = {}

        # Callables for avatar change notification
        self.event_sinks = []

        self.builtin_avatars = None
        # File containing default avatar if not defined
        self.default_avatar_hash = None
        self.default_avatar_file = "img/ghost.png"


    def AskNotify(self, callback):
        """
        Ask to be notified when an peer's avatar is changed.
        The callback will be notified with a list of peer_ids.
        """
        self.event_sinks.append(callback)

    def GetRandomAvatarHash(self):
        """
        Get a random avatar hash from the default avatar list.
        """
        self._LoadDefaultAvatars()
        return random.choice(self.builtin_avatars)

    def BindHashToPeer(self, hash_, peer_id):
        """
        Tries to add an avatar based on its hash value.
        Returns True if ok, False if the hash was not found.
        (if hash is None, use the default avatar)
        """
        self._LoadDefaultAvatars()
        if hash_ is None:
            hash_ = self.default_avatar_hash
        try:
            pil = self.pil_avatar_cache[hash_]
        except KeyError:
            # If the avatar is not known yet, remove the former binding
            # from the peer -> avatar table
            try:
                del self.peer_avatar_hashes[hash_]
            except KeyError:
                pass
            return False
        self.peer_avatar_hashes[peer_id] = hash_
        self._Notify([peer_id])
        return True

    def BindAvatarToPeer(self, data, peer_id):
        """
        Adds an avatar based on its binary data.
        Returns its hash.
        """
        # Get the already cached version, or create it if it doesn't exist
        hash_ = self._HashAvatarData(data)
        try:
            pil = self.pil_avatar_cache[hash_]
        except KeyError:
            self._AddAvatar(data, hash_)
        self.peer_avatar_hashes[peer_id] = hash_
        self._Notify([peer_id])
        return hash_

    def GetAvatarBitmap(self, peer_id):
        """
        Returns a peer's avatar as a wxBitmap, or None if not found.
        """
        try:
            hash_ = self.peer_avatar_hashes[peer_id]
        except KeyError:
            return None
        self._CalculateAvatar(hash_)
        return self.original_avatar_cache[hash_]

    def GetProcessedAvatarBitmap(self, peer_id):
        """
        Returns a peer's processed avatar as a wxBitmap, or None if not found.
        """
        try:
            hash_ = self.peer_avatar_hashes[peer_id]
        except KeyError:
            return None
        self._CalculateAvatar(hash_)
        return self.processed_avatar_cache[hash_]

    def GetProcessedAvatarSize(self):
        return self.processed_avatar_size

    def SetProcessedAvatarSize(self, size):
        self.processed_avatar_size = size
        # Clear the cache
        self.processed_avatar_cache.clear()
        # Notify all sinks so that they redisplay everything
        self._Notify(self.peer_avatar_hashes.keys())

    #
    # Private functions
    #
    def _Notify(self, peer_list):
        """
        Notify all event sinks that some avatars have been updated.
        """
        if len(peer_list):
            for sink in self.event_sinks:
                sink(peer_list)

    def _AddAvatar(self, data, hash_=None):
        """
        Adds the avatar data to the internal cache and returns its hash.
        """
        if hash_ is None:
            hash_ = self._HashAvatarData(data)
        pil = self._PILFromData(data)
        self.pil_avatar_cache[hash_] = pil
        return hash_

    def _CalculateAvatar(self, hash_):
        """
        Make sure the wxBitmap versions of the avatar are up-to-date.
        """
        try:
            original = self.original_avatar_cache[hash_]
        except KeyError:
            pil = self.pil_avatar_cache[hash_]
            original = self._BitmapFromPIL(pil)
            self.original_avatar_cache[hash_] = original
        try:
            processed = self.processed_avatar_cache[hash_]
        except KeyError:
            pil = self.pil_avatar_cache[hash_]
            pil2 = self._ProcessAvatar(pil)
            processed = self._BitmapFromPIL(pil2)
            self.processed_avatar_cache[hash_] = processed

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
            print "Failed to open image with PIL library from raw data: '%s'" % str(e)
            print "(image is %d bytes long)" % len(data)
            im = None
        else:
            im.load()
        sio.close()
        del sio
        return im

    def _ProcessAvatar(self, source):
        """
        Process the original avatar (as PIL image) and returns
        its processed counterpart (as PIL image).
        """
        # 1. Crop a square area inside the image
        w, h = source.size
        crop_offset = (max(w, h) - min(w, h)) // 2
        if w > h:
            crop_box = (crop_offset, 0, w - crop_offset, h)
        else:
            crop_box = (0, crop_offset, w, h - crop_offset)
        cropped = source.crop(crop_box)

        # 2. Resize to desired target size
        s = min(self.processed_avatar_size, w, h)
        resized = cropped.resize((s, s), Image.ANTIALIAS)

        # 3. Build mask to shape the avatar inside a circle
        transparent = (0,255,0,0)
        opaque = (255,0,0,255)
        background = (0,0,255,0)
        mask = Image.new('RGBA', (s, s), transparent)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, s - 1, s - 1), outline=opaque, fill=opaque)

        # 4. Build the final result by masking
        target = Image.new('RGBA', (s, s), background)
        target.paste(resized, None, mask)

        return target

    def _BitmapFromPIL(self, im):
        """
        Creates a wxBitmap from a PIL image.
        """
        bands = im.getbands()
        if bands != ('R', 'G', 'B', 'A'):
            im = im.convert('RGBA')
        r, g, b, alpha = im.split()
        rgb_data = Image.merge('RGB', (r, g, b))
        w, h = im.size
        wxim = wx.EmptyImage(w, h)
        wxim.SetData(rgb_data.tostring())
        wxim.SetAlphaData(alpha.tostring())
        return wx.BitmapFromImage(wxim)

    def _HashAvatarData(self, data):
        """
        Computes the avatar's hash from its data.
        """
        return sha.new(data).hexdigest()

    def _LoadAvatar(self, path):
        """
        Load an avatar contained in a file.
        """
        try:
            f = file(path, 'rb')
        except (IOError, OSError), e:
            print "Failed to load '%s':" % path
            print str(e)
            return None
        else:
            data = f.read()
            f.close()
            hash_ = self._AddAvatar(data)
            return hash_

    def _LoadDefaultAvatars(self):
        """
        Loads binary contents of default avatars.
        """
        # If already loaded, do nothing
        if self.builtin_avatars is not None:
            return
        self.builtin_avatars = []
        avatar_dir = 'avatars'
        l = os.listdir(avatar_dir)
        for filename in l:
            if filename.startswith('.') or filename.startswith('_'):
                continue
            path = os.path.join(avatar_dir, filename)
            if not os.path.isfile(path):
                continue
            hash_ = self._LoadAvatar(path)
            if hash_:
                self.builtin_avatars.append(hash_)
        self.default_avatar_hash = self._LoadAvatar(self.default_avatar_file)


AvatarRepository = Singleton(_AvatarRepository)
