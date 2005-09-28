# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Thu Jul  7 18:38:50 2005

import wx
import sys

from solipsis.util.wxutils import _
from solipsis.services.profile.gui.PreviewPanel import MyHtmlWindow
from solipsis.services.profile.view import HtmlView

# begin wxGlade: dependencies
# end wxGlade

class MatchPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MatchPanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.window_1 = wx.SplitterWindow(self, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.previews_pane = wx.Panel(self.window_1, -1)
        self.list_pane = wx.Panel(self.window_1, -1)
        self.list_sizer_staticbox = wx.StaticBox(self.list_pane, -1, _("Matches"))
        self.matches_list = wx.ListCtrl(self.list_pane, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.preview_notebook = wx.Notebook(self.previews_pane, -1, style=0)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        # {peer_id: tab}
        self.tabs = {}
        self.matches = {}

        self.PopulateList()
        self.bind_controls()

    def PopulateList(self):
        self.matches_list.InsertColumn(0, _("Name"))
        self.matches_list.InsertColumn(1, _("Filter"))
        self.matches_list.InsertColumn(2, _("Matches"))
        self.matches_list.SetColumnWidth(0, 100)
        self.matches_list.SetColumnWidth(1, 100)
        self.matches_list.SetColumnWidth(2, 200)

    def set_matches(self, peer_match):
        """add or update list with match of given peer"""
        node_id = peer_match.get_id()
        # attributes
        for a_filter in [peer_match.title,
                         peer_match.firstname,
                         peer_match.lastname,
                         peer_match.photo,
                         peer_match.email]:
            if a_filter:
                self._set_list(node_id, a_filter)
        # customs & files
        for c_filter in peer_match.customs.values():
            self._set_list(node_id, c_filter)
        for f_filters in peer_match.files.values():
            for f_filter in f_filters:
                self._set_list(node_id, f_filter)
            
    def _set_list(self, node_id, filter_result):
        """add or update list with match of given peer"""
        if not filter_result.get_name() in self.matches:
            self._add_list(node_id, filter_result)
        else:
            self._update_list(node_id, filter_result)

    def _add_list(self, node_id, filter_result):
        index = self.matches_list.InsertStringItem(sys.maxint, filter_result.get_name())
        self.matches[filter_result.get_name()] = (index, [node_id])
        self.matches_list.SetStringItem(index, 1, filter_result.get_description())
        self.matches_list.SetStringItem(index, 2, filter_result.get_match())

    def _update_list(self, node_id, filter_result):
        index, node_ids = self.matches[filter_result.get_name()]
        node_ids.append(node_id)
        previous = self.matches_list.GetItem(index, 2).GetText().split(',')
        if not filter_result.get_match() in previous:
            self.matches_list.SetStringItem(index, 2, ', '.join(previous, + [filter_result.get_match()]))
    
    def set_tab(self, peer_desc):
        """add or update tab with preview of given peer"""
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
        preview_tab.preview = match_preview
        preview_tab.SetAutoLayout(True)
        preview_tab.SetSizer(tab_sizer)
        tab_sizer.Fit(preview_tab)
        tab_sizer.SetSizeHints(preview_tab)
        self.preview_notebook.AddPage(preview_tab, peer_desc.document.get_pseudo())
        self.tabs[peer_desc.node_id] = preview_tab
        self._update_tab(peer_desc)

    def _update_tab(self, peer_desc):
        """update tab with preview of given peer"""
        view = HtmlView(peer_desc)
        preview = self.tabs[peer_desc.node_id].preview
        preview.SetPage(view.get_view())
        self.tabs[peer_desc.node_id].Show(True)

    def hide_tab(self, peer_id):
        """hide tab"""
        if peer_id in self.tabs:
            self.tabs[peer_id].Hide()

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.matches_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_list)
        self.matches_list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect_list)

    def on_deselect_list(self, evt):
        """new match selected"""
        if self.matches_list.GetSelectedItemCount() == 0:
            for peer_id in self.tabs:
                self.tabs[peer_id].Show()

    def on_select_list(self, evt):
        """new match selected"""
        for peer_id in self.tabs:
            self.tabs[peer_id].Show()
        match_item = self.matches_list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        match_name = self.matches_list.GetItemText(match_item)
        index, peer_ids = self.matches[match_name]
        for peer_id in self.tabs:
            if not peer_id in peer_ids:
                self.tabs[peer_id].Hide()
        
    def __set_properties(self):
        # begin wxGlade: MatchPanel.__set_properties
        pass
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MatchPanel.__do_layout
        match_sizer = wx.BoxSizer(wx.VERTICAL)
        preview_sizer = wx.BoxSizer(wx.VERTICAL)
        list_sizer = wx.StaticBoxSizer(self.list_sizer_staticbox, wx.VERTICAL)
        list_sizer.Add(self.matches_list, 1, wx.EXPAND, 0)
        self.list_pane.SetAutoLayout(True)
        self.list_pane.SetSizer(list_sizer)
        list_sizer.Fit(self.list_pane)
        list_sizer.SetSizeHints(self.list_pane)
        preview_sizer.Add(self.preview_notebook, 1, wx.EXPAND, 0)
        self.previews_pane.SetAutoLayout(True)
        self.previews_pane.SetSizer(preview_sizer)
        preview_sizer.Fit(self.previews_pane)
        preview_sizer.SetSizeHints(self.previews_pane)
        self.window_1.SplitHorizontally(self.list_pane, self.previews_pane, 20)
        match_sizer.Add(self.window_1, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(match_sizer)
        match_sizer.Fit(self)
        match_sizer.SetSizeHints(self)
        # end wxGlade

# end of class MatchPanel


