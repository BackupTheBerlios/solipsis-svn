# -*- coding: iso-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Tue Mar 22 11:28:12 2005
"""Panel to manage file sharing"""

import os, os.path
import wx, wx.gizmos
import sys
from os.path import abspath
from solipsis.util.wxutils import _
from solipsis.services.profile.pathutils import formatbytes
from solipsis.services.profile.facade import get_facade
from solipsis.services.profile.path_containers import DirContainer, DEFAULT_TAG
from solipsis.services.profile import ADD_REPO, DEL_REPO, ENCODING, \
     SHARE, UNSHARE, EDIT, PREVIEW, \
     NAME_COL, SIZE_COL, TAG_COL, SHARED_COL, \
     NB_SHARED_COL, FULL_PATH_COL

from FileDialog import FileDialog

# begin wxGlade: dependencies
# end wxGlade
                
class FilePanel(wx.Panel):
    """Display shared file and allow user add/remove some"""
    def __init__(self, parent, id,
                 cb_modified=lambda x: sys.stdout.write(str(x))):
        # set members
        self.do_modified = cb_modified
        args = (parent, id)
        kwds = {}
        # begin wxGlade: FilePanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.window_1 = wx.SplitterWindow(self, -1, style=wx.SP_3D|wx.SP_BORDER)
        self.window_1_pane_2 = wx.Panel(self.window_1, -1)
        self.window_1_pane_1 = wx.Panel(self.window_1, -1)
        self.actions_sizer_staticbox = wx.StaticBox(self, -1, _("Actions"))
        self.label_2 = wx.StaticText(self, -1, _("Tag:"))
        self.tag_value = wx.TextCtrl(self, -1, "")
        self.edit_button = wx.BitmapButton(self, -1, wx.Bitmap(EDIT(),wx.BITMAP_TYPE_ANY))
        self.share_button = wx.BitmapButton(self, -1, wx.Bitmap(SHARE(),wx.BITMAP_TYPE_ANY))
        self.unshare_button = wx.BitmapButton(self, -1, wx.Bitmap(UNSHARE(),wx.BITMAP_TYPE_ANY))
        self.tree_list = wx.gizmos.TreeListCtrl(self.window_1_pane_1, -1)
        self.dir_list = wx.ListCtrl(self.window_1_pane_2, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

        # Popup menus
        self.tree_menu = wx.Menu()
        self.add_item = wx.MenuItem(self.tree_menu, wx.NewId(), _('Add directory'))
        self.tree_menu.AppendItem(self.add_item)
        self.del_item = wx.MenuItem(self.tree_menu, wx.NewId(), _('Remove directory'))
        self.tree_menu.AppendItem(self.del_item)
        self.tree_menu.AppendSeparator()
        self.share_all_item = wx.MenuItem(self.tree_menu, wx.NewId(), _('Share recursively'))
        self.tree_menu.AppendItem(self.share_all_item)
        self.unshare_all_item = wx.MenuItem(self.tree_menu, wx.NewId(), _('Unshare recursively'))
        self.tree_menu.AppendItem(self.unshare_all_item)
        
        self.list_menu = wx.Menu()
        self.tag_item = wx.MenuItem(self.list_menu, wx.NewId(), _('Tag'))
        self.list_menu.AppendItem(self.tag_item)
        self.share_item = wx.MenuItem(self.list_menu, wx.NewId(), _('Share'))
        self.list_menu.AppendItem(self.share_item)
        self.unshare_item = wx.MenuItem(self.list_menu, wx.NewId(), _('Unshare'))
        self.list_menu.AppendItem(self.unshare_item)

        # images
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
        self.dir_list.InsertColumn(SIZE_COL, _("Size"), wx.LIST_FORMAT_RIGHT)
        self.dir_list.InsertColumn(SHARED_COL, _("Shared"), wx.LIST_FORMAT_RIGHT)
        self.dir_list.InsertColumn(TAG_COL, _("Tag"))
        self.dir_list.SetColumnWidth(NAME_COL, 150)
        self.dir_list.SetColumnWidth(SIZE_COL, 60)
        self.dir_list.SetColumnWidth(SHARED_COL, wx.LIST_AUTOSIZE_USEHEADER)
        self.dir_list.SetColumnWidth(TAG_COL, wx.LIST_AUTOSIZE_USEHEADER)

        # specific stuff
        self.list_state = SelectedListState(self)
        self.tree_state = SelectedTreeState(self)
        self.current_state = None
        self.bind_controls()

        # build tree list view
        self.tree_list.AddColumn(_("Explorer"))
        self.tree_list.AddColumn(_("#shared"))
        self.tree_list.AddColumn(_("full path"))
        self.tree_list.SetMainColumn(0)
        self.tree_list.SetColumnWidth(0, 150)
        self.tree_list.SetColumnWidth(NB_SHARED_COL, 40)
        self.root = self.tree_list.AddRoot(_("File System..."))

        # shared file preview
        self.file_dlg = FileDialog(self, -1)
        wx.Dialog.SetTitle(self.file_dlg, _("Your shared files"))

    # EVENTS
    
    def bind_controls(self):
        """bind all controls with facade"""
        # selection
        self.dir_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_list)
        self.dir_list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_popup_list)
        
        self.tree_list.Bind(wx.EVT_TREE_SEL_CHANGING, self.on_select_tree)
        self.tree_list.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_popup_tree)
        self.tree_list.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_expand)
        # button
        self.share_button.Bind(wx.EVT_BUTTON, self.on_share)
        self.unshare_button.Bind(wx.EVT_BUTTON, self.on_unshare)
        self.edit_button.Bind(wx.EVT_BUTTON, self.on_tag)
        # popu menus
        self.Bind(wx.EVT_MENU, self.on_browse, id=self.add_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_remove, id=self.del_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_share, id=self.share_all_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_unshare, id=self.unshare_all_item.GetId())
        
        self.Bind(wx.EVT_MENU, self.on_tag, id=self.tag_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_share, id=self.share_item.GetId())
        self.Bind(wx.EVT_MENU, self.on_unshare, id=self.unshare_item.GetId())
        
    def on_browse(self, evt):
        """add shared directory to list"""
        # pop up to choose repository
        dlg = wx.DirDialog(self, message=_("Choose your repository"),
                           defaultPath = os.path.expanduser("~/"),
                           style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            # path chosen
            path = dlg.GetPath()
            get_facade().add_repository(path)
            get_facade().recursive_share((path, True))
        dlg.Destroy()
        
    def on_remove(self, evt):
        """remove shared directory from repository"""
        file_name = self.tree_list.GetItemText(self.tree_list.GetSelection(), FULL_PATH_COL)
        repositories = get_facade()._desc.document.get_repositories()
        if file_name and os.path.exists(file_name) and file_name in repositories:
            self.dir_list.DeleteAllItems()
            self.tree_list.SelectItem(self.root)
            item = get_facade().get_file_container(file_name)
            self.tree_list.DeleteChildren(item.get_data())
            self.tree_list.Delete(item.get_data())
            get_facade().del_repository(file_name)
            self.do_modified(True)
        
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
        
    def on_preview(self, evt):
        """display all shared files in a FileDialog"""
        self.file_dlg._activated = True
        self.file_dlg.Show(do_show=not self.file_dlg.IsShown())
        evt.Skip()

    def on_expand(self, evt):
        """put into cache new information when dir expanded in tree"""
        self.current_state = self.tree_state
        file_name = self.tree_list.GetItemText(evt.GetItem(), FULL_PATH_COL)
        if evt.GetItem() != self.root:
            get_facade().expand_dir(abspath(file_name))
            get_facade().expand_children(abspath(file_name))
        evt.Skip()

    def on_select_list(self, evt):
        """new shared directory selecetd"""
        self.current_state = self.list_state
        dir_name = self.tree_list.GetItemText(self.tree_list.GetSelection(), FULL_PATH_COL)
        file_name = self.dir_list.GetItemText(self.dir_list.GetNextItem(-1, state=wx.LIST_STATE_SELECTED))
        full_path = abspath(os.path.join(dir_name, file_name))
        data = get_facade().get_file_container(full_path)

    def on_select_tree(self, evt):
        """new shared directory selecetd"""
        self.current_state = self.tree_state
        file_name = self.tree_list.GetItemText(evt.GetItem(), FULL_PATH_COL)
        if not file_name:
            self.dir_list.DeleteAllItems()
        else:
            if evt.GetItem() != self.root:
                data = get_facade().get_file_container(abspath(file_name))
                self._display_dir_content(data)

    def on_popup_list(self, evt):
        item = evt.GetItem()
        self.PopupMenu(self.list_menu)
        
    def on_popup_tree(self, evt):
        item = evt.GetItem()
        self.tree_list.SelectItem(item)
        self.PopupMenu(self.tree_menu)

    def _display_dir_content(self, dir_container):
        """update list view with content of directory"""
        self.dir_list.DeleteAllItems()
        for name, container in dir_container.iteritems():
            if isinstance(container, DirContainer):
                index = self.dir_list.InsertImageStringItem(sys.maxint, unicode(name, ENCODING), self.dir_fldridx)
                self.dir_list.SetItemTextColour(index, wx.LIGHT_GREY)
            else:
                index = self.dir_list.InsertImageStringItem(sys.maxint, unicode(name, ENCODING), self.dir_fileidx)
                self.dir_list.SetStringItem(index, SIZE_COL, formatbytes(container.size,
                                                                        kiloname="Ko",
                                                                        meganame="Mo",
                                                                        bytename="o"))
                self.dir_list.SetItemTextColour(index, container._shared and wx.BLUE or wx.BLACK)
                self.dir_list.SetStringItem(index, SHARED_COL, str(container._shared))
                self.dir_list.SetStringItem(index, TAG_COL, container._tag)
        self.dir_list.SetColumnWidth(TAG_COL, wx.LIST_AUTOSIZE)
    
    def cb_update_tree(self, container):
        """synchronize tree list with sharing container"""
        # update tree
        self._add_container_in_tree(self.root, container)
        # update list
        try:
            selected_item = self.tree_list.GetItemText(self.tree_list.GetSelection(), FULL_PATH_COL)
            data = get_facade().get_file_container(abspath(selected_item))
            self._display_dir_content(data)
        except:
            #no selection
            pass
        self.tree_list.Expand(self.root)

    def _add_container_in_tree(self, parent, container):
        """format item in tree view"""
        child = self._add_item_in_tree(parent, container)
        for key, container in container.iteritems():
            if isinstance(container, DirContainer):
                self._add_container_in_tree(child, container)

    def _add_item_in_tree(self, parent, container):
        """add items in tree"""
        # create item
        container_path = container.get_path()
        if container.get_data() is None:
            name = os.path.basename(container_path)
            child = self.tree_list.AppendItem(parent, unicode(name, ENCODING))
            container.set_data(child)
            self.tree_list.SetItemImage(child, self.tree_fldridx, which = wx.TreeItemIcon_Normal)
            self.tree_list.SetItemImage(child, self.tree_fldropenidx, which = wx.TreeItemIcon_Expanded)
        else:
            child = container.get_data()
        nb_shared = container.nb_shared()
        str_shared = str(nb_shared)
        self.tree_list.SetItemText(child, u"%s"% str_shared, NB_SHARED_COL)
        self.tree_list.SetItemText(child, unicode(container_path, ENCODING), FULL_PATH_COL)
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

    def on_change_facade(self):
        """setter"""
        self.file_dlg.on_change_facade()
            
    def __set_properties(self):
        """init widgets properties"""
        # begin wxGlade: FilePanel.__set_properties
        self.tag_value.SetToolTipString(_("Complementary information on file"))
        self.edit_button.SetToolTipString(_("Tag"))
        self.edit_button.SetSize(self.edit_button.GetBestSize())
        self.share_button.SetToolTipString(_("Share"))
        self.share_button.SetSize(self.share_button.GetBestSize())
        self.unshare_button.SetToolTipString(_("Unshare"))
        self.unshare_button.SetSize(self.unshare_button.GetBestSize())
        # end wxGlade

    def __do_layout(self):
        """set up widgets"""
        # begin wxGlade: FilePanel.__do_layout
        file_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        actions_sizer = wx.StaticBoxSizer(self.actions_sizer_staticbox, wx.HORIZONTAL)
        actions_sizer.Add(self.label_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        actions_sizer.Add(self.tag_value, 1, wx.LEFT|wx.RIGHT|wx.EXPAND|wx.FIXED_MINSIZE, 5)
        actions_sizer.Add(self.edit_button, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        actions_sizer.Add(self.share_button, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        actions_sizer.Add(self.unshare_button, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
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
        self.window_1.SplitVertically(self.window_1_pane_1, self.window_1_pane_2, 180)
        file_sizer.Add(self.window_1, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(file_sizer)
        file_sizer.Fit(self)
        file_sizer.SetSizeHints(self)
        # end wxGlade
        # reset splitter since bug in wxGlade
        self.window_1.SplitVertically(self.window_1_pane_1, self.window_1_pane_2, 180)

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
        get_facade().share_files((dir_name, file_names, True))
        self.owner.do_modified(True)
        
    def on_unshare(self, evt):
        """cancel sharing of selected files"""
        dir_name = self.owner.tree_list.GetItemText(self.owner.tree_list.GetSelection(), FULL_PATH_COL)
        file_names = [self.owner.dir_list.GetItemText(item)
                      for item in self.owner._get_selected_listitems()]
        get_facade().share_files((dir_name, file_names, False))
        self.owner.do_modified(True)
        
    def on_tag(self, evt):
        """tag selected files or directory"""
        dir_name = self.owner.tree_list.GetItemText(self.owner.tree_list.GetSelection(), FULL_PATH_COL)
        file_names = [os.path.join(dir_name, self.owner.dir_list.GetItemText(item))
                      for item in self.owner._get_selected_listitems()]
        tag_value = self.owner.tag_value.GetValue()
        for file_name in file_names:
            get_facade().tag_file((file_name, tag_value))
        self.owner.do_modified(True)

class SelectedTreeState(FilePanelState):
    """Abstract class for states"""
    def __init__(self, owner):
        FilePanelState.__init__(self, owner)
        
    def on_share(self, evt):
        """share all files in directory"""
        for selection in self.get_selection():
            get_facade().recursive_share((selection, True))
        self.owner.do_modified(True)
        
    def on_unshare(self, evt):
        """share all files in directory"""
        for selection in self.get_selection():
            get_facade().recursive_share((selection, False))
        self.owner.do_modified(True)
        
    def on_tag(self, evt):
        """tag selected files or directory"""
        for selection in self.get_selection():
            get_facade().tag_file((selection, self.owner.tag_value.GetValue()))
        self.owner.do_modified(True)

    def get_selection(self):
        selections = []
        # all repositories
        if self.owner.root in self.owner.tree_list.GetSelections():
            child, cookie = self.owner.tree_list.GetFirstChild(self.owner.root)
            selections.append(self.owner.tree_list.GetItemText(child, FULL_PATH_COL))
            next = self.owner.tree_list.GetNextSibling(child)
            while next.IsOk():
                selections.append(self.owner.tree_list.GetItemText(next, FULL_PATH_COL))
                next = self.owner.tree_list.GetNextSibling(next)
        # selected only
        else:
            selections = [self.owner.tree_list.GetItemText(selected_item, FULL_PATH_COL)
                          for selected_item in self.owner.tree_list.GetSelections()]
        return selections
