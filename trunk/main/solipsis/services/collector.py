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

from solipsis.util.uiproxy import UIProxy

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
                meth(self.service_id, *args, **kargs)
            setattr(self, name, fun)
            return fun

    def __init__(self, params, ui):
        self.params = params
        self.ui = UIProxy(ui)
        self.dir = self.params.services_dir
        self.Reset()

    def Reset(self):
        self.plugins = {}

    def ReadServices(self):
        l = os.listdir(self.dir)
        for f in l:
            if f.startswith('.') or f.startswith('_'):
                continue
            path = os.path.join(self.dir, f)
            if not os.path.isdir(path):
                continue
            self.LoadService(path, f)

    def LoadService(self, path, name):
        plugin_file = os.path.join(path, 'plugin.py')
        assert os.path.isfile(plugin_file), "Bad service plug-in: %s" % plugin_file
        print "Loading service '%s'..." % name
        plugin_module = _import('solipsis.services.%s.plugin' %name)
        api = self.ServiceAPI(self, name)
        plugin = plugin_module.Plugin(api)
        plugin.Enable()
        self.plugins[name] = plugin

    def NewPeer(self, peer):
        pass

    def ChangedPeer(self, peer):
        pass
    
    def LostPeer(self, peer_id):
        pass
    
    #
    # API callable from service plugins
    #
    def service_SetMenu(self, service_id, title, menu):
        print "setting menu '%s' for service '%s'" % (title, service_id)
        self.ui.SetServiceMenu(service_id, title, menu)
