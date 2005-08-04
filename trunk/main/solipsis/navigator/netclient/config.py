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

from solipsis.navigator.config import BaseConfigData


class ConfigData(BaseConfigData):
    """
    This class holds all configuration values that are settable from
    the user interface.
    """

    # These are the configuration variables that can be changed on a
    # per-identity basis
    identity_vars = BaseConfigData.identity_vars \
                    + ["services", "testing"]

    def __init__(self, params=None):
        BaseConfigData.__init__(self, params)
        self.used_services = params and params.services or []
        self.testing = params and params.testing or False
