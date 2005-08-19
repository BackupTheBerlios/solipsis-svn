# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Mon Jun 20 17:24:56 2005

import wx
import sys

from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxy
from solipsis.services.profile import PROFILE_FILE
from solipsis.services.profile.prefs import get_prefs
from solipsis.services.profile.file_document import FileDocument
from solipsis.services.profile.view import HtmlView
from solipsis.services.profile.data import PeerDescriptor, load_blogs
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.gui.PreviewPanel import MyHtmlWindow
from solipsis.services.profile.gui.BlogPanel import BlogPanel
from solipsis.services.profile.gui.FilePanel import FilePanel

from solipsis.services.profile.gui.BlogDialog import BlogDialog
from solipsis.services.profile.gui.FileDialog import FileDialog
from solipsis.services.profile.gui.ProfileDialog import ProfileDialog
from solipsis.services.profile.gui.AboutDialog import AboutDialog

# begin wxGlade: dependencies
# end wxGlade

class ViewerFrame(wx.Frame):
    def __init__(self, options, parent, id, title, plugin=None, **kwds):
        self.plugin = plugin
        self.options = options
        args = (parent, id, title)
        # begin wxGlade: ViewerFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.viewer_book = wx.Notebook(self, -1, style=0)
        self.file_tab = wx.Panel(self.viewer_book, -1)
        self.blog_tab = wx.Panel(self.viewer_book, -1)
        self.view_tab = wx.Panel(self.viewer_book, -1)
        
        # Menu Bar
        self.viewer_menu = wx.MenuBar()
        self.SetMenuBar(self.viewer_menu)
        self.action_item = wx.Menu()
        self.export_item = wx.MenuItem(self.action_item, wx.NewId(), _("&Export HTML ...\tCtrl+E"), _("Write profile as HTML File"), wx.ITEM_NORMAL)
        self.action_item.AppendItem(self.export_item)
        self.quit_item = wx.MenuItem(self.action_item, wx.NewId(), _("&Close\tCtrl+W"), _("Close profile management"), wx.ITEM_NORMAL)
        self.action_item.AppendItem(self.quit_item)
        self.viewer_menu.Append(self.action_item, _("Action"))
        self.refresh_menu = wx.Menu()
        self.r_all_item = wx.MenuItem(self.refresh_menu, wx.NewId(), _("Refresh All"), "", wx.ITEM_NORMAL)
        self.refresh_menu.AppendItem(self.r_all_item)
        self.refresh_menu.AppendSeparator()
        self.r_profile_item = wx.MenuItem(self.refresh_menu, wx.NewId(), _("Profile\tCtrl+P"), "", wx.ITEM_NORMAL)
        self.refresh_menu.AppendItem(self.r_profile_item)
        self.r_blog_item = wx.MenuItem(self.refresh_menu, wx.NewId(), _("Blog\tCtrl+B"), "", wx.ITEM_NORMAL)
        self.refresh_menu.AppendItem(self.r_blog_item)
        self.r_files_item = wx.MenuItem(self.refresh_menu, wx.NewId(), _("List files\tCtrl+L"), "", wx.ITEM_NORMAL)
        self.refresh_menu.AppendItem(self.r_files_item)
        self.viewer_menu.Append(self.refresh_menu, _("Refresh"))
        self.status_item = wx.Menu()
        self.anonymous_item = wx.MenuItem(self.status_item, wx.NewId(), _("&Anonymous\tCtrl+A"), "", wx.ITEM_RADIO)
        self.status_item.AppendItem(self.anonymous_item)
        self.friend_item = wx.MenuItem(self.status_item, wx.NewId(), _("&Friend\tCtrl+F"), "", wx.ITEM_RADIO)
        self.status_item.AppendItem(self.friend_item)
        self.blacklisted_item = wx.MenuItem(self.status_item, wx.NewId(), _("&Ignore\tCtrl+I"), "", wx.ITEM_RADIO)
        self.status_item.AppendItem(self.blacklisted_item)
        self.viewer_menu.Append(self.status_item, _("Status"))
        self.help_menu = wx.Menu()
        self.about_item = wx.MenuItem(self.help_menu, wx.NewId(), _("About...\tCtrl+?"), "", wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.about_item)
        self.viewer_menu.Append(self.help_menu, _("Help"))
        # Menu Bar end
        self.viewer_statusbar = self.CreateStatusBar(1, 0)
        self.html_view = MyHtmlWindow(self.view_tab, -1)
        self.blog_panel = BlogPanel(self.blog_tab, -1)
        self.file_panel = FilePanel(self.file_tab, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        # quite different initialisation according to launched by navigator or not
        if self.options["standalone"]:
            self.import_item = wx.MenuItem(self.action_item, wx.NewId(), _("Import...\tCtrl+I"), _("Load a profile and add it in contact list"), wx.ITEM_NORMAL)
            self.action_item.AppendItem(self.import_item)
        # set up dialogs
        self.profile_dlg = UIProxy(ProfileDialog(parent, -1, plugin=self.plugin))
        self.peer_dlg = UIProxy(BlogDialog(parent, -1, plugin=self.plugin))
        self.file_dlg = UIProxy(FileDialog(parent, -1, plugin=self.plugin))
        self.bind_controls()

    def on_change_facade(self):
        self.blog_panel.on_change_facade()
        self.file_panel.on_change_facade()

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        # actions
        self.Bind(wx.EVT_MENU, self.on_export, id=self.export_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_close, id=self.quit_item.GetId())
        self.Bind(wx.EVT_CLOSE, self.on_close)
        if self.options["standalone"]:
            self.Bind(wx.EVT_MENU, self.on_add, id=self.import_item.GetId())
        # refresh
        self.Bind(wx.EVT_MENU, self.on_get_all, id=self.r_all_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_get_profile, id=self.r_profile_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_get_blog, id=self.r_blog_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_get_files, id=self.r_files_item.GetId())
        # change status
        self.Bind(wx.EVT_MENU, self.on_make_friend, id=self.friend_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_blacklist, id=self.blacklisted_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_anonymous, id=self.anonymous_item.GetId())
        # about
        self.Bind(wx.EVT_MENU, self.on_about, id=self.about_item.GetId())
        
    def on_export(self, evt):
        """export .html"""
        dlg = wx.FileDialog(
            self, message="Export HTML file as ...",
            defaultDir=get_prefs("profile_dir"),
            defaultFile="",
            wildcard="HTML File (*.html)|*.html",
            style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            get_facade().export_profile(path)
        
    def on_close(self, evt):
        """hide  application"""
        get_facade().save()
        if self.options["standalone"]:
            self._close()
        else:
            self.Hide()

    def _close(self):
        """termainate application"""
        self.profile_dlg.Destroy()
        self.peer_dlg.Destroy()
        self.file_dlg.Destroy()
        self.Destroy()
        sys.exit()
        
    def on_add(self, evt):
        """save profile .prf"""
        dlg = wx.FileDialog(
            self, message="Add profile ...",
            defaultDir=get_prefs("profile_dir"),
            defaultFile="",
            wildcard="Solipsis file (*.prf)|*.prf",
            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            directory, pseudo = os.path.split(dlg.GetPath()[:-4])
            loader = FileDocument(pseudo, directory)
            loader.load()
            blogs = load_blogs(pseudo, directory)
            pseudo = loader.pseudo
            get_facade().fill_data((pseudo, loader))
            get_facade().get_peer(pseudo).set_blog(blogs)

    def on_get_all(self, evt):
        """display peer's blog"""
        pass

    def on_get_profile(self, evt):
        """display peer's files"""
        peer_id = self.other_tab.get_peer_selected()
        if peer_id:
            peer_desc = get_facade().get_peer(peer_id)
            if peer_desc.connected:
                self.plugin.get_profile(peer_id)
            else:
                print "not connected"
                self.display_profile(peer_desc)
        else:
            "no peer selected"

    def on_get_blog(self, evt):
        """display peer's blog"""
        peer_id = self.other_tab.get_peer_selected()
        if peer_id:
            peer_desc = get_facade().get_peer(peer_id)
            if peer_desc.connected:
                self.plugin.get_blog_file(peer_id)
            else:
                print "not connected"
                self.display_blog(peer_desc)
        else:
            print "no peer selected"

    def on_get_files(self, evt):
        """display peer's files"""
        peer_id = self.other_tab.get_peer_selected()
        if peer_id:
            peer_desc = get_facade().get_peer(peer_id)
            if peer_desc.connected:
                self.plugin.select_files(peer_id)
            else:
                print "not connected"
                self.display_files(peer_desc)
        else:
            "no peer selected"

    def on_make_friend(self, evt):
        """end application"""
        pseudo = self.other_tab.get_peer_selected()
        if pseudo:
            get_facade().make_friend(pseudo)
        else:
            print "no peer selected"

    def on_blacklist(self, evt):
        """end application"""
        pseudo = self.other_tab.get_peer_selected()
        if pseudo:
            get_facade().blacklist_peer(pseudo)
        else:
            print "no peer selected"

    def on_anonymous(self, evt):
        """end application"""
        pseudo = self.other_tab.get_peer_selected()
        if pseudo:
            get_facade().unmark_peer(pseudo)
        else:
            print "no peer selected"

    def on_about(self, evt):
        """display about"""
        # not modal because would freeze the wx thread while twisted
        # one goes on and initialize profile
        about_dlg = AboutDialog(get_prefs("disclaimer"), self, -1)
        about_dlg.Show()

    def display_profile(self, peer_desc):
        """display blog in dedicated window"""
        # profile dialog
        self.profile_dlg.Show(peer_desc)
        
    def display_blog(self, peer_desc):
        """display blog in dedicated window"""
        # blog dialog
        self.peer_dlg.SetTitle(peer_desc)
        # display
        self.peer_dlg.Show(peer_desc.blog)

    def display_files(self, peer_desc):
        """display blog in dedicated window"""
        # file dialog
        self.file_dlg.set_desc(peer_desc)
        self.file_dlg.SetTitle()
        # display files {repos: {names:tags}, }
        self.file_dlg.Show(files=peer_desc.shared_files)

    def __set_properties(self):
        # begin wxGlade: ViewerFrame.__set_properties
        self.SetTitle(_("Profile Viewer"))
        self.SetSize((460, 600))
        self.viewer_statusbar.SetStatusWidths([-1])
        # statusbar fields
        viewer_statusbar_fields = [_("status")]
        for i in range(len(viewer_statusbar_fields)):
            self.viewer_statusbar.SetStatusText(viewer_statusbar_fields[i], i)
        # end wxGlade

        self.r_all_item.Enable(False)
        self.enable_peer_states(False)

    def __do_layout(self):
        # begin wxGlade: ViewerFrame.__do_layout
        viewer_sizer = wx.BoxSizer(wx.VERTICAL)
        file_sizer = wx.BoxSizer(wx.VERTICAL)
        blog_sizer = wx.BoxSizer(wx.VERTICAL)
        view_sizer = wx.BoxSizer(wx.HORIZONTAL)
        view_sizer.Add(self.html_view, 1, wx.EXPAND, 0)
        self.view_tab.SetAutoLayout(True)
        self.view_tab.SetSizer(view_sizer)
        view_sizer.Fit(self.view_tab)
        view_sizer.SetSizeHints(self.view_tab)
        blog_sizer.Add(self.blog_panel, 1, wx.EXPAND, 0)
        self.blog_tab.SetAutoLayout(True)
        self.blog_tab.SetSizer(blog_sizer)
        blog_sizer.Fit(self.blog_tab)
        blog_sizer.SetSizeHints(self.blog_tab)
        file_sizer.Add(self.file_panel, 1, wx.EXPAND, 0)
        self.file_tab.SetAutoLayout(True)
        self.file_tab.SetSizer(file_sizer)
        file_sizer.Fit(self.file_tab)
        file_sizer.SetSizeHints(self.file_tab)
        self.viewer_book.AddPage(self.view_tab, _("View"))
        self.viewer_book.AddPage(self.blog_tab, _("Blog"))
        self.viewer_book.AddPage(self.file_tab, _("Files"))
        viewer_sizer.Add(self.viewer_book, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(viewer_sizer)
        self.Layout()
        self.Centre()
        # end wxGlade

    def enable_peer_states(self, enable, status=PeerDescriptor.ANONYMOUS):
        """(Dis)Activate menu items"""
        # select correct status
        if status == PeerDescriptor.FRIEND:
            self.friend_item.Check(True)
        elif status == PeerDescriptor.BLACKLISTED:
            self.blacklisted_item.Check(True)
        else:
            self.anonymous_item.Check(True)
        # (dis)activate items
        self.r_all_item.Enable(enable)
        self.r_profile_item.Enable(enable)
        self.r_blog_item.Enable(enable)
        self.r_files_item.Enable(enable)
        self.anonymous_item.Enable(enable)
        self.blacklisted_item.Enable(enable)
        self.friend_item.Enable(enable)

# end of class ViewerFrame


