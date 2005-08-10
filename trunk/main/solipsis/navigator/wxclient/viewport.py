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
import images
import time
import math
import bisect

from solipsis.util.timer import *
from solipsis.navigator.viewport import BaseViewport

def _optimize(obj):
    try:
        import psyco
    except ImportError:
        pass
    else:
        psyco.bind(obj)

class DrawableItem(object):
    def __init__(self, id_, drawable, index, rel_pos, z_order):
        self.id_ = id_
        self.drawable = drawable
        self.index = index
        self.rel_pos = rel_pos
        self.z_order = z_order

class Viewport(BaseViewport):
    """
    This class is a viewport that displays
    drawable objects in a wx.Window.
    """

    overview_ratio = 1.15
    glide_duration = 0.8
    destination_radius = 20.0

    def __init__(self, window, world_size = 2**128):
        BaseViewport.__init__(self, world_size)
        self.window = window
        self.draw_buffer = None
        self.background = None
        self.fps = 0.0
        self.redraws = 0
        self.need_further_redraw = True
        self.redraw_pending = False
        self.last_redraw_duration = 0.01
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
        self.auto_rotate = False

        self.Reset()

    def Reset(self):
        """
        Reinitialize the viewport. Clears all objects.
        """
        BaseViewport.Reset(self)
        # (object name -> index) dictionary
        self.obj_glider = []
        # List of dicts of drawables
        self.obj_drawables = []
        self.obj_arrays += (self.obj_glider, self.obj_drawables, )
        # List of (z-index, dict { painter-type -> dict of drawables } )
        self.radix_list = []
        # Different painter instances
        self.painters = {}

        # List of sensitive areas as (index, (x1, y1, x2, y2)) tuples
        self.sensitive_areas = []
        # Currently hovered object area, or None
        self.hovered_area = None

    def Draw(self, onPaint = False):
        """
        Refresh the viewport.
        """
        # Spare machine time if the window is hidden or if there is something wrong
        try:
            if not self.window.IsShown() or self.window.IsBeingDeleted():
                return False
        except Exception, e:
            print str(e)
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
        sensitive_areas = []
        # First we traverse the radix list in Z order
        for z_order, dict_ in self.radix_list:
            # Then we select the drawables for each painter at the same Z
            for painter, items in dict_.iteritems():
                l = []
                p = []
                objs = []
                for it in items.itervalues():
                    # Transform relative drawable position into an absolute position
                    index = it.index
                    x, y = it.rel_pos
                    #~ print index, positions[index]
                    x = int(x + positions[index][0])
                    y = int(y + positions[index][1])
                    if isinstance(x, int) and isinstance(y, int):
                        objs.append(index)
                        l.append(it.drawable)
                        p.append((x, y))
                if len(l) > 0:
                    bboxes = self.painters[painter].Paint(dc, l, p)
                    sensitive_areas.extend(zip(objs, bboxes))

        # Store sensitive areas
        self.sensitive_areas = sensitive_areas

        # If the viewport is disabled, we dim it
        if self.disabled:
            dim_dc = self._HalfTransparentDC(width, height)
            dc.BlitPointSize((0,0), (width, height), dim_dc, (0,0), useMask=True)

        # End drawing
        if not self.disabled:
            #~ (tick, elapsed) = self.fps_timer.Read()
            #~ c = 0.5
            #~ self.fps = (1.0 - c) * self.fps + c / max(tick, 0.001)
            #~ cpu_ratio = cpu_time / max(tick, 0.001) * 100
            #~ dc.DrawTextPoint("FPS: %.2f, objects: %d, geometry CPU: %.1f%%" % (self.fps, nb_objects, cpu_ratio), (10,10))
            cx, cy = self.center
            cx = (float(cx) / self.world_size) % 1.0
            cy = (float(cy) / self.world_size) % 1.0
            dc.DrawTextPoint("Position: %.5f, %.5f" % (cx, cy), (10, 10))
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
        index = BaseViewport.AddObject(self, name, obj, position)
        # Then initialize the object's properties
        self.obj_drawables[index] = {}
        self.obj_glider[index] = ExpEvolver(duration = self.glide_duration)
        self._ObjectsGeometryChanged()
        return index

    def AddDrawable(self, obj_name, drawable, rel_pos, z_order=0):
        """
        Add a drawable owned by a given object.
        Returns its internal id.
        """

        # Append to the object's drawable list
        index = self.obj_dict[obj_name]
        id_ = obj_name + '%' + str(id(drawable))
        item = DrawableItem(id_, drawable, index, rel_pos, z_order)
        self.obj_drawables[index][id_] = item
        # If necessary, create painter
        painter = drawable.painter
        if painter not in self.painters:
            self.painters[painter] = painter()
        # Insert into radix_list
        i = bisect.bisect(self.radix_list, (z_order, None))
        if i < len(self.radix_list) and self.radix_list[i][0] == z_order:
            d = self.radix_list[i][1]
        else:
            d = {}
            bisect.insort(self.radix_list, (z_order, d))
        if painter not in d:
            d[painter] = {}
        d[painter][id_] = item
        self._ObjectsGeometryChanged()
        return id_

    def RemoveDrawable(self, obj_name, id_):
        """
        Removes a single drawable.
        """
        # Fetch drawable item
        try:
            index = self.obj_dict[obj_name]
        except KeyError:
            print "cannot modify unknown object '%s' in viewport" % obj_name
            return
        item = self.obj_drawables[index][id_]
        self._RemoveDrawableItem(item)
        del self.obj_drawables[index][id_]
        self._ObjectsGeometryChanged()

    def MoveObject(self, name, position):
        """
        Move an existing object in the viewport.
        """
        try:
            index = BaseViewport.MoveObject(self, name, position)
            self.obj_glider[index].Reset(0.0, 1.0)
            self._ObjectsGeometryChanged()
        except KeyError:
            return

    def JumpTo(self, position):
        """
        Jump to a position in logical coordinates.
        """
        self._SetCenter(position)
        self._SetAngle(math.pi / 2)
        self._ViewportGeometryChanged()

    def MoveTo(self, position):
        """
        Move to a position in logical coordinates.
        """
        self._SetFutureCenter(position)
        self._ViewportGeometryChanged()

    def MoveToPixels(self, position, strafe=False):
        """
        Move to a position in physical (pixel) coordinates.
        """
        w, h = self._WindowSize()
        cx, cy = self.center
        x = float(position[0]) - w / 2
        y = h / 2 - float(position[1])
        cs = math.cos(-self.angle)
        sn = math.sin(-self.angle)
        fx = self.normalize((x * cs - y * sn) / self.ratio) + cx
        fy = self.normalize((y * cs + x * sn) / self.ratio) + cy
        self._SetFutureCenter((fx, fy))

        # Change orientation according to the destination we move towards
        if self.auto_rotate and not strafe and (abs(x) > 1 or abs(y) > 1):
            d = math.sqrt(x**2 + y**2)
            if abs(x) > abs(y):
                angle = math.asin(x / d)
                if y < 0:
                    angle = math.pi - angle
            else:
                angle = math.acos(y / d)
                if x < 0:
                    angle = -angle
            pi = math.pi
            if angle > pi / 2:
                angle = -pi + angle
            elif angle < -pi / 2:
                angle = pi + angle
            self._SetFutureAngle(self.angle + angle)

        self._ViewportGeometryChanged()
        fx = fx % self.world_size
        fy = fy % self.world_size
        return (fx, fy)
    
    def MoveToRelative(self, (dx, dy)):
        """
        Move to a position relatively to the current one and the viewport size.
        """
        w, h = self._WindowSize()
        w /= 2
        h /= 2
        pixels = (w + dx * w, h + dy * h)
        return self.MoveToPixels(pixels, strafe=True)

    def Hover(self, (px, py)):
        """
        Hover a specific pixel in the viewport.
        """
        if self.hovered_area is not None:
            # If an area is already being hovered, go the fast path to see
            # if nothing has changed.
            index, (x1, y1, x2, y2) = self.hovered_area
            if x1 <= px and y1 <= py and x2 >= px and y2 >= py:
                return (None, None)
        # Normal path: check all sensitive areas
        areas = [(index, (x1, y1, x2, y2)) for index, (x1, y1, x2, y2) in self.sensitive_areas
            if x1 <= px and y1 <= py and x2 >= px and y2 >= py]
        old_area = self.hovered_area
        if len(areas) == 0:
            self.hovered_area = None
            changed = old_area is not None
        else:
            self.hovered_area = areas[0]
            changed = old_area is None or old_area[0] != self.hovered_area[0]
        if changed:
            if self.hovered_area is not None:
                self.window.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
                return (changed, self.obj_name[areas[0][0]])
            else:
                self.window.SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))
        return (changed, "")

    def PendingRedraw(self):
        """
        Is there a redraw pending ?
        """
        r = self.redraw_pending
        self.redraw_pending = True
        return r

    def HoveredItem(self):
        """
        Returns the name of the object currently hovered by the mouse, or None.
        """
        h = self.hovered_area
        if h is None:
            return None
        index, box = h
        return self.obj_name[index]

    def LastRedrawDuration(self):
        """
        Returns the time spent in the last redraw (in seconds).
        Be careful, this does not always include the actual redraw by the
        graphics layer (e.g. X11).
        """
        return self.last_redraw_duration

    def Empty(self):
        """
        Returns True if the viewport is empty.
        """
        return len(self.obj_list) == 0
    
    def AutoRotate(self, flag):
        """
        Set the autorotate flag. If True, the viewport will smoothly change
        its orientation when a relative move is done.
        """
        self.auto_rotate = flag

    #
    # Private methods: object management
    #
    def _RemoveDrawableItem(self, item):
        id_ = item.id_
        painter = item.drawable.painter
        # Find the drawable's slot in the radix list
        i = bisect.bisect(self.radix_list, (item.z_order, None))
        assert self.radix_list[i][0] == item.z_order
        d = self.radix_list[i][1]

        del d[painter][id_]
        if len(d[painter]) == 0:
            del d[painter]
        if len(d) == 0:
            del self.radix_list[i]

    def _RemoveByIndex(self, index):
        """
        Remove an object giving its index rather than its name.
        """
        # Remove all drawables
        for item in self.obj_drawables[index].values():
            self._RemoveDrawableItem(item)
        # Delete stored object properties
        name = self.obj_name[index]
        for a in self.obj_arrays:
            del a[index]
        del self.obj_dict[name]
        # Re-arrange moved objects in dictionary
        _names = self.obj_name
        _drawables = self.obj_drawables
        for i in xrange(index, len(_names)):
            self.obj_dict[_names[i]] = i
            for item in _drawables[i].itervalues():
                item.index = i
        self._ObjectsGeometryChanged()


    #
    # Private methods: window ops
    #
    def _ViewportGeometryChanged(self):
        if not self.Empty() and not self.disabled:
            self._SetFutureRatio()
            self._AskRedraw()

    def _ObjectsGeometryChanged(self):
        if not self.Empty() and not self.disabled:
            self._SetFutureRatio()
            self._AskRedraw()

    def _WindowSize(self):
        """ Returns the current size of the drawing area, in pixels. """
        return self.window.GetClientSizeTuple()

    def _AskRedraw(self):
        """ Asks a redraw of the underlying window. """
        if not self.PendingRedraw():
            self.window.Refresh(eraseBackground=False)

    def _RebuildBackgroundDC(self, width, height):
        """ Builds a DC suitable for blitting the background from. """

        image = self.images.GetImage(images.IMG_2D_BACKGROUND)
        w, h = image.GetSize()
        rw = float(width) / w
        rh = float(height) / h
        r = max(rw, rh)
        w, h = int(r * w), int(r * h)
        image = image.Scale(w, h)
        if rw < rh:
            dx = (w - width) // 2
            dy = 0
        else:
            dx = 0
            dy = (h - height) // 2
        bitmap = wx.BitmapFromImage(image.Scale(w, h))
        mem_dc = wx.MemoryDC()
        mem_dc.SelectObject(bitmap)
        self.background = None
        background_dc = wx.MemoryDC()
        background_dc.SelectObject(wx.EmptyBitmap(width, height))
        background_dc.BlitPointSize((0,0), (width, height), mem_dc, (dx, dy))
        self.background = background_dc

    def _HalfTransparentDC(self, width, height):
        """
        Returns a half transparent DC suitable for dimming the viewport.
        Unfortunately drawing/blitting this is very slow under Linux/GTK2.
        """
        if self.dim_dc is not None:
            w, h = self.dim_dc.GetSize()
            if w >= width and h >= height:
                return self.dim_dc
            else:
                # Avoid too many recalculations
                width = int(width * 1.5)
                height = int(height * 1.5)
        #~ print "Rebuilding dim DC %d*%d..." % (width, height)
        
        opaque = wx.Colour(63, 63, 63)
        transparent = wx.RED
        # Create bitmap & enable transparency
        bmp = wx.EmptyBitmap(width, height)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        # Start with single tile
        w, h = 3, 3
        dc.BeginDrawing()
        dc.SetPen(wx.Pen(transparent))
        dc.DrawPointList([(x, y) for x in range(w) for y in range(h)])
        dc.SetPen(wx.Pen(opaque))
        dc.DrawPointList([(x, y) for (x, y) in zip(range(w), range(h))])
        # Tile all DC
        while w < width:
            dc.BlitPointSize((w, 0), (w, h), dc, (0, 0))
            w *= 2
        while h < height:
            dc.BlitPointSize((0, h), (width, h), dc, (0, 0))
            h *= 2
        dc.EndDrawing()
        # Under Windows, we must temporarily de-select the bitmap to set its mask
        dc.SelectObject(wx.NullBitmap)
        bmp.SetMaskColour(transparent)
        dc.SelectObject(bmp)
        self.dim_dc = dc
        return self.dim_dc

    def _UpdateAnimations(self):
        """ Update all animations in the viewport. """

        if not self.disabled:
            dirty = self._Glide()
        else:
            dirty = False
        self.need_further_redraw = dirty
        self.draw_destination = dirty

    def _DrawDestination(self, dc, brightness=TriangleLooper(loop=1.4, bottom=0, top=255)):
        """ Draw destination when in movement. """

        p = [self.center, self.future_center[0]]
        (cx, cy), (fx, fy) = self._ConvertPositions(positions=p)
        dist = math.sqrt((fx - cx) ** 2 + (fy - cy) ** 2)
        if dist > 0.2:
            rgb = brightness.Read()
            colour = wx.Colour(255, 64 + rgb * 0.5, 0)
            pen = wx.Pen(colour, width=5)
            dc.SetPen(pen)
            r = self.destination_radius / dist
            dx, dy = (fx - cx) * r, (fy - cy) * r
            try:
                dc.DrawLine(fx - dx, fy - dy, fx + dx, fy + dy)
                dc.DrawLine(fx - dy, fy + dx, fx + dy, fy - dx)
            except OverflowError:
                pass

    def _Animate(self, dc):
        """ Draw all pending animations in the viewport. """

        if self.draw_destination:
            self._DrawDestination(dc)

    #
    # Private methods: geometric ops
    #

    def _SetCenter(self, position):
        """
        Immediately set the viewport center in logical coordinates.
        """
        self.center = position
        self.future_center = position, position

    def _SetFutureCenter(self, position):
        """
        Set the viewport center in logical coordinates.
        """
        self.future_center = position, self.center
        self.center_glider.Reset(0.0, 1.0)

    def _SetRatio(self, ratio):
        """
        Immediately set the viewport ratio.
        """
        self.ratio = ratio

    def _SetFutureRatio(self, ratio=None):
        """
        Set the viewport ratio.
        """

        if ratio is None:
            ratio = self._UserOptimalRatio()
        # It is more pleasant if we don't always change the ratio
        # to accomodate for small changes in the scene dimensions
        if (ratio < self.ratio * 0.99) or (ratio > self.ratio * self.overview_ratio):
            self.ratio_glider.Reset(self.ratio, ratio)

    def _SetAngle(self, angle):
        """ Immediately set the viewport angle. """
        self.angle = angle
        self.future_angle = angle

    def _SetFutureAngle(self, angle):
        """ Set the viewport angle (in radians). """

        pi = math.pi
        pi2 = 2.0 * pi
        # Normalize angle and calculate minimal difference
        angle = math.modf(angle / pi2)[0] * pi2
        if angle < 0:
            angle += pi2
        diff = math.modf((angle - self.angle) / pi2)[0] * pi2
        if diff < -pi:
            diff += pi2
        elif diff > pi:
            diff -= pi2
        # Normalize the current angle so as to correctly
        # "glide" to the future angle
        self.angle = angle - diff
        self.future_angle = angle
        self.angle_glider.Reset(self.angle, angle)

    def _Indices(self):
        """
        Returns an iterator on indices of all visible objects.
        """
        v = self.obj_visible
        d = self.obj_drawables
        return [i for i in xrange(len(v)) if v[i] == True and len(d[i]) > 0]

    def _RelativePositions(self, positions, indices):
        xc, yc = self.center
        p = positions
        _normalize = self.normalize
        relative_positions = [(_normalize(p[i][0] - xc), _normalize(p[i][1] - yc)) for i in indices]
        return relative_positions

    def _RelativeBBox(self, indices):
        """
        Returns a tuple containing the upper left and the bottom right
        of the objects' bounding box relatively to the center of the viewport.
        """
        cs = math.cos(self.angle)
        sn = math.sin(self.angle)
        p = self._RelativePositions(self.positions, indices)
        xs = [x * cs - y * sn for (x, y) in p] or [0.0]
        ys = [y * cs + x * sn for (x, y) in p] or [0.0]
        r = (min(xs), min(ys)), (max(xs), max(ys))
        return r

    def _ConvertPositions(self, indices=None, positions=None):
        """
        Converts the objects' logical positions to physical center-relative (pixel) positions.
        """
        if positions is not None:
            p = positions
        else:
            p = self.positions
        if indices is None:
            indices = xrange(len(p))

        w, h = self._WindowSize()
        ratio = self.ratio
        cs = math.cos(self.angle)
        sn = math.sin(self.angle)
        w /= 2.0
        h /= 2.0
        # These lines do several things at once:
        # - center view
        # - warp accross world borders
        # - rotate view
        # - scale view
        relative_positions = self._RelativePositions(p, indices)
        display_positions = [(w + ratio * (cs * x - sn * y), h - ratio * (sn * x + cs * y)) for (x, y) in relative_positions]
        return display_positions

    def _OptimalRatio(self, indices):
        """
        Calculates the optimal display ratio given displayed objects.
        """
        (xmin, ymin), (xmax, ymax) = self._RelativeBBox(indices)
        w, h = self._WindowSize()
        xradius = max(abs(xmin), abs(xmax))
        yradius = max(abs(ymin), abs(ymax))
        if xradius > 0:
            xratio = float(w) / (2.0 * xradius)
        else:
            xratio = 0.0
        if yradius > 0:
            yratio = float(h) / (2.0 * yradius)
        else:
            yratio = 0.0
        ratio = (min(xratio, yratio) or 1.0)
        return ratio

    def _UserOptimalRatio(self):
        """
        Calculate the viewport's target display ratio.
        """
        optimal_ratio = self._OptimalRatio(self._Indices())
        ratio = max(optimal_ratio, self.user_ratio) / self.overview_ratio
        return ratio

    def _Glide(self):
        """
        Manage smooth movements of objects and of the central point.
        Returns True if some values changed (redrawing needed), False otherwise.
        """
        dirty = False
        # Glide the viewport center
        if not self.center_glider.Finished():
            (fx, fy), (cx, cy) = self.future_center
            r = self.center_glider.Read()
            x = fx * r + cx * (1.0 - r)
            y = fy * r + cy * (1.0 - r)
            self.center = (x, y)
            dirty = True

        # Glide the viewport angle
        if not self.angle_glider.Finished():
            if dirty:
                self.angle = self.angle_glider.Read()
            else:
                self.angle_glider.Terminate()

        # Glide objects
        for i, glider in enumerate(self.obj_glider):
            if not glider.Finished():
                (fx, fy), (x, y) = self.future_positions[i]
                dx = self.normalize(x - fx)
                dy = self.normalize(y - fy)
                r = glider.Read()
                x = fx + dx * (1.0 - r)
                y = fy + dy * (1.0 - r)
                self.positions[i] = (x, y)
                dirty = True

        # Glide the viewport ratio
        if dirty:
            self.ratio = self.ratio_glider.Read()
            self._SetFutureRatio()
        if not self.ratio_glider.Finished():
            self.ratio = self.ratio_glider.Read()
            dirty = True

        return dirty


# We optimize the whole object.
# If problematic, we could just optimize selected methods.
#~ _optimize(Viewport)
