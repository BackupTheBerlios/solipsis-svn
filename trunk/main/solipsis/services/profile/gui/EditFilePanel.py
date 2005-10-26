# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4 on Tue Oct 25 10:04:51 2005

import wx
from solipsis.util.wxutils import _
from solipsis.services.profile.filter_facade import get_filter_facade

# begin wxGlade: dependencies
# end wxGlade

class EditFilePanel(wx.Panel):
    def __init__(self, frame, *args, **kwds):
        self.frame = frame
        # begin wxGlade: EditFilePanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.edit_file_sizer_staticbox = wx.StaticBox(self, -1, _("Edit file..."))
        self.filter_name_label = wx.StaticText(self, -1, _("Filter name :"))
        self.filter_name_value = wx.TextCtrl(self, -1, _("Filter name"))
        self.file_name = wx.StaticText(self, -1, _("File name :"))
        self.file_name_value = wx.TextCtrl(self, -1, _("File name"))
        self.file_size = wx.StaticText(self, -1, _("File size: "))
        self.size_value = wx.TextCtrl(self, -1, _("File size"))
        self.clear_button = wx.Button(self, -1, _("Clear"))
        self.apply_button = wx.Button(self, -1, _("Apply"))

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT, self.on_filter_name, self.filter_name_value)
        self.Bind(wx.EVT_BUTTON, self.on_clear, self.clear_button)
        self.Bind(wx.EVT_BUTTON, self.on_apply, self.apply_button)
        # end wxGlade

    def reset(self):
        self.filter_name_value.Clear()
        self.file_name_value.Clear()
        self.size_value.Clear()

    def update(self, new_filter):
        self.filter_name_value.SetValue(new_filter.filter_name)
        self.file_name_value.SetValue(new_filter.name.description)
        self.size_value.SetValue(new_filter.size.description)

    def __set_properties(self):
        # begin wxGlade: EditFilePanel.__set_properties
        pass
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: EditFilePanel.__do_layout
        edit_file_sizer = wx.StaticBoxSizer(self.edit_file_sizer_staticbox, wx.VERTICAL)
        edit_file_sizer.Add(self.filter_name_label, 0, wx.ADJUST_MINSIZE, 0)
        edit_file_sizer.Add(self.filter_name_value, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        edit_file_sizer.Add(self.file_name, 0, wx.TOP|wx.ADJUST_MINSIZE, 5)
        edit_file_sizer.Add(self.file_name_value, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        edit_file_sizer.Add(self.file_size, 0, wx.TOP|wx.ADJUST_MINSIZE, 5)
        edit_file_sizer.Add(self.size_value, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        edit_file_sizer.Add((20, 20), 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        edit_file_sizer.Add(self.clear_button, 0, wx.TOP|wx.EXPAND|wx.ADJUST_MINSIZE, 1)
        edit_file_sizer.Add(self.apply_button, 0, wx.TOP|wx.EXPAND|wx.ADJUST_MINSIZE, 1)
        self.SetAutoLayout(True)
        self.SetSizer(edit_file_sizer)
        edit_file_sizer.Fit(self)
        edit_file_sizer.SetSizeHints(self)
        # end wxGlade

    def on_filter_name(self, event): # wxGlade: EditFilePanel.<event_handler>
        self.apply_button.Enable(bool(self.filter_name_value.GetValue()))
        event.Skip()

    def on_clear(self, event): # wxGlade: EditFilePanel.<event_handler>
        self.reset()
        event.Skip()

    def on_apply(self, event): # wxGlade: EditFilePanel.<event_handler>
        props = {'name': self.file_name_value.GetValue(),
            'size': self.size_value.GetValue()}
        # set filter
        get_filter_facade().update_file_filter(
            self.filter_name_value.GetValue(),
            **props)
        self.frame.do_modified(True)
        event.Skip()

# end of class EditFilePanel


