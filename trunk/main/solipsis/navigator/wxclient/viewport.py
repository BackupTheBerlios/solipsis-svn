
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
        # List of dicts of drawables
        self.obj_drawables = []
        self.positions = []
        self.obj_arrays = (self.obj_list, self.obj_name, self.obj_visible, self.obj_drawables, self.positions)

        # List of (z-index, dict { painter-type -> dict of drawables } )
        self.radix_list = []
        # Different painter instances
        self.painters = {}

        self.future_positions = []

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
            self.draw_buffer = wx.EmptyBitmap(width, height)
            self._SetFutureRatio()

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
        self.obj_visible[index] = True
        self.obj_drawables[index] = {}
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
        id_ = obj_name + '%' + str(id(drawable))
        item = DrawableItem(drawable, index, rel_pos, z_order)
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

    def RemoveByIndex(self, index):
        """
        Remove an object giving its index rather than its name.
        """
        # Remove all drawables
        for id_, item in self.obj_drawables[index].iteritems():
            painter = item.drawable.painter
            i = bisect.bisect(self.radix_list, (item.z_order, None))
            assert self.radix_list[i][0] == item.z_order
            d = self.radix_list[i][1]

            del d[painter][id_]
            if len(d[painter]) == 0:
                del d[painter]
            if len(d) == 0:
                del self.radix_list[i]
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

    def RemoveObject(self, name):
        """
        Remove an object from this viewport (and all its associated drawables).
        """
        try:
            index = self.obj_dict[name]
        except:
            print "Cannot remove unknown object '%s' from viewport" % name
            return
        self.RemoveByIndex(index)

    def MoveObject(self, name, position):
        """
        Move an existing object in the viewport.
        """
        try:
            index = self.obj_dict[name]
        except:
            print "Cannot move unknown object '%s' in viewport" % name
            return
        self.positions[index] = position
        self._ObjectsGeometryChanged()

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

    def MoveToPixels(self, position):
        """
        Move to a position in physical (pixel) coordinates.
        """
        w, h = self._WindowSize()
        cx, cy = self.center
        x = float(position[0]) - w / 2
        y = h / 2 - float(position[1])
        print x, y
        cs = math.cos(-self.angle)
        sn = math.sin(-self.angle)
        fx = self.normalize((x * cs - y * sn) / self.ratio) + cx
        fy = self.normalize((y * cs + x * sn) / self.ratio) + cy
        self._SetFutureCenter((fx,fy))

        # Change orientation according to the destination we move towards
        if abs(x) > 1 or abs(y) > 1:
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

    def PendingRedraw(self):
        r = self.redraw_pending
        self.redraw_pending = True
        return r

    def LastRedrawDuration(self):
        return self.last_redraw_duration

    def Empty(self):
        return len(self.obj_list) == 0

    def Disable(self):
        self.disabled = True

    def Enable(self):
        self.disabled = False

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
        print "Rebuilding dim DC %d*%d..." % (width, height)
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
        bmp.SetMaskColour(transparent)
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
            except:
                pass

    def _Animate(self, dc):
        """ Draw all pending animations in the viewport. """

        if self.draw_destination:
            self._DrawDestination(dc)

    #
    # Private methods: geometric ops
    #

    def _SetCenter(self, position):
        """ Immediately set the viewport center in logical coordinates. """
        self.center = position
        self.future_center = position, position

    def _SetFutureCenter(self, position):
        """ Set the viewport center in logical coordinates. """

        fx, fy = position
        cx, cy = self.center
        dist = (fx - cx) ** 2 + (fy - cy) ** 2
        #self.future_center = position, dist
        self.future_center = position, self.center
        self.center_glider.Reset(0.0, 1.0)

    def _SetRatio(self, ratio):
        """ Immediately set the viewport ratio. """
        self.ratio = ratio

    def _SetFutureRatio(self, ratio=None):
        """ Set the viewport center in logical coordinates. """

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
        xc, yc = self.center
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
        xc, yc = self.center
        cs = math.cos(self.angle)
        sn = math.sin(self.angle)
        w /= 2.0
        h /= 2.0
        lim = float(self.world_size)
        # These lines do several things at once:
        # - center view
        # - warp accross world borders
        # - rotate view
        # - scale view
        relative_positions = self._RelativePositions(p, indices)
        display_positions = [(w + ratio * (cs * x - sn * y), h - ratio * (sn * x + cs * y)) for (x, y) in relative_positions]
        return display_positions

    def _OptimalRatio(self, indices):
        """ Calculates the optimal display ratio given displayed objects. """

        (xmin, ymin), (xmax, ymax) = self._RelativeBBox(indices)
        xc, yc = self.center
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
        """ Calculate the viewport's target display ratio. """
        optimal_ratio = self._OptimalRatio(self._Indices())
        ratio = max(optimal_ratio, self.user_ratio) / self.overview_ratio
        return ratio

    def _Glide(self):
        """ Manage smooth movements of objects and of the central point.
        Returns True if some values changed (redrawing needed), False otherwise. """

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
_optimize(Viewport)



#
# Built-in self test
#

def __test():
    class W(object):
        def GetClientSizeTuple(self):
            return (640,480)

    class O(object):
        pass

    w = W()
    v = Viewport(w)
    v.SetCenter((50, 3000))
    objects = [ ( "a", 12555, -256 ),
                ( "b", 123, 7885 ),
                ( "c", -45645, 0 ),
                ( "d", 235, 66 ),
                ]
    for i in xrange(5):
        for name, x, y in objects:
            v.Add(name + str(i), O(), position=(x, y))
    print v._Ratio(v._Indices())
    for i in xrange(50000):
        v._ConvertPositions(v._Indices())
    print v._ConvertPositions(v._Indices())

if __name__ == '__main__':
    __test()
