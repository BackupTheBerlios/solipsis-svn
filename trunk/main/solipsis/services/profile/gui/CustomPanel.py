# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Tue Mar 22 11:28:12 2005

import wx, wx.lib.editor
from solipsis.services.profile.facade import get_facade

# begin wxGlade: dependencies
# end wxGlade

class CustomPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: CustomPanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.action_sizer_staticbox = wx.StaticBox(self, -1, _("Actions"))
        self.keywords_sizer_staticbox = wx.StaticBox(self, -1, _("Hobbies, special interests... (one per line)"))
        self.hobbies_value = wx.TextCtrl(self, -1, _("List of keywords you wish to be refered to..."), style=wx.TE_PROCESS_ENTER|wx.TE_PROCESS_TAB|wx.TE_MULTILINE|wx.HSCROLL|wx.TE_RICH2|wx.TE_LINEWRAP)
        self.custom_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.more_button = wx.Button(self, -1, _("More"))

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.facade = get_facade()
        self.bind_controls()

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.hobbies_value.Bind(wx.EVT_KILL_FOCUS, self.on_hobbies)
        #self.custom_list
        self.more_button.Bind(wx.EVT_BUTTON, self.on_more)
        
    def on_hobbies(self, evt):
        """language loses focus"""
        evt.Skip()
        
    def on_more(self, evt):
        """firstname loses focus"""
        evt.Skip()
        
    def __set_properties(self):
        # begin wxGlade: CustomPanel.__set_properties
        pass
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: CustomPanel.__do_layout
        custom_sizer = wx.BoxSizer(wx.VERTICAL)
        action_sizer = wx.StaticBoxSizer(self.action_sizer_staticbox, wx.HORIZONTAL)
        keywords_sizer = wx.StaticBoxSizer(self.keywords_sizer_staticbox, wx.VERTICAL)
        keywords_sizer.Add(self.hobbies_value, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        custom_sizer.Add(keywords_sizer, 1, wx.ALL|wx.EXPAND, 3)
        custom_sizer.Add(self.custom_list, 1, wx.EXPAND, 0)
        action_sizer.Add(self.more_button, 0, wx.FIXED_MINSIZE, 0)
        action_sizer.Add((20, 20), 0, wx.FIXED_MINSIZE, 0)
        custom_sizer.Add(action_sizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_RIGHT, 3)
        self.SetAutoLayout(True)
        self.SetSizer(custom_sizer)
        custom_sizer.Fit(self)
        custom_sizer.SetSizeHints(self)
        # end wxGlade

# end of class CustomPanel


