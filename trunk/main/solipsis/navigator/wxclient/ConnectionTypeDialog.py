# -*- coding: UTF-8 -*-
# generated by wxGlade 0.4cvs on Wed May 18 15:09:46 2005

import wx

from solipsis.util.wxutils import _

# begin wxGlade: dependencies
# end wxGlade

class ConnectionTypeDialog(wx.Dialog):
    def __init__(self, config_data, *args, **kwds):
        self.config_data = config_data

        # begin wxGlade: ConnectionTypeDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.THICK_FRAME
        wx.Dialog.__init__(self, *args, **kwds)
        self.radio_btn_local = wx.RadioButton(self, -1, _("Launch a dedicated Solipsis node\non this computer."))
        self.label_local_port = wx.StaticText(self, -1, _("Use UDP port:"))
        self.text_ctrl_local_port = wx.TextCtrl(self, -1, "")
        self.radio_btn_remote = wx.RadioButton(self, -1, _("Connect using an existing Solipsis node\n(possibly on a remote computer):"))
        self.label_remote_host = wx.StaticText(self, -1, _("Host:"))
        self.text_ctrl_remote_host = wx.TextCtrl(self, -1, "")
        self.label_remote_port = wx.StaticText(self, -1, _("Port:"))
        self.text_ctrl_remote_port = wx.TextCtrl(self, -1, "")
        self.button_close = wx.Button(self, wx.ID_CLOSE, "")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioLocal, self.radio_btn_local)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadioRemote, self.radio_btn_remote)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=wx.ID_CLOSE)
        # end wxGlade

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Initialize UI values
        conntype = self.config_data.connection_type
        self.radio_btn_local.SetValue(conntype == 'local')
        self.radio_btn_remote.SetValue(conntype == 'remote')
        self.text_ctrl_local_port.SetValue(str(self.config_data.solipsis_port))
        self.text_ctrl_remote_host.SetValue(self.config_data.host)
        self.text_ctrl_remote_port.SetValue(str(self.config_data.port))
        self._UpdateUI()

    def __set_properties(self):
        # begin wxGlade: ConnectionTypeDialog.__set_properties
        self.SetTitle(_("Connection type"))
        self.text_ctrl_remote_host.SetMinSize((160, -1))
        self.text_ctrl_remote_host.SetToolTipString(_("Name or IP address of the machine on which the node is running"))
        self.button_close.SetDefault()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ConnectionTypeDialog.__do_layout
        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_11 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6.Add(self.radio_btn_local, 0, wx.ALL|wx.EXPAND, 3)
        sizer_7.Add((30, 5), 0, wx.ADJUST_MINSIZE, 0)
        sizer_7.Add(self.label_local_port, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_7.Add(self.text_ctrl_local_port, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_6.Add(sizer_7, 0, wx.EXPAND, 0)
        sizer_6.Add(self.radio_btn_remote, 0, wx.ALL, 3)
        sizer_8.Add((30, 5), 0, wx.ADJUST_MINSIZE, 0)
        sizer_10.Add(self.label_remote_host, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_10.Add(self.text_ctrl_remote_host, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_9.Add(sizer_10, 1, wx.EXPAND, 0)
        sizer_11.Add(self.label_remote_port, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_11.Add(self.text_ctrl_remote_port, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_9.Add(sizer_11, 1, wx.EXPAND, 0)
        sizer_8.Add(sizer_9, 1, wx.EXPAND, 0)
        sizer_6.Add(sizer_8, 0, wx.EXPAND, 0)
        sizer_6.Add(self.button_close, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 3)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_6)
        sizer_6.Fit(self)
        sizer_6.SetSizeHints(self)
        self.Layout()
        self.Centre()
        # end wxGlade

    #
    # Event handlers
    #
    def OnRadioLocal(self, event): # wxGlade: ConnectionTypeDialog.<event_handler>
        wx.CallAfter(self._UpdateUI)

    def OnRadioRemote(self, event): # wxGlade: ConnectionTypeDialog.<event_handler>
        wx.CallAfter(self._UpdateUI)

    def OnClose(self, event): # wxGlade: ConnectionTypeDialog.<event_handler>
        if self._Validate():
            self._Apply()
            self.EndModal(wx.ID_OK)
        else:
            dialog = wx.MessageDialog(self,
                message=_("Some parameters have wrong values.\nPlease enter proper values."),
                caption=_("Error"),
                style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()

    #
    # Private methods
    #
    def _ValidatePort(self, text):
        try:
            p = int(text)
        except ValueError:
            return False
        return p > 0 and p < 65536

    def _Validate(self):
        if self.radio_btn_local.GetValue():
            if not self._ValidatePort(self.text_ctrl_local_port.GetValue()):
                return False
        if self.radio_btn_remote.GetValue():
            if not self._ValidatePort(self.text_ctrl_remote_port.GetValue()):
                return False
        return True

    def _UpdateUI(self):
        # Enable sub-parameters based on radio button choice
        enable = self.radio_btn_local.GetValue()
        self.text_ctrl_local_port.Enable(enable=enable)
        enable = self.radio_btn_remote.GetValue()
        self.text_ctrl_remote_host.Enable(enable=enable)
        self.text_ctrl_remote_port.Enable(enable=enable)
        
        # Adapt dialog size
        self.Layout()
        self.SetSize(self.GetBestVirtualSize())
    
    def _Apply(self):
        if self.radio_btn_local.GetValue():
            self.config_data.connection_type = 'local'
            self.config_data.solipsis_port = int(self.text_ctrl_local_port.GetValue())
        elif self.radio_btn_remote.GetValue():
            self.config_data.connection_type = 'remote'
            self.config_data.host = str(self.text_ctrl_remote_host.GetValue())
            self.config_data.port = int(self.text_ctrl_remote_port.GetValue())


# end of class ConnectionTypeDialog
