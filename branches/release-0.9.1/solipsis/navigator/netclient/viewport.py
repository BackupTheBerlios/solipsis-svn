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

from solipsis.navigator.netclient import get_log_stream

def _pretty_pos((x, y)):
    """returns pretty formated position"""
    return "%f,%f"% (x/float(2**128), y/float(2**128))

class Viewport(object):

    overview_ratio = 1.15
    glide_duration = 0.8
    destination_radius = 20.0

    def __init__(self):
        self.disabled = True

    def Reset(self):
        pass

    def Draw(self, onPaint = False):
        pass

    def NeedsFurtherRedraw(self):
        return False
 
    def AddObject(self, name, obj, position):
        pass
#         print >> get_log_stream(),  "Viewport: Add object %s"% name

    def AddDrawable(self, obj_name, drawable, rel_pos, z_order=0):
        pass
#         print >> get_log_stream(),  "Viewport: Add %s"% obj_name
    
    def RemoveDrawable(self, obj_name, id_):
        pass
#         print >> get_log_stream(),  "Viewport: Remove %s"% obj_name

    def RemoveObject(self, name):
        pass
#         print >> get_log_stream(),  "Viewport: Remove %s"% name

    def MoveObject(self, name, position):
        pass
#         print >> get_log_stream(),  "Viewport: Move object %s to %s"% (name, _pretty_pos(position))

    def JumpTo(self, position):
        pass
#         print >> get_log_stream(),  "Viewport: Jump to %s"% _pretty_pos(position)

    def MoveTo(self, position):
        pass
#         print >> get_log_stream(),  "Viewport: Move to %s"% _pretty_pos(position)

    def MoveToPixels(self, position, strafe=False):
        print >> get_log_stream(),  "Viewport: Move to pixels %s"% _pretty_pos(position)
    
    def MoveToRelative(self, (dx, dy)):
        print >> get_log_stream(),  "Viewport: Move to relative %s"% str((dx, dy))

    def Hover(self, (px, py)):
        print >> get_log_stream(),  "Viewport: Hover %s"% str((px, py))
        return (False, "")

    def PendingRedraw(self):
        print >> get_log_stream(),  "Viewport: no PendingRedraw"
        return False
    
    def HoveredItem(self):
        print >> get_log_stream(),  "Viewport: no Hovered"
        return None
    
    def LastRedrawDuration(self):
        print >> get_log_stream(),  "Viewport: no LastRedrawDuration"
        return 1

    def Empty(self):
        print >> get_log_stream(),  "Viewport: empty"
        return True
    
    def Disable(self):
#         print >> get_log_stream(),  "Viewport: Disable"
        self.disabled = True

    def Enable(self):
#         print >> get_log_stream(),  "Viewport: Enable"
        self.disabled = False
    
    def AutoRotate(self, flag):
        print >> get_log_stream(),  "Viewport: AutoRotate %s"% flag

    # Private methods: object management
    def _RemoveDrawableItem(self, item):
        raise NotImplementedError

    def _RemoveByIndex(self, index):
        raise NotImplementedError

    # Private methods: window ops
    def _ViewportGeometryChanged(self):
        raise NotImplementedError

    def _ObjectsGeometryChanged(self):
        raise NotImplementedError

    def _WindowSize(self):
        raise NotImplementedError

    def _AskRedraw(self):
        raise NotImplementedError

    def _RebuildBackgroundDC(self, width, height):
        raise NotImplementedError

    def _HalfTransparentDC(self, width, height):
        raise NotImplementedError

    def _UpdateAnimations(self):
        raise NotImplementedError

    def _DrawDestination(self, dc, brightness=None):
        raise NotImplementedError

    def _Animate(self, dc):
        raise NotImplementedError

    # Private methods: geometric ops
    def _SetCenter(self, position):
        raise NotImplementedError

    def _SetFutureCenter(self, position):
        raise NotImplementedError

    def _SetRatio(self, ratio):
        raise NotImplementedError

    def _SetFutureRatio(self, ratio=None):
        raise NotImplementedError

    def _SetAngle(self, angle):
        raise NotImplementedError

    def _SetFutureAngle(self, angle):
        raise NotImplementedError

    def _Indices(self):
        raise NotImplementedError

    def _RelativePositions(self, positions, indices):
        raise NotImplementedError

    def _RelativeBBox(self, indices):
        raise NotImplementedError

    def _ConvertPositions(self, indices=None, positions=None):
        raise NotImplementedError

    def _OptimalRatio(self, indices):
        raise NotImplementedError

    def _UserOptimalRatio(self):
        raise NotImplementedError

    def _Glide(self):
        raise NotImplementedError
