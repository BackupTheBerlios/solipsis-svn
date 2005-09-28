# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Tue Jun 21 11:01:29 2005

import wx
import sys
from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxy
from solipsis.services.profile import REGEX_HTML, PROFILE_EXT
from solipsis.services.profile.prefs import get_prefs, set_prefs
from solipsis.services.profile.facade import get_filter_facade, get_facade
from solipsis.services.profile.file_document import FileDocument
from solipsis.services.profile.gui.AboutDialog import AboutDialog
from solipsis.services.profile.gui.ProfileDialog import ProfileDialog
from solipsis.services.profile.gui.MatchFrame import MatchFrame

# begin wxGlade: dependencies
from FileFilterPanel import FileFilterPanel
from PersonalFilterPanel import PersonalFilterPanel
# end wxGlade

class FilterFrame(wx.Frame):
    def __init__(self, options, parent, id, title, plugin=None, **kwds):
        self.plugin = plugin
        self.modified = False
        self.options = options
        args = (parent, id, title)
        # begin wxGlade: FilterFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.filter_book = wx.Notebook(self, -1, style=0)
        
        # Menu Bar
        self.filter_menu = wx.MenuBar()
        self.SetMenuBar(self.filter_menu)
        self.profile_item = wx.Menu()
        self.activate_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Activated\tCtrl+A"), _("Switch filters on/off"), wx.ITEM_CHECK)
        self.profile_item.AppendItem(self.activate_item)
        self.profile_item.AppendSeparator()
        self.save_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Save\tCtrl+S"), _("Save profile into file"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.save_item)
        self.quit_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Close\tCtrl+W"), _("Close profile management"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.quit_item)
        self.filter_menu.Append(self.profile_item, _("Action"))
        self.help_menu = wx.Menu()
        self.help_item = wx.MenuItem(self.help_menu, wx.NewId(), _("Help...\tCtrl+H"), _("Display information about regular expressions"), wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.help_item)
        self.help_menu.AppendSeparator()
        self.about_item = wx.MenuItem(self.help_menu, wx.NewId(), _("About...\tCtrl+?"), "", wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.about_item)
        self.filter_menu.Append(self.help_menu, _("Info"))
        # Menu Bar end
        self.filter_statusbar = self.CreateStatusBar(1, 0)
        self.personal_filter_tab = PersonalFilterPanel(self.filter_book, -1)
        self.file_filter_tab = FileFilterPanel(self.filter_book, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        # quite different initialisation according to launched by navigator or not
        if self.options["standalone"]:
            self.import_item = wx.MenuItem(self.profile_item, wx.NewId(), _("Import...\tCtrl+I"), _("Load & Match a profile and add it in contact list"), wx.ITEM_NORMAL)
            self.profile_item.AppendItem(self.import_item)
        # events
        self.match_frame = UIProxy(MatchFrame(options, parent, -1, plugin=self.plugin))
        self.help_dialog = ProfileDialog(parent, -1)
        self.help_dialog.profile_window.SetPage(open(REGEX_HTML()).read())
        self.help_dialog.SetTitle(_("Using regular expressions"))
        self.bind_controls()

    def on_change_facade(self):
        """called when user changes identity (facade chanegd)"""
        get_filter_facade()._activated = self.activate_item.IsChecked()
        
    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        # action
        self.Bind(wx.EVT_MENU, self.on_activate, id=self.activate_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_save, id=self.save_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_close, id=self.quit_item.GetId())
        self.Bind(wx.EVT_CLOSE, self.on_close)
        if self.options["standalone"]:
            self.Bind(wx.EVT_MENU, self.on_import, id=self.import_item.GetId())
        # about
        self.Bind(wx.EVT_MENU, self.on_about,id=self.about_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_help,id=self.help_item.GetId())

    def on_activate(self, evt):
        """activate service"""
        print self.activate_item.IsChecked() and "Activating..." \
              or "Disactivated"
        get_filter_facade()._activated = self.activate_item.IsChecked()

    def on_import(self, evt):
        """match current filter with given profile"""
        dlg = wx.FileDialog(
            self, message="Match profile ...",
            defaultDir=get_prefs("profile_dir"),
            defaultFile="",
            wildcard="Solipsis file (*.prf)|*.prf",
            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()[:-4]
            loader = FileDocument()
            loader.load(path + PROFILE_EXT)
            get_facade().fill_data(loader.get_pseudo(), loader)
            get_filter_facade().fill_data(loader.get_pseudo(), loader)
        
    def on_save(self, evt):
        """save .prf"""
        self.do_modified(False)
        get_filter_facade()._desc.save()
        
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
                self.on_save(evt)
        # save size
        new_size = self.GetSize()
        set_prefs("filter_width", new_size.GetWidth())
        set_prefs("filter_height", new_size.GetHeight())
        # close dialog
        if self.options["standalone"]:
            self._close()
        else:
            self.Hide()

    def _close(self):
        """termainate application"""
        self.help_dialog.Destroy()
        self.Destroy()
        sys.exit()

    def on_help(self, evt):
        """display dialog about regular expression"""
        wx.Dialog.Show(self.help_dialog)
        
    def on_about(self, evt):
        """display about"""
        # not modal because would freeze the wx thread while twisted
        # one goes on and initialize profile
        about_dlg = AboutDialog(get_prefs("disclaimer"), self, -1)
        about_dlg.Show()

    def do_modified(self, modified):
        """change state according to modified"""
        self.modified = modified
        if self.modified:
            self.save_item.Enable(True)
        else:
            self.save_item.Enable(False)

    def __set_properties(self):
        # begin wxGlade: FilterFrame.__set_properties
        self.SetTitle(_("Profile Filters"))
        self.SetSize((460, 600))
        self.filter_statusbar.SetStatusWidths([-1])
        # statusbar fields
        filter_statusbar_fields = [_("status")]
        for i in range(len(filter_statusbar_fields)):
            self.filter_statusbar.SetStatusText(filter_statusbar_fields[i], i)
        # end wxGlade
        width = get_prefs("filter_width")
        height = get_prefs("filter_height")
        self.SetSize((width, height))
        self.do_modified(False)
        self.activate_item.Check()
        # should be passed through constructor but wxglade does not allow it
        self.personal_filter_tab.do_modified = self.do_modified
        self.file_filter_tab.do_modified = self.do_modified


    def __do_layout(self):
        # begin wxGlade: FilterFrame.__do_layout
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        self.filter_book.AddPage(self.personal_filter_tab, _("Personal"))
        self.filter_book.AddPage(self.file_filter_tab, _("Files"))
        frame_sizer.Add(self.filter_book, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(frame_sizer)
        self.Layout()
        self.Centre()
        # end wxGlade

# end of class FilterFrame


