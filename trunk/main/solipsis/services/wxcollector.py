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

import os
import wx

from collector import ServiceCollector

from solipsis.util.entity import Service
from solipsis.util.uiproxy import UIProxy
from solipsis.util.wxutils import GetCharset, IdPool


class WxServiceCollector(ServiceCollector):
    """
    This is a version of the ServiceCollector enhanced for use
    within a wxWidgets client.
    """
    def __init__(self, params, ui, reactor):
        self.app = ui
        self.main_window = ui.main_window
        self.ui = UIProxy(ui)
        self.charset = GetCharset()
        ServiceCollector.__init__(self, params, reactor)

    def Reset(self):
        self.action_ids = IdPool()
        super(WxServiceCollector, self).Reset()

    def InitService(self, service_id, plugin):
        # Initialize plugin-specific localization files
        path = self._ServiceDirectory(service_id)
        translation_dir = os.path.join(path, 'po')
        if os.path.isdir(translation_dir):
            locale = wx.GetLocale()
            locale.AddCatalogLookupPathPrefix(translation_dir)
            if not locale.AddCatalog("solipsis_%s" % service_id):
                print "Warning: failed to load translations for plugin '%s'" % service_id
        else:
            print "Warning: plugin \"%s\" has no translation directory" % service_id
    
        super(WxServiceCollector, self).InitService(service_id, plugin)

    def GetPopupMenuItems(self, menu, id_):
        """
        Get specific service items for the UI pop-up menu.
        """
        l = []
        self.action_ids.Begin()
        for service_id in self._Services():
            plugin = self.plugins[service_id]
            if id_ is not None:
                if self.peers[id_].GetService(service_id) is not None:
                    titles = plugin.GetPointToPointActions()
                else:
                    titles = []
            else:
                titles = plugin.GetActions()
            i = 0
            for title in titles:
                item_id = self.action_ids.GetId()
                item = wx.MenuItem(menu, item_id, title.encode(self.charset))
                def _clicked(evt, p=plugin, it = i ):
                    if id_ is not None:
                        p.DoPointToPointAction(it, self.peers[id_])
                    else:
                        p.DoAction(it)
                wx.EVT_MENU(self.main_window, item_id, _clicked)
                l.append(item)
                i += 1
        return l

    #
    # API callable from service plugins
    #
    def service_GetMainWindow(self, service_id):
        """
        Get the navigator main window (wxWindow object).
        """
        return self.main_window

    def service_SetMenu(self, service_id, title, menu):
        """
        Set service-specific menu in the navigator's menubar.
        """
        self.ui.SetServiceMenu(service_id, title, menu)

    def service_SendData(self, service_id, peer_id, data):
        """
        Send service-specific data using the Solipsis network.
        """
        self.ui.SendServiceData(peer_id, service_id, data)
