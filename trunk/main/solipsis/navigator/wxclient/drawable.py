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
