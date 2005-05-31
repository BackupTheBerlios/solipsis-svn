# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Fri May 27 17:40:42 2005

import wx
from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxyReceiver
from solipsis.services.profile.facade import get_facade

# begin wxGlade: dependencies
# end wxGlade

class PeerHtmlListBox(wx.HtmlListBox):

    def __init__(self, parent, id):
        wx.HtmlListBox.__init__(self, parent, id)
        self.blog = None
        self.SetItemCount(0)
        
    def add_blog(self, text):
        """store blog in cache as wx.HtmlListBox is virtual"""
        if self.blog:
            self.blog.add_blog(text)
            self.refresh()
        else:
            print "no blog set"

    def remove_blog(self):
        if self.blog:
            selected = self.GetSelection()
            if selected != wx.NOT_FOUND:
                self.blog.remove_blog(selected)
                self.refresh()
            else:
                print "none selected"
        else:
            print "no blog set"
        
    def add_comment(self, text):
        """store blog in cache as wx.HtmlListBox is virtual"""
        if self.blog:
            selected = self.GetSelection()
            if selected != wx.NOT_FOUND:
                pseudo = get_facade().documents['cache'].get_pseudo()
                self.blog.get_blog(selected).add_comment(text, pseudo)
                self.refresh()
            else:
                print "none selected"
        else:
            print "no blog set"

    def OnGetItem(self, n):
        """callback to display item"""
        return self.blog.get_blog(n).html()

    def refresh(self):
        self.SetItemCount(self.blog.count_blogs())
        self.RefreshAll()

class BlogDialog(wx.Dialog, UIProxyReceiver):
    def __init__(self, *args, **kwds):
        UIProxyReceiver.__init__(self)
        # begin wxGlade: BlogDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.peerblog_actions_staticbox = wx.StaticBox(self, -1, _("Actions"))
        self.add_comment_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/edit_file.gif", wx.BITMAP_TYPE_ANY))
        self.del_comment_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/delete_file.gif", wx.BITMAP_TYPE_ANY))
        self.upload_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/add_file.gif", wx.BITMAP_TYPE_ANY))
        self.peerblog_text = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER|wx.TE_MULTILINE|wx.TE_RICH2|wx.TE_LINEWRAP)
        self.peerblog_list = PeerHtmlListBox(self, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        # specific stuff
        self.bind_controls()

    def Show(self, blog, do_show=True):
        """overrides Show"""
        self.peerblog_list.blog = blog
        wx.Dialog.Show(self, do_show)
        self.peerblog_list.refresh()
        
    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.add_comment_button.Bind(wx.EVT_BUTTON, self.add_comment)
        self.del_comment_button.Bind(wx.EVT_BUTTON, self.remove_comment)
        self.upload_button.Bind(wx.EVT_BUTTON, self.upload_change)
        
    def add_comment(self, evt):
        self.peerblog_list.add_comment(self.peerblog_text.GetValue())

    def remove_comment(self, evt):
        pass
        
    def upload_change(self, evt):
        pass

    def __set_properties(self):
        # begin wxGlade: BlogDialog.__set_properties
        self.SetTitle(_("Peer's Blog"))
        self.SetSize((460, 410))
        self.add_comment_button.SetSize(self.add_comment_button.GetBestSize())
        self.del_comment_button.SetSize(self.del_comment_button.GetBestSize())
        self.upload_button.SetSize(self.upload_button.GetBestSize())
        # end wxGlade
        self.del_comment_button.Enable(False)
        self.upload_button.Enable(False)

    def __do_layout(self):
        # begin wxGlade: BlogDialog.__do_layout
        peerblog_sizer = wx.BoxSizer(wx.VERTICAL)
        peerblog_actions = wx.StaticBoxSizer(self.peerblog_actions_staticbox, wx.HORIZONTAL)
        peerblog_actions.Add(self.add_comment_button, 0, wx.FIXED_MINSIZE, 0)
        peerblog_actions.Add(self.del_comment_button, 0, wx.FIXED_MINSIZE, 0)
        peerblog_actions.Add(self.upload_button, 0, wx.FIXED_MINSIZE, 0)
        peerblog_sizer.Add(peerblog_actions, 0, 0, 0)
        peerblog_sizer.Add(self.peerblog_text, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        peerblog_sizer.Add(self.peerblog_list, 5, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(peerblog_sizer)
        self.Layout()
        # end wxGlade

# end of class BlogDialog


