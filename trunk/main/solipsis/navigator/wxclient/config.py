# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>


import wx
from wx.xrc import XRCCTRL, XRCID

from solipsis.util.entity import Entity, Service
from solipsis.util.address import Address
from solipsis.util.wxutils import _, ManagedData


class ConfigData(ManagedData):
    """
    This class holds all configuration values that are settable from
    the user interface.
    """
    def __init__(self, host=None, port=None, pseudo=None):
        ManagedData.__init__(self)
        self.pseudo = pseudo or u"guest"
        self.host = host or "localhost"
        self.port = port or 8550
        self.always_try_without_proxy = True
        self.proxymode_auto = True
        self.proxymode_manual = False
        self.proxy_mode = ""
        self.proxy_pac_url = ""
        self.proxy_host = ""
        self.proxy_port = 0
        self.proxy_autodetect_done = False

    def Autocomplete(self):
        self.proxy_mode = self.proxymode_auto and "auto" or (
            self.proxymode_manual and "manual" or "none")
        if self.proxy_mode == "auto":
            from solipsis.util.httpproxy import discover_http_proxy
            proxy_host, proxy_port = discover_http_proxy()
            self.proxy_host = proxy_host or ""
            self.proxy_port = proxy_port or 0
            #~ print "detected proxy (%s, %d)" % (self.proxy_host, self.proxy_port)

    def GetNode(self):
        node = Entity()
        node.pseudo = self.pseudo
        lang_code = wx.Locale.GetLanguageInfo(wx.Locale.GetSystemLanguage()).CanonicalName
        if lang_code:
            node.languages = [ str(lang_code.split('_')[0]) ]
        # Dummy value to avoid None-marshaling
        node.address = Address()
        # Test data
        node.AddService(Service('chat', address='127.0.0.1:5555'))
        node.AddService(Service('video', address='127.0.0.1:6543'))
        return node


class ConfigUI(object):
    """
    This class handles the UI side of the configuration mechanism.
    """
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