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


class CyclingAvatar(object):
    period = 5.0

    def __init__(self, plugin):
        self.plugin = plugin
        self.future_call = None
        self.avatars = None

    def SetAvatars(self, avatars):
        self.avatars = list(avatars)

    def Start(self):
        if self.future_call:
            self.future_call.Stop()
        self.index = 0
        self._NextAvatar()

    def Stop(self):
        if self.future_call:
            self.future_call.Stop()
            self.future_call = None

    def _NextAvatar(self):
        index = self.index % len(self.avatars)
        avatar = self.avatars[index]
        self.index = index + 1
        self.plugin.SetNodeAvatar(avatar)
        self.future_call = wx.FutureCall(1000.0 * self.period, self._NextAvatar)


