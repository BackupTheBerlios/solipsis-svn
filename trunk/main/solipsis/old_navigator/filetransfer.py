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
from solipsis.navigator.basic.image import ImageManager

class WxFileTransfer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        [ wxID_WXMAINFRAMELOGO_WINDOW, wxID_WXMAINFRAMELOGOBITMAP
          ] = map(lambda _init_ctrls: wx.NewId(), range(2))

        self.logo_window = wx.Window(id=wxID_WXMAINFRAMELOGO_WINDOW,
                                     name='logo_window', parent=self, pos=wx.Point(0, 0),
                                     size=wx.Size(295, 76), style=0)
        
        logo = ImageManager.getBitmap(ImageManager.IMG_SOLIPSIS_LOGO)
        self.logoBitmap = wx.StaticBitmap(bitmap=logo,
                                          id=wxID_WXMAINFRAMELOGOBITMAP,
                                          name='logoBitmap', parent=self.logo_window,
                                          pos=wx.Point(0, 0), size=wx.Size(295, 76),
                                          style=0)

        button = wx.Button(self, -1, 'I do nothing')
