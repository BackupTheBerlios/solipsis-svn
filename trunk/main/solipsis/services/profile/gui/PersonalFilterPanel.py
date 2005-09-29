# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Tue Jun 21 11:01:29 2005

import wx
import sys

from solipsis.util.wxutils import _
from solipsis.services.profile import ADD_CUSTOM, DEL_CUSTOM
from solipsis.services.profile.facade import get_filter_facade
from solipsis.services.profile.filter_document import FilterValue

# begin wxGlade: dependencies
# end wxGlade

class PersonalFilterPanel(wx.Panel):
    def __init__(self, parent, id,
                 cb_modified=lambda x: sys.stdout.write(str(x))):
        # set members
        self.edited_item = None
        self.do_modified = cb_modified
        args = (parent, id)
        kwds = {}
        # begin wxGlade: PersonalFilterPanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.p_action_sizer_staticbox = wx.StaticBox(self, -1, _("Specify here a filter to use for a given keyword"))
        self.identity_sizer_staticbox = wx.StaticBox(self, -1, _("Identity"))
        self.title_checkbox = wx.CheckBox(self, -1, "")
        self.title_value = wx.ComboBox(self, -1, choices=["", _("Mr"), _("Mrs"), _("Ms")], style=wx.CB_DROPDOWN|wx.CB_SIMPLE|wx.CB_READONLY)
        self.firstname_checkbox = wx.CheckBox(self, -1, "")
        self.firstname_value = wx.TextCtrl(self, -1, _("First name"))
        self.lastname_checkbox = wx.CheckBox(self, -1, "")
        self.lastname_value = wx.TextCtrl(self, -1, _("Last Name"))
        self.pseudo_checkbox = wx.CheckBox(self, -1, _("Pseudo: "))
        self.pseudo_value = wx.TextCtrl(self, -1, "")
        self.email_checkbox = wx.CheckBox(self, -1, _("E-Mail: "))
        self.email_value = wx.TextCtrl(self, -1, "")
        self.p_key_value = wx.TextCtrl(self, -1, _("Favourite Book"))
        self.p_filter_value = wx.TextCtrl(self, -1, _(".*Potter.*"))
        self.add_p_filter_button = wx.BitmapButton(self, -1, wx.Bitmap(ADD_CUSTOM(),wx.BITMAP_TYPE_ANY))
        self.del_p_filter_button = wx.BitmapButton(self, -1, wx.Bitmap(DEL_CUSTOM(),wx.BITMAP_TYPE_ANY))
        self.p_filters_list = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.LC_SORT_ASCENDING|wx.NO_BORDER)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        
        self.PopulateList()
        self.bind_controls()

    def PopulateList(self):
        self.p_filters_list.InsertColumn(0, _("MetaData"))
        self.p_filters_list.InsertColumn(1, _("Filter expresion"))
        self.p_filters_list.SetColumnWidth(0, 200)
        self.p_filters_list.SetColumnWidth(1, 200)

    # EVENTS
    def bind_controls(self):
        """bind all controls with facade"""
        # custom list
        self.p_filters_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selected)
        self.add_p_filter_button.Bind(wx.EVT_BUTTON, self.on_add)
        self.del_p_filter_button.Bind(wx.EVT_BUTTON, self.on_del)
        # boxes
        self.title_checkbox.Bind(wx.EVT_CHECKBOX, self.on_check_title)
        self.firstname_checkbox.Bind(wx.EVT_CHECKBOX, self.on_check_firstname)
        self.lastname_checkbox.Bind(wx.EVT_CHECKBOX, self.on_check_lastname)
        self.pseudo_checkbox.Bind(wx.EVT_CHECKBOX, self.on_check_pseudo)
        self.email_checkbox.Bind(wx.EVT_CHECKBOX, self.on_check_email)
        # set focus
        self.title_value.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.firstname_value.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.lastname_value.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.pseudo_value.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.email_value.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        # kill focus
        self.title_value.Bind(wx.EVT_KILL_FOCUS, self.on_check_title)
        self.firstname_value.Bind(wx.EVT_KILL_FOCUS, self.on_check_firstname)
        self.lastname_value.Bind(wx.EVT_KILL_FOCUS, self.on_check_lastname)
        self.pseudo_value.Bind(wx.EVT_KILL_FOCUS, self.on_check_pseudo)
        self.email_value.Bind(wx.EVT_KILL_FOCUS, self.on_check_email)

    def on_focus(self, evt):
        self.do_modified(True)

    def on_selected(self, evt):
        """meta data"""
        self.edited_item = (evt.GetIndex(), evt.GetItem().GetText())
        self.p_key_value.SetValue(self.edited_item[1])
        self.p_filter_value.SetValue(self.p_filters_list.GetItem(evt.GetIndex(), 1).GetText())
        
    def on_add(self, evt):
        """a custom attribute has been modified"""
        try:
            # update cache, facade will refresh window (through FilterView)
            filter_value = FilterValue(value=self.p_filter_value.GetValue(),
                                       activate=True)
            get_filter_facade().add_custom_attributes(self.p_key_value.GetValue(), filter_value)
            self.do_modified(True)
        except Exception:
            self._regex_not_valid("attribute", self.p_filter_value.GetValue())

    def on_del(self, evt):
        """a custom attribute has been modified"""
        # update data
        index = self.p_filters_list.FindItem(0, self.p_key_value.GetValue())
        if index != -1 and self.p_filters_list.DeleteItem(index):
            get_filter_facade().del_custom_attributes(self.p_key_value.GetValue())
            self.do_modified(True)

    def on_check_title(self, evt):
        """activate field and notify facade"""
        try:
            filter_value = FilterValue(value=self.title_value.GetValue(),
                                       activate=self.title_checkbox.IsChecked())
            if get_filter_facade().change_title(filter_value) != False:
                self.do_modified(True)
        except Exception:
            self._regex_not_valid("title", self.title_value.GetValue())
        evt.Skip()

    def on_check_firstname(self, evt):
        """activate field and notify facade"""
        try:
            filter_value = FilterValue(value=self.firstname_value.GetValue(),
                                       activate=self.firstname_checkbox.IsChecked())
            if get_filter_facade().change_firstname(filter_value) != False:
                self.do_modified(True)
        except Exception:
            self._regex_not_valid("firstname", self.firstname_value.GetValue())
        evt.Skip()

    def on_check_lastname(self, evt):
        """activate field and notify facade"""
        try:
            filter_value = FilterValue(value=self.lastname_value.GetValue(),
                                       activate=self.lastname_checkbox.IsChecked())
            if get_filter_facade().change_lastname(filter_value) != False:
                self.do_modified(True)
        except Exception:
            self._regex_not_valid("lastname", self.lastname_value.GetValue())
        evt.Skip()

    def on_check_pseudo(self, evt):
        """activate field and notify facade"""
        try:
            filter_value = FilterValue(value=self.pseudo_value.GetValue(),
                                       activate=self.pseudo_checkbox.IsChecked())
            if get_filter_facade().change_pseudo(filter_value) != False:
                self.do_modified(True)
        except Exception, err:
            self._regex_not_valid("pseudo", self.pseudo_value.GetValue())
        evt.Skip()

    def on_check_email(self, evt):
        """activate field and notify facade"""
        try:
            filter_value = FilterValue(value=self.email_value.GetValue(),
                                    activate=self.email_checkbox.IsChecked())
            if get_filter_facade().change_email(filter_value) != False:
                self.do_modified(True)
        except Exception:
            self._regex_not_valid("email", self.email_value.GetValue())
        evt.Skip()

    def _regex_not_valid(self, attribute, expression):
        dlg = wx.MessageDialog(self, """Regular expression '%s' not valid.
See Info > Help for more information"""% expression,
                               "Error on %s"% attribute,
                               wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()

    def __set_properties(self):
        # begin wxGlade: PersonalFilterPanel.__set_properties
        self.title_value.Enable(False)
        self.title_value.SetSelection(0)
        self.firstname_value.Enable(False)
        self.lastname_value.Enable(False)
        self.pseudo_value.SetToolTipString(_("How you appear to other peers"))
        self.pseudo_value.Enable(False)
        self.email_value.Enable(False)
        self.add_p_filter_button.SetSize(self.add_p_filter_button.GetBestSize())
        self.del_p_filter_button.SetSize(self.del_p_filter_button.GetBestSize())
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: PersonalFilterPanel.__do_layout
        p_filter_sizer = wx.FlexGridSizer(3, 1, 0, 0)
        p_action_sizer = wx.StaticBoxSizer(self.p_action_sizer_staticbox, wx.HORIZONTAL)
        identity_sizer = wx.StaticBoxSizer(self.identity_sizer_staticbox, wx.VERTICAL)
        contact_sizer = wx.FlexGridSizer(3, 2, 3, 0)
        name_sizer = wx.FlexGridSizer(1, 6, 3, 3)
        name_sizer.Add(self.title_checkbox, 0, wx.ADJUST_MINSIZE, 0)
        name_sizer.Add(self.title_value, 0, wx.FIXED_MINSIZE, 0)
        name_sizer.Add(self.firstname_checkbox, 0, wx.ADJUST_MINSIZE, 0)
        name_sizer.Add(self.firstname_value, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        name_sizer.Add(self.lastname_checkbox, 0, wx.ADJUST_MINSIZE, 0)
        name_sizer.Add(self.lastname_value, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        name_sizer.AddGrowableCol(3)
        name_sizer.AddGrowableCol(5)
        identity_sizer.Add(name_sizer, 0, wx.EXPAND, 0)
        contact_sizer.Add(self.pseudo_checkbox, 0, wx.ADJUST_MINSIZE, 0)
        contact_sizer.Add(self.pseudo_value, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        contact_sizer.Add(self.email_checkbox, 0, wx.ADJUST_MINSIZE, 0)
        contact_sizer.Add(self.email_value, 0, wx.EXPAND|wx.FIXED_MINSIZE, 0)
        contact_sizer.AddGrowableCol(1)
        identity_sizer.Add(contact_sizer, 0, wx.TOP|wx.EXPAND, 3)
        p_filter_sizer.Add(identity_sizer, 0, wx.EXPAND, 0)
        p_action_sizer.Add(self.p_key_value, 1, wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 3)
        p_action_sizer.Add(self.p_filter_value, 1, wx.ALL|wx.EXPAND|wx.FIXED_MINSIZE, 3)
        p_action_sizer.Add(self.add_p_filter_button, 0, wx.LEFT|wx.FIXED_MINSIZE, 3)
        p_action_sizer.Add(self.del_p_filter_button, 0, wx.FIXED_MINSIZE, 0)
        p_filter_sizer.Add(p_action_sizer, 0, wx.ALL|wx.EXPAND|wx.ALIGN_RIGHT, 3)
        p_filter_sizer.Add(self.p_filters_list, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(p_filter_sizer)
        p_filter_sizer.Fit(self)
        p_filter_sizer.SetSizeHints(self)
        p_filter_sizer.AddGrowableRow(2)
        p_filter_sizer.AddGrowableCol(0)
        # end wxGlade

# end of class PersonalFilterPanel


