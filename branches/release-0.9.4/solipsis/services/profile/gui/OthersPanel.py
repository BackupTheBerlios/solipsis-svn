# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Tue Mar 22 11:28:12 2005

import wx, wx.html
import os, os.path
from solipsis.util.wxutils import _
from solipsis.services.profile import PROFILE_EXT, \
     BULB_ON_IMG, BULB_OFF_IMG
from solipsis.services.profile.prefs import get_prefs
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.document import PeerDescriptor
from solipsis.services.profile.view import HtmlView
from solipsis.services.profile.data import PeerDescriptor

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
        self.peers_list = wx.TreeCtrl(self.peers_panel, -1, style=wx.TR_HAS_BUTTONS|wx.TR_NO_LINES|wx.TR_LINES_AT_ROOT|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.detail_preview = wx.html.HtmlWindow(self.details_panel, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        root = self.peers_list.AddRoot(_("Peers"))
        self.friends = self.peers_list.AppendItem(root, _("Friends"))
        self.anonymous = self.peers_list.AppendItem(root, _("Anonymous"))
        self.blacklisted = self.peers_list.AppendItem(root, _("Blacklisted"))

        self.frame = self
        # FIXME dirty but isinstance on ProfileFrame not working...
        while self.frame and (not hasattr(self.frame, 'enable_peer_states')):
            self.frame = self.frame.GetParent()
        self.facade = get_facade()
        self.peers = None
        
        il = wx.ImageList(16, 16)
        self.on_img = il.Add(wx.Bitmap(BULB_ON_IMG(),wx.BITMAP_TYPE_ANY))
        self.off_img = il.Add(wx.Bitmap(BULB_OFF_IMG(),wx.BITMAP_TYPE_ANY))
        self.peers_list.SetImageList(il)
        self.il = il
        
        self.bind_controls()

    def get_peer_selected(self):
        """returns selected peer_id"""
        try:
            peer_id = self.peers_list.GetItemText(self.peers_list.GetSelection())
            if self.peers.has_key(peer_id):
                return peer_id
            elif self.pseudos.has_key(peer_id):
                return self.pseudos[peer_id].peer_id
            else:
                return None
        except:
            return None

    def refresh_view(self, peer_id):
        """refresh html view of peer"""
        # get descriptor
        if self.facade.has_peer(peer_id):
            peer_desc = self.facade.get_peer(peer_id)
        else:
            peer_desc = PeerDescriptor(peer_id)
        # get document
        full_path = os.sep.join([get_prefs("profile_dir"), peer_id, PROFILE_EXT])
        if not peer_desc.document and os.path.exists(full_path):
            doc = FileDocument()
            doc.load(full_path)
            peer_desc.set_document(doc)
        # display
        if peer_desc.document:
            view = HtmlView(peer_desc.document)
            self.detail_preview.SetPage(view.get_view(True))
            self.frame.enable_peer_states(True, peer_desc.state)
        else:
            self.detail_preview.SetPage("<font color='blue'>%s</font>"\
                                        % _("select neighbor to display"))
            self.frame.enable_peer_states(False)
    
    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.peers_list.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selected)

    def cb_update_peers(self, peers):
        """called when peers have been modified"""
        self.peers = peers
        self.pseudos = {}
        self.items = {}
        friends = []
        anonymous = []
        blacklisted = []
        # get pseudos and sort them out
        for peer_id, peer_desc in self.peers.iteritems():
            # get 'pseudo'
            pseudo = peer_desc.get_pseudo()
            # create lists
            index = 1
            while self.pseudos.has_key(pseudo):
                index += 1
                pseudo = "%s_%02d"% (pseudo, index)
            self.pseudos[pseudo] = peer_desc
            if peer_desc.state == PeerDescriptor.FRIEND:
                friends.append(pseudo)
            elif peer_desc.state == PeerDescriptor.BLACKLISTED:
                blacklisted.append(pseudo)
            else: # peer.state == PeerDescriptor.ANONYMOUS
                anonymous.append(pseudo)
        # sort
        friends.sort()
        anonymous.sort()
        blacklisted.sort()
        # display
        self.peers_list.DeleteChildren(self.friends)
        self.peers_list.DeleteChildren(self.anonymous)
        self.peers_list.DeleteChildren(self.blacklisted)
        for pseudo in friends:
            self._append(self.friends, pseudo)
        for pseudo in anonymous:
            self._append(self.anonymous, pseudo)
        for pseudo in blacklisted:
            self._append(self.blacklisted, pseudo)
        # get peer to display
        to_display = self.get_peer_selected()
        # refresh HTMLView
        if to_display:
            self.refresh_view(to_display)

    def _append(self, list, pseudo):
        """use to append item in tree"""
        item = self.peers_list.AppendItem(list, pseudo)
        self.items[pseudo] = item
        self.peers_list.SetItemImage(item,
            self.pseudos[pseudo].connected and self.on_img or self.off_img,
            wx.TreeItemIcon_Normal)
        self.peers_list.SetItemImage(item,
            self.pseudos[pseudo].connected and self.on_img or self.off_img,
            wx.TreeItemIcon_Expanded)
        
    def on_selected(self, evt):
        """peer selected"""
        peer_id = self.get_peer_selected()
        if peer_id:
            self.refresh_view(peer_id)

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
        self.other_split.SplitVertically(self.peers_panel, self.details_panel, 200)
        other_size.Add(self.other_split, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(other_size)
        other_size.Fit(self)
        other_size.SetSizeHints(self)
        # end wxGlade

# end of class OthersPanel
