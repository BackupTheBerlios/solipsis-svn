# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Tue Jun 21 10:17:16 2005
"""Main class of editing GUI"""

import wx
import sys
from solipsis.util.wxutils import _
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile import PROFILE_DIR, skip_disclaimer

from solipsis.services.profile.gui.FileDialog import FileDialog
from solipsis.services.profile.gui.ProfileDialog import ProfileDialog
from solipsis.services.profile.gui.AboutDialog import AboutDialog

# begin wxGlade: dependencies
from BlogPanel import BlogPanel
from FilePanel import FilePanel
from PersonalPanel import PersonalPanel
# end wxGlade

class EditorFrame(wx.Frame):
    """Frame where profile is edited"""
    
    def __init__(self, options, parent, id, title, plugin=None, **kwds):
        self.facade = get_facade()
        self.plugin = plugin
        self.modified = False
        self.options = options
        args = (parent, id, title)
        # begin wxGlade: EditorFrame.__init__
        kwds["style"] = wx.ICONIZE|wx.CAPTION|wx.MINIMIZE|wx.CLOSE_BOX|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.SYSTEM_MENU|wx.RESIZE_BORDER|wx.CLIP_CHILDREN
        wx.Frame.__init__(self, *args, **kwds)
        self.profile_book = wx.Notebook(self, -1, style=0)
        
        # Menu Bar
        self.profile_menu = wx.MenuBar()
        self.SetMenuBar(self.profile_menu)
        self.profile_item = wx.Menu()
        self.activate_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Online\tCtrl+O"), _("Allow users seeing profile"), wx.ITEM_CHECK)
        self.profile_item.AppendItem(self.activate_item)
        self.filters_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Filters...\tCtrl+F"), _("Create active filters to get notified on peers approach"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.filters_item)
        self.profile_item.AppendSeparator()
        self.export_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Export HTML ...\tCtrl+E"), _("Write profile as HTML File"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.export_item)
        self.save_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Save\tCtrl+S"), _("Save profile into file"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.save_item)
        self.quit_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Close\tCtrl+W"), _("Close profile management"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.quit_item)
        self.profile_menu.Append(self.profile_item, _("Action"))
        self.help_menu = wx.Menu()
        self.about_item = wx.MenuItem(self.help_menu, wx.NewId(), _("About...\tCtrl+?"), "", wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.about_item)
        self.preview_item = wx.MenuItem(self.help_menu, wx.NewId(), _("Preview...\tCtrl+P"), "", wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.preview_item)
        self.profile_menu.Append(self.help_menu, _("Info"))
        # Menu Bar end
        self.profile_statusbar = self.CreateStatusBar(1, 0)
        self.personal_tab = PersonalPanel(self.profile_book, -1)
        self.blog_tab = BlogPanel(self.profile_book, -1)
        self.file_tab = FilePanel(self.profile_book, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        if self.options["standalone"]:
            #put here special initialisation for standalone editor
            pass

        self.profile_dlg = ProfileDialog(parent, -1, plugin=self.plugin)
        self.personal_tab.set_facade(self.facade)
        self.blog_tab.set_facade(self.facade)
        self.file_tab.set_facade(self.facade)
        self.profile_dlg.set_facade(self.facade, auto_refresh=True)
        # events
        self.bind_controls()
        # disclaimer
        if not skip_disclaimer():
            self.on_about(None)

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        # action
        self.Bind(wx.EVT_MENU, self.on_activate, id=self.activate_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_export, id=self.export_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_save, id=self.save_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_close, id=self.quit_item.GetId())
        self.Bind(wx.EVT_CLOSE, self.on_close)
        # about
        self.Bind(wx.EVT_MENU, self.on_about,id=self.about_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_display_profile, id=self.preview_item.GetId())
        if self.options["standalone"]:
            #put here special initialisation for standalone editor
            pass

    def on_activate(self, evt):
        """activate service"""
        print self.activate_item.IsChecked() and "Activating..." \
              or "Disactivated"
        active = self.activate_item.IsChecked()
        self.facade.activate(active)
        self.plugin.activate(active)
        
    def on_save(self, evt):
        """save .prf"""
        self.facade.save_profile()
        self.do_modified(False)
        
    def on_export(self, evt):
        """export .html"""
        dlg = wx.FileDialog(
            self, message="Export HTML file as ...",
            defaultDir=PROFILE_DIR,
            defaultFile="%s.html"% self.facade.get_pseudo(),
            wildcard="HTML File (*.html)|*.html",
            style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.facade.export_profile(path)
        
    def on_close(self, evt=None):
        """hide  application"""
        # ask for saving
        if self.modified:
            self.do_modified(False)
            dlg = wx.MessageDialog(
                self,
                'Your profile has been modified. Do you want to change it?',
                'Saving Dialog',
                wx.YES_NO | wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_YES:
                self.facade.save_profile()
        # close dialog
        if self.options["standalone"]:
            self._close()
        else:
            self.Hide()

    def _close(self):
        """termainate application"""
        self.profile_dlg.Destroy()
        self.Destroy()
        sys.exit()
        
    def on_about(self, evt):
        """display about"""
        # not modal because would freeze the wx thread while twisted
        # one goes on and initialize profile
        about_dlg = AboutDialog(not skip_disclaimer(), self, -1)
        about_dlg.Show()

    def on_display_profile(self, evt):
        """display blog in dedicated window"""
        self.profile_dlg.Show()

    def do_modified(self, modified):
        """change state according to modified"""
        self.modified = modified
        if self.modified:
            self.save_item.Enable(True)
        else:
            self.save_item.Enable(False)
            
    def __set_properties(self):
        """generated by SetTitle"""
        # begin wxGlade: EditorFrame.__set_properties
        self.SetTitle(_("Profile Editor"))
        self.SetSize((460, 600))
        self.profile_statusbar.SetStatusWidths([-1])
        # statusbar fields
        profile_statusbar_fields = [_("status")]
        for i in range(len(profile_statusbar_fields)):
            self.profile_statusbar.SetStatusText(profile_statusbar_fields[i], i)
        # end wxGlade
        
        self.do_modified(False)
        self.filters_item.Enable(False)
        self.activate_item.Check()
        # should be passed through constructor but wxglade does not allow it
        self.personal_tab.do_modified = self.do_modified
        self.blog_tab.do_modified = self.do_modified
        self.file_tab.do_modified = self.do_modified

    def __do_layout(self):
        """generated by SetTitle"""
        # begin wxGlade: EditorFrame.__do_layout
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self.profile_book.AddPage(self.personal_tab, _("Personal"))
        self.profile_book.AddPage(self.blog_tab, _("Blog"))
        self.profile_book.AddPage(self.file_tab, _("Files"))
        frame_sizer.Add(self.profile_book, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(frame_sizer)
        self.Layout()
        self.Centre()
        # end wxGlade

# end of class EditorFrame


