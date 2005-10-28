# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Tue Jun 21 10:17:16 2005
"""Main class of editing GUI"""

import wx
import sys
from solipsis.util.wxutils import _
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.prefs import get_prefs, set_prefs

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
        self.plugin = plugin
        self.modified = False
        self.options = options
        args = (parent, id, title)
        # begin wxGlade: EditorFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.profile_book = wx.Notebook(self, -1, style=0)
        
        # Menu Bar
        self.profile_menu = wx.MenuBar()
        self.SetMenuBar(self.profile_menu)
        self.profile_item = wx.Menu()
        self.activate_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Online\tCtrl+O"), _("Allow users seeing profile"), wx.ITEM_CHECK)
        self.profile_item.AppendItem(self.activate_item)
        self.profile_item.AppendSeparator()
        self.export_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Export HTML ...\tCtrl+E"), _("Write profile as HTML File"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.export_item)
        self.save_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Save\tCtrl+S"), _("Save profile into file"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.save_item)
        self.quit_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Close\tCtrl+W"), _("Close profile management"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.quit_item)
        self.profile_menu.Append(self.profile_item, _("Action"))
        self.files_menu = wx.Menu()
        self.add_item = wx.MenuItem(self.files_menu, wx.NewId(), _("&Add directory...\tCtrl+A"), "", wx.ITEM_NORMAL)
        self.files_menu.AppendItem(self.add_item)
        self.del_item = wx.MenuItem(self.files_menu, wx.NewId(), _("&Remove directory...\tCtrl+R"), "", wx.ITEM_NORMAL)
        self.files_menu.AppendItem(self.del_item)
        self.files_menu.AppendSeparator()
        self.share_item = wx.MenuItem(self.files_menu, wx.NewId(), _("Share"), "", wx.ITEM_NORMAL)
        self.files_menu.AppendItem(self.share_item)
        self.unshare_item = wx.MenuItem(self.files_menu, wx.NewId(), _("Unshare"), "", wx.ITEM_NORMAL)
        self.files_menu.AppendItem(self.unshare_item)
        self.profile_menu.Append(self.files_menu, _("Files"))
        self.help_menu = wx.Menu()
        self.preview_item = wx.MenuItem(self.help_menu, wx.NewId(), _("&Profile...\tCtrl+P"), _("Preview your profile"), wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.preview_item)
        self.shared_item = wx.MenuItem(self.help_menu, wx.NewId(), _("S&hared Files...\tCtrl+H"), _("Preview your shared files"), wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.shared_item)
        self.help_menu.AppendSeparator()
        self.about_item = wx.MenuItem(self.help_menu, wx.NewId(), _("About...\tCtrl+?"), "", wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.about_item)
        self.profile_menu.Append(self.help_menu, _("Info"))
        # Menu Bar end
        self.statusbar = self.CreateStatusBar(1, 0)
        self.personal_tab = PersonalPanel(self.profile_book, -1)
        self.blog_tab = BlogPanel(self.profile_book, -1)
        self.file_tab = FilePanel(self.profile_book, -1,
                                  cb_selected=self.cb_selected)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        if self.options["standalone"]:
            #put here special initialisation for standalone editor
            pass
        self.profile_dlg = ProfileDialog(parent, -1, plugin=self.plugin)
        # events
        self.bind_controls()

    def Show(self, show=True):
        wx.Frame.Show(self, show)
        # disclaimer
        if show and get_prefs("disclaimer"):
            self.on_about(None)

    def on_change_facade(self):
        """update facade"""
        self.personal_tab.on_change_facade()
        self.blog_tab.on_change_facade()
        self.file_tab.on_change_facade()
        self.profile_dlg.on_change_facade(auto_refresh=True)

    def cb_selected(self, file_name):
            self.share_item.SetText(_("Share '%s'"% file_name))
            self.unshare_item.SetText(_("UnShare '%s'"% file_name))

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        # action
        self.Bind(wx.EVT_MENU, self.on_activate, id=self.activate_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_export, id=self.export_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_save, id=self.save_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_close, id=self.quit_item.GetId())
        self.Bind(wx.EVT_CLOSE, self.on_close)
        # Files
        self.Bind(wx.EVT_MENU, self.file_tab.on_browse, id=self.add_item.GetId())
        self.Bind(wx.EVT_MENU, self.file_tab.on_remove, id=self.del_item.GetId())
        self.Bind(wx.EVT_MENU, self.file_tab.on_share, id=self.share_item.GetId())
        self.Bind(wx.EVT_MENU, self.file_tab.on_unshare, id=self.unshare_item.GetId())
        # about
        self.Bind(wx.EVT_MENU, self.on_display_profile, id=self.preview_item.GetId())
        self.Bind(wx.EVT_MENU, self.file_tab.on_preview, id=self.shared_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_about,id=self.about_item.GetId())
        if self.options["standalone"]:
            #put here special initialisation for standalone editor
            pass

    def on_activate(self, evt):
        """activate service"""
        activate = self.activate_item.IsChecked()
        print activate and "Activating..." \
              or "Disactivated"
        get_facade()._activated = activate
        
    def on_save(self, evt):
        """save .prf"""
        get_facade()._desc.save()
        self.do_modified(False)
        
    def on_export(self, evt):
        """export .html"""
        dlg = wx.FileDialog(
            self, message=_("Export HTML file as ..."),
            defaultDir=get_prefs("profile_dir"),
            defaultFile="%s.html"% get_facade()._desc.document.get_pseudo(),
            wildcard=_("HTML File (*.html)|*.html"),
            style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            get_facade().export_profile(path)
        
    def on_close(self, evt=None):
        """hide  application"""
        # ask for saving
        if self.modified:
            self.do_modified(False)
            dlg = wx.MessageDialog(
                self,
                _('Your profile has been modified. Do you want to change it?'),
                _('Saving Dialog'),
                wx.YES_NO | wx.ICON_INFORMATION)
            if dlg.ShowModal() == wx.ID_YES:
                self.on_save(evt)
        # save size
        new_size = self.GetSize()
        set_prefs("profile_width", new_size.GetWidth())
        set_prefs("profile_height", new_size.GetHeight())
        # close dialog
        if self.options["standalone"]:
            self.profile_dlg.Destroy()
            self.Destroy()
            self.options['App'].ExitMainLoop()
        else:
            self.Hide()

    def on_about(self, evt):
        """display about"""
        # not modal because would freeze the wx thread while twisted
        # one goes on and initialize profile
        about_dlg = AboutDialog(get_prefs("disclaimer"), self, -1)
        about_dlg.Show()

    def on_display_profile(self, evt):
        """display blog in dedicated window"""
        self.profile_dlg.Show(get_facade()._desc)

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
        self.SetMinSize((460, 600))
        self.statusbar.SetStatusWidths([-1])
        # statusbar fields
        statusbar_fields = [_("status")]
        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)
        # end wxGlade
        # set previous size
        width = get_prefs("profile_width")
        height = get_prefs("profile_height")
        self.SetSize((width, height))
        self.do_modified(False)
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


