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
import time
import math
import bisect
from itertools import izip

from solipsis.util.timer import *
import images

def _optimize(obj):
    try:
        import psyco
        psyco.bind(obj)
    except:
        pass


class Viewport(object):
    """
    This class is a viewport that displays
    drawable objects in a wx.Window.
    """

    overview_ratio = 1.15
    glide_duration = 0.8
    destination_radius = 20.0

    def __init__(self, window, world_size = 2**128):
        self.window = window
        self.draw_buffer = None
        self.background = None
        self.fps = 0.0
        self.redraws = 0
        self.need_further_redraw = True
        self.redraw_pending = False
        self.last_redraw_duration = 0.01
        self.world_size = world_size
        self.normalize = (lambda x, lim=float(self.world_size) / 2.0: (x + lim) % (lim + lim) - lim)
        self.images = images.ImageRepository() # for 2D background

        self.fps_timer = AutoTimer()
        self.center_glider = ExpEvolver(duration = self.glide_duration)
        self.angle_glider = LinearEvolver(duration = self.glide_duration)
        self.ratio_glider = ExpEvolver(duration = self.glide_duration)

        self.user_ratio = 0.0
        self._SetRatio(1.0)
        self._SetCenter((0,0))
        self._SetAngle(0.0)

        self.dim_dc = None
        self.disabled = True

        self.Reset()

    def Reset(self):
        """
        Reinitialize the viewport. Clears all objects.
        """
        # (object name -> index) dictionary
        self.obj_dict = {}
        # List of objects
        self.obj_list = []
        self.obj_name = []
        self.obj_visible = []
        self.obj_glider = []
        # List of dicts of drawables
        self.obj_drawables = []
        self.positions = []
        self.future_positions = []
        self.obj_arrays = (self.obj_list, self.obj_name, self.obj_visible, self.obj_glider,
            self.obj_drawables, self.positions, self.future_positions)

        # List of (z-index, dict { painter-type -> dict of drawables } )
        self.radix_list = []
        # Different painter instances
        self.painters = {}

    def Draw(self, onPaint = False):
        """
        Refresh the viewport.
        """

        # Spare machine time if the window is hidden or if there is something wrong
        try:
            if not self.window.IsShown() or self.window.IsBeingDeleted():
                return False
        except:
            return False

        # Create a new buffer if the size has changed
        (width, height) = self._WindowSize()
        resized = False
        if self.draw_buffer is None or self.draw_buffer.GetSize() != (width, height):
            resized = True
            self._SetFutureRatio()

        # Under Windows, it seems we cannot re-use the same buffer twice (why ?)
        self.draw_buffer = wx.EmptyBitmap(width, height)
        cpu_timer = AutoTimer()
        draw_timer = AutoTimer()
        cpu_time = 0

        # First, update animations
        self.redraw_pending = False
        self.need_further_redraw = False
        cpu_timer.Reset()
        self._UpdateAnimations()
        cpu_time += cpu_timer.Read()[0]

        # Prepare drawing context (DC)
        # Wx mandates a different DC if we are inside an EVT_PAINT handler
        if onPaint:
            dc = wx.BufferedPaintDC(self.window, self.draw_buffer)
        else:
            client_dc = wx.ClientDC(self.window)
            dc = wx.BufferedDC(client_dc, self.draw_buffer)

        # Begin drawing
        start_draw = time.time()
        dc.SetOptimization(True)
        dc.BeginDrawing()
        nb_blits = 0

        # Draw the background image
        if self.background is None or resized:
            self._RebuildBackgroundDC(width, height)
        dc.BlitPointSize((0,0), (width, height), self.background, (0,0))

        # Animate
        self._Animate(dc)

        # Draw everything
        cpu_timer.Reset()
        indices = self._Indices()
        positions = self._ConvertPositions(indices)
        cpu_time += cpu_timer.Read()[0]
        nb_objects = len(indices)
        # First we traverse the radix list in Z order
        for z_order, d in self.radix_list:
            # Then we select the drawables for each painter at the same Z
            for painter, items in d.iteritems():
                l = []
                p = []
                for it in items.itervalues():
                    i = it.index
                    x, y = it.rel_pos
                    x = int(x + positions[i][0])
                    y = int(y + positions[i][1])
                    if isinstance(x, int) and isinstance(y, int):
                        l.append(it.drawable)
                        p.append((x, y))
                if len(l) > 0:
                    self.painters[painter].Paint(dc, l, p)

        # If the viewport is disabled, we dim it
        if self.disabled:
            dim_dc = self._HalfTransparentDC(width, height)
#             dc.DrawBitmapPoint(dim_dc, (0, 0), useMask=True)
            dc.BlitPointSize((0,0), (width, height), dim_dc, (0,0), useMask=True)

        # End drawing
        (tick, elapsed) = self.fps_timer.Read()
        c = 0.5
        self.fps = (1.0 - c) * self.fps + c / max(tick, 0.001)
        cpu_ratio = cpu_time / max(tick, 0.001) * 100
        dc.DrawTextPoint("FPS: %.2f, objects: %d, geometry CPU: %.1f%%" % (self.fps, nb_objects, cpu_ratio), (10,10))
        dc.EndDrawing()
        self.redraws += 1
        (tick, elapsed) = draw_timer.Read()
        self.last_redraw_duration = tick
        if not self.Empty() and not onPaint:
            self.window.Update()

    def NeedsFurtherRedraw(self):
        """
        Returns True if the viewport needs redrawing, False otherwise.
        """
        return not self.Empty() and not self.disabled and self.need_further_redraw

    def AddObject(self, name, obj, position):
        """
        Add an object to this viewport.
        """

        # First add the object to the dictionary
        name = intern(name)
        if name in self.obj_dict:
            print "Cannot add already existing object '%s' to viewport" % name
            return self.obj_dict[name]

        index = len(self.obj_list)
        self.obj_dict[name] = index
        for a in self.obj_arrays:
            a.append(None)
        self.obj_list[index] = obj

        # Then initialize the object's properties
        self.obj_name[index] = name
        self.positions[index] = position
        self.future_positions[index] = position, position
        self.obj_visible[index] = True
        self.obj_drawables[index] = {}
        self.obj_glider[index] = ExpEvolver(duration = self.glide_duration)
        self._ObjectsGeometryChanged()

        return index

    def AddDrawable(self, obj_name, drawable, rel_pos, z_order=0):
        """
        Add a drawable owned by a given object.
        """
        class DrawableItem(object):
            def __init__(self, drawable, index, rel_pos, z_order):
                self.drawable = drawable
                self.index = index
                self.rel_pos = rel_pos
                self.z_order = z_order

        # Append to the object's drawable list
        index = self.obj_dict[obj_name]
        id_ = obj_name + '%' + str(id(dra