# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Tue Jun 21 11:01:29 2005

#############
#
# TODO: after generation
#       self.edit_file_panel = EditFilePanel(self, self.edit_pane, -1)
#
#############

import wx
import sys
from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxy
from solipsis.services.profile import REGEX_HTML, PROFILE_EXT, FILTER_EXT
from solipsis.services.profile.gui import get_all_labels, get_new_label, \
     get_item_id_by_label, get_selected_labels
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.prefs import get_prefs, set_prefs
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.view import HtmlView
from solipsis.services.profile.filter_data import FileFilter, PeerFilter
from solipsis.services.profile.filter_facade import get_filter_facade
from solipsis.services.profile.file_document import FileDocument
from solipsis.services.profile.gui.AboutDialog import AboutDialog
from solipsis.services.profile.gui.ProfileDialog import ProfileDialog
from solipsis.services.profile.gui.EditFilePanel import EditFilePanel
from solipsis.services.profile.gui.EditProfilePanel import EditProfilePanel
from solipsis.services.profile.gui.ViewFilePanel import ViewFilePanel
from solipsis.services.profile.gui.ViewProfilePanel import ViewProfilePanel
from solipsis.services.profile.gui.PreviewPanel import MyHtmlWindow

# begin wxGlade: dependencies
# end wxGlade

class FilterFrame(wx.Frame):
    def __init__(self, options, parent, id, title, plugin=None, **kwds):
        self.plugin = plugin
        self.modified = False
        self.options = options
        self.tabs = {}
        args = (parent, id, title)
        # begin wxGlade: FilterFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.window_2 = wx.SplitterWindow(self, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.window_2_pane_2 = wx.Panel(self.window_2, -1)
        self.window_3 = wx.SplitterWindow(self.window_2_pane_2, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.window_3_pane_2 = wx.Panel(self.window_3, -1)
        self.window_3_pane_1 = wx.Panel(self.window_3, -1)
        self.window_4 = wx.SplitterWindow(self.window_3_pane_1, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.view_pane = wx.Panel(self.window_4, -1)
        self.window_4_pane_1 = wx.Panel(self.window_4, -1)
        self.edit_pane = wx.Panel(self.window_2, -1)
        self.edit_notebook = wx.Notebook(self.edit_pane, -1, style=0)
        self.notebook_1_pane_2 = wx.Panel(self.edit_notebook, -1)
        self.sizer_4_staticbox = wx.StaticBox(self.window_4_pane_1, -1, _("Filters"))
        self.sizer_6_staticbox = wx.StaticBox(self.window_3_pane_2, -1, _("Profile details..."))
        self.notebook_1_pane_1 = wx.Panel(self.edit_notebook, -1)
        
        # Menu Bar
        self.filter_menu = wx.MenuBar()
        self.SetMenuBar(self.filter_menu)
        self.profile_item = wx.Menu()
        self.activate_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Activate filters\tCtrl+A"), _("Switch filters on/off"), wx.ITEM_CHECK)
        self.profile_item.AppendItem(self.activate_item)
        self.new_file_item = wx.MenuItem(self.profile_item, wx.NewId(), _("New &File filter\tCtrl+F"), _("Create a new file filter"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.new_file_item)
        self.new_profile_item = wx.MenuItem(self.profile_item, wx.NewId(), _("New &Profile filter\tCtrl+P"), _("Create a new profile filter"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.new_profile_item)
        self.profile_item.AppendSeparator()
        self.save_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Save\tCtrl+S"), _("Save profile into file"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.save_item)
        self.quit_item = wx.MenuItem(self.profile_item, wx.NewId(), _("&Close\tCtrl+W"), _("Close profile management"), wx.ITEM_NORMAL)
        self.profile_item.AppendItem(self.quit_item)
        self.filter_menu.Append(self.profile_item, _("Action"))
        self.help_menu = wx.Menu()
        self.help_item = wx.MenuItem(self.help_menu, wx.NewId(), _("Help...\tCtrl+H"), _("Display information syntax of filters"), wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.help_item)
        self.help_menu.AppendSeparator()
        self.about_item = wx.MenuItem(self.help_menu, wx.NewId(), _("About...\tCtrl+?"), "", wx.ITEM_NORMAL)
        self.help_menu.AppendItem(self.about_item)
        self.filter_menu.Append(self.help_menu, _("Info"))
        # Menu Bar end
        self.statusbar = self.CreateStatusBar(1, 0)
        self.edit_file_panel = EditFilePanel(self, self.notebook_1_pane_1, -1)
        self.edit_profile_panel = EditProfilePanel(self, self.notebook_1_pane_2, -1)
        self.filter_list = wx.ListCtrl(self.window_4_pane_1, -1, style=wx.LC_REPORT|wx.LC_EDIT_LABELS|wx.LC_SORT_ASCENDING|wx.SUNKEN_BORDER)
        self.view_file_panel = ViewFilePanel(self.view_pane, -1)
        self.preview_notebook = wx.Notebook(self.window_3_pane_2, -1, style=0)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_MENU, self.on_activate, self.activate_item)
        self.Bind(wx.EVT_MENU, self.on_new_file, self.new_file_item)
        self.Bind(wx.EVT_MENU, self.on_new_profile, self.new_profile_item)
        self.Bind(wx.EVT_MENU, self.on_save, self.save_item)
        self.Bind(wx.EVT_MENU, self.on_close, self.quit_item)
        self.Bind(wx.EVT_MENU, self.on_help, self.help_item)
        self.Bind(wx.EVT_MENU, self.on_about, self.about_item)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_change_tab, self.edit_notebook)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_filter, self.filter_list)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_right_click_filter, self.filter_list)
        self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.on_right_click_col_filter, self.filter_list)
        # end wxGlade

        # filter list
        self.filter_list.InsertColumn(0, "Name")
        self.filter_list.InsertColumn(1, "#/##")
        self.filter_list.InsertColumn(2, "Type")
        self.filter_list.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        self.filter_list.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        self.filter_list.SetColumnWidth(2, wx.LIST_AUTOSIZE_USEHEADER)
        sash_position = 0
        for column in range(3):
            sash_position += self.filter_list.GetColumnWidth(column)
        self.window_4.SetSashPosition(sash_position+20)

        # file, profile panels & help dialog
        self.current_edit = self.edit_file_panel
        self.current_view = self.view_file_panel
        self.view_profile_panel = ViewProfilePanel(self.view_pane, -1)
        self.help_dialog = ProfileDialog(parent, -1)
        self.help_dialog.profile_window.SetPage(open(REGEX_HTML()).read())
        self.help_dialog.SetTitle(_("Syntax of filters"))
        
        # quite different initialisation according to launched by navigator or not
        if self.options["standalone"]:
            self.import_item = wx.MenuItem(self.profile_item, wx.NewId(), _("Import...\tCtrl+I"), _("Load & Match a profile and add it in contact list"), wx.ITEM_NORMAL)
            self.profile_item.AppendItem(self.import_item)
            self.Bind(wx.EVT_MENU, self.on_import, id=self.import_item.GetId())

        # popup menu
        self.popup_menu = wx.Menu()
        refresh_item = wx.MenuItem(self.popup_menu, wx.NewId(), _("Refresh"))
        delete_item = wx.MenuItem(self.popup_menu, wx.NewId(), _("Delete"))
        new_file_item = wx.MenuItem(self.popup_menu, wx.NewId(), _("New File filter"))
        new_profile_item = wx.MenuItem(self.popup_menu, wx.NewId(), _("New Profile filter"))
        self.popup_menu.AppendItem(refresh_item)
        self.popup_menu.AppendItem(delete_item)
        self.popup_menu.AppendSeparator()
        self.popup_menu.AppendItem(new_file_item)
        self.popup_menu.AppendItem(new_profile_item)
        self.Bind(wx.EVT_MENU, self.on_delete, delete_item)
        self.Bind(wx.EVT_MENU, self.on_refresh_filter, refresh_item)
        self.Bind(wx.EVT_MENU, self.on_new_file, new_file_item)
        self.Bind(wx.EVT_MENU, self.on_new_profile, new_profile_item)

        self.popup_col_menu = wx.Menu()
        new_file_item = wx.MenuItem(self.popup_col_menu, wx.NewId(), _("New File filter"))
        new_profile_item = wx.MenuItem(self.popup_col_menu, wx.NewId(), _("New Profile filter"))
        self.popup_col_menu.AppendItem(new_file_item)
        self.popup_col_menu.AppendItem(new_profile_item)
        self.Bind(wx.EVT_MENU, self.on_new_file, new_file_item)
        self.Bind(wx.EVT_MENU, self.on_new_profile, new_profile_item)
        
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.set_profile_view()
        self.set_file_view()

    # state ##########################################################
    def get_filter_names(self):
        return get_all_labels(self.filter_list)
    
    def on_change_facade(self):
        """called when user changes identity (facade chanegd)"""
        get_filter_facade()._activated = self.activate_item.IsChecked()

    def do_modified(self, modified):
        """change state according to modified"""
        self.modified = modified
        if self.modified:
            self.save_item.Enable(True)
        else:
            self.save_item.Enable(False)

    def cb_update(self, filter_name):
        # get line
        try:
            item_id = get_item_id_by_label(self.filter_list, filter_name)
        except KeyError:
            item_id = self.filter_list.InsertStringItem(sys.maxint, filter_name)
        # get data
        filter_ = get_filter_facade().get_filter(filter_name)
        try:
            counter = 0
            all_counter = 0
            for matches in get_filter_facade().get_results(filter_name).values():
                if matches:
                    counter += 1
                    all_counter += len(matches)
        except KeyError:
            pass
        # update data
        self.filter_list.SetStringItem(
            item_id, 1,
            str(counter)+"/"+str(all_counter))
        self.filter_list.SetStringItem(
            item_id, 2,
            isinstance(filter_, FileFilter) and "file" or "peer")

    def cb_delete(self, filter_name):
        item_id = get_item_id_by_label(self.filter_list, filter_name)
        self.filter_list.DeleteItem(item_id)
        self.view_profile_panel.reset()
        self.view_file_panel.reset()
        
    # tab ############################################################
    def set_tab(self, peer_id):
        """add or update tab with preview of given peer"""
        peer_desc = get_facade().get_peer(peer_id)
        if peer_desc.node_id in self.tabs:
            self._update_tab(peer_desc)
        else:
            self._add_tab(peer_desc)

    def _add_tab(self, peer_desc):
        """add tab with preview of given peer"""
        tab_sizer = wx.BoxSizer(wx.VERTICAL)
        preview_tab = wx.Panel(self.preview_notebook, -1)
        match_preview = MyHtmlWindow(preview_tab, -1)
        tab_sizer.Add(match_preview, 1, wx.EXPAND, 0)
        view = HtmlView(peer_desc)
        self.tabs[peer_desc.node_id] = preview_tab
        preview_tab.preview = match_preview
        preview_tab.pseudo = peer_desc.document.get_pseudo()
        preview_tab.SetAutoLayout(True)
        preview_tab.SetSizer(tab_sizer)
        preview_tab.preview.SetPage(view.get_view())
        tab_sizer.Fit(preview_tab)
        tab_sizer.SetSizeHints(preview_tab)
        self._update_tab(peer_desc)

    def _update_tab(self, peer_desc):
        """update tab with preview of given peer"""
        index = self.get_tab_index(peer_desc.node_id)
        if index == -1:
            self.preview_notebook.AddPage(self.tabs[peer_desc.node_id],
                                          peer_desc.document.get_pseudo())
            self.tabs[peer_desc.node_id].Show()
            self.preview_notebook.SetSelection(
                self.preview_notebook.GetPageCount()-1)
        
    def hide_tab(self, peer_id):
        """hide tab"""
        index = self.get_tab_index(peer_id)
        if index != -1:
            self.preview_notebook.RemovePage(index)
            self.tabs[peer_id].Hide()

    def get_tab_index(self, peer_id):
        peer_desc = get_facade().get_peer(peer_id)
        if peer_id in self.tabs:
            for index in range(self.preview_notebook.GetPageCount()):
                if self.preview_notebook.GetPage(index).pseudo \
                       == peer_desc.document.get_pseudo():
                    return index
        return -1
        
        
    # events #########################################################
    def on_activate(self, event): # wxGlade: FilterFrame.<event_handler>
        """activate service"""
        print self.activate_item.IsChecked() and "Activating..." \
              or "Disactivated"
        get_filter_facade()._activated = self.activate_item.IsChecked()
        event.Skip()

    def on_new_file(self, event): # wxGlade: FilterFrame.<event_handler>
        self.set_file_view()
        self.edit_file_panel.reset()
        self.edit_file_panel.filter_name_value.SetValue(
            get_new_label(self.filter_list, "filter_"))

    def on_new_profile(self, event): # wxGlade: FilterFrame.<event_handler>
        self.set_profile_view()
        self.edit_profile_panel.reset()
        self.edit_profile_panel.filter_name_value.SetValue(
            get_new_label(self.filter_list, "filter_"))
        
    def on_save(self, event): # wxGlade: FilterFrame.<event_handler>
        """save .prf"""
        self.do_modified(False)
        get_filter_facade().save()
        event.Skip()
        
    def on_close(self, event=None): # wxGlade: FilterFrame.<event_handler>
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
                self.on_save(event)
        # save size
        new_size = self.GetSize()
        set_prefs("filter_width", new_size.GetWidth())
        set_prefs("filter_height", new_size.GetHeight())
        # close dialog
        if self.options["standalone"]:
            self.help_dialog.Destroy()
            self.Destroy()
            self.options['App'].ExitMainLoop()
        else:
            self.Hide()

    def on_help(self, event): # wxGlade: FilterFrame.<event_handler>
        """display dialog about regular expression"""
        wx.Dialog.Show(self.help_dialog)
        event.Skip()
        
    def on_about(self, event): # wxGlade: FilterFrame.<event_handler>
        """display about"""
        # not modal because would freeze the wx thread while twisted
        # one goes on and initialize profile
        about_dlg = AboutDialog(get_prefs("disclaimer"), self, -1)
        about_dlg.Show()
        event.Skip()

    def on_select_filter(self, event): # wxGlade: FilterFrame.<event_handler>
        filter_names = get_selected_labels(self.filter_list)
        if filter_names:
            selected_filter = get_filter_facade().get_filter(filter_names[0])
            if isinstance(selected_filter, PeerFilter):
                # update edit panel
                self.set_profile_view()
                self.edit_profile_panel.update(selected_filter)
                self.view_profile_panel.update(filter_names[0])
            elif isinstance(selected_filter, FileFilter):
                # update edit panel
                self.set_file_view()
                self.edit_file_panel.update(selected_filter)
                self.view_file_panel.update(filter_names[0])
            else:
                print "unrecognised filter", selected_filter.__class__.__name__
            # get ids to display in notebook
            peer_ids = []
            for filter_name in filter_names:
                try:
                    for result_id, mathes in get_filter_facade().get_results(filter_name).items():
                        if result_id not in peer_ids and len(mathes) > 0:
                            peer_ids.append(result_id)
                except KeyError:
                    pass
            # update notebook
            for peer_id in peer_ids:
                self.set_tab(peer_id)
            for peer_id in self.tabs:
                if not peer_id in peer_ids:
                    self.hide_tab(peer_id)
        event.Skip()

    def on_refresh_filter(self, event):
        filter_names = get_selected_labels(self.filter_list)
        for peer in get_facade().get_peers().values():
            get_filter_facade().match(peer, filter_names)
        self.on_select_filter(event)
        event.Skip()

    def on_right_click_filter(self, event): # wxGlade: FilterFrame.<event_handler>
        self.PopupMenu(self.popup_menu)
        event.Skip()

    def on_right_click_col_filter(self, event): # wxGlade: FilterFrame.<event_handler>
        self.PopupMenu(self.popup_col_menu)
        event.Skip()

    def on_import(self, event):
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
            get_filter_facade().match(PeerDescriptor(loader.get_pseudo(),
                                                     document = loader))
        event.Skip()

    def on_delete(self, event): # wxGlade: FilterFrame.<event_handler>
        filter_names = get_selected_labels(self.filter_list)
        get_filter_facade().delete_filters(filter_names)
        self.do_modified(True)

    def on_change_tab(self, event): # wxGlade: FilterFrame.<event_handler>
        if 0 == self.edit_notebook.GetSelection():
            self.set_file_view()
        else:
            self.set_profile_view()
        event.Skip()

    # layout #########################################################
    def set_file_view(self):
        if self.current_edit == self.edit_file_panel:
            return
        self.current_edit = self.edit_file_panel
        self.edit_notebook.SetSelection(0)
        # view
        view_sizer = self.view_pane.GetSizer()
        view_sizer.Detach(self.current_view)
        view_sizer.Add(self.view_file_panel, 1, wx.EXPAND, 0)
        self.current_view = self.view_file_panel
        self.view_file_panel.Show()
        self.view_profile_panel.Hide()
        view_sizer.Layout()

    def set_profile_view(self):
        if self.current_edit == self.edit_profile_panel:
            return
        self.current_edit = self.edit_profile_panel
        self.edit_notebook.SetSelection(1)
        # view
        view_sizer = self.view_pane.GetSizer()
        view_sizer.Detach(self.current_view)
        view_sizer.Add(self.view_profile_panel, 1, wx.EXPAND, 0)
        self.current_view = self.view_profile_panel
        self.view_profile_panel.Show()
        self.view_file_panel.Hide()
        view_sizer.Layout()
    
    def __set_properties(self):
        # begin wxGlade: FilterFrame.__set_properties
        self.SetTitle(_("Profile Filters"))
        self.SetSize((709, 632))
        self.statusbar.SetStatusWidths([-1])
        # statusbar fields
        statusbar_fields = [_("status")]
        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)
        # end wxGlade

        # properties not generated by wxglade
        width = get_prefs("filter_width")
        height = get_prefs("filter_height")
        self.SetSize((width, height))
        self.do_modified(False)
        self.activate_item.Check()

    def __do_layout(self):
        # begin wxGlade: FilterFrame.__do_layout
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        view_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.StaticBoxSizer(self.sizer_4_staticbox, wx.VERTICAL)
        edit_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(self.edit_file_panel, 1, wx.EXPAND, 0)
        self.notebook_1_pane_1.SetAutoLayout(True)
        self.notebook_1_pane_1.SetSizer(sizer_3)
        sizer_3.Fit(self.notebook_1_pane_1)
        sizer_3.SetSizeHints(self.notebook_1_pane_1)
        sizer_5.Add(self.edit_profile_panel, 1, wx.EXPAND, 0)
        self.notebook_1_pane_2.SetAutoLayout(True)
        self.notebook_1_pane_2.SetSizer(sizer_5)
        sizer_5.Fit(self.notebook_1_pane_2)
        sizer_5.SetSizeHints(self.notebook_1_pane_2)
        self.edit_notebook.AddPage(self.notebook_1_pane_1, _("File"))
        self.edit_notebook.AddPage(self.notebook_1_pane_2, _("Peer"))
        edit_sizer.Add(self.edit_notebook, 1, wx.EXPAND, 0)
        self.edit_pane.SetAutoLayout(True)
        self.edit_pane.SetSizer(edit_sizer)
        edit_sizer.Fit(self.edit_pane)
        edit_sizer.SetSizeHints(self.edit_pane)
        sizer_4.Add(self.filter_list, 1, wx.EXPAND, 0)
        self.window_4_pane_1.SetAutoLayout(True)
        self.window_4_pane_1.SetSizer(sizer_4)
        sizer_4.Fit(self.window_4_pane_1)
        sizer_4.SetSizeHints(self.window_4_pane_1)
        view_sizer.Add(self.view_file_panel, 1, wx.EXPAND, 0)
        self.view_pane.SetAutoLayout(True)
        self.view_pane.SetSizer(view_sizer)
        view_sizer.Fit(self.view_pane)
        view_sizer.SetSizeHints(self.view_pane)
        self.window_4.SplitVertically(self.window_4_pane_1, self.view_pane)
        sizer_2.Add(self.window_4, 1, wx.EXPAND, 0)
        self.window_3_pane_1.SetAutoLayout(True)
        self.window_3_pane_1.SetSizer(sizer_2)
        sizer_2.Fit(self.window_3_pane_1)
        sizer_2.SetSizeHints(self.window_3_pane_1)
        sizer_6.Add(self.preview_notebook, 1, wx.EXPAND, 0)
        self.window_3_pane_2.SetAutoLayout(True)
        self.window_3_pane_2.SetSizer(sizer_6)
        sizer_6.Fit(self.window_3_pane_2)
        sizer_6.SetSizeHints(self.window_3_pane_2)
        self.window_3.SplitHorizontally(self.window_3_pane_1, self.window_3_pane_2)
        sizer_1.Add(self.window_3, 1, wx.EXPAND, 0)
        self.window_2_pane_2.SetAutoLayout(True)
        self.window_2_pane_2.SetSizer(sizer_1)
        sizer_1.Fit(self.window_2_pane_2)
        sizer_1.SetSizeHints(self.window_2_pane_2)
        self.window_2.SplitVertically(self.edit_pane, self.window_2_pane_2, 100)
        frame_sizer.Add(self.window_2, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(frame_sizer)
        self.Layout()
        self.Centre()
        # end wxGlade

# end of class FilterFrame


