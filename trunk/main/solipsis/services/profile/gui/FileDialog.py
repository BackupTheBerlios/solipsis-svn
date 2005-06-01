# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Fri May 27 10:37:01 2005

import wx
import sys
import os.path
from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxyReceiver
from solipsis.services.profile.facade import get_facade

# begin wxGlade: dependencies
# end wxGlade

class FileDialog(wx.Dialog, UIProxyReceiver):
    def __init__(self, *args, **kwds):
        UIProxyReceiver.__init__(self)
        # begin wxGlade: FileDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.fileaction_sizer_staticbox = wx.StaticBox(self, -1, _("Actions"))
        self.download_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/down_file.gif", wx.BITMAP_TYPE_ANY))
        self.peerfiles_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.peerfiles_list.InsertColumn(0, "File")
        self.peerfiles_list.InsertColumn(1, "Tag")
        self.data = {}

    def Show(self, files, do_show=True):
        """overrides Show, files is {repos: {names:tags}, }"""
#        self.peerfiles_list.ClearAll()
        if len(files) > 0:
            # reformat data
            file_data = []
            for repo, file_desc in files.iteritems():
                for name, tag  in file_desc.iteritems():
                    file_data.append([os.path.join(repo, name), os.path.basename(name), tag])
            # clear previous data
            for key in self.data.keys():
                del self.data[key]
            # fill list
            for path, name, tag in file_data:
                index = self.peerfiles_list.InsertStringItem(sys.maxint, name)
                self.peerfiles_list.SetStringItem(index, 1, tag)
                self.data[index] = (path, name, tag)
        # show result
        self.peerfiles_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.peerfiles_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        wx.Dialog.Show(self, do_show)

    def __set_properties(self):
        # begin wxGlade: FileDialog.__set_properties
        self.SetTitle(_("Chose Files"))
        self.SetSize((460, 410))
        self.download_button.SetToolTipString(_("Download selected files"))
        self.download_button.SetSize(self.download_button.GetBestSize())
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: FileDialog.__do_layout
        peerfiles_sizer = wx.BoxSizer(wx.VERTICAL)
        fileaction_sizer = wx.StaticBoxSizer(self.fileaction_sizer_staticbox, wx.HORIZONTAL)
        fileaction_sizer.Add(self.download_button, 0, wx.FIXED_MINSIZE, 0)
        peerfiles_sizer.Add(fileaction_sizer, 0, wx.EXPAND, 0)
        peerfiles_sizer.Add(self.peerfiles_list, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(peerfiles_sizer)
        self.Layout()
        # end wxGlade

# end of class FileDialog

