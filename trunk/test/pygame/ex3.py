import os
import sys
import wx
import pygame
import time

from bouncingball import BouncingBall

class SDLPanel(wx.Panel):
    def __init__(self, parent, id_, size):
        wx.Panel.__init__(self, parent, id_, size=size, style=wx.WS_EX_PROCESS_IDLE)

        self._initialized = 0
        self._resized = 0
        self._surface = None
        self.__needsDrawing = 1

        wx.EVT_IDLE(self, self.OnIdle)
        wx.EVT_PAINT(self, self.OnPaint)

        self.Fit()

    def OnIdle(self, ev):
        if self._resized or not self._initialized:
            if not self._initialized:
                # get the handle
                hwnd = self.GetHandle()
                print "handle =", hwnd
                if not hwnd:
                    return

                print "pygame init..."
                os.environ['SDL_WINDOWID'] = str(hwnd)
                if sys.platform == 'win32':
                    os.environ['SDL_VIDEODRIVER'] = 'windib'

                pygame.init()

                wx.EVT_SIZE(self, self.OnSize)
                self._initialized = 1
            x, y = self.GetSizeTuple()
            self._surface = pygame.display.set_mode((x, y), pygame.DOUBLEBUF)
            self._resized = 0

#         print "EVT_IDLE", time.time()
        if self.__needsDrawing:
            self.draw()
            self.__needsDrawing = 0

    def OnPaint(self, ev):
        print "EVT_PAINT"
        self.__needsDrawing = 1
        ev.Skip()

    def OnSize(self, ev):
        print "EVT_SIZE"
        self._resized = 1
        ev.Skip()

    def draw(self):
        raise NotImplementedError('please define a .draw() method!')

    def on_idle(self):
        pass

    def getSurface(self):
        return self._surface


class MyFrame(wx.Frame):
    def __init__(self, parent, ID, strTitle, tplSize):
        wx.Frame.__init__(self, parent, ID, strTitle, size=tplSize)
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("lorem ipsum")
#         self.pnlSDL = SDLPanel(self, -1, tplSize)
        #self.Fit()

class CirclePanel(SDLPanel):
    "draw a circle in a wxPython / PyGame window"
    def draw(self):
        surface = self.getSurface()
        if surface is not None:
            topcolor = 5
            bottomcolor = 100
            pygame.draw.circle(surface, (250,0,0), (100,100), 50)
            pygame.display.flip()

class BouncingPanel(SDLPanel):
    """
    Draw a bouncing ball in a wxPython / PyGame window
    """
    def __init__(self, *args, **kargs):
        SDLPanel.__init__(self, *args, **kargs)
        self.ball = None

    def draw(self):
        surface = self.getSurface()
        if surface is not None:
            self.ball = self.ball or BouncingBall(surface)
            self.ball.animate()
            self.ball.draw()
            pygame.display.flip()
            wx.FutureCall(50, self.draw)
#             topcolor = 5
#             bottomcolor = 100
#             pygame.draw.circle(surface, (250,0,0), (100,100), 50)
#             pygame.display.flip()

    def on_idle(self):
        self.__needsDrawing = True


if __name__ == "__main__":
    app = wx.PySimpleApp()
    size = 640, 480
    frame = MyFrame(None, -1, "SDL Frame", size)
#     panel = CirclePanel(frame, -1, size=size)
    panel = BouncingPanel(frame, -1, size=size)
    frame.Show()
    panel.Show()
    app.MainLoop()

