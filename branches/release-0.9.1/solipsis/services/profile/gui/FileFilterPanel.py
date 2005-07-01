# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Tue Jun 21 11:01:29 2005

import wx

# begin wxGlade: dependencies
# end wxGlade

class FileFilterPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: FileFilterPanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.f_action_sizer_staticbox = wx.StaticBox(self, -1, _("Name here a filter to use on file names"))
        self.f_key_value = wx.TextCtrl(self, -1, _("MP3 Filter"))
        self.f_filter_value = wx.TextCtrl(self, -1, _("*.mp3"))
        self.add_f_filter_button = wx.BitmapButton(self, -1, wx.Bitmap(ADD_CUSTOM(),wx.BITMAP_TYPE_ANY))
        self.del_f_filter_button = wx.BitmapButton(self, -1, wx.Bitmap(DEL_CUSTOM(),wx.BITMAP_TYPE_ANY))
        self.f_filters_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: FileFilterPanel.__set_properties
        self.add_f_filter_button.SetSize(self.add_f_filter_button.GetBestSize())
        self.del_f_filter_button.SetSize(self.del_f_filter_button.GetBestSize())
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: FileFilterPanel.__do_layout
        f_filter_sizer = wx.BoxSizer(wx.VERTICAL)
        f_action_sizer = wx.StaticBoxSizer(self.f_action_sizer_staticbox, wx.HORIZONTAL)
        f_action_sizer.Add(self.f_key_value, 1, wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 3)
        f_action_sizer.Add(self.f_filter_value, 1, wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 3)
        f_action_sizer.Add(self.add_f_filter_button, 0, wx.LEFT|wx.FIXED_MINSIZE, 3)
        f_action_sizer.Add(self.del_f_filter_button, 0, wx.FIXED_MINSIZE, 0)
        f_filter_sizer.Add(f_action_sizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_RIGHT, 3)
        f_filter_sizer.Add(self.f_filters_list, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(f_filter_sizer)
        f_filter_sizer.Fit(self)
        f_filter_sizer.SetSizeHints(self)
        # end wxGlade

# end of class FileFilterPanel


