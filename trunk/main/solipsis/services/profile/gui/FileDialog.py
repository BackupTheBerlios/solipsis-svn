# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Fri May 27 10:37:01 2005

import wx
import sys
import os.path
from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxyReceiver
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile import DOWNLOAD

# begin wxGlade: dependencies
# end wxGlade

class FileDialog(wx.Dialog, UIProxyReceiver):
    def __init__(self, parent, id, plugin=None, **kwds):
        UIProxyReceiver.__init__(self)
        args = (parent, id)
        # begin wxGlade: FileDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.fileaction_sizer_staticbox = wx.StaticBox(self, -1, _("Actions"))
        self.download_button = wx.BitmapButton(self, -1, wx.Bitmap(DOWNLOAD,wx.BITMAP_TYPE_ANY))
        self.peerfiles_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.peerfiles_list.InsertColumn(0, "File")
        self.peerfiles_list.InsertColumn(1, "Tag")
        self.data = {}
        self.plugin = plugin
        self.peer_id = None
        self.facade = get_facade()
        self.bind_controls()

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.download_button.Bind(wx.EVT_BUTTON, self.on_download)

    def on_download(self, evt):
        """dowload selected files"""
        assert self.peer_id != None, "no peer linked to sharelist"
        selections = []
        selected = -1
        # get selected path
        for index in range(self.peerfiles_list.GetSelectedItemCount()):
            selected = self.peerfiles_list.GetNextItem(selected, state=wx.LIST_STATE_SELECTED)
            selections.append(self.data[selected])
        # send network command
        self.plugin.get_files(self.peer_id, selections)

    def Show(self, files, do_show=True):
        """overrides Show, files is {repos: {names:tags}, }"""
        self.peerfiles_list.DeleteAllItems()
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
                self.data[index] = path
        # show result
        self.peerfiles_list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.peerfiles_list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        wx.Dialog.Show(self, do_show)

    def SetTitle(self, title):
        self.peer_id = title
        wx.Dialog.SetTitle(self, "%s's %s"% (title, _("Blog")))

    def __set_properties(self):
        # begin wxGlade: FileDialog.__set_properties
        self.SetTitle(_("Chose Files"))
        self.SetSize((460, 410))
        self.download_button.SetToolTipString(_("Download selected files"))
        self.download_button.SetSize(self.download_button.GetBestSize())
        # end wxGlade

        self.download_button.Enable(False)

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


