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

import cPickle as pickle
import random
import wx
from wx.xrc import XRCCTRL, XRCID

from solipsis.util.entity import Entity, Service
from solipsis.util.address import Address
from solipsis.util.wxutils import _ 
from solipsis.util.utils import ManagedData

from bookmarks import BookmarkList


class ConfigData(ManagedData):
    """
    This class holds all configuration values that are settable from
    the user interface.
    """

    # These are the configuration variables that can be changed on a per-identity basis
    identity_vars = [ 'pseudo', 'host', 'port', 'connection_type', 'solipsis_port',
        #~ 'proxymode_auto', 'proxymode_manual', 'proxymode_none', 'proxy_host', 'proxy_port',
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
        self.local_control_port_min = params and params.local_control_port_min or 8501
        self.local_control_port_max = params and params.local_control_port_max or 8599
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

        # 5. User-defined bookmarks
        self.bookmarks = BookmarkList()
        
        # 99. Identities
        self.identities = []
        self.current_identity = -1
        # Store current identity as default one
        self.CreateIdentity()
        self.StoreCurrentIdentity()

    def CreateIdentity(self):
        """
        Creates a new identity and returns its index number.
        """
        identity = {}
        for var in self.identity_vars:
            identity[var] = getattr(self, var)
        self.identities.append(identity)
        self.current_identity = len(self.identities) - 1
        return self.current_identity
    
    def StoreCurrentIdentity(self):
        """
        Stores current config values in current identity.
        """
        identity = self.identities[self.current_identity]
        for var in self.identity_vars:
            identity[var] = getattr(self, var)
    
    def LoadIdentity(self, index):
        """
        Loads another identity into current config values.
        """
        self.StoreCurrentIdentity()
        self.current_identity = index
        identity = self.identities[self.current_identity]
        for var in self.identity_vars:
            setattr(self, var, identity[var])

    def RemoveCurrentIdentity(self):
        """
        Remove the current identity.
        Returns True if succeeded, False otherwise.
        The only possible cause of failure is if there is only one identity:
        it is forbidden to empty the identities list.
        """
        if len(self.identities) < 2:
            return False
        del self.identities[self.current_identity]
        if self.current_identity == len(self.identities):
            self.current_identity -= 1
        # Update config values for current identity
        identity = self.identities[self.current_identity]
        for var in self.identity_vars:
            setattr(self, var, identity[var])
        return True

    def GetIdentities(self):
        """
        Get a list of all identities as dictionaries containing config values,
        ordered according to their index number.
        """
        l = []
        for identity in self.identities:
            d = {}
            for var in self.identity_vars:
                d[var] = identity[var]
            l.append(d)
        return l
    
    def GetCurrentIdentity(self):
        """
        Returns the index of the current identity.
        """
        return self.current_identity

    def Compute(self):
        """
        Compute some "hidden" or temporary configuration values 
        (e.g. HTTP proxy auto-configuration URL).
        """
        self.StoreCurrentIdentity()
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
    
    def Load(self, infile):
        """
        Restore configuration from a readable file object.
        """
        d = pickle.load(infile)
        self.UpdateDict(d)
        self.StoreCurrentIdentity()
    
    def Save(self, outfile):
        """
        Store configuration in a writable file object.
        """
        self.StoreCurrentIdentity()
        #~ if len(self.identities) == 1:
            #~ self.CreateIdentity()
        d = self.GetDict()
        # Python < 2.4 compatibility: documentation for the cPickle module is partly wrong
        #~ pickle.dump(d, outfile, protocol=-1)
        pickle.dump(d, outfile, -1)

    def GetNode(self):
        """
        Get the object representing the node (i.e. ourselves).
        """
        node = Entity()
        node.pseudo = self.pseudo
        lang_code = wx.Locale.GetLanguageInfo(wx.Locale.GetSystemLanguage()).CanonicalName
        if lang_code:
            node.languages = [ str(lang_code.split('_')[0]) ]
        # Dummy value to avoid None-marshaling
        node.address = Address()
        # Test data
        for s in self.services:
            node.AddService(s)
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
