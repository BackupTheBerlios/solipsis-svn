
from itertools import izip
import wx

import images


class ImagePainter(object):
    """
    Paints a list of images to a wx.DC.
    """
    def __init__(self):
        pass

    def Paint(self, dc, images, positions):
        for image, (x, y) in izip(images, positions):
            x -= image.width // 2
            y -= image.height // 2
            dc.DrawBitmapPoint(image.bitmap, (x, y), True)

class TextPainter(object):
    """
    Paints a list of texts to a wx.DC.
    """
    def __init__(self):
        pass

    def Paint(self, dc, texts, positions):
        real_pos = []
        for text, (x, y) in izip(texts, positions):
            if text.size is None:
                text.size = dc.GetTextExtent(text.text)
            real_pos.append((x - text.size[0] // 2, y - text.size[1] // 2))
        dc.DrawTextList([t.text for t in texts], real_pos)
#                 text_dc = wx.MemoryDC()
#                 bmp = wx.EmptyBitmap(300, 30)
#                 text_dc.SelectObject(bmp)
#                 brush = wx.Brush(wx.BLUE)
#                 text_dc.BeginDrawing()
#                 text_dc.SetBackground(brush)
#                 text_dc.Clear()
#                 tw, th = text_dc.GetTextExtent(s)
#                 text_dc.DrawTextPoint(s, (0, 0))
#                 text_dc.EndDrawing()
#                 bmp.SetMaskColour(wx.BLUE)
#                 dc.BlitPointSize((x, y), (tw, th), text_dc, (0, 0), useMask=True)
#                 text_dc = None

class Image(object):
    """
    A drawable image.
    """
    painter = ImagePainter
    repository = images.ImageRepository()

    def __init__(self, image_id):
        self.bitmap = self.repository.GetBitmap(image_id)
        self.width, self.height = self.bitmap.GetSize()

class Text(object):
    """
    A drawable text.
    """
    painter = TextPainter

    def __init__(self, text, font=None):
        self.font = font or wx.SWISS_FONT
        self.text = text
        self.size = None
