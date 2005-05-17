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
    """This the working class for services plugins."""

    
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
        # peer_ip: connector
        self.peers = {}
        # declare actions
        self.MAIN_ACTION = {"Modify ...": self.modify_profile,}
        self.POINT_ACTIONS = {"Get profile": self.get_profile,
                              "Get files...": self.get_files,
                              "Send profile": self.send_profile,
                              }

    # Service setup

    # FIXME: need to abstract action layer of plugins so that it does
    # not depend on navigator mode (in our case: netclient or
    # wxclient)
    def EnableBasic(self):
        """enable non graphic part"""
        pass
        
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
        for action, method in self.MAIN_ACTION.iteritems():
            item_id = wx.NewId()
            menu.Append(item_id, _(action))
            def _clicked(event):
                method()
            wx.EVT_MENU(main_window, item_id, _clicked)
        self.service_api.SetMenu(self.GetTitle(), menu)
    
    def Disable(self):
        """It is called when the user chooses to disable the service."""
        pass

    # Service methods
    def modify_profile(self):
        pass
    
    def get_profile(self, peer_id):
        pass

    def get_files(self, peer_id):
        pass

    def send_profile(self, peer_id):
        pass

    # Service description methods
    def GetTitle(self):
        """Returns a short title of the plugin."""
        return _("Profile")

    def GetDescription(self):
        """Returns a short description of the plugin. """
        return _("Manage personal information and share it with people")

    def GetActions(self):
        """Returns an array of strings advertising possible actions
        with all peers, or None if no such action is allowed.
        """
        return [_(desc) for desc in self.MAIN_ACTION]

    def GetPointToPointActions(self):
        """Returns an array of strings advertising point-to-point
        actions with another peer, or None if point-to-point actions
        are not allowed.
        """
        return [_(desc) for desc in self.POINT_ACTIONS]

    def DescribeService(self, service):
        """
        Fills the Service object used to describe the service to other peers.
        """
        service.address = "%s:%d" % (self.host, self.port)

    # UI event responses
    def DoAction(self, it):
        """Called when the general action is invoked, if available."""
        print "Profile: DoAction", it

    def DoPointToPointAction(self, it, peer):
        """Called when a point-to-point action is invoked, if available."""
        print "Profile: DoPointToPointAction", it, peer.id_

    # Peer management
    def NewPeer(self, peer, service):
        # probe its server (service.address)
        pass

    def ChangedPeer(self, peer, service):
        pass

    def LostPeer(self, peer_id):
        print "Profile: LostPeer", peer_id

    def ChangedNode(self, node):
        pass

    def GotServiceData(self, peer_id, data):
        print "Profile: GotServiceData", peer_id, data
