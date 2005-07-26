# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Thu Jun  9 18:59:08 2005

import wx

from solipsis.util.wxutils import _
from solipsis.services.profile.prefs import get_prefs
from solipsis.services.profile import TORE_IMG, VERSION, DISCLAIMER

# begin wxGlade: dependencies
# end wxGlade

class AboutDialog(wx.Dialog):
    def __init__(self, display, parent, id, **kwds):
        self.display = display
        args = (parent, id)
        # begin wxGlade: AboutDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.STAY_ON_TOP
        wx.Dialog.__init__(self, *args, **kwds)
        self.tore_pic = wx.StaticBitmap(self, -1, wx.Bitmap(TORE_IMG(), wx.BITMAP_TYPE_ANY), style=wx.SIMPLE_BORDER)
        self.disclaimer_lbl = wx.TextCtrl(self, -1, _("Disclaimer"), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_CENTRE|wx.TE_LINEWRAP|wx.TE_WORDWRAP|wx.NO_BORDER)
        self.separator = wx.StaticLine(self, -1)
        self.display_check = wx.CheckBox(self, -1, _("Display at startup"))
        self.button_1 = wx.Button(self, wx.ID_CLOSE, _("Ok"))

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.bind_controls()

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.display_check.Bind(wx.EVT_CHECKBOX, self.on_check_display)
        self.button_1.Bind(wx.EVT_BUTTON, self.on_close)

    def on_check_display(self, evt):
        """set whether disclaimer will be displayed at startup or not"""
        get_prefs().set("disclaimer", self.display_check.IsChecked())

    def on_close(self, evt):
        self.Close()
        
    def __set_properties(self):
        # begin wxGlade: AboutDialog.__set_properties
        self.SetTitle(_("About Profile"))
        self.SetSize((300, 300))
        self.tore_pic.SetMinSize((300, 156))
        self.disclaimer_lbl.SetBackgroundColour(wx.Colour(226, 226, 226))
        self.disclaimer_lbl.Enable(False)
        self.display_check.SetValue(1)
        # end wxGlade
        self.SetTitle("%s %s"% (_("Solipsis Profile"), VERSION))
        self.display_check.SetValue(self.display)
        self.disclaimer_lbl.SetValue(DISCLAIMER)

    def __do_layout(self):
        # begin wxGlade: AboutDialog.__do_layout
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(self.tore_pic, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_3.Add(self.disclaimer_lbl, 1, wx.ALL|wx.EXPAND, 5)
        sizer_3.Add(self.separator, 0, wx.EXPAND, 0)
        sizer_5.Add(self.display_check, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_5.Add(self.button_1, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        sizer_3.Add(sizer_5, 0, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_3)
        self.Layout()
        # end wxGlade

# end of class AboutDialog


