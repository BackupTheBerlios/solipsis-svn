# pylint: disable-msg=C0103,W0131
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
"""Simple interface for viewports. Those functions are callbacks used
by world.py"""

class BaseViewport(object):

    overview_ratio = 1.15
    glide_duration = 0.8
    destination_radius = 20.0

    def __init__(self, world_size=2**128, disable=True):
        self.world_size = world_size
        self.normalize = (lambda x, lim=float(self.world_size) / 2.0: \
                          (x + lim) % (lim + lim) - lim)
        self.disabled = disable
 
    def Disable(self):
        self.disabled = True

    def Enable(self):
        self.disabled = False

    def Reset(self):
        raise NotImplementedError

    def Draw(self, onPaint = False):
        """refresh the viewport"""
        raise NotImplementedError

    def AddObject(self, name, obj, position):
        raise NotImplementedError

    def RemoveObject(self, name):
        raise NotImplementedError

    def MoveObject(self, name, position):
        raise NotImplementedError

    def JumpTo(self, position):
        raise NotImplementedError

    def MoveTo(self, position):
        raise NotImplementedError
 
