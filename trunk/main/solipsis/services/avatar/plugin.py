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


class Plugin(ServicePlugin):

    def Init(self):
        self.reactor = self.service_api.GetReactor()
        # TODO: smartly discover our own address IP
        # (this is where duplicated code starts to appear...)
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = random.randrange(7100, 7200)
        self.hosts = {}

    def GetTitle(self):
        return _("Avatars")

    def GetDescription(self):
        return _("Exchange avatars to customize your appearance")

    def GetAction(self):
        return None

    def GetPointToPointAction(self):
        return None
    
    def DescribeService(self, service):
        service.address = "%s:%d" % (self.host, self.port)

    #
    # Here comes the real action
    #
    def Enable(self):
        # Set up avatar GUI
        dialog = ConfigDialog(self, self.service_api.GetDirectory())
        self.ui = UIProxy(dialog)
        # Set up main GUI hooks
        main_window = self.service_api.GetMainWindow()
        menu = wx.Menu()
        item_id = wx.NewId()
        menu.Append(item_id, _("&Configure"))
        wx.EVT_MENU(main_window, item_id, self._Configure)
        self.service_api.SetMenu(_("Avatar"), menu)

    def Disable(self):
        #~ self.network.Stop()
        #~ self.network = None
        self.ui.Destroy()
        self.ui = None

    def NewPeer(self, peer, service):
        try:
            host, port = self._ParseAddress(service.address)
        except ValueError:
            pass
        else:
            #~ self.ui.AddPeer(peer)
            self.hosts[peer.id_] = host, port

    def ChangedPeer(self, peer, service):
        try:
            host, port = self._ParseAddress(service.address)
        except ValueError:
            if peer.id_ in self.hosts:
                del self.hosts[peer.id_]
                #~ self.ui.RemovePeer(peer.id_)
                self._SetHosts()
        else:
            #~ self.ui.UpdatePeer(peer)
            self.hosts[peer.id_] = host, port

    def LostPeer(self, peer_id):
        if peer_id in self.hosts:
            del self.hosts[peer_id]
            #~ self.ui.RemovePeer(peer_id)
    
    def ChangedNode(self, node):
        pass
        #~ self.ui.RemovePeer(node.id_)
        #~ self.ui.AddPeer(node)
    
    def _Configure(self, evt):
        self.ui.Configure()

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
