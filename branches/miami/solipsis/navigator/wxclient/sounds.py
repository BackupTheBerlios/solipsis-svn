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

import wx, os

from solipsis.util.singleton import Singleton

SND_NEW_CHAT = 'cow.wav'
SND_NEW_PEER = 'laser.wav'
SND_LOST_PEER = 'laser.wav'


class _SoundRepository(object):
    # Directory where images are stored
    sound_dir = "snd" + os.sep

    def __init__(self):
        self.sounds = {}

    def GetSound(self, sound_id):
        if sound_id not in self.sounds:
            self.sounds[sound_id] = wx.Sound(self.sound_dir + sound_id)
        return self.sounds[sound_id]

SoundRepository = Singleton(_SoundRepository)

