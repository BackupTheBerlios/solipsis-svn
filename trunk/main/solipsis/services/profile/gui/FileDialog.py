# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Fri May 27 10:37:01 2005

import wx
import sys
import os.path
from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxyReceiver
from solipsis.services.profile import DOWNLOAD, DOWNLOAD_DIR, DOWNLOAD_REPO
from solipsis.services.profile.facade import get_facade

# begin wxGlade: dependencies
# end wxGlade

class FileDialog(wx.Dialog, UIProxyReceiver):
    def __init__(self, parent, id, plugin=None, **kwds):
        UIProxyReceiver.__init__(self)
        self.data = {}
        self.plugin = plugin
        self.peer_id = _("Anonymous")
        self.download_repo = DOWNLOAD_REPO
        self.facade = get_facade()
        args = (parent, id)
        # begin wxGlade: FileDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.fileaction_sizer_staticbox = wx.StaticBox(self, -1, _("Actions"))
        self.repo_button = wx.BitmapButton(self, -1, wx.Bitmap(DOWNLOAD_DIR(),wx.BITMAP_TYPE_ANY))
        self.download_button = wx.BitmapButton(self, -1, wx.Bitmap(DOWNLOAD(),wx.BITMAP_TYPE_ANY))
        self.peerfiles_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.peerfiles_list.InsertColumn(0, "File")
        self.peerfiles_list.InsertColumn(1, "Tag")
        self.bind_controls()

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.download_button.Bind(wx.EVT_BUTTON, self.on_download)
        self.repo_button.Bind(wx.EVT_BUTTON, self.on_set_repo)

    def on_set_repo(self, evt):
        """add shared directory to list"""
        # pop up to choose repository
        dlg = wx.DirDialog(self, message=_("Choose location to download files into"),
                           defaultPath = self.facade.get_document().get_download_repo(),
                           style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            # path chosen
            path = dlg.GetPath()
            self.facade.change_download_repo(path)
        dlg.Destroy()
        
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

    def refresh(self, files=None):
        """overrides Show, files is {repos: [FileDescriptors], }"""
        if files is None:
            if self.facade is None:
                return
            files = self.facade.get_document().get_shared_files()
        self.peerfiles_list.DeleteAllItems()
        if len(files) > 0:
            # reformat data
            file_data = []
            for file_descs in files.values():
                for file_desc in file_descs:
                    file_data.append([file_desc.path,
                                      os.path.basename(file_desc.path),
                                      file_desc._tag])
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

    def Show(self, files=None, do_show=True):
        """overrides Show, files is {repos: {names:tags}, }"""
        if do_show:
            self.refresh(files)
        wx.Dialog.Show(self, do_show)

    def SetTitle(self, peer_desc=None):
        if isinstance(peer_desc, unicode) or isinstance(peer_desc, str):
            wx.Dialog.SetTitle(self, peer_desc)
            return
        if peer_desc and peer_desc.document:
            self.peer_id = peer_desc.peer_id
            pseudo = peer_desc.get_pseudo()
        else:
            pseudo = self.peer_id
        wx.Dialog.SetTitle(self, "%s's %s to go into %s"\
                           % (pseudo, _("Files"),
                              os.path.basename(self.download_repo)))

    def set_download_repo(self, value):
        """set value and update Title"""
        self.download_repo = value
        self.repo_button.SetToolTipString(self.download_repo)
        self.SetTitle()

    def set_facade(self, facade):
        self.facade = facade
        
    def __set_properties(self):
        # begin wxGlade: FileDialog.__set_properties
        self.SetTitle(_("Chose Files"))
        self.SetSize((460, 410))
        self.repo_button.SetToolTipString(_("Dowload repository"))
        self.repo_button.SetSize(self.repo_button.GetBestSize())
        self.download_button.SetToolTipString(_("Download selected files"))
        self.download_button.SetSize(self.download_button.GetBestSize())
        # end wxGlade
        if not self.plugin:
            self.download_button.Enable(False)

    def __do_layout(self):
        # begin wxGlade: FileDialog.__do_layout
        peerfiles_sizer = wx.BoxSizer(wx.VERTICAL)
        fileaction_sizer = wx.StaticBoxSizer(self.fileaction_sizer_staticbox, wx.HORIZONTAL)
        fileaction_sizer.Add(self.repo_button, 0, wx.ADJUST_MINSIZE, 0)
        fileaction_sizer.Add(self.download_button, 0, wx.FIXED_MINSIZE, 0)
        peerfiles_sizer.Add(fileaction_sizer, 0, wx.EXPAND, 0)
        peerfiles_sizer.Add(self.peerfiles_list, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(peerfiles_sizer)
        self.Layout()
        # end wxGlade

# end of class FileDialog


