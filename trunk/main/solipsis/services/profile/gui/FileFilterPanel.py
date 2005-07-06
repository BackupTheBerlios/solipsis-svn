# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Tue Jun 21 11:01:29 2005

import wx
import sys

from solipsis.util.wxutils import _
from solipsis.services.profile import ADD_CUSTOM, DEL_CUSTOM
from solipsis.services.profile.facade import get_filter_facade
from solipsis.services.profile.filter_document import FilterValue

# begin wxGlade: dependencies
# end wxGlade

class FileFilterPanel(wx.Panel):
    def __init__(self, parent, id,
                 cb_modified=lambda x: sys.stdout.write(str(x))):
        # set members
        self.edited_item = None
        self.do_modified = cb_modified
        args = (parent, id)
        kwds = {}
        # begin wxGlade: FileFilterPanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.f_action_sizer_staticbox = wx.StaticBox(self, -1, _("Name here a filter to use on file names"))
        self.f_key_value = wx.TextCtrl(self, -1, _("MP3 Filter"))
        self.f_filter_value = wx.TextCtrl(self, -1, _(".*\\.mp3"))
        self.add_f_filter_button = wx.BitmapButton(self, -1, wx.Bitmap(ADD_CUSTOM(),wx.BITMAP_TYPE_ANY))
        self.del_f_filter_button = wx.BitmapButton(self, -1, wx.Bitmap(DEL_CUSTOM(),wx.BITMAP_TYPE_ANY))
        self.f_filters_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.PopulateList()
        self.bind_controls()

    def PopulateList(self):
        self.f_filters_list.InsertColumn(0, _("Filter name"))
        self.f_filters_list.InsertColumn(1, _("Filter expresion"))
        self.f_filters_list.SetColumnWidth(0, 200)
        self.f_filters_list.SetColumnWidth(1, 200)

    # EVENTS
    def bind_controls(self):
        """bind all controls with facade"""
        # file list
        self.f_filters_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selected)
        self.add_f_filter_button.Bind(wx.EVT_BUTTON, self.on_add)
        self.del_f_filter_button.Bind(wx.EVT_BUTTON, self.on_del)

    def on_selected(self, evt):
        """meta data"""
        self.edited_item = (evt.GetIndex(), evt.GetItem().GetText())
        self.f_key_value.SetValue(self.edited_item[1])
        self.f_filter_value.SetValue(self.f_filters_list.GetItem(evt.GetIndex(), 1).GetText())
        
    def on_add(self, evt):
        """a custom attribute has been modified"""
        try:
            # update cache, facade will refresh window (through FilterView)
            filter_value = FilterValue(value=self.f_filter_value.GetValue(),
                                       activate=True)
            get_filter_facade().add_file((self.f_key_value.GetValue(), filter_value))
            self.do_modified(True)
        except Exception:
            print "Regular expression not valid. See Info > Help for more information"

    def on_del(self, evt):
        """a custom attribute has been modified"""
        # update data
        index = self.f_filters_list.FindItem(0, self.f_key_value.GetValue())
        if index != -1 and self.f_filters_list.DeleteItem(index):
            get_filter_facade().del_file(self.f_key_value.GetValue())
            self.do_modified(True)

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
