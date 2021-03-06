# -*- coding: iso-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Tue Mar 22 11:28:12 2005
"""Panel to manage file sharing"""

import os, os.path
import wx, wx.gizmos
import sys
from os.path import abspath
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.data import DirContainer
from solipsis.services.profile.data import SHARING_ALL

# tree list
NB_SHARED_COL = 1
FULL_PATH_COL = 2
# dir list
NAME_COL = 0
TAG_COL = 1
IS_SHARED_COL = 2

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
        self.add_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/browse.jpeg", wx.BITMAP_TYPE_ANY))
        self.del_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/del_file.jpeg", wx.BITMAP_TYPE_ANY))
        self.share_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/add_file.gif", wx.BITMAP_TYPE_ANY))
        self.unshare_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/delete_file.gif", wx.BITMAP_TYPE_ANY))
        self.tag_value = wx.TextCtrl(self, -1, "")
        self.edit_button = wx.BitmapButton(self, -1, wx.Bitmap("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/edit_file.gif", wx.BITMAP_TYPE_ANY))
        self.tree_list = wx.gizmos.TreeListCtrl(self.window_1_pane_1, -1)
        self.dir_list = wx.ListCtrl(self.window_1_pane_2, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        isz = (16, 16)
        tree_il = wx.ImageList(isz[0], isz[1])
        self.tree_fldridx     = tree_il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.tree_fldropenidx = tree_il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN,   wx.ART_OTHER, isz))
        self.tree_list.SetImageList(tree_il)
        self.tree_il = tree_il
        
        dir_il = wx.ImageList(isz[0], isz[1])
        self.dir_fldridx     = dir_il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.dir_fileidx     = dir_il.Add(wx.ArtProvider_GetBitmap(wx.ART_REPORT_VIEW, wx.ART_OTHER, isz))
        self.dir_list.SetImageList(dir_il, wx.IMAGE_LIST_SMALL)
        self.dir_il = dir_il
        
        # build dir list view
        self.dir_list.InsertColumn(0, _("Name"))
        self.dir_list.InsertColumn(TAG_COL, _("Tag"))
        self.dir_list.InsertColumn(IS_SHARED_COL, _("Shared"), wx.LIST_FORMAT_RIGHT)
        self.dir_list.SetColumnWidth(0, 150)
        self.dir_list.SetColumnWidth(TAG_COL, 80)
        self.dir_list.SetColumnWidth(IS_SHARED_COL, 50)

        # specific stuff
        self.facade = get_facade()
        self.list_state = SelectedListState(self)
        self.tree_state = SelectedTreeState(self)
        self.current_state = None
        self.bind_controls()

        # build tree list view
        self.tree_list.AddColumn(_("Explorer"))
        self.tree_list.AddColumn(_("#shared"))
        self.tree_list.AddColumn(_("full path"))
        self.tree_list.SetMainColumn(0)
        self.tree_list.SetColumnWidth(0, 300)
        self.tree_list.SetColumnWidth(NB_SHARED_COL, 40)
        self.root = self.tree_list.AddRoot(_("File System..."))

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        self.add_button.Bind(wx.EVT_BUTTON, self.on_browse)
        self.del_button.Bind(wx.EVT_BUTTON, self.on_remove)
        self.share_button.Bind(wx.EVT_BUTTON, self.on_share)
        self.unshare_button.Bind(wx.EVT_BUTTON, self.on_unshare)
        self.edit_button.Bind(wx.EVT_BUTTON, self.on_tag)
        
        self.dir_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_list)
        self.tree_list.Bind(wx.EVT_TREE_SEL_CHANGING, self.on_select_tree)
        self.tree_list.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_expand)
        
    def on_browse(self, evt):
        """add shared directory to list"""
        # pop up to choose repository

        dlg = wx.DirDialog(self, message=_("Choose your repository"),
                           defaultPath = os.path.expanduser("~/"),
                           style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            # path chosen
            path = dlg.GetPath()
            self.facade.add_repository(path)
            self.facade.expand_dir(path)
        dlg.Destroy()
        
    def on_remove(self, evt):
        """remove shared directory from repository"""
        pass
        
    def on_share(self, evt):
        """share selected files or directory"""
        if self.current_state:
            self.current_state.on_share(evt)
        evt.Skip()
        
    def on_unshare(self, evt):
        """cancel sharing of selected files or directory"""
        if self.current_state:
            self.current_state.on_unshare(evt)
        evt.Skip()
        
    def on_tag(self, evt):
        """cancel sharing of selected files or directory"""
        if self.current_state:
            self.current_state.on_tag(evt)
        evt.Skip()

    def on_expand(self, evt):
        """put into cache new information when dir expanded in tree"""
        self.current_state = self.tree_state
        file_name = self.tree_list.GetItemText(evt.GetItem(), FULL_PATH_COL)
        if evt.GetItem() != self.root:
            self.facade.expand_dir(abspath(file_name))
            self.facade.expand_children('gui', abspath(file_name))
        evt.Skip()

    def on_select_list(self, evt):
        """new shared directory selecetd"""
        self.current_state = self.list_state
        dir_name = self.tree_list.GetItemText(self.tree_list.GetSelection(), FULL_PATH_COL)
        file_name = self.dir_list.GetItemText(evt.GetItem().GetId())
        data = self.facade.get_container('gui', abspath(os.path.join(dir_name,
                                                                     file_name)))
        # update tag
        self.tag_value.SetValue(data._tag)

    def on_select_tree(self, evt):
        """new shared directory selecetd"""
        self.current_state = self.tree_state
        file_name = self.tree_list.GetItemText(evt.GetItem(), FULL_PATH_COL)
        if evt.GetItem() != self.root:
            # update list
            data = self.facade.get_container('gui', abspath(file_name))
            self._display_dir_content(data)
            # update tag
            self.tag_value.SetValue(data._tag)

    def _display_dir_content(self, dir_container):
        """update list view with content of directory"""
        self.dir_list.DeleteAllItems()
        for name, container in dir_container.iteritems():
            if isinstance(container, DirContainer):
                index = self.dir_list.InsertImageStringItem(sys.maxint, name, self.dir_fldridx)
                self.dir_list.SetStringItem(index, 1, container._tag)
                self.dir_list.SetStringItem(index, 2, str(container._shared))
            else:
                index = self.dir_list.InsertImageStringItem(sys.maxint, name, self.dir_fileidx)
                self.dir_list.SetStringItem(index, 1, container._tag)
                self.dir_list.SetStringItem(index, 2, str(container._shared))

    def cb_update_tree(self, containers):
        """synchronize tree list with sharing container"""
        # update tree
        self._add_container_in_tree(self.root, containers)
        # update list
        selected_item = None
        try:
            selected_item = self.tree_list.GetItemText(self.tree_list.GetSelection(), FULL_PATH_COL)
        except:
            # no selection
            pass
        if selected_item:
            data = self.facade.get_container('gui', abspath(selected_item))
            self._display_dir_content(data)

    def _add_container_in_tree(self, parent, container):
        """format item in tree view"""
        child = self._add_item_in_tree(parent, container)
        for key, container in container.iteritems():
            if isinstance(container, DirContainer):
                self._add_container_in_tree(child, container)

    def _add_item_in_tree(self, parent, container):
        """add items in tree"""
        # create item
        if container.get_data() is None:
            name = os.path.basename(container.path)
            child = self.tree_list.AppendItem(parent, name)
            container.set_data(child)
            self.tree_list.SetItemImage(child, self.tree_fldridx, which = wx.TreeItemIcon_Normal)
            self.tree_list.SetItemImage(child, self.tree_fldropenidx, which = wx.TreeItemIcon_Expanded)
        else:
            child = container.get_data()
        nb_shared = container.nb_shared()
        if nb_shared == SHARING_ALL:
            str_shared = "All"
        else:
            str_shared = str(nb_shared)
        self.tree_list.SetItemText(child, u"%s"% str_shared, NB_SHARED_COL)
        self.tree_list.SetItemText(child, container.path, FULL_PATH_COL)
        return child

    def _get_selected_listitems(self):
        """returns all selected items in dir list"""
        result = []
        item = -1;
        while len(result) < self.dir_list.GetSelectedItemCount():
            item = self.dir_list.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if item == -1:
                break;
            else:
                result.append(item)
        return result
            
    def __set_properties(self):
        """init widgets properties"""
        # begin wxGlade: FilePanel.__set_properties
        self.add_button.SetSize(self.add_button.GetBestSize())
        self.del_button.SetSize(self.del_button.GetBestSize())
        self.share_button.SetSize(self.share_button.GetBestSize())
        self.unshare_button.SetSize(self.unshare_button.GetBestSize())
        self.tag_value.SetToolTipString(_("Complementary information on file"))
        self.edit_button.SetSize(self.edit_button.GetBestSize())
        # end wxGlade

    def __do_layout(self):
        """set up widgets"""
        # begin wxGlade: FilePanel.__do_layout
        file_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        actions_sizer = wx.StaticBoxSizer(self.actions_sizer_staticbox, wx.HORIZONTAL)
        actions_sizer.Add(self.add_button, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        actions_sizer.Add(self.del_button, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        actions_sizer.Add(self.share_button, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        actions_sizer.Add(self.unshare_button, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        actions_sizer.Add(self.tag_value, 1, wx.LEFT|wx.EXPAND|wx.FIXED_MINSIZE, 3)
        actions_sizer.Add(self.edit_button, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
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
        self.window_1.SplitVertically(self.window_1_pane_1, self.window_1_pane_2, 400)
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
        
    def on_share(self, evt):
        """share selected files or directory"""
        raise NotImplementedError("need a selection to share")
        
    def on_unshare(self, evt):
        """cancel sharing of selected files or directory"""
        raise NotImplementedError("need a selection to unshare")
        
    def on_tag(self, evt):
        """tag selected files or directory"""
        raise NotImplementedError("need a selection to tag")


class SelectedListState(FilePanelState):
    """Abstract class for states"""
    def __init__(self, owner):
        FilePanelState.__init__(self, owner)
        
    def on_share(self, evt):
        """share selected files"""
        dir_name = self.owner.tree_list.GetItemText(self.owner.tree_list.GetSelection(), FULL_PATH_COL)
        file_names = [self.owner.dir_list.GetItemText(item)
                      for item in self.owner._get_selected_listitems()]
        self.owner.facade.share_files((dir_name, file_names, True))
        
    def on_unshare(self, evt):
        """cancel sharing of selected files"""
        dir_name = self.owner.tree_list.GetItemText(self.owner.tree_list.GetSelection(), FULL_PATH_COL)
        file_names = [self.owner.dir_list.GetItemText(item)
                      for item in self.owner._get_selected_listitems()]
        self.owner.facade.share_files((dir_name, file_names, False))
        
    def on_tag(self, evt):
        """tag selected files or directory"""
        dir_name = self.owner.tree_list.GetItemText(self.owner.tree_list.GetSelection(), FULL_PATH_COL)
        file_names = [self.owner.dir_list.GetItemText(item)
                      for item in self.owner._get_selected_listitems()]
        self.owner.facade.tag_files((dir_name, file_names, self.owner.tag_value.GetValue()))

class SelectedTreeState(FilePanelState):
    """Abstract class for states"""
    def __init__(self, owner):
        FilePanelState.__init__(self, owner)
        
    def on_share(self, evt):
        """share all files in directory"""
        selections = [self.owner.tree_list.GetItemText(selected_item, FULL_PATH_COL)
                      for selected_item in self.owner.tree_list.GetSelections()]
        self.owner.facade.share_dirs((selections, True))
        
    def on_unshare(self, evt):
        """share all files in directory"""
        selections = [self.owner.tree_list.GetItemText(selected_item, FULL_PATH_COL)
                      for selected_item in self.owner.tree_list.GetSelections()]
        self.owner.facade.share_dirs((selections, False))
        for selection in selections:
            self.owner.facade.share_file((selection, False))
        
    def on_tag(self, evt):
        """tag selected files or directory"""
        selections = [self.owner.tree_list.GetItemText(selected_item, FULL_PATH_COL)
                      for selected_item in self.owner.tree_list.GetSelections()]
        for selection in selections:
            self.owner.facade.tag_file((selection, self.owner.tag_value.GetValue()))
