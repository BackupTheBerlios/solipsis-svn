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
from wx.xrc import XRCCTRL, XRCID

from PIL import Image, ImageDraw

from solipsis.util.uiproxy import UIProxyReceiver
from solipsis.util.wxutils import _
from solipsis.util.wxutils import *        # '*' doesn't import '_'


class ConfigDialog(wx.EvtHandler, XRCLoader, UIProxyReceiver):
    size = 64

    def __init__(self, plugin, dir):
        self.plugin = plugin
        self.dir = dir

        wx.EvtHandler.__init__(self)
        UIProxyReceiver.__init__(self)

    def Configure(self):
        f = 'avatars/dauphin.jpg'
        source = Image.open(f)
        # Resize to desired target size
        resized = source.resize((self.size, self.size), Image.BICUBIC)
        # Build mask to shape the avatar inside a circle
        transparent = (0,255,0,0)
        opaque = (255,0,0,255)
        background = (0,0,255,0)
        mask = Image.new('RGBA', (self.size, self.size), transparent)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, self.size - 1, self.size - 1), outline=opaque, fill=opaque)
        # Build the final result
        target = Image.new('RGBA', (self.size, self.size), background)
        target.paste(resized, None, mask)
        target.show()
        # Convert to wxBitmap
        r, g, b, alpha = target.split()
        rgb_data = Image.merge('RGB', (r, g, b))
        image = wx.EmptyImage(self.size, self.size)
        print len(rgb_data.tostring()), len(alpha.tostring())
        image.SetData(rgb_data.tostring())
        image.SetAlphaData(alpha.tostring())
        bitmap = wx.BitmapFromImage(image)
        print bitmap.GetSize()

    def Destroy(self):
        pass
