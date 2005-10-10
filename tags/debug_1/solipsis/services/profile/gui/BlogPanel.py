# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Wed May 18 17:54:16 2005

import wx
import sys
from solipsis.util.wxutils import _
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.message import display_error, display_warning
from solipsis.services.profile import ADD_BLOG, DEL_BLOG, ADD_COMMENT


# begin wxGlade: dependencies
# end wxGlade

class MyHtmlListBox(wx.HtmlListBox):

    def __init__(self, parent, id):
        wx.HtmlListBox.__init__(self, parent, id)
        self.SetItemCount(0)

    def on_change_facade(self):
        """setter"""
        pass
        
    def add_blog(self, text):
        """store blog in cache as wx.HtmlListBox is virtual"""
        assert get_facade(), "Facade not initialiazed"
        get_facade().add_blog(text)

    def remove_blog(self):
        assert get_facade(), "Facade not initialiazed"
        selected = self.GetSelection()
        if selected != wx.NOT_FOUND:
            get_facade().remove_blog(selected)
        else:
            display_warning(_("none selected"))
        
    def add_comment(self, text):
        """store blog in cache as wx.HtmlListBox is virtual"""
        assert get_facade(), "Facade not initialiazed"
        selected = self.GetSelection()
        if selected != wx.NOT_FOUND:
            get_facade().add_comment(selected, text, get_facade()._desc.document.get_pseudo())
        else:
            display_warning(_("none selected"))

    def OnGetItem(self, n):
        """callback to display item"""
        assert get_facade(), "Facade not initialiazed"
        try:
            return get_facade()._desc.blog.get_blog(n).html()
        except IndexError, err:
            display_error(_('Could not get blog.'), error=err)
            return "<p>Corrupted Blog</p>"

    def refresh(self):
        assert get_facade(), "Facade not initialiazed"
        self.SetItemCount(get_facade()._desc.blog.count_blogs())
        self.RefreshAll()

class BlogPanel(wx.Panel):
    def __init__(self, parent, id, 
                 cb_modified=lambda x: sys.stdout.write(str(x))):
        # set members
        self.do_modified = cb_modified
        args = (parent, id)
        kwds = {}
        # begin wxGlade: BlogPanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.blog_actions_sizer_staticbox = wx.StaticBox(self, -1, _("Actions"))
        self.add_blog_button = wx.BitmapButton(self, -1, wx.Bitmap(ADD_BLOG(),wx.BITMAP_TYPE_ANY))
        self.del_blog_button = wx.BitmapButton(self, -1, wx.Bitmap(DEL_BLOG(),wx.BITMAP_TYPE_ANY))
        self.comment_blog_button = wx.BitmapButton(self, -1, wx.Bitmap(ADD_COMMENT(),wx.BITMAP_TYPE_ANY))
        self.blog_text = wx.TextCtrl(self, -1, _("Enter your text here"), style=wx.TE_MULTILINE|wx.TE_RICH2|wx.TE_LINEWRAP|wx.TE_WORDWRAP)
        self.blog_list = MyHtmlListBox(self, -1)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        self.bind_controls()

    # EVENTS
    def bind_controls(self):
        """bind all controls with facade"""
        self.add_blog_button.Bind(wx.EVT_BUTTON, self.add_blog)
        self.del_blog_button.Bind(wx.EVT_BUTTON, self.remove_blog)
        self.comment_blog_button.Bind(wx.EVT_BUTTON, self.add_comment)
        
    def add_blog(self, evt):
        self.blog_list.add_blog(self.blog_text.GetValue())
        self.do_modified(True)

    def remove_blog(self, evt):
        self.blog_list.remove_blog()
        self.do_modified(True)
        
    def add_comment(self, evt):
        self.blog_list.add_comment(self.blog_text.GetValue())
        self.do_modified(True)

    def on_update(self):
        self.blog_list.refresh()

    def on_change_facade(self):
        """setter"""
        self.blog_list.on_change_facade()
        
    def __set_properties(self):
        # begin wxGlade: BlogPanel.__set_properties
        self.add_blog_button.SetToolTipString(_("New blog"))
        self.add_blog_button.SetSize(self.add_blog_button.GetBestSize())
        self.del_blog_button.SetToolTipString(_("Delete blog"))
        self.del_blog_button.SetSize(self.del_blog_button.GetBestSize())
        self.comment_blog_button.SetToolTipString(_("Comment"))
        self.comment_blog_button.SetSize(self.comment_blog_button.GetBestSize())
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: BlogPanel.__do_layout
        blog_sizer = wx.BoxSizer(wx.VERTICAL)
        blog_actions_sizer = wx.StaticBoxSizer(self.blog_actions_sizer_staticbox, wx.HORIZONTAL)
        blog_actions_sizer.Add(self.add_blog_button, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        blog_actions_sizer.Add(self.del_blog_button, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        blog_actions_sizer.Add(self.comment_blog_button, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        blog_sizer.Add(blog_actions_sizer, 0, wx.ALL|wx.EXPAND, 3)
        blog_sizer.Add(self.blog_text, 1, wx.BOTTOM|wx.EXPAND|wx.FIXED_MINSIZE, 5)
        blog_sizer.Add(self.blog_list, 4, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(blog_sizer)
        blog_sizer.Fit(self)
        blog_sizer.SetSizeHints(self)
        # end wxGlade

# end of class BlogPanel