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

import wx
import copy

from solipsis.util.utils import ManagedData, CreateSecureId
from solipsis.navigator.wxclient.bookmarks import BookmarkList
from solipsis.navigator.config import BaseConfigData

class ConfigData(BaseConfigData):
    """
    This class holds all configuration values that are settable from
    the user interface.
    """

    # These are the configuration variables that can be changed on a
    # per-identity basis
    identity_vars = BaseConfigData.identity_vars \
                    + ['bookmarks']

    def __init__(self, params=None):
        BaseConfigData.__init__(self, params)

        # 1. User-defined bookmarks
        self.bookmarks = BookmarkList()

        # Override languages
        lang_code = wx.Locale.GetLanguageInfo(
            wx.Locale.GetSystemLanguage()).CanonicalName
        if lang_code:
            self.languages = [str(lang_code.split('_')[0])]

        # 99. Identities
        self.identities = []
        self.current_identity = -1
        # Store current identity as default one
        self.CreateIdentity()
        self.StoreCurrentIdentity()


    # OVERRIDEN METHODS
    # -----------------
    def Compute(self):
        """
        Compute some "hidden" or temporary configuration values 
        (e.g. HTTP proxy auto-configuration URL).
        """
        self.StoreCurrentIdentity()
        BaseConfigData.Compute(self)

    def _Load(self, infile):
        """
        Restore configuration from a readable file object.
        """
        BaseConfigData._Load(self, infile)
        self.StoreCurrentIdentity()

    def Save(self, outfile):
        """
        Store configuration in a writable file object.
        """
        self.StoreCurrentIdentity()
        BaseConfigData.Save(self, outfile)

    def GetNode(self):
        """
        Get the object representing the node (i.e. ourselves).
        """
        node = BaseConfigData.GetNode(self)
        return node


    # SPECIFIC METHODS
    # ----------------
    def CreateIdentity(self):
        """
        Creates a new identity and returns its index number.
        """
        identity = {}
        for var in self.identity_vars:
            identity[var] = copy.deepcopy(getattr(self, var))
        # We generate a new node ID for each identity
        self.node_id = identity['node_id'] = CreateSecureId()
        self.identities.append(identity)
        self.current_identity = len(self.identities) - 1
        return self.current_identity

    def StoreCurrentIdentity(self):
        """
        Stores current config values in current identity.
        """
        identity = self.identities[self.current_identity]
        for var in self.identity_vars:
            identity[var] = copy.deepcopy(getattr(self, var))
        # If the identity does not already have a node ID, create one
        if not identity['node_id']:
            identity['node_id'] = CreateSecureId()

    def LoadIdentity(self, index):
        """
        Loads another identity into current config values.
        """
        self.StoreCurrentIdentity()
        self.current_identity = index
        identity = self.identities[self.current_identity]
        for var in self.identity_vars:
            try:
                setattr(self, var, copy.deepcopy(identity[var]))
                #~ print var, getattr(self, var)
            except KeyError:
                setattr(self, var, copy.deepcopy(getattr(self, var)))
        self._Notify()

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
            try:
                setattr(self, var, copy.deepcopy(identity[var]))
            except KeyError:
                pass
        self._Notify()
        return True

    def GetIdentities(self):
        """
        Get a list of all identities as dictionaries containing config values,
        ordered according to their index number.
        You should not try to modify these values, or unexpected things can happen.
        """
        configs = []
        for identity in self.identities:
            config = {}
            for var in self.identity_vars:
                try:
                    config[var] = identity[var]
                except KeyError:
                    config[var] = getattr(self, var)
            configs.append(config)
        return configs

    def GetCurrentIdentity(self):
        """
        Returns the index of the current identity.
        """
        return self.current_identity
