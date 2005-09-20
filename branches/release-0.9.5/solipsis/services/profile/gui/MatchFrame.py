# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Fri Jul  8 10:26:48 2005

import wx
import sys

from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxyReceiver
from solipsis.services.profile.prefs import get_prefs, set_prefs
from solipsis.services.profile.facade import get_filter_facade
from solipsis.services.profile.gui.MatchPanel import MatchPanel
from solipsis.services.profile.gui.AboutDialog import AboutDialog

# begin wxGlade: dependencies
# end wxGlade

class MatchFrame(wx.Frame, UIProxyReceiver):
    def __init__(self, options, parent, id, plugin=None, **kwds):
        UIProxyReceiver.__init__(self)
        self.plugin = plugin
        self.options = options
        args = (parent, id)
        # begin wxGlade: MatchFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        
        # Menu Bar
        self.match_frame_menubar = wx.MenuBar()
        self.SetMenuBar(self.match_frame_menubar)
        self.action_menu = wx.Menu()
        self.getfile_item = wx.MenuItem(self.action_menu, wx.NewId(), _("&Get files\tCtrl+G"), "", wx.ITEM_NORMAL)
        self.action_menu.AppendItem(self.getfile_item)
        self.closematch_item = wx.MenuItem(self.action_menu, wx.NewId(), _("&Close\tCtrl+W"), "", wx.ITEM_NORMAL)
        self.action_menu.AppendItem(self.closematch_item)
        self.match_frame_menubar.Append(self.action_menu, _("Actions"))
        self.info_menu = wx.Menu()
        self.about_item = wx.MenuItem(self.info_menu, wx.NewId(), _("About...\tCtrl+?"), "", wx.ITEM_NORMAL)
        self.info_menu.AppendItem(self.about_item)
        self.match_frame_menubar.Append(self.info_menu, _("Info"))
        # Menu Bar end
        self.matched_panel = MatchPanel(self, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        # quite different initialisation according to launched by navigator or not
        if self.options["standalone"]:
            self.viewpeer_item = wx.MenuItem(self.action_menu, wx.NewId(), _("View peer...\tCtrl+V"), "", wx.ITEM_NORMAL)
            self.action_menu.AppendItem(self.viewpeer_item)
            self.hide_item = wx.MenuItem(self.action_menu, wx.NewId(), _("Hide...\tCtrl+R"), _("Hide profile from note book"), wx.ITEM_NORMAL)
            self.action_menu.AppendItem(self.hide_item)
        # events
        self.bind_controls()

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.Bind(wx.EVT_MENU, self.on_get_files, id=self.getfile_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_close, id=self.closematch_item.GetId())
        self.Bind(wx.EVT_CLOSE, self.on_close)
        # action
        if self.options["standalone"]:
            self.Bind(wx.EVT_MENU, self.on_view_profile, id=self.viewpeer_item.GetId())
            self.Bind(wx.EVT_MENU, self.on_hide, id=self.hide_item.GetId())
        # about
        self.Bind(wx.EVT_MENU, self.on_about,id=self.about_item.GetId())

    def on_get_files(self, evt):
        """download selected files"""
        pass

    def on_view_profile(self, evt):
        """display all profile info in ViewerFrame"""
        pass
    
    def on_hide(self, evt):
        """match current filter with given profile"""
        dlg = wx.SingleChoiceDialog(
                self, 'Select peer to hide', 'Hide preview',
                self.matched_panel.tabs.keys(), 
                wx.CHOICEDLG_STYLE
                )
        if dlg.ShowModal() == wx.ID_OK:
            self.matched_panel.hide_tab(dlg.GetStringSelection())
        
    def on_close(self, evt=None):
        """hide  application"""
        # save size
        new_size = self.GetSize()
        set_prefs("match_width", new_size.GetWidth())
        set_prefs("match_height", new_size.GetHeight())
        # do not destroy window
        self.Hide()
        
    def on_about(self, evt):
        """display about"""
        # not modal because would freeze the wx thread while twisted
        # one goes on and initialize profile
        about_dlg = AboutDialog(get_prefs("disclaimer"), self, -1)
        about_dlg.Show()

    def set_page(self):
        document = get_filter_facade().get_document()
        last_added = document.get_last_downloaded_desc()
        if last_added:
            peer_match = get_filter_facade().get_peer(last_added.get_id())
            if peer_match.has_match():
                self.matched_panel.set_matches(peer_match)
                self.matched_panel.set_tab(peer_match.peer_desc)
                if get_filter_facade().is_activated():
                    self.Show()
            document.reset_last_downloaded_desc()

    def __set_properties(self):
        # begin wxGlade: MatchFrame.__set_properties
        self.SetTitle(_("Matches"))
        self.SetSize((460, 600))
        # end wxGlade
        width = get_prefs("match_width")
        height = get_prefs("match_height")
        self.SetSize((width, height))

    def __do_layout(self):
        # begin wxGlade: MatchFrame.__do_layout
        match_frame_sizer = wx.BoxSizer(wx.VERTICAL)
        match_frame_sizer.Add(self.matched_panel, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(match_frame_sizer)
        self.Layout()
        # end wxGlade

# end of class MatchFrame


