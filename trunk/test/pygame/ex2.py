import os
import sys
import wx
import pygame
import time

class wxSDLWindow(wx.Frame):
    def __init__(self, parent, id, title = 'SDL window', **options):
        options['style'] = wx.DEFAULT_FRAME_STYLE | wx.TRANSPARENT_WINDOW
        wx.Frame.__init__(*(self, parent, id, title), **options)

        self._initialized = 0
        self._resized = 0
        self._surface = None
        self.__needsDrawing = 1

        wx.EVT_IDLE(self, self.OnIdle)
        wx.EVT_PAINT(self, self.OnPaint)

    def OnIdle(self, ev):
        if self._resized or not self._initialized:
            if not self._initialized:
                # get the handle
                hwnd = self.GetHandle()
                print "handle =", hwnd

                os.environ['SDL_WINDOWID'] = str(hwnd)
                if sys.platform == 'win32':
                    os.environ['SDL_VIDEODRIVER'] = 'windib'

                pygame.init()

                wx.EVT_SIZE(self, self.OnSize)
                self._initialized = 1
            x,y = self.GetSizeTuple()
            self._surface = pygame.display.set_mode((x,y))
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

    def getSurface(self):
        return self._surface


if __name__ == "__main__":
    class CircleWindow(wxSDLWindow):
        "draw a circle in a wxPython / PyGame window"
        def draw(self):
            surface = self.getSurface()
            if not surface is None:
                topcolor = 5
                bottomcolor = 100

                pygame.draw.circle(surface, (250,0,0), (100,100), 50)

                pygame.display.flip()

    def pygametest():
        app = wx.PySimpleApp()
        sizeT = (400, 300)
        w = CircleWindow(None, -1, size = sizeT)
        w.Show(1)
        app.MainLoop()

    pygametest()
