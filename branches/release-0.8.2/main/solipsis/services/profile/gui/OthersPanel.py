# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Tue Mar 22 11:28:12 2005

import wx, wx.html
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.document import PeerDescriptor
from solipsis.services.profile.view import HtmlView

# begin wxGlade: dependencies
# end wxGlade

class OthersPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: OthersPanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.other_split = wx.SplitterWindow(self, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.details_panel = wx.Panel(self.other_split, -1)
        self.peers_panel = wx.Panel(self.other_split, -1)
        self.peers_list = wx.TreeCtrl(self.peers_panel, -1, style=wx.TR_HAS_BUTTONS|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.detail_preview = wx.html.HtmlWindow(self.details_panel, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        root = self.peers_list.AddRoot(_("Peers"))
        self.friends = self.peers_list.AppendItem(root, _("Friends"))
        self.anonymous = self.peers_list.AppendItem(root, _("Anonymous"))
        self.blacklisted = self.peers_list.AppendItem(root, _("Blacklisted"))
        
        self.facade = get_facade()
        self.peers = None
        self.bind_controls()

    def get_peer_selected(self):
        """returns selected pseudo"""
        return self.peers_list.GetItemText(self.peers_list.GetSelection())

    def refresh_view(self, active_doc):
        """refresh html view of peer"""
        if active_doc:
            view = HtmlView(active_doc)
            self.detail_preview.SetPage(view.get_view(True))
        else:
            self.detail_preview.SetPage("<font color='blue'>%s</font>"\
                                        % _("no neighbors yet"))
    
    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.peers_list.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selected)

    def cb_update_peers(self, peers):
        """called when peers have been modified"""
        self.peers = peers
        # retreive pseudos
        friends = [peer[0].pseudo for peer in peers.values()
                   if peer[0].state == PeerDescriptor.FRIEND]
        anonymous = [peer[0].pseudo for peer in peers.values()
                     if peer[0].state == PeerDescriptor.ANONYMOUS]
        blacklisted = [peer[0].pseudo for peer in peers.values()
                       if peer[0].state == PeerDescriptor.BLACKLISTED]
        # sort
        friends.sort()
        anonymous.sort()
        blacklisted.sort()
        # display
        self.peers_list.DeleteChildren(self.friends)
        self.peers_list.DeleteChildren(self.anonymous)
        self.peers_list.DeleteChildren(self.blacklisted)
        for pseudo in friends:
            self.peers_list.AppendItem(self.friends, pseudo)
        for pseudo in anonymous:
            self.peers_list.AppendItem(self.anonymous, pseudo)
        for pseudo in blacklisted:
            self.peers_list.AppendItem(self.blacklisted, pseudo)
        # get peer to display
        to_display = self.get_peer_selected()
        if peers.has_key(to_display):
            active_doc = peers[to_display][1]
        else:
            all = friends + anonymous
            if all:
                to_display = all[0]
                active_doc = peers[to_display][1]
            else:
                active_doc = None
        # refresh HTMLView
        self.refresh_view(active_doc)
        
    def on_selected(self, evt):
        """peer selected"""
        pseudo = self.get_peer_selected()
        if self.peers.has_key(pseudo):
            active_doc = self.peers[pseudo][1]
            self.refresh_view(active_doc)

    def __set_properties(self):
        # begin wxGlade: OthersPanel.__set_properties
        pass
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: OthersPanel.__do_layout
        other_size = wx.BoxSizer(wx.HORIZONTAL)
        details_sizer = wx.BoxSizer(wx.HORIZONTAL)
        peers_sizer = wx.BoxSizer(wx.HORIZONTAL)
        peers_sizer.Add(self.peers_list, 1, wx.EXPAND, 0)
        self.peers_panel.SetAutoLayout(True)
        self.peers_panel.SetSizer(peers_sizer)
        peers_sizer.Fit(self.peers_panel)
        peers_sizer.SetSizeHints(self.peers_panel)
        details_sizer.Add(self.detail_preview, 1, wx.EXPAND, 0)
        self.details_panel.SetAutoLayout(True)
        self.details_panel.SetSizer(details_sizer)
        details_sizer.Fit(self.details_panel)
        details_sizer.SetSizeHints(self.details_panel)
        self.other_split.SplitVertically(self.peers_panel, self.details_panel, 150)
        other_size.Add(self.other_split, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(other_size)
        other_size.Fit(self)
        other_size.SetSizeHints(self)
        # end wxGlade

# end of class OthersPanel


