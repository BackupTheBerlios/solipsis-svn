# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Fri May 27 17:40:42 2005

import wx
from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxyReceiver

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
                self.blog.add_comment((selected, text))
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
        self.sizer_6_staticbox = wx.StaticBox(self, -1, _("Actions"))
        self.bitmap_button_2 = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/edit_file.gif", wx.BITMAP_TYPE_ANY))
        self.bitmap_button_3 = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/delete_file.gif", wx.BITMAP_TYPE_ANY))
        self.bitmap_button_4 = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/add_file.gif", wx.BITMAP_TYPE_ANY))
        self.window_2 = PeerHtmlListBox(self, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        # specific stuff
        self.bind_controls()

    def Show(self, blog, do_show=True):
        """overrides Show"""
        self.window_2.blog = blog
        wx.Dialog.Show(self, do_show)
        self.window_2.refresh()
        
    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        pass
        
    def add_blog(self, evt):
        pass

    def remove_blog(self, evt):
        pass
        
    def upload_change(self, evt):
        pass

    def __set_properties(self):
        # begin wxGlade: BlogDialog.__set_properties
        self.SetTitle(_("Peer's Blog"))
        self.SetSize((460, 410))
        self.bitmap_button_2.SetSize(self.bitmap_button_2.GetBestSize())
        self.bitmap_button_3.SetSize(self.bitmap_button_3.GetBestSize())
        self.bitmap_button_4.SetSize(self.bitmap_button_4.GetBestSize())
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: BlogDialog.__do_layout
        sizer_5 = wx.BoxSizer(wx.VERTICAL)
        sizer_6 = wx.StaticBoxSizer(self.sizer_6_staticbox, wx.HORIZONTAL)
        sizer_6.Add(self.bitmap_button_2, 0, wx.FIXED_MINSIZE, 0)
        sizer_6.Add(self.bitmap_button_3, 0, wx.FIXED_MINSIZE, 0)
        sizer_6.Add(self.bitmap_button_4, 0, wx.FIXED_MINSIZE, 0)
        sizer_5.Add(sizer_6, 0, 0, 0)
        sizer_5.Add(self.window_2, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_5)
        self.Layout()
        # end wxGlade

# end of class BlogDialog


