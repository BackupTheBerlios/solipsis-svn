
import wx
import time
import math
from itertools import izip

from solipsis.util.timer import *
from images import *


def _optimize(obj):
    try:
        import psyco
        psyco.bind(obj)
    except:
        pass


class Viewport(object):
    """ This class manages a viewport that displays
    drawable objects in a wxWindow. """

    overview_ratio = 1.15
    glide_duration = 0.8
    destination_radius = 20.0

    def __init__(self, window, world_size = 2**128):
        self.window = window
        self.images = ImageRepository()
        self.draw_buffer = None
        self.background = None
        self.fps = 0.0
        self.redraws = 0
        self.need_further_redraw = True
        self.redraw_pending = False
        self.last_redraw_duration = 0.01
        self.world_size = world_size
        #self.world_size = 1.0
        self.fmod = (lambda x, lim=float(self.world_size) / 2.0, fmod=math.fmod:
                        x >= 0.0 and fmod(x + lim, lim + lim) - lim or lim - fmod(lim - x, lim + lim))

        self.fps_timer = AutoTimer()
        self.center_glider = ExpEvolver(duration = self.glide_duration)
        self.angle_glider = LinearEvolver(duration = self.glide_duration)
        self.ratio_glider = ExpEvolver(duration = self.glide_duration)

        self.obj_dict = {}
        self.obj_list = []
        self.obj_name = []
        self.obj_visible = []
        self.positions = []
        self.obj_arrays = (self.obj_list, self.obj_name, self.obj_visible, self.positions)

        self.future_positions = []

        self.user_ratio = 0.0
        self._SetRatio(1.0)
        self._SetCenter((0,0))
        self._SetAngle(0.0)

    def Draw(self, onPaint = False):
        """ Refresh the viewport. """

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
            print "resized %d*%d" % (width, height)

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

        # Draw the characters
        bmp_avatar = self.images.GetBitmap(IMG_AVATAR)
        (w, h) = bmp_avatar.GetSize()
        w /= 2
        h /= 2
        cpu_timer.Reset()
        indices = self._Indices()
        positions = self._ConvertPositions(indices)
        cpu_time += cpu_timer.Read()[0]
        for i, pos in izip(indices, positions):
            x = int(pos[0] - w)
            y = int(pos[1] - h)
            # Safety guard against too big coordinates
            if isinstance(x, int) and isinstance(y, int):
                dc.DrawBitmapPoint(bmp_avatar, (pos[0] - w, pos[1] - h), True)
        nb_blits += len(indices)

        # End drawing
        (tick, elapsed) = self.fps_timer.Read()
        c = 0.5
        self.fps = (1.0 - c) * self.fps + c / max(tick, 0.001)
        cpu_ratio = cpu_time / max(tick, 0.001) * 100
        dc.DrawTextPoint("FPS: %.2f, blits: %d, geometry CPU: %.1f%%" % (self.fps, nb_blits, cpu_ratio), (10,10))
        dc.EndDrawing()
        self.redraws += 1
        (tick, elapsed) = draw_timer.Read()
        self.last_redraw_duration = tick
        if not onPaint:
            self.window.Update()

    def NeedsFurtherRedraw(self):
        """ Returns True if the viewport needs redrawing, False otherwise. """
        return self.need_further_redraw

    def Add(self, name, obj, position=None):
        """ Add a drawable object to this viewport. """

        # First add the object to the dictionary
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
        # (It may be better to replace this code
        # with some generic keyword-argument management)
        if position is not None:
            self.positions[index] = position
        self.obj_visible[index] = True
        self._ObjectsGeometryChanged()

        return index

    def RemoveByIndex(self, index):
        """ Remove a drawable object giving its index rather than its name. """
        name = self.obj_name[index]
        for a in self.obj_arrays:
            del a[index]
        del self.obj_dict[name]
        # Re-arrange moved objects in dictionary
        for i in xrange(index, len(self.obj_name)):
            self.obj_dict[self.obj_name[i]] = i
        self._ObjectsGeometryChanged()

    def Remove(self, name):
        """ Remove a drawable object from this viewport. """
        try:
            index = self.obj_dict[name]
        except:
            print "Cannot remove unknown object '%s' from viewport" % name
            return
        self.RemoveByIndex(index)

    def MoveObject(self, name, position):
        """ Move an existing object in the viewport. """
        try:
            index = self.obj_dict[name]
        except:
            print "Cannot move unknown object '%s' in viewport" % name
            return
        self.positions[index] = position
        self._ObjectsGeometryChanged()

    def JumpTo(self, position):
        """ Move to a position in logical coordinates. """
        self._SetCenter(position)
        self._SetAngle(math.pi / 2)
        self._ViewportGeometryChanged()

    def MoveTo(self, position):
        """ Move to a position in logical coordinates. """
        self._SetFutureCenter(position)
        self._ViewportGeometryChanged()

    def MoveToPixels(self, position):
        """ Move to a position in physical (pixel) coordinates. """
        w, h = self._WindowSize()
        cx, cy = self.center
        x = float(position[0]) - w / 2
        y = h / 2 - float(position[1])
        print x, y
        cs = math.cos(-self.angle)
        sn = math.sin(-self.angle)
        fx = self.fmod((x * cs - y * sn) / self.ratio) + cx
        fy = self.fmod((y * cs + x * sn) / self.ratio) + cy
#         fx = ((x * cs - y * sn) / self.ratio) + cx
#         fy = ((y * cs + x * sn) / self.ratio) + cy
        print x, y, "=", fx, fy
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

    def PendingRedraw(self):
        r = self.redraw_pending
        self.redraw_pending = True
        return r

    def LastRedrawDuration(self):
        return self.last_redraw_duration

    #
    # Private methods: window ops
    #

    def _ViewportGeometryChanged(self):
        self._SetFutureRatio()
        self._AskRedraw()

    def _ObjectsGeometryChanged(self):
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

        image = self.images.GetImage(IMG_2D_BACKGROUND)
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
        background_dc = wx.MemoryDC()
        background_dc.SelectObject(wx.EmptyBitmap(width, height))
        background_dc.BlitPointSize((0,0), (width, height), mem_dc, (dx, dy))
        self.background = background_dc

    def _UpdateAnimations(self):
        """ Update all animations in the viewport. """

        dirty = self._Glide()
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
            dc.DrawLine(fx - dx, fy - dy, fx + dx, fy + dy)
            dc.DrawLine(fx - dy, fy + dx, fx + dy, fy - dx)

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
        """ Simple function that returns an iterator on indices of all objects. """

        v = self.obj_visible
        return [i for i in xrange(len(v)) if v[i] == True]

    def _RelativePositions(self, positions, indices=None):
        if indices is None:
            indices = xrange(len(positions))
        xc, yc = self.center
        fmod = self.fmod
        p = positions
        relative_positions = [(fmod(p[i][0] - xc), fmod(p[i][1] - yc)) for i in indices]
        return relative_positions

    def _RelativeBBox(self, indices):
        """ Returns a tuple containing the upper left and the bottom right
        of the objects' bounding box relatively to the center of the viewport. """

        cs = math.cos(self.angle)
        sn = math.sin(self.angle)
        xc, yc = self.center
        p = self._RelativePositions(self.positions, indices)
        xs = [x * cs - y * sn for (x, y) in p] or [0.0]
        ys = [y * cs + x * sn for (x, y) in p] or [0.0]
#         xs = [(p[i][0] - xc) * cs - (p[i][1] - yc) * sn for i in indices] or [0.0]
#         ys = [(p[i][1] - yc) * cs + (p[i][0] - xc) * sn for i in indices] or [0.0]
        r = (min(xs), min(ys)), (max(xs), max(ys))
        return r

    def _ConvertPositions(self, indices=None, positions=None):
        """ Converts the objects' logical positions to physical center-relative (pixel) positions. """

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
#         print p
#         print relative_positions
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
    import psyco
    psyco.profile()

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
