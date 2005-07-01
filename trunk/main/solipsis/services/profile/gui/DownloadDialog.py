# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Thu Jun 30 16:49:23 2005

import wx

from solipsis.util.wxutils import _
from solipsis.services.profile import set_always_display

# begin wxGlade: dependencies
# end wxGlade

class DownloadDialog(wx.Dialog):
    def __init__(self, display, parent, id, *args, **kwds):
        self.display = display
        args = (parent, id)
        # begin wxGlade: DownloadDialog.__init__
        kwds["style"] = wx.CAPTION
        wx.Dialog.__init__(self, *args, **kwds)
        self.bitmap_1 = wx.StaticBitmap(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/download_complete.gif", wx.BITMAP_TYPE_ANY))
        self.dl_label = wx.StaticText(self, -1, _("Download Complete"))
        self.separator_copy = wx.StaticLine(self, -1)
        self.always_display_check = wx.CheckBox(self, -1, _("Always display"))
        self.ok_button = wx.Button(self, wx.ID_CLOSE, _("Ok"))

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.bind_controls()

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.always_display_check.Bind(wx.EVT_CHECKBOX, self.on_check_display)
        self.ok_button.Bind(wx.EVT_BUTTON, self.on_close)

    def on_check_display(self, evt):
        """set whether disclaimer will be displayed at startup or not"""
        set_always_display(self.always_display_check.IsChecked())

    def on_close(self, evt):
        self.Close()
        
    def __set_properties(self):
        # begin wxGlade: DownloadDialog.__set_properties
        self.SetTitle(_("Download complete"))
        self.always_display_check.SetValue(1)
        # end wxGlade
        self.always_display_check.SetValue(self.display)

    def __do_layout(self):
        # begin wxGlade: DownloadDialog.__do_layout
        dl_sizer = wx.BoxSizer(wx.VERTICAL)
        always_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(self.bitmap_1, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_4.Add(self.dl_label, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        dl_sizer.Add(sizer_4, 0, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 10)
        dl_sizer.Add(self.separator_copy, 1, wx.EXPAND, 0)
        always_sizer.Add(self.always_display_check, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        always_sizer.Add(self.ok_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        dl_sizer.Add(always_sizer, 0, wx.ALL|wx.EXPAND, 10)
        self.SetAutoLayout(True)
        self.SetSizer(dl_sizer)
        dl_sizer.Fit(self)
        dl_sizer.SetSizeHints(self)
        self.Layout()
        # end wxGlade

# end of class DownloadDialog


