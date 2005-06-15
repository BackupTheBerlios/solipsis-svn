# -*- coding: UTF-8 -*-
# generated by wxGlade 0.4cvs on Mon Apr 25 16:31:38 2005

import wx

from solipsis.util.utils import set
from solipsis.util.wxutils import _
from solipsis.util.wxutils import GetStockToolbarBitmap as TB

# begin wxGlade: dependencies
# end wxGlade

# ID allocation
_ids = [
    "TOOL_ADD_BOOKMARK",
    "TOOL_DEL_BOOKMARK",
]
for _id in _ids:
    locals()[_id] = wx.NewId()

COL_PSEUDO = 0


class BookmarksDialog(wx.Frame):
    def __init__(self, app, world, config_data, menu, *args, **kwds):
        self.app = app
        self.world = world
        self.config_data = config_data
        self.menu = menu

        # Item index => peer
        self.item_map = {}
        # Peer IDs
        self.selected_items = set()
        # Menu items
        self.menu_items = []

        # begin wxGlade: BookmarksDialog.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.panel_1 = wx.Panel(self, -1)
        
        # Tool Bar
        self.toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL|wx.TB_TEXT|wx.TB_HORZ_LAYOUT|wx.TB_HORZ_TEXT)
        self.SetToolBar(self.toolbar)
        self.toolbar.AddLabelTool(TOOL_ADD_BOOKMARK, _("Add bookmark"), (TB(wx.ART_ADD_BOOKMARK)), wx.NullBitmap, wx.ITEM_NORMAL, _("Bookmark a node"), "")
        self.toolbar.AddLabelTool(TOOL_DEL_BOOKMARK, _("Remove"), (TB(wx.ART_DEL_BOOKMARK)), wx.NullBitmap, wx.ITEM_NORMAL, _("Remove selected bookmark"), "")
        # Tool Bar end
        self.list_ctrl = wx.ListCtrl(self.panel_1, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.button_close = wx.Button(self.panel_1, wx.ID_CLOSE, "")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TOOL, self.OnAddBookmark, id=TOOL_ADD_BOOKMARK)
        self.Bind(wx.EVT_TOOL, self.OnDelBookmark, id=TOOL_DEL_BOOKMARK)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnDeselectItem, self.list_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectItem, self.list_ctrl)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=wx.ID_CLOSE)
        # end wxGlade
        self.Bind(wx.EVT_SHOW, self.OnShow)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.config_data.AskNotify(self.ApplyConfig)
        self.ApplyConfig()

    def __set_properties(self):
        # begin wxGlade: BookmarksDialog.__set_properties
        self.SetTitle(_("Bookmarks"))
        self.SetMinSize((319, 216))
        self.toolbar.Realize()
        self.button_close.SetDefault()
        # end wxGlade

        self.UpdateToolbarState()
        self.list_ctrl.InsertColumn(COL_PSEUDO, _("Pseudo"))

    def __do_layout(self):
        # begin wxGlade: BookmarksDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.list_ctrl, 1, wx.EXPAND, 0)
        sizer_2.Add(self.button_close, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.panel_1.SetAutoLayout(True)
        self.panel_1.SetSizer(sizer_2)
        sizer_2.Fit(self.panel_1)
        sizer_2.SetSizeHints(self.panel_1)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        self.Layout()
        self.Centre()
        # end wxGlade

    #
    # Event handlers
    #
    def OnAddBookmark(self, event): # wxGlade: BookmarksDialog.<event_handler>
        all_peers = self.world.GetAllPeers()
        bookmarked_peers = set([peer.id_ for peer in self.bookmarks.GetAllPeers()])
        peers = [peer for peer in all_peers if peer.id_ not in bookmarked_peers]
        dialog = wx.SingleChoiceDialog(parent=self,
            message=_("Please choose the peer to add to your bookmarks list."),
            caption=_("Add bookmark"),
            choices=[peer.pseudo for peer in peers])
        if dialog.ShowModal() == wx.ID_OK:
            peer = peers[dialog.GetSelection()]
            self.bookmarks.AddPeer(peer)
            self.UpdateUI()

    def OnDelBookmark(self, event): # wxGlade: BookmarksDialog.<event_handler>
        for peer_id in self.selected_items:
            self.bookmarks.RemoveById(peer_id)
        self.selected_items.clear()
        self.UpdateUI()

    def OnSelectItem(self, event): # wxGlade: BookmarksDialog.<event_handler>
        index = event.GetIndex()
        peer_id = self.item_map[index].id_
        self.selected_items.add(peer_id)
        self.UpdateToolbarState()

    def OnDeselectItem(self, event): # wxGlade: BookmarksDialog.<event_handler>
        index = event.GetIndex()
        peer_id = self.item_map[index].id_
        if peer_id in self.selected_items:
            self.selected_items.remove(peer_id)
        self.UpdateToolbarState()

    def OnClose(self, event): # wxGlade: BookmarksDialog.<event_handler>
        self.Hide()
    
    def OnShow(self, event):
        self.selected_items.clear()
        self.UpdateUI()

    def ApplyConfig(self):
        self.bookmarks = self.config_data.bookmarks
        self.UpdateUI()

    #
    # Helper methods
    #
    def UpdateUI(self):
        self.selected_items.clear()
        self.UpdateBookmarks()
        self.UpdateToolbarState()
        self.UpdateMenubar()

    def UpdateMenubar(self):
        for menu_item in self.menu_items:
            self.menu.DeleteItem(menu_item)
        self.menu_items = []
        peers = self.bookmarks.GetAllPeers()
        for peer in peers:
            def _clicked(evt, address=peer.address):
                self.app._JumpNearAddress(address)
            item_id = wx.NewId()
            menu_item = self.menu.Append(item_id, peer.pseudo)
            wx.EVT_MENU(self.app.main_window, item_id, _clicked)
            self.menu_items.append(menu_item)

    def UpdateBookmarks(self):
        peers = self.bookmarks.GetAllPeers()
        self.list_ctrl.DeleteAllItems()
        self.item_map.clear()
        for peer in peers:
            index = self.list_ctrl.GetItemCount()
            self.list_ctrl.InsertStringItem(index, peer.pseudo)
            self.item_map[index] = peer
        self.list_ctrl.SetColumnWidth(COL_PSEUDO, wx.LIST_AUTOSIZE)
    
    def UpdateToolbarState(self):
        self.toolbar.EnableTool(TOOL_DEL_BOOKMARK, len(self.selected_items) > 0)


# end of class BookmarksDialog
