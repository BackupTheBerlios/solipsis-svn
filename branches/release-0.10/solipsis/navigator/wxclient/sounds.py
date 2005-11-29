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


class NullSound(object):
    def Play(self):
        pass

class _SoundRepository(object):
    # Directory where images are stored
    sound_dir = "snd" + os.sep

    def __init__(self):
        self.sounds = {}

    def GetSound(self, sound_id):
        try:
            sound = self.sounds[sound_id]
        except KeyError:
            path = self.sound_dir + sound_id
            # Unfortunately wx.Sound displays an annoying error window when
            # the file is not found, instead of throwing an exception
            if os.path.isfile(path):
                sound = wx.Sound(path)
            else:
            #except (IOError, OSError), e:
                #print "Failed to load sound '%s': %s" % (path, str(e))
                print "Failed to load sound '%s': file does not exist" % path
                sound = NullSound()
            self.sounds[sound_id] = sound
        return sound

SoundRepository = Singleton(_SoundRepository)

