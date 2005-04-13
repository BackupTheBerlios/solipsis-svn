# -*- coding: iso-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Tue Mar 22 11:28:12 2005
"""Panel to manage file sharing"""

import os, os.path
import wx, wx.gizmos
import sys
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.data import SharingContainer

# begin wxGlade: dependencies
# end wxGlade
                
class FilePanel(wx.Panel):
    """Display shared file and allow user add/remove some"""
    def __init__(self, *args, **kwds):
        # begin wxGlade: FilePanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.window_1 = wx.SplitterWindow(self, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.window_1_pane_2 = wx.Panel(self.window_1, -1)
        self.window_1_pane_1 = wx.Panel(self.window_1, -1)
        self.actions_sizer_staticbox = wx.StaticBox(self, -1, _("Actions"))
        self.browse_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/browse.jpeg", wx.BITMAP_TYPE_ANY))
        self.add_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/add_file.jpeg", wx.BITMAP_TYPE_ANY))
        self.del_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/del_file.jpeg", wx.BITMAP_TYPE_ANY))
        self.tag_value = wx.TextCtrl(self, -1, "")
        self.tree_list = wx.TreeCtrl(self.window_1_pane_1, -1, style=wx.TR_HAS_BUTTONS|wx.TR_LINES_AT_ROOT|wx.TR_MULTIPLE|wx.TR_MULTIPLE|wx.TR_DEFAULT_STYLE|wx.SUNKEN_BORDER)
        self.dir_list = wx.ListCtrl(self.window_1_pane_2, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        isz = (16, 16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        self.fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_REPORT_VIEW, wx.ART_OTHER, isz))
        self.tree_list.SetImageList(il)
        self.dir_list.SetImageList(il, wx.IMAGE_LIST_SMALL)
        self.il = il
        
        # build dir list view
        self.dir_list.InsertColumn(0, "Name")
        self.dir_list.InsertColumn(1, "Tag")
        self.dir_list.InsertColumn(2, "Shared", wx.LIST_FORMAT_RIGHT)

        # specific stuff
        self.facade = get_facade()
        self.list_state = SelectedListState(self)
        self.tree_state = SelectedTreeState(self)
        self.current_state = FilePanelState(self)
        self.bind_controls()

        # build tree list view
        self.root = self.tree_list.AddRoot(_("File System..."))
        self.dirs = {}

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.browse_button.Bind(wx.EVT_BUTTON, self.on_browse)
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add)
        self.del_button.Bind(wx.EVT_BUTTON, self.on_del)
        
        self.dir_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_list)
        self.tree_list.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_expand)
        self.tree_list.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_select_tree)
        
    def on_browse(self, evt):
        """add shared directory to list"""
        # pop up to choose repository
        dlg = wx.DirDialog(self, message=_("Choose your repository"),
                           defaultPath = os.path.expanduser("~/"),
                           style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            # path chosen
            path = dlg.GetPath()
            # add item
            container = self.facade.add_dir(path)["cache"]
            item = self._add_item_in_tree(self.root, path, container)
            # fill new directories
            new_dirs = self.facade.expand_dir(path)
            for path, container in new_dirs.iteritems():
                self._add_item_in_tree(item, path, container)
        dlg.Destroy()

    def _add_item_in_tree(self, item, path, container):
        """add items in tree"""
        # create item
        child = self.tree_list.AppendItem(item, path.split(os.path.sep)[-1])
        self.tree_list.SetPyData(child, path)
        if os.path.isdir(path):
            self.tree_list.SetItemImage(child, self.fldridx, which = wx.TreeItemIcon_Normal)
            self.tree_list.SetItemImage(child, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
            self.tree_list.SetItemText(child, container.nb_shared, 1)
            self.tree_list.SetItemText(child, container.path, 2)
        else:
            self.tree_list.SetItemImage(child, self.fileidx, which = wx.TreeItemIcon_Normal)
            self.tree_list.SetItemImage(child, self.fileidx, which = wx.TreeItemIcon_Expanded)
        # link wx item with container in cache
        self.dirs[path] = container
        print "ADDED", path, container
        return child

    def on_expand(self, evt):
        """put into cache new information when dir expanded in tree"""
        item = evt.GetItem()
        path =  self.tree_list.GetPyData(item)
        print str(path)
        if path is None:
            evt.Skip()
            return
        container = self.dirs[path]
        new_dirs = self.facade.expand_dir(container.path)
        for new_dir, new_container in new_dirs.iteritems():
            new_path = os.path.join(path, new_dir)
            child_item = self.tree_list.AppendItem(item, new_dir)
            self.tree_list.SetPyData(child_item, new_path)
            self.dirs[new_path] = new_container
            self.tree_list.SetItemImage(child_item, self.fldridx, which = wx.TreeItemIcon_Normal)
            self.tree_list.SetItemImage(child_item, self.fldropenidx, which = wx.TreeItemIcon_Expanded)
            self.tree_list.SetItemText(child_item, new_container.nb_shared, 1)
            self.tree_list.SetItemText(child_item, new_container.path, 2)
        evt.Skip()
        
    def on_add(self, evt):
        """share selected files or directory"""
        self.current_state.on_add(evt)
        evt.Skip()
        
    def on_del(self, evt):
        """cancel sharing of selected files or directory"""
        self.current_state.on_del(evt)
        evt.Skip()

    def on_select_list(self, evt):
        """new shared directory selecetd"""
        self.current_state = self.list_state
        self.current_state.on_select(evt)
        evt.Skip()

    def on_select_tree(self, evt):
        """new shared directory selecetd"""
        self.current_state = self.tree_state
        self.current_state.on_select(evt)
        evt.Skip()

    def _add_item_in_list(self, full_path):
        """format item in tree view"""
        self.dir_list.ClearAll()
        file_content = self.facade.get_keys(full_path)
        for file_name, file_container in file_content.iteritems():
            #add to file list
            index = self.dir_list.InsertImageStringItem(sys.maxint, file_name, self.fileidx)
            self.dir_list.SetStringItem(index, 1, file_container.tag)
            self.dir_list.SetStringItem(index, 2, file_container.shared)
            self.dir_list.SetPyData(index, os.path.join(full_path, file_name))
        

    def _display_content_in_list(self, full_path):
        """format item in tree view"""
        self.dir_list.ClearAll()
        file_content = self.facade.get_keys(full_path)
        for file_name, file_container in file_content.iteritems():
            #add to file list
            index = self.dir_list.InsertImageStringItem(sys.maxint, file_name, self.fileidx)
            self.dir_list.SetStringItem(index, 1, file_container.tag)
            self.dir_list.SetStringItem(index, 2, file_container.shared)
            self.dir_list.SetPyData(index, os.path.join(full_path, file_name))
            
    def __set_properties(self):
        """init widgets properties"""
        # begin wxGlade: FilePanel.__set_properties
        self.browse_button.SetSize(self.browse_button.GetBestSize())
        self.add_button.SetSize(self.add_button.GetBestSize())
        self.del_button.SetSize(self.del_button.GetBestSize())
        self.tag_value.SetToolTipString(_("Complementary information on file"))
        # end wxGlade

    def __do_layout(self):
        """set up widgets"""
        # begin wxGlade: FilePanel.__do_layout
        file_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        actions_sizer = wx.StaticBoxSizer(self.actions_sizer_staticbox, wx.HORIZONTAL)
        actions_sizer.Add(self.browse_button, 0, wx.FIXED_MINSIZE, 0)
        actions_sizer.Add(self.add_button, 0, wx.FIXED_MINSIZE, 0)
        actions_sizer.Add(self.del_button, 0, wx.FIXED_MINSIZE, 0)
        actions_sizer.Add(self.tag_value, 1, wx.LEFT|wx.EXPAND|wx.FIXED_MINSIZE, 3)
        file_sizer.Add(actions_sizer, 0, wx.ALL|wx.EXPAND, 3)
        sizer_1.Add(self.tree_list, 1, wx.EXPAND, 0)
        self.window_1_pane_1.SetAutoLayout(True)
        self.window_1_pane_1.SetSizer(sizer_1)
        sizer_1.Fit(self.window_1_pane_1)
        sizer_1.SetSizeHints(self.window_1_pane_1)
        sizer_2.Add(self.dir_list, 1, wx.EXPAND, 0)
        self.window_1_pane_2.SetAutoLayout(True)
        self.window_1_pane_2.SetSizer(sizer_2)
        sizer_2.Fit(self.window_1_pane_2)
        sizer_2.SetSizeHints(self.window_1_pane_2)
        self.window_1.SplitVertically(self.window_1_pane_1, self.window_1_pane_2, 250)
        file_sizer.Add(self.window_1, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(file_sizer)
        file_sizer.Fit(self)
        file_sizer.SetSizeHints(self)
        # end wxGlade

# end of class FilePanel


class FilePanelState:
    """Abstract class for states"""
    def __init__(self, owner):
        self.owner = owner
        
    def on_add(self, evt):
        """share selected files or directory"""
        raise NotImplementedError("need a selection to share")
        
    def on_del(self, evt):
        """cancel sharing of selected files or directory"""
        raise NotImplementedError("need a selection to unshare")
    
    def on_select(self, evt):
        """tag selected files or all directory"""
        raise NotImplementedError


class SelectedListState(FilePanelState):
    """Abstract class for states"""
    def __init__(self, owner):
        FilePanelState.__init__(self, owner)
        
    def on_add(self, evt):
        """share selected files"""
        raise NotImplementedError("no selection")
        
    def on_del(self, evt):
        """cancel sharing of selected files"""
        raise NotImplementedError
    
    def on_select(self, evt):
        """acrtion on selection"""
        self.owner.tag_value.SetValue(container._tag)

class SelectedTreeState(FilePanelState):
    """Abstract class for states"""
    def __init__(self, owner):
        FilePanelState.__init__(self, owner)
        
    def on_add(self, evt):
        """share directory"""
        raise NotImplementedError
        
    def on_del(self, evt):
        """cancel sharing of directory"""
        raise NotImplementedError
    
    def on_select(self, evt):
        """acrtion on selection"""
        item = evt.GetItem()
        data = self.owner.tree_list.GetPyData(item)
        if data is None:
            data = self.owner.tree_list.GetItemText(item)
        print str(data)
        self.owner._display_dir_content(data)

