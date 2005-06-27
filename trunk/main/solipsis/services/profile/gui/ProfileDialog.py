# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Tue Jun 14 16:50:40 2005

import wx
from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxyReceiver
from solipsis.services.profile.gui.PreviewPanel import MyHtmlWindow
from solipsis.services.profile.view import HtmlView

# begin wxGlade: dependencies
# end wxGlade

class ProfileDialog(wx.Dialog, UIProxyReceiver):
    def __init__(self, parent, id, plugin=None, **kwds):
        UIProxyReceiver.__init__(self)
        self.facade = None
        self.plugin = plugin
        args = (parent, id)
        # begin wxGlade: ProfileDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.profile_window = MyHtmlWindow(self, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def set_page(self, page):
        self.profile_window.SetPage(page)
        self.Show()

    def set_facade(self, facade, auto_refresh):
        self.facade = facade
        view = HtmlView(self.facade._desc,
                        html_window=self.profile_window,
                        auto_refresh=auto_refresh)
        self.facade.add_view(view)
    
    def __set_properties(self):
        # begin wxGlade: ProfileDialog.__set_properties
        self.SetTitle(_("Profile"))
        self.SetSize((460, 410))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ProfileDialog.__do_layout
        profile_sizer = wx.BoxSizer(wx.VERTICAL)
        profile_sizer.Add(self.profile_window, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(profile_sizer)
        self.Layout()
        # end wxGlade

# end of class ProfileDialog


