

import wx
from wx.xrc import XRCCTRL, XRCID

from solipsis.util.wxutils import _


class ConfigUI(object):
    def __init__(self, config_data, prefs_dialog):
        self.config_data = config_data
        self.prefs_dialog = prefs_dialog
        self.proxy_host_ctrl = XRCCTRL(self.prefs_dialog, "proxy_host")
        self.proxy_port_ctrl = XRCCTRL(self.prefs_dialog, "proxy_port")
        if self.config_data.proxymode_manual:
            self._EnableManualProxy()
        else:
            self._DisableManualProxy()

        # Setup UI events
        wx.EVT_CLOSE(self.prefs_dialog, self._ClosePrefs)
        wx.EVT_BUTTON(self.prefs_dialog, XRCID("prefs_close"), self._ClosePrefs)
        wx.EVT_RADIOBUTTON(self.prefs_dialog, XRCID("proxymode_auto"), self._AutoProxy)
        wx.EVT_RADIOBUTTON(self.prefs_dialog, XRCID("proxymode_manual"), self._ManualProxy)
        wx.EVT_RADIOBUTTON(self.prefs_dialog, XRCID("proxymode_none"), self._NoProxy)

    def _AutoProxy(self, evt):
        self._DisableManualProxy()

    def _ManualProxy(self, evt):
        self._EnableManualProxy()

    def _NoProxy(self, evt):
        self._DisableManualProxy()

    def _EnableManualProxy(self):
        self.proxy_host_ctrl.Enable()
        self.proxy_port_ctrl.Enable()

    def _DisableManualProxy(self):
        self.proxy_host_ctrl.Disable()
        self.proxy_port_ctrl.Disable()

    #
    # Event handlers for the preferences dialog
    #
    def _ClosePrefs(self, evt):
        """ Called on close "preferences dialog" event. """
        if (self.prefs_dialog.Validate()):
            self.prefs_dialog.Hide()
