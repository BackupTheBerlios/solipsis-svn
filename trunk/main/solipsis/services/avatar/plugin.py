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

import socket
import wx
import random

from solipsis.util.wxutils import _
from solipsis.util.uiproxy import TwistedProxy, UIProxy
from solipsis.services.plugin import ServicePlugin

from gui import ConfigDialog
from network import NetworkLauncher
from repository import AvatarRepository


class Plugin(ServicePlugin):
    avatar_size_step = 12

    def Init(self):
        self.avatars = AvatarRepository()
        self.reactor = self.service_api.GetReactor()
        # TODO: smartly discover our own address IP
        # (this is where duplicated code starts to appear...)
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 7780 + random.randrange(0,100)
        self.hosts = {}
        self.node_avatar_hash = None

    def GetTitle(self):
        return _("Avatars")

    def GetDescription(self):
        return _("Exchange avatars to customize your appearance")

    def GetActions(self):
        return []

    def GetPointToPointActions(self):
        return []
    
    def DescribeService(self, service):
        service.address = "%s:%d" % (self.host, self.port)

    #
    # Here comes the real action
    #
    def Enable(self):
        """
        Enable the service.
        """
        # Set up avatar GUI
        dialog = ConfigDialog(self, self.service_api.GetDirectory())
        self.ui = UIProxy(dialog)
        # Set up main GUI hooks
        main_window = self.service_api.GetMainWindow()
        menu = wx.Menu()
        item_id = wx.NewId()
        menu.Append(item_id, _("&Configure"))
        wx.EVT_MENU(main_window, item_id, self.Configure)
        item_id = wx.NewId()
        menu.Append(item_id, _("Stretch avatars\tCtrl+M"))
        wx.EVT_MENU(main_window, item_id, self.StretchAvatars)
        item_id = wx.NewId()
        menu.Append(item_id, _("Shrink avatars\tCtrl+-"))
        wx.EVT_MENU(main_window, item_id, self.ShrinkAvatars)
        self.service_api.SetMenu(_("Avatar"), menu)
        # Set up network handler
        network = NetworkLauncher(self.reactor, self, self.port)
        self.network = TwistedProxy(network, self.reactor)
        # Start network
        self.network.Start()

    def Disable(self):
        """
        Disable the service.
        """
        self.network.Stop()
        self.network = None
        self.ui.Destroy()
        self.ui = None

    def NewPeer(self, peer, service):
        try:
            host, port = self._ParseAddress(service.address)
        except ValueError:
            pass
        else:
            self.hosts[peer.id_] = host, port
            if self.node_avatar_hash is not None:
                self.service_api.SendData(peer.id_, self.node_avatar_hash)

    def ChangedPeer(self, peer, service):
        try:
            host, port = self._ParseAddress(service.address)
        except ValueError:
            if peer.id_ in self.hosts:
                del self.hosts[peer.id_]
        else:
            self.hosts[peer.id_] = host, port

    def LostPeer(self, peer_id):
        if peer_id in self.hosts:
            del self.hosts[peer_id]
    
    def ChangedNode(self, node):
        pass
    
    def Configure(self, evt=None):
        """
        Called when the "Configure" action is selected.
        """
        # The result of the Configure() method will be passed
        # to the callback, if successful.
        # This is because self.ui goes through an asynchronous proxy.
        def _configured(filename):
            self.network.SetFile(filename)
            node_id = self.service_api.GetNode().id_
            data = file(filename, "rb").read()
            # Add the avatar to the repository, and send its hash to all peers
            self.node_avatar_hash = self.avatars.BindAvatarToPeer(data, node_id)
            for peer_id in self.hosts.keys():
                self.service_api.SendData(peer_id, self.node_avatar_hash)

        self.ui.Configure(callback=_configured)

    def StretchAvatars(self, evt=None):
        """
        Called when the "Stretch Avatars" action is selected.
        """
        s = self.avatars.GetProcessedAvatarSize()
        self.avatars.SetProcessedAvatarSize(s + self.avatar_size_step)

    def ShrinkAvatars(self, evt=None):
        """
        Called when the "Shrink Avatars" action is selected.
        """
        s = self.avatars.GetProcessedAvatarSize()
        if s > self.avatar_size_step:
            self.avatars.SetProcessedAvatarSize(s - self.avatar_size_step)

    def GotServiceData(self, peer_id, hash_):
        """
        Called when another peer sent its avatar hash.
        """
        if not self.avatars.BindHashToPeer(hash_, peer_id):
            def _got_avatar(data):
                self.avatars.BindAvatarToPeer(data, peer_id)
            def _failed(error):
                print "failed getting avatar from '%s': %s" % (peer_id, str(error))
            host, port = self.hosts[peer_id]
            self.network.GetPeerFile(host, port, _got_avatar, _failed)

    #
    # Private methods
    #

    def _ParseAddress(self, address):
        try:
            t = address.split(':')
            if len(t) != 2:
                raise ValueError
            host = str(t[0]).strip()
            port = int(t[1])
            if not host:
                raise ValueError
            if port < 1 or port > 65535:
                raise ValueError
            return host, port
        except ValueError:
            #~ print "Wrong avatar address '%s'" % address
            raise
