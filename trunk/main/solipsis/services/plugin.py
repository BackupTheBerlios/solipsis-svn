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


class ServicePlugin(object):
    """
    This the base class for services plugins. The plugin is the class that
    communicates with the navigator core.
    Each plugin should subclass this class and implement the required methods.
    """
    def __init__(self, service_api):
        """
        Builds the plugin object.
        The service_api provides a set of methods to the plugin so that
        it can query some useful objects and information.
        """
        self.service_api = service_api
    
    def GetTitle(self):
        """
        Returns a short title of the plugin.
        (e.g. "Chat", "File transfer", etc.)
        """
        raise NotImplementedError

    def GetDescription(self):
        """
        Returns a short description of the plugin.
        (e.g. "talk with people around you", "send or receive files and documents")
        """
        raise NotImplementedError

    def GetPointToPointAction(self):
        """
        Returns a string advertising a point-to-point action
        with another peer, or None if point-to-point actions are not allowed.
        """
        raise NotImplementedError

    def GetIcon(self, size):
        """
        Returns an icon representing the plugin.
        The standard size in pixels should be 24x24.
        """
        raise NotImplementedError

    def NewPeer(self, peer):
        raise NotImplementedError

    def ChangedPeer(self, peer):
        raise NotImplementedError

    def LostPeer(self, peer_id):
        raise NotImplementedError
