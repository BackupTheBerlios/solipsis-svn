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
import os.path
import wx

try:
    set
except:
    from sets import Set as set

from solipsis.util.uiproxy import UIProxy
from solipsis.util.wxutils import _, GetCharset, IdPool


# Helper (see Python documentation for built-in function __import__)
def _import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


class ServiceCollector(object):
    """
    The service collector detects and initializes all available services.
    It also handles dispatching and collecting data to/from service plugins.
    """
    class ServiceAPI(object):
        def __init__(self, collector, service_id):
            self.target = collector
            self.service_id = service_id
        def __getattr__(self, name):
            meth = getattr(self.target, 'service_' + name)
            def fun(*args, **kargs):
                return meth(self.service_id, *args, **kargs)
            setattr(self, name, fun)
            return fun

    def __init__(self, params, ui, reactor):
        self.params = params
        self.wxApp = ui
        self.ui = UIProxy(ui)
        self.reactor = reactor
        self.dir = self.params.services_dir
        self.charset = GetCharset()
        self.Reset()

    def Reset(self):
        self.plugins = {}
        self.peers = {}
        self.action_ids = IdPool()

    def ReadServices(self):
        """
        Read available services from the service directory.
        """
        l = os.listdir(self.dir)
        for f in l:
            if f.startswith('.') or f.startswith('_'):
                continue
            path = os.path.join(self.dir, f)
            if not os.path.isdir(path):
                continue
            self.LoadService(path, f)

    def LoadService(self, path, name):
        """
        Load a service plugin, register it and initialize it.
        """
        plugin_file = os.path.join(path, 'plugin.py')
        assert os.path.isfile(plugin_file), "Bad service plug-in: %s" % plugin_file
        print "Loading service '%s'..." % name
        plugin_module = _import('solipsis.services.%s.plugin' %name)
        api = self.ServiceAPI(self, name)
        plugin = plugin_module.Plugin(api)
        self.plugins[name] = plugin
        # When plugin.Init() is called, everything else should have been
        # properly initialized for the plugin to interact with it.
        plugin.Init()
        plugin.Enable()

    def GetPopupMenuItems(self, menu):
        """
        Get specific service items for the UI pop-up menu.
        """
        l = []
        self.action_ids.Begin()
        for service_id in self._Services():
            plugin = self.plugins[service_id]
            title = plugin.GetAction()
            if title is not None:
                item_id = self.action_ids.GetId()
                item = wx.MenuItem(menu, item_id, title.encode(self.charset))
                def _clicked(evt):
                    plugin.DoAction()
                wx.EVT_MENU(self.wxApp, item_id, _clicked)
                l.append(item)
        return l

    def AddPeer(self, peer):
        """
        Called when a peer has appeared.
        """
        peer_id = peer.id_
        self.peers[peer_id] = peer
        # Notify the new peer to interested plugins
        services = peer.GetServices()
        for service in services:
            try:
                plugin = self.plugins[service.id_]
            except KeyError:
                pass
            else:
                plugin.NewPeer(peer, service)

    def UpdatePeer(self, peer):
        """
        Called when a peer has changed.
        """
        peer_id = peer.id_
        old_peer = self.peers[peer_id]
        self.peers[peer_id] = peer
        # Compare the peer's old services to its new ones...
        new_ids = set([_service.id_ for _service in peer.GetServices()])
        old_ids = set([_service.id_ for _service in old_peer.GetServices()])
        # Notify removed services
        for service_id in old_ids - new_ids:
            try:
                plugin = self.plugins[service_id]
            except KeyError:
                pass
            else:
                plugin.LostPeer(peer_id)
        # Notify added services
        for service_id in new_ids - old_ids:
            try:
                plugin = self.plugins[service_id]
            except KeyError:
                pass
            else:
                plugin.NewPeer(peer, peer.GetService(service_id))
        # Notify updated services
        for service_id in new_ids & old_ids:
            try:
                plugin = self.plugins[service_id]
            except KeyError:
                pass
            else:
                plugin.ChangedPeer(peer, peer.GetService(service_id))

    def RemovePeer(self, peer_id):
        """
        Called when a peer has disappeared.
        """
        try:
            peer = self.peers.pop(peer_id)
        except KeyError:
            return
        # Notify the removed peer to interested plugins
        services = peer.GetServices()
        for service in services:
            try:
                plugin = self.plugins[service.id_]
            except KeyError:
                pass
            else:
                plugin.LostPeer(peer_id)

    #
    # API callable from service plugins
    #
    def service_SetMenu(self, service_id, title, menu):
        """
        Set service-specific menu in the navigator's menubar.
        """
        print "setting menu '%s' for service '%s'" % (title, service_id)
        self.ui.SetServiceMenu(service_id, title, menu)

    def service_GetReactor(self, service_id):
        """
        Get the Twisted reactor object.
        """
        return self.reactor

    #
    # Private methods
    #
    def _Services(self):
        """
        List of services (sorted by id).
        """
        l = self.plugins.keys()
        l.sort()
        return l