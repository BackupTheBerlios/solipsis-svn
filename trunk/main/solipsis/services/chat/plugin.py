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

import random
import wx
import socket

from solipsis.util.wxutils import _
from solipsis.util.uiproxy import TwistedProxy, UIProxy
from solipsis.services.plugin import ServicePlugin

from network import NetworkLauncher
from gui import ChatWindow


class Plugin(ServicePlugin):
    str_action = "Chat with all peers"

    def Init(self):
        self.reactor = self.service_api.GetReactor()
        # TODO: smartly discover our own address IP
        # (this is where duplicated code starts to appear...)
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = random.randrange(7000, 7100)
        self.hosts = {}

    def GetTitle(self):
        return _("Chat")

    def GetDescription(self):
        return _("Talk with the people that are currently around you")

    def GetAction(self):
        return _(self.str_action)

    def GetPointToPointAction(self):
        return None
    
    def DescribeService(self, service):
        service.address = "%s:%d" % (self.host, self.port)

    #
    # Here comes the real action
    #
    def Enable(self):
        # Set up chat GUI
        window = ChatWindow(self, self.service_api.GetDirectory())
        main_window = self.service_api.GetMainWindow()
        self.ui = UIProxy(window)
        #~ self.ui.AddPeer(self.service_api.GetNode())
        # Set up network connection
        #~ n = NetworkLauncher(self.reactor, self, self.port)
        #~ self.network = TwistedProxy(n, self.reactor)
        #~ self.network.Start(self.GotMessage)
        self._SetHosts()
        # Set up main GUI hooks
        menu = wx.Menu()
        item_id = wx.NewId()
        menu.Append(item_id, _(self.str_action))
        wx.EVT_MENU(main_window, item_id, self.DoAction)
        self.service_api.SetMenu(_("Chat"), menu)

    def Disable(self):
        #~ self.network.Stop()
        #~ self.network = None
        self.ui.Destroy()
        self.ui = None

    def DoAction(self, evt=None):
        self.ui.Show()
    
    #~ def GotMessage(self, text, (host, port)):
        #~ # This method is called in network context (i.e. Twisted thread)
        #~ self.ui.AppendMessage(text)
    
    def SendMessage(self, text):
        # This method is called in UI context (i.e. wx Thread)
        #~ self.network.SendMessage(text)
        data = text
        for peer_id in self.hosts.keys():
            self.service_api.SendData(peer_id, data)
        self.ui.AppendSelfMessage(self.service_api.GetNode().id_, text)

    def GotServiceData(self, peer_id, data):
        # This method is called in network context (i.e. Twisted thread)
        self.ui.AppendMessage(peer_id, data)
    
    def NewPeer(self, peer, service):
        try:
            host, port = self._ParseAddress(service.address)
        except ValueError:
            pass
        else:
            self.ui.AddPeer(peer)
            self.hosts[peer.id_] = host, port
            self._SetHosts()

    def ChangedPeer(self, peer, service):
        try:
            host, port = self._ParseAddress(service.address)
        except ValueError:
            if peer.id_ in self.hosts:
                del self.hosts[peer.id_]
                self.ui.RemovePeer(peer.id_)
                self._SetHosts()
        else:
            self.ui.UpdatePeer(peer)
            self.hosts[peer.id_] = host, port
            self._SetHosts()

    def LostPeer(self, peer_id):
        if peer_id in self.hosts:
            del self.hosts[peer_id]
            self.ui.RemovePeer(peer_id)
            self._SetHosts()
    
    def ChangedNode(self, node):
        self.ui.RemovePeer(node.id_)
        self.ui.AddPeer(node)

    def _SetHosts(self):
        # For test purposes, chat with ourselves ;)
        hosts = self.hosts.values()
        hosts.append((self.host, self.port))
        #~ self.network.SetHosts(hosts)

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
            #~ print "Wrong chat address '%s'" % address
            raise
