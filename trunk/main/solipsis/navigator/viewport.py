
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

    def __init__(self, window):
        self.window = window
        self.images = ImageRepository()
        self.draw_buffer = None
        self.background = None
        self.fps = 0.0
        self.redraws = 0
        self.need_further_redraw = True
        self.redraw_pending = False
        self.last_redraw_duration = 0.01

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

        # First add the object to the directory
        if name in self.obj_dict:
            raise NameError, "An object named '%s' already exists in viewport" % name
        index = len(self.obj_list)
        self.obj_dict[name] = index
        for a in self.obj_arrays:
            a.append(None)
        self.obj_list[index] = object
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
        self._ObjectsGeometryChanged()

    def Remove(self, name):
        """ Remove a drawable object from this viewport. """
        try:
            index = self.obj_dict[name]
        except:
            raise NameError, "No object named '%s' in viewport" % name
        self.RemoveByIndex(index)

    def MoveObject(self, name, position):
        """ Move an existing object in the viewport. """
        try:
            index = self.obj_dict[name]
        except:
            raise NameError, "No object named '%s' in viewport" % name
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
        x = position[0] - w / 2
        y = h / 2 - position[1]
        print x, y
        cs = math.cos(-self.angle)
        sn = math.sin(-self.angle)
        fx = (x * cs - y * sn) / self.ratio + cx
        fy = (y * cs + x * sn) / self.ratio + cy
        print fx, fy
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
