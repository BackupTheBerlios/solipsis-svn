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
    
    def Init(self):
        """
        Please override this method to do any kind of concrete initialization
        stuff, rather than doing it in __init__.
        Especially, the service_api must *not* be used in __init__, since 
        all data relating to the plugin may not have been initialized on the
        API side.
        """
        pass

    #
    # Service description methods
    #

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

    def GetAction(self):
        """
        Returns a string advertising an action with all peers,
        or None if no such action is allowed.
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
        Returns the file name of an icon representing the plugin.
        There should be at least a 16x16 icon (for pop-up menus).
        """
        raise NotImplementedError
    
    def DescribeService(self, service):
        """
        Fills the Service object used to describe the service to other peers.
        """
        raise NotImplementedError

    #
    # Service setup
    #

    def Enable(self):
        """
        All real actions involved in initializing the service should be
        defined here, not in the constructor.
        This includes e.g. opening sockets, collecting data from directories, etc.
        """
        raise NotImplementedError
    
    def Disable(self):
        """
        This routine should invalidate all actions take in the Enable() method.
        It is called when the user chooses to disable the service.
        """
        raise NotImplementedError

    #
    # UI event responses
    #
    
    def DoAction(self):
        """
        Called when the general action is invoked, if available.
        """
        raise NotImplementedError

    def DoPointToPointAction(self, peer):
        """
        Called when a point-to-point action is invoked, if available.
        """
        raise NotImplementedError

    #
    # Peer management
    #

    def NewPeer(self, peer, service):
        """
        Called when a new peer bearing the service appears.
        """
        raise NotImplementedError

    def ChangedPeer(self, peer, service):
        """
        Called when a peer bearing the service is changed.
        """
        raise NotImplementedError

    def LostPeer(self, peer_id):
        """
        Called when a peer bearing the service disappears.
        """
        raise NotImplementedError

    def ChangedNode(self, node):
        """
        Called when the node has changed.
        """
        raise NotImplementedError

    def GotServiceData(self, peer_id, data):
        """
        Called when some service-specific data has been received.
        """
        raise NotImplementedError
