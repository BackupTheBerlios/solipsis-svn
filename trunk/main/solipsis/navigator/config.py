# pylint: disable-msg=C0103
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
"""base class for config. Contains all parameters but identities & bookmarks"""

import cPickle as pickle
import random

from solipsis.util.entity import Entity
from solipsis.util.address import Address
from solipsis.util.utils import ManagedData


class BaseConfigData(ManagedData):
    """
    This class holds all configuration values that are settable from
    the user interface.
    """
    # These are the configuration variables that can be changed on a
    # per-identity basis
    identity_vars = [ 'pseudo', 'host', 'port', 
                      'connection_type', 'solipsis_port', 'service_config',
                      #~ 'proxymode_auto', 'proxymode_manual',
                      #'proxymode_none', 'proxy_host', 'proxy_port',
                      ]

    def __init__(self, params=None):
        ManagedData.__init__(self)
        # Initialize all values
        # 1. Basic connection data
        self.pseudo = params and params.pseudo or u""
        self.host = "localhost"
        self.port = 8550
        self.connection_type = 'local'
        self.solipsis_port = 6010
        self.local_control_port_min = params and params.local_control_port_min \
                                      or 8501
        self.local_control_port_max = params and params.local_control_port_max \
                                      or 8599
        self.local_control_port = 0

        # 2. HTTP proxy configuration (for XMLRPC)
        self.proxymode_auto = True
        self.proxymode_manual = False
        self.proxymode_none = False
        self.proxy_mode = ""
        self.proxy_pac_url = ""
        self.proxy_host = ""
        self.proxy_port = 0
        
        # 3. Other preferences
        self.node_autokill = True
        self.multiple_identities = False

        # 4. Service-specific configuration data
        self.services = []
        self.service_config = {}

        # Callables for config change notification
        self._event_sinks = []

    def AskNotify(self, callback):
        """
        Ask to be notified when the configuration is changed.
        """
        self._event_sinks.append(callback)


    def Compute(self):
        """
        Compute some "hidden" or temporary configuration values 
        (e.g. HTTP proxy auto-configuration URL).
        """
        self.proxy_mode = self.proxymode_auto and "auto" or (
            self.proxymode_manual and "manual" or "none")
        if self.connection_type == "local":
            # Choose random control port for the local node we wish to launch
            self.local_control_port = random.randrange(
                self.local_control_port_min,
                self.local_control_port_max + 1)
        else:
            # If necessary, autodetect proxy address
            if self.proxy_mode == "auto":
                from solipsis.util.httpproxy import discover_http_proxy
                proxy_host, proxy_port = discover_http_proxy()
                self.proxy_host = proxy_host or ""
                self.proxy_port = proxy_port or 0

    def SetServices(self, services):
        """
        Set service list.
        """
        self.services = list(services)
    
    def SetServiceConfig(self, service_id, data):
        """
        Store service-specific configuration data.
        """
        self.service_config[service_id] = data
    
    def GetServiceConfig(self, service_id):
        """
        Retrieve service-specific configuration data.
        """
        try:
            return self.service_config[service_id]
        except KeyError:
            return None
    
    def _Load(self, infile):
        """
        Restore configuration from a readable file object.
        """
        loaded = pickle.load(infile)
        self.UpdateDict(loaded)
    
    def Load(self, infile):
        """
        Restore configuration from a readable file object.
        """
        self._Load(infile)
        self._Notify()

    def Save(self, outfile):
        """
        Store configuration in a writable file object.
        """
        config = self.GetDict()
        # Python < 2.4 compatibility:
        #     documentation for the cPickle module is partly wrong
        #~ pickle.dump(d, outfile, protocol=-1)
        pickle.dump(config, outfile, -1)

    def GetNode(self):
        """
        Get the object representing the node (i.e. ourselves).
        """
        node = Entity()
        node.pseudo = self.pseudo
        # Dummy value to avoid None-marshaling
        node.address = Address()
        # Test data
        for service in self.services:
            node.AddService(service)
        return node

    def _Notify(self):
        """
        Notify all event sinks that the config has been updated.
        """
        for sink in self._event_sinks:
            sink()
