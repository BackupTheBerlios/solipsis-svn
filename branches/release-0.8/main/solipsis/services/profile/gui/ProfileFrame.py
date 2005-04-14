# -*- coding: iso-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Tue Mar 22 11:28:12 2005

import wx, os, os.path
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.document import FileDocument
from solipsis.services.profile import PROFILE_DIR, PROFILE_FILE

# begin wxGlade: dependencies
from FilePanel import FilePanel
from PersonalPanel import PersonalPanel
from OthersPanel import OthersPanel
from CustomPanel import CustomPanel
from PreviewPanel import PreviewPanel
# end wxGlade

class ProfileFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: ProfileFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.profile_book = wx.Notebook(self, -1, style=0)
        
        # Menu Bar
        self.profile_menu = wx.MenuBar()
        self.SetMenuBar(self.profile_menu)
        self.profile_item = wx.Menu()
        self.activate_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Online\tCtrl+O"), _("Allow users seeing profile"), wx.ITEM_CHECK)
        self.profile_item.AppendItem(self.activate_item)
        self.export_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Export HTML ...\tCtrl+E"), _("Write profile as HTML File"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.export_item)
        self.profile_item.AppendSeparator()
        self.load_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Load ... \tCtrl+L"), _("Load profile from file"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.load_item)
        self.save_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Save ...\tCtrl+S"), _("Save profile into file"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.save_item)
        self.quit_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Quit\tCtrl+Q"), _("Exit profile management"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.quit_item)
        self.profile_menu.Append(self.profile_item, _("Profile"))
        self.peers_item = wx.Menu()
        self.addpeer_item = wx.MenuItem(self.peers_item, wx.NewId(), _("&Add...\tCtrl+A"), "", wx.ITEM_NORMAL)
        self.peers_item.AppendItem(self.addpeer_item)
        self.peers_item.AppendSeparator()
        self.anonymous_item = wx.MenuItem(self.peers_item, wx.NewId(), _("Anonymous"), "", wx.ITEM_RADIO)
        self.peers_item.AppendItem(self.anonymous_item)
        self.friend_item = wx.MenuItem(self.peers_item, wx.NewId(), _("Friend"), "", wx.ITEM_RADIO)
        self.peers_item.AppendItem(self.friend_item)
        self.blacklisted_item = wx.MenuItem(self.peers_item, wx.NewId(), _("Black listed"), "", wx.ITEM_RADIO)
        self.peers_item.AppendItem(self.blacklisted_item)
        self.peers_item.AppendSeparator()
        self.raw_item = wx.MenuItem(self.peers_item, wx.NewId(), _("&Find...\tCtrl+F"), _("Search profile in surrounding area"), wx.ITEM_NORMAL)
        self.peers_item.AppendItem(self.raw_item)
        self.filters_item = wx.MenuItem(self.peers_item, wx.NewId(), _("Filters...\tCtrl+H"), _("Create active filters to get notified on peers approach"), wx.ITEM_NORMAL)
        self.peers_item.AppendItem(self.filters_item)
        self.profile_menu.Append(self.peers_item, _("Peers"))
        self.display_item = wx.Menu()
        self.autorefresh_item = wx.MenuItem(self.display_item, wx.NewId(), _("Auto refresh"), _("Automatically call refresh on any change in profile"), wx.ITEM_CHECK)
        self.display_item.AppendItem(self.autorefresh_item)
        self.refresh_item = wx.MenuItem(self.display_item, wx.NewId(), _("&Refresh\tCtrl+R"), "", wx.ITEM_NORMAL)
        self.display_item.AppendItem(self.refresh_item)
        self.profile_menu.Append(self.display_item, _("Display"))
        self.about_item = wx.Menu()
        self.profile_menu.Append(self.about_item, _("About"))
        # Menu Bar end
        self.profile_statusbar = self.CreateStatusBar(1, 0)
        self.preview_tab = PreviewPanel(self.profile_book, -1)
        self.personal_tab = PersonalPanel(self.profile_book, -1)
        self.custom_tab = CustomPanel(self.profile_book, -1)
        self.file_tab = FilePanel(self.profile_book, -1)
        self.other_tab = OthersPanel(self.profile_book, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.facade = get_facade()
        self.bind_controls()

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.Bind(wx.EVT_MENU, self.on_export, id=self.export_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_save, id=self.save_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_load, id=self.load_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_quit, id=self.quit_item.GetId())
        
        self.Bind(wx.EVT_MENU, self.on_add, id=self.addpeer_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_make_friend, id=self.friend_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_blacklist, id=self.blacklisted_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_anonymous, id=self.anonymous_item.GetId())
        
        self.Bind(wx.EVT_MENU, self.set_refresh, id=self.autorefresh_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_refresh, id=self.refresh_item.GetId())

    def on_add(self, evt):
        """save profile .prf"""
        dlg = wx.FileDialog(
            self, message="Add profile ...",
            defaultDir=PROFILE_DIR,
            defaultFile="",
            wildcard="Solipsis file (*.prf)|*.prf",
            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            loader = FileDocument()
            loader.load(path)
            self.facade.add_peer(loader.get_pseudo())
            self.facade.fill_data((loader.get_pseudo(), loader))
            self.facade.display_peer_preview(loader.get_pseudo())

    def on_load(self, evt):
        """load profile .prf"""
        dlg = wx.FileDialog(
            self, message="Load profile ...",
            defaultDir=PROFILE_DIR,
            defaultFile=".prf",
            wildcard="Solipsis file (*.prf)|*.prf",
            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.facade.load_profile(path)
            self.facade.refresh_html_preview()

    def on_save(self, evt):
        """save .prf"""
        dlg = wx.FileDialog(
            self, message="Save profile as ...",
            defaultDir=PROFILE_DIR,
            defaultFile=self.personal_tab.nickname_value.GetValue()+".prf",
            wildcard="Solipsis file (*.prf)|*.prf",
            style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.facade.save_profile(path)
        
    def on_export(self, evt):
        """export .html"""
        dlg = wx.FileDialog(
            self, message="Export HTML file as ...",
            defaultDir=PROFILE_DIR,
            defaultFile="",
            wildcard="HTML File (*.html)|*.html",
            style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.facade.export_profile(path)

    def on_quit(self, evt):
        """end application"""
        self.Close()

    def on_make_friend(self, evt):
        """end application"""
        pseudo = self.other_tab.peers_list.get_peer_selected()
        if pseudo:
            self.facade.make_friend(pseudo)

    def on_blacklist(self, evt):
        """end application"""
        pseudo = self.other_tab.peers_list.get_peer_selected()
        if pseudo:
            self.facade.blacklist_peer(pseudo)

    def on_anonymous(self, evt):
        """end application"""
        pseudo = self.other_tab.peers_list.get_peer_selected()
        if pseudo:
            self.facade.unmark_peer(pseudo)

    def set_refresh(self, evt):
        """refresh HTML preview"""
        self.facade.set_auto_refresh_html(evt.IsChecked())

    def on_refresh(self, evt):
        """refresh HTML preview"""
        self.facade.refresh_html_preview()
        
    def __set_properties(self):
        # begin wxGlade: ProfileFrame.__set_properties
        self.SetTitle(_("profile_frame"))
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/icon.gif", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((700, 600))
        self.profile_statusbar.SetStatusWidths([-1])
        # statusbar fields
        profile_statusbar_fields = [_("status")]
        for i in range(len(profile_statusbar_fields)):
            self.profile_statusbar.SetStatusText(profile_statusbar_fields[i], i)
        self.profile_book.SetSize((400, 300))
        # end wxGlade
        self.activate_item.Check()
        self.autorefresh_item.Check()

    def __do_layout(self):
        # begin wxGlade: ProfileFrame.__do_layout
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self.profile_book.AddPage(self.preview_tab, _("Preview"))
        self.profile_book.AddPage(self.personal_tab, _("Personal"))
        self.profile_book.AddPage(self.custom_tab, _("Special Interests"))
        self.profile_book.AddPage(self.file_tab, _("Files"))
        self.profile_book.AddPage(self.other_tab, _("Contacts"))
        frame_sizer.Add(wx.NotebookSizer(self.profile_book), 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(frame_sizer)
        self.Layout()
        self.Centre()
        # end wxGlade

# end of class ProfileFrame


