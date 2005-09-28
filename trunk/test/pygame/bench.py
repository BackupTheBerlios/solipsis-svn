import os
import sys
import wx
import pygame
import time
from PIL import Image

from bouncingball import BouncingBall

def time_function(func, n=100):
    _t= time.time
    print "%s..." % func.__name__,
    t1 = _t()
    for i in xrange(int(n)):
        func()
    t2 = _t()
    dt = float(t2 - t1) / n
    print "%f s." % dt


image_path = len(sys.argv) > 1 and sys.argv[1] or "toucan.png"
sizes = [(400, 300), (800, 600)]
# sizes = [(640, 480)]


# Test functions

def pygame_draw_ball():
    ball.draw()
#     ball.animate()

def pil_draw_ball():
    pil_surface.paste(pil_image, (3, 1), pil_image)

def wx_draw_ball():
    wx_dc.DrawBitmapPoint(wx_bitmap, (3, 1), True)

def pygame_to_raw():
    pygame.image.tostring(pyg_surface, 'RGB')

def pil_to_raw():
    pil_surface.tostring()

def raw_to_wx():
    wxim = wx.EmptyImage(*size)
    wxim.SetData(raw_rgb_data)
    wx.BitmapFromImage(wxim)


# Init
pygame.init()
black = 0, 0, 0
# Needed for wx to function
app = wx.PySimpleApp()

# Common data
pil_image = Image.open(image_path)
pil_image = pil_image.convert('RGBA')
wx_bitmap = wx.Bitmap(image_path)

for size in sizes:
    print "... %s bitmap to a %s surface..." % (pil_image.size, size, )
    pygame.display.set_mode(size)

    # pygame
    pyg_surface = pygame.Surface(size)
    ball = BouncingBall(pyg_surface)

    # PIL
    pil_surface = Image.new('RGB', size, black)
    raw_rgb_data = pil_surface.tostring()

    # wx
    wx_surface = wx.EmptyBitmap(*size)
    wx_dc = wx.MemoryDC()
    wx_dc.SelectObject(wx_surface)
    wx_dc.BeginDrawing()
    wx_dc.Clear()

    time_function(pygame_draw_ball, 3e4)
    time_function(pil_draw_ball, 1e3)
    time_function(wx_draw_ball, 1e3)
    time_function(pygame_to_raw, 1e3)
    time_function(pil_to_raw, 1e3)
    time_function(raw_to_wx, 1e2)

    wx_dc.EndDrawing()
    print


