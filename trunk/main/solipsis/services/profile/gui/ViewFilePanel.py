# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4 on Tue Oct 25 10:04:51 2005

import sys
import wx
import wx.gizmos as gizmos
from solipsis.util.wxutils import _
from solipsis.services.profile.filter_facade import get_filter_facade

# begin wxGlade: dependencies
# end wxGlade

class ViewFilePanel(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: ViewFilePanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.sizer_9_staticbox = wx.StaticBox(self, -1, _("Matching files"))
        self.matching_list = gizmos.TreeListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        isz = (16,16)
        self.il = wx.ImageList(isz[0], isz[1])
        self.fldridx     = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.fldropenidx = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        self.fileidx     = self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        self.matching_list.SetImageList(self.il)
        
        # matching list
        self.matching_list.AddColumn("peer")
        self.matching_list.AddColumn("value matched")
        self.matching_list.SetMainColumn(0)
        self.matching_list.SetColumnWidth(0, 150)
        self.matching_list.SetColumnWidth(1, 250)
        self.root = self.matching_list.AddRoot("Matching peers")
        self.matching_list.SetItemImage(self.root, self.fldridx, which = wx.TreeItemIcon_Normal)
        self.matching_list.SetItemImage(self.root, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
        self.items = {}

    def reset(self):
        self.matching_list.DeleteChildren(self.root)
        self.items.clear()
        
    def update(self, filter_name):
        self.reset()
        try:
            results = get_filter_facade().get_results(filter_name)
            for peer_id, matches in results.items():
                # add peer if matches
                if matches:
                    if not peer_id in self.items:
                        child = self.matching_list.AppendItem(self.root, peer_id)
                        self.matching_list.SetItemImage(child, self.fldridx, which = wx.TreeItemIcon_Normal)
                        self.matching_list.SetItemImage(child, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
                        self.items[peer_id] = child
                    else:
                        child = self.items[peer_id]
                # add matches
                for matche in matches:
                    match_item = self.matching_list.AppendItem(
                        child, matche.get_name())
                    self.matching_list.SetItemImage(match_item, self.fileidx, which = wx.TreeItemIcon_Normal)
                    self.matching_list.SetItemText(match_item, matche.match, 1)
            self.matching_list.Expand(self.root)
        except KeyError:
            print "no match for", filter_name

    def __set_properties(self):
        # begin wxGlade: ViewFilePanel.__set_properties
        pass
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ViewFilePanel.__do_layout
        sizer_9 = wx.StaticBoxSizer(self.sizer_9_staticbox, wx.VERTICAL)
        sizer_9.Add(self.matching_list, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_9)
        sizer_9.Fit(self)
        sizer_9.SetSizeHints(self)
        # end wxGlade

# end of class ViewFilePanel


