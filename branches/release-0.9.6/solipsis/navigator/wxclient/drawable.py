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
from solipsis.util.compat import safe_str, safe_unicode

class ImagePainter(object):
    """
    Paints a list of images to a wx.DC.
    """
    def Paint(self, dc, images, positions):
        boxes = []
        for image, (x, y) in izip(images, positions):
            w, h = image.width, image.height
            x -= w // 2
            y -= h // 2
            dc.DrawBitmapPoint(image.bitmap, (x, y), True)
            boxes.append((x, y, x + w, y + h))
        return boxes

class TextPainter(object):
    """
    Paints a list of texts to a wx.DC.
    """
    def Paint(self, dc, texts, positions):
        real_pos = []
        boxes = []
        for text, (x, y) in izip(texts, positions):
            if text.size is None:
                text.size = dc.GetTextExtent(text.text)
            w, h = text.size
            x -= w // 2
            y -= h // 2
            real_pos.append((x, y))
            boxes.append((x, y, x + w, y + h))
            dc.DrawText(text.text, x, y)
        return boxes

class Image(object):
    """
    A drawable image.
    """
    painter = ImagePainter

    def __init__(self, bitmap):
        assert isinstance(bitmap, wx.Bitmap)
        self.bitmap = bitmap
        self.width, self.height = self.bitmap.GetSize()

class Text(object):
    """
    A drawable text.
    """
    painter = TextPainter

    def __init__(self, text, font=None):
        self.font = font or wx.SWISS_FONT
        #~ print repr(text), type(text) #, '=>', repr(self.text)
        self.text = safe_unicode(text)
        self.size = None
