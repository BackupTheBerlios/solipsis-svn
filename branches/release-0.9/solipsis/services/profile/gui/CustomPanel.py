# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Tue Mar 22 11:28:12 2005

import sys
import wx, wx.lib.editor 
import wx.lib.mixins.listctrl  as  listmix
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile import ADD_CUSTOM, DEL_CUSTOM
from solipsis.util.wxutils import _
from wx import ImageFromStream, BitmapFromImage
from StringIO import StringIO

# begin wxGlade: dependencies
# end wxGlade

class CustomPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: CustomPanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.keywords_sizer_staticbox = wx.StaticBox(self, -1, _("Type here interests which do not fall into any precise category. (one per line)"))
        self.action_sizer_staticbox = wx.StaticBox(self, -1, _("Specify here a field of interest. For instance: (favorite book: Harry Potter) or (instrument: piano) "))
        self.key_value = wx.TextCtrl(self, -1, _("favorite book"))
        self.custom_value = wx.TextCtrl(self, -1, _("Harry Potter"))
        self.add_custom_button = wx.BitmapButton(self, -1, wx.Bitmap(ADD_CUSTOM(),wx.BITMAP_TYPE_ANY))
        self.del_custom_button = wx.BitmapButton(self, -1, wx.Bitmap(DEL_CUSTOM(),wx.BITMAP_TYPE_ANY))
        self.custom_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_SORT_ASCENDING|wx.NO_BORDER)
        self.hobbies_value = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_RICH2|wx.TE_LINEWRAP)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        self.il = wx.ImageList(16, 16)
        self.sm_up = self.il.Add(getSmallUpArrowBitmap())
        self.sm_dn = self.il.Add(getSmallDnArrowBitmap())
        self.custom_list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
                
        self.PopulateList()
        
        self.facade = get_facade()
        self.bind_controls()
        self.edited_item = None

    def PopulateList(self):
        self.custom_list.InsertColumn(0, _("MetaData"))
        self.custom_list.InsertColumn(1, _("Custom value"))
        
        self.custom_list.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
        self.custom_list.SetColumnWidth(1, wx.LIST_AUTOSIZE_USEHEADER)
        
        
    # Used by the ColumnSorterMixin, see wxPython/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self.custom_list

    # Used by the ColumnSorterMixin, see wxPython/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)
    
    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.hobbies_value.Bind(wx.EVT_KILL_FOCUS, self.on_hobbies)
        self.custom_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selected)
        self.add_custom_button.Bind(wx.EVT_BUTTON, self.on_add)
        self.del_custom_button.Bind(wx.EVT_BUTTON, self.on_del)

    def on_selected(self, evt):
        """meta data"""
        self.edited_item = (evt.GetIndex(), evt.GetItem().GetText())
        self.key_value.SetValue(self.edited_item[1])
        self.custom_value.SetValue(self.custom_list.GetItem(evt.GetIndex(), 1).GetText())
        
    def on_add(self, evt):
        """a custom attribute has been modified"""
        if self.edited_item and self.edited_item[1] == self.key_value.GetValue():
            # update data
            self.custom_list.SetStringItem(self.edited_item[0], 0, self.key_value.GetValue())
            self.custom_list.SetStringItem(self.edited_item[0], 1, self.custom_value.GetValue())
        else:
            # new
            index = self.custom_list.InsertStringItem(sys.maxint, self.key_value.GetValue())
            self.custom_list.SetStringItem(index, 1, self.custom_value.GetValue())
        # update cache
        self.facade.add_custom_attributes((self.key_value.GetValue(),
                                           self.custom_value.GetValue()))
        # resize columns
        self.custom_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.custom_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def on_del(self, evt):
        """a custom attribute has been modified"""
        # update data
        if self.custom_list.DeleteItem(self.custom_list.FindItem(0, self.key_value.GetValue())):
            # update cache
            self.facade.del_custom_attributes(self.key_value.GetValue())
        
    def on_hobbies(self, evt):
        """language loses focus"""
        self.facade.change_hobbies(evt.GetEventObject().GetValue().split('\n'))
        evt.Skip()
        
    def on_more(self, evt):
        """firstname loses focus"""
        index = self.custom_list.InsertStringItem(sys.maxint, "New")
        self.custom_list.SetStringItem(index, 1, u"?")
        
    def __set_properties(self):
        # begin wxGlade: CustomPanel.__set_properties
        self.add_custom_button.SetSize(self.add_custom_button.GetBestSize())
        self.del_custom_button.SetSize(self.del_custom_button.GetBestSize())
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: CustomPanel.__do_layout
        custom_sizer = wx.BoxSizer(wx.VERTICAL)
        keywords_sizer = wx.StaticBoxSizer(self.keywords_sizer_staticbox, wx.VERTICAL)
        action_sizer = wx.StaticBoxSizer(self.action_sizer_staticbox, wx.HORIZONTAL)
        action_sizer.Add(self.key_value, 1, wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 3)
        action_sizer.Add(self.custom_value, 1, wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 3)
        action_sizer.Add(self.add_custom_button, 0, wx.LEFT|wx.FIXED_MINSIZE, 3)
        action_sizer.Add(self.del_custom_button, 0, wx.FIXED_MINSIZE, 0)
        custom_sizer.Add(action_sizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_RIGHT, 3)
        custom_sizer.Add(self.custom_list, 2, wx.EXPAND, 0)
        keywords_sizer.Add(self.hobbies_value, 1, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        custom_sizer.Add(keywords_sizer, 1, wx.ALL|wx.EXPAND, 3)
        self.SetAutoLayout(True)
        self.SetSizer(custom_sizer)
        custom_sizer.Fit(self)
        custom_sizer.SetSizeHints(self)
        # end wxGlade

# end of class CustomPanel

#----------------------------------------------------------------------
def getSmallUpArrowData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00<IDATx\x9ccddbf\xa0\x040Q\xa4{h\x18\xf0\xff\xdf\xdf\xffd\x1b\x00\xd3\
\x8c\xcf\x10\x9c\x06\xa0k\xc2e\x08m\xc2\x00\x97m\xd8\xc41\x0c \x14h\xe8\xf2\
\x8c\xa3)q\x10\x18\x00\x00R\xd8#\xec\x95{\xc4\x11\x00\x00\x00\x00IEND\xaeB`\
\x82' 

def getSmallUpArrowBitmap():
    return BitmapFromImage(getSmallUpArrowImage())

def getSmallUpArrowImage():
    stream = StringIO(getSmallUpArrowData())
    return ImageFromStream(stream)

#----------------------------------------------------------------------
def getSmallDnArrowData():
    return \
"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00HIDATx\x9ccddbf\xa0\x040Q\xa4{\xd4\x00\x06\x06\x06\x06\x06\x16t\x81\
\xff\xff\xfe\xfe'\xa4\x89\x91\x89\x99\x11\xa7\x0b\x90%\ti\xc6j\x00>C\xb0\x89\
\xd3.\x10\xd1m\xc3\xe5*\xbc.\x80i\xc2\x17.\x8c\xa3y\x81\x01\x00\xa1\x0e\x04e\
\x1d\xc4;\xb7\x00\x00\x00\x00IEND\xaeB`\x82" 

def getSmallDnArrowBitmap():
    return BitmapFromImage(getSmallDnArrowImage())

def getSmallDnArrowImage():
    stream = StringIO(getSmallDnArrowData())
    return ImageFromStream(stream)


