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
"""main class for plugin. Allow 'plug&Play' into navigator"""

import socket
import random
import wx

from solipsis.util.wxutils import _
from solipsis.services.plugin import ServicePlugin

class Plugin(ServicePlugin):
    """
    This the working class for services plugins. The plugin is the class that
    communicates with the navigator core. It MUST be named 'Plugin'.
    """
    
    def Init(self):
        """
        This method does any kind of concrete initialization stuff,
        rather than doing it in __init__.  Especially, the service_api
        must *not* be used in __init__, since all data relating to the
        plugin may not have been initialized on the API side.
        """
        # TODO: smartly discover our own address IP
        # (this is where duplicated code starts to appear...)
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = random.randrange(7000, 7100)
        self.profile = None

    #
    # Service description methods
    #

    def GetTitle(self):
        """
        Returns a short title of the plugin.
        (e.g. 'Chat', 'File transfer', etc.)
        """
        return _("Profile")

    def GetDescription(self):
        """
        Returns a short description of the plugin.  (e.g. 'talk with
        people around you', 'send or receive files and documents')
        """
        return _("Manage personal information and share it with people")

    def GetActions(self):
        """
        Returns an array of strings advertising possible actions with
        all peers, or None if no such action is allowed.
        """
        # TODO: what about a dictionary mapping function to be
        # called. This would easier DoAction...  Drawback: what about
        # complex menus... dictonary to include a function to create
        # item?
        return [_("Modify ..."),
                _("Add files ..."),
                _("Delete files ..."),
                _("Search ..."),]

    def GetPointToPointActions(self):
        """
        Returns an array of strings advertising point-to-point actions
        with another peer, or None if point-to-point actions are not allowed.
        """
        return [_("Show info"),
                _("Request profile"),]

    def GetIcon(self, size):
        """
        Returns the file name of an icon representing the plugin.
        There should be at least a 16x16 icon (for pop-up menus).
        """
        return "images/icon.gif"
    
    def DescribeService(self, service):
        """
        Fills the Service object used to describe the service to other peers.
        """
        service.address = "%s:%d" % (self.host, self.port)

    #
    # Service setup
    #

    # FIXME: need to abstract action layer of plugins so that it does
    # not depend on navigator mode (in our case: netclient or
    # wxclient)
    def EnableBasic(self):
        """enable non graphic part"""
        pass
#         print "Profile: enable"
        
    def Enable(self):
        """
        All real actions involved in initializing the service should
        be defined here, not in the constructor.  This includes
        e.g. opening sockets, collecting data from directories, etc.
        """
        # Set up main GUI hooks
        main_window = self.service_api.GetMainWindow()
        menu = wx.Menu()
        # TODO: if GetActions returns dictionary, we could map
        # _clicked with the right function at once
        for index, action in enumerate(self.GetActions()):
            item_id = wx.NewId()
            menu.Append(item_id, action)
            def _clicked(event, it=index):
                self.DoAction(it)
            wx.EVT_MENU(main_window, item_id, _clicked)
        self.service_api.SetMenu(self.GetTitle(), menu)
    
    def Disable(self):
        """
        This routine should invalidate all actions take in the
        Enable() method.  It is called when the user chooses to
        disable the service.
        """
        pass
#         print "Profile: Disable"

    #
    # UI event responses
    #
    
    def DoAction(self, it):
        """
        Called when the general action is invoked, if available.
        """
        print "Profile: DoAction", it

    def DoPointToPointAction(self, it, peer):
        """
        Called when a point-to-point action is invoked, if available.
        """
        print "Profile: DoPointToPointAction", it, peer.id_

    #
    # Peer management
    #

    def NewPeer(self, peer, service):
        """
        Called when a new peer bearing the service appears.
        """
        print "Profile: NewPeer", service.address

    def ChangedPeer(self, peer, service):
        """
        Called when a peer bearing the service is changed.
        """
        pass

    def LostPeer(self, peer_id):
        """
        Called when a peer bearing the service disappears.
        """
        print "Profile: LostPeer", peer_id

    def ChangedNode(self, node):
        """
        Called when the node has changed.
        """
        pass
#         print "Profile: ChangedNode", node.id_

    def GotServiceData(self, peer_id, data):
        """
        Called when some service-specific data has been received.
        """
        print "Profile: GotServiceData", peer_id, data
