# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Thu Jun 30 16:49:23 2005

import wx

from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxyReceiver

from solipsis.services.profile import DISPLAY_IMG, force_unicode
from solipsis.services.profile.tools.prefs import set_prefs

# begin wxGlade: dependencies
# end wxGlade

class DownloadDialog(wx.Dialog, UIProxyReceiver):
    def __init__(self, display, parent, id, *args, **kwds):
        UIProxyReceiver.__init__(self)
        self.display = display
        args = (parent, id)
        # begin wxGlade: DownloadDialog.__init__
        kwds["style"] = wx.CAPTION
        wx.Dialog.__init__(self, *args, **kwds)
        self.bitmap_1 = wx.StaticBitmap(self, -1, wx.Bitmap(DISPLAY_IMG(), wx.BITMAP_TYPE_ANY))
        self.download_label = wx.StaticText(self, -1, _("Connecting..."))
        self.separator_copy = wx.StaticLine(self, -1)
        self.always_display_check = wx.CheckBox(self, -1, _("Always display"))
        self.ok_button = wx.Button(self, wx.ID_CLOSE, _("Ok"))
        self.download_gauge = wx.Gauge(self, -1, 10, style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        self.counter = 0
        self.bind_controls()

    def init(self):
        """reset gaucge and display file name"""
        self.SetTitle(_("Downloading ..."))
        self.counter = 0
        self.download_gauge.SetValue(0)

    def update_file(self, name, size):
        """reset gaucge and display file name"""
        self.SetTitle(_("Downloading %s"% name))
        self.download_label.SetLabel(force_unicode(name))
        self.download_gauge.SetRange(size)
        self.download_gauge.SetValue(0)
        self.counter += 1

    def update_download(self, size):
        if size < self.download_gauge.GetRange():
            self.download_gauge.SetValue(size)

    def complete_all_files(self):
        self.SetTitle(_("Downloaded %d files"% self.counter))
        self.download_label.SetLabel(_("Download Complete"))
        self.download_gauge.SetValue(self.download_gauge.GetRange())
        self.counter = 0

    # EVENTS
    def bind_controls(self):
        """bind all controls with facade"""
        self.always_display_check.Bind(wx.EVT_CHECKBOX, self.on_check_display)
        self.ok_button.Bind(wx.EVT_BUTTON, self.on_close)

    def on_check_display(self, evt):
        """set whether disclaimer will be displayed at startup or not"""
        set_prefs("display_dl", self.always_display_check.IsChecked())

    def on_close(self, evt):
        self.Close()
        
    def __set_properties(self):
        # begin wxGlade: DownloadDialog.__set_properties
        self.SetTitle(_("Downloading"))
        self.always_display_check.SetValue(1)
        # end wxGlade
        self.always_display_check.SetValue(self.display)

    def __do_layout(self):
        # begin wxGlade: DownloadDialog.__do_layout
        dl_sizer = wx.BoxSizer(wx.VERTICAL)
        always_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4.Add(self.bitmap_1, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_4.Add(self.download_label, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        dl_sizer.Add(sizer_4, 0, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 10)
        dl_sizer.Add(self.separator_copy, 1, wx.EXPAND, 0)
        always_sizer.Add(self.always_display_check, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        always_sizer.Add(self.ok_button, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        dl_sizer.Add(always_sizer, 0, wx.ALL|wx.EXPAND, 10)
        dl_sizer.Add(self.download_gauge, 0, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 10)
        self.SetAutoLayout(True)
        self.SetSizer(dl_sizer)
        dl_sizer.Fit(self)
        dl_sizer.SetSizeHints(self)
        self.Layout()
        # end wxGlade

# end of class DownloadDialog


