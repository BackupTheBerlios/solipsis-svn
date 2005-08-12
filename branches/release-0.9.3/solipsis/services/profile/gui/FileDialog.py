# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Fri May 27 10:37:01 2005

import wx
import sys
import os.path
from solipsis.util.wxutils import _
from solipsis.util.uiproxy import UIProxyReceiver
from solipsis.services.profile.prefs import get_prefs
from solipsis.services.profile.pathutils import formatbytes
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile import DOWNLOAD, DOWNLOAD_DIR, \
     ENCODING, NAME_COL, SIZE_COL

TAG_COL = 2

# begin wxGlade: dependencies
# end wxGlade

class FileDialog(wx.Dialog, UIProxyReceiver):
    def __init__(self, parent, id, plugin=None, **kwds):
        UIProxyReceiver.__init__(self)
        self.data = {}
        self.plugin = plugin
        self.peer_desc = None
        self.active = False
        args = (parent, id)
        # begin wxGlade: FileDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.fileaction_sizer_staticbox = wx.StaticBox(self, -1, _("Actions"))
        self.label_1 = wx.StaticText(self, -1, _("Incoming dir:"))
        self.repo_value = wx.TextCtrl(self, -1, "")
        self.repo_button = wx.BitmapButton(self, -1, wx.Bitmap(DOWNLOAD_DIR(),wx.BITMAP_TYPE_ANY))
        self.download_button = wx.BitmapButton(self, -1, wx.Bitmap(DOWNLOAD(),wx.BITMAP_TYPE_ANY))
        self.peerfiles_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.peerfiles_list.InsertColumn(NAME_COL, "File")
        self.peerfiles_list.InsertColumn(TAG_COL, "Tag")
        self.peerfiles_list.InsertColumn(SIZE_COL, "Size")
        self.peerfiles_list.SetColumnWidth(NAME_COL, 150)
        self.peerfiles_list.SetColumnWidth(SIZE_COL, 60)
        self.peerfiles_list.SetColumnWidth(TAG_COL, wx.LIST_AUTOSIZE_USEHEADER)
        self.bind_controls()

    def activate(self):
        self.active = True

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.download_button.Bind(wx.EVT_BUTTON, self.on_download)
        self.repo_button.Bind(wx.EVT_BUTTON, self.on_browse_repo)
        self.repo_value.Bind(wx.EVT_KILL_FOCUS, self.on_set_repo)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, evt):
        """hiding instead of closing"""
        self.active = False
        wx.Dialog.Show(self, False)
        evt.Skip()

    def on_set_repo(self, evt):
        """set download directory according to value"""
        path = self.repo_value.GetValue()
        while path and not os.path.isdir(path):
            path = os.path.dirname(path)
        get_prefs().set("download_repo", path.encode(ENCODING))
        self.repo_value.SetValue(path)
        self.repo_button.SetToolTipString(path)
        self.SetTitle()

    def on_browse_repo(self, evt):
        """select download directory in DirDialog"""
        # pop up to choose repository
        dlg = wx.DirDialog(self, message=_("Choose location to download files into"),
                           defaultPath = unicode(get_prefs().get("download_repo"), ENCODING),
                           style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            # path chosen
            path = dlg.GetPath()
            get_prefs().set("download_repo", path.encode(ENCODING))
            self.repo_value.SetValue(path)
            self.repo_button.SetToolTipString(path)
            self.SetTitle()
        dlg.Destroy()
        
    def on_download(self, evt):
        """dowload selected files"""
        assert self.peer_desc.node_id != None, "no peer linked to sharelist"
        selections = []
        selected = -1
        # get selected path
        for index in range(self.peerfiles_list.GetSelectedItemCount()):
            selected = self.peerfiles_list.GetNextItem(selected, state=wx.LIST_STATE_SELECTED)
            selections.append(self.data[selected])
        # send network command
        self.plugin.get_files(self.peer_desc.node_id, selections)

    def refresh(self, files=None):
        """overrides Show, files is {repos: [FileDescriptors], }"""
        if files is None:
            if get_facade() is None:
                return
            files = get_facade().get_document().get_shared_files()
        self.peerfiles_list.DeleteAllItems()
        if len(files) > 0:
            # reformat data
            file_data = []
            for file_descs in files.values():
                for file_desc in file_descs:
                    file_data.append([file_desc.get_path(),
                                      file_desc.name,
                                      file_desc._tag,
                                      file_desc.size])
            # clear previous data
            for key in self.data.keys():
                del self.data[key]
            # fill list
            for path, name, tag, size in file_data:
                index = self.peerfiles_list.InsertStringItem(sys.maxint,
                                                             unicode(name, ENCODING))
                self.peerfiles_list.SetStringItem(index, TAG_COL, tag)
                self.peerfiles_list.SetStringItem(index, SIZE_COL, formatbytes(size,
                                                                        kiloname="Ko",
                                                                        meganame="Mo",
                                                                        bytename="o"))
                self.data[index] = (path.split(os.sep), size)
        # show result
        self.peerfiles_list.SetColumnWidth(TAG_COL, wx.LIST_AUTOSIZE)

    def Show(self, files=None, do_show=True):
        """overrides Show, files is {repos: {names:tags}, }"""
        if do_show:
            self.refresh(files)
            if self.active:
                wx.Dialog.Show(self, True)
        else:
            self.active = False
            wx.Dialog.Show(self, False)

    def SetTitle(self, title=None):
        if not title:
            if self.peer_desc:
                title = self.peer_desc.pseudo + "'s files"
            else:
                title = unicode("your files going into " + \
                                get_prefs().get("download_repo"), ENCODING)
        wx.Dialog.SetTitle(self, title)

    def set_desc(self, value):
        """set value and update Title"""
        self.peer_desc = value
        self.SetTitle()

    def on_change_facade(self):
        self.peer_desc = get_facade()._desc
        self.SetTitle()
        
    def __set_properties(self):
        # begin wxGlade: FileDialog.__set_properties
        self.SetTitle(_("Chose Files"))
        self.SetSize((460, 410))
        self.repo_button.SetToolTipString(_("Dowload repository"))
        self.repo_button.SetSize(self.repo_button.GetBestSize())
        self.download_button.SetToolTipString(_("Download selected files"))
        self.download_button.SetSize(self.download_button.GetBestSize())
        # end wxGlade
        self.repo_value.SetValue(unicode(get_prefs().get("download_repo"), ENCODING))
        if not self.plugin:
            self.download_button.Enable(False)

    def __do_layout(self):
        # begin wxGlade: FileDialog.__do_layout
        peerfiles_sizer = wx.BoxSizer(wx.VERTICAL)
        fileaction_sizer = wx.StaticBoxSizer(self.fileaction_sizer_staticbox, wx.HORIZONTAL)
        fileaction_sizer.Add(self.label_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        fileaction_sizer.Add(self.repo_value, 1, wx.LEFT|wx.RIGHT|wx.ADJUST_MINSIZE, 5)
        fileaction_sizer.Add(self.repo_button, 0, wx.ADJUST_MINSIZE, 0)
        fileaction_sizer.Add(self.download_button, 0, wx.FIXED_MINSIZE, 0)
        peerfiles_sizer.Add(fileaction_sizer, 0, wx.EXPAND, 0)
        peerfiles_sizer.Add(self.peerfiles_list, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(peerfiles_sizer)
        self.Layout()
        # end wxGlade

# end of class FileDialog


