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
    def Init(self):
        self.reactor = self.service_api.GetReactor()
        self.port = random.randrange(7000, 7100)
        self.hosts = {}

    def GetTitle(self):
        return _("Chat")

    def GetDescription(self):
        return _("Talk with the people that are currently around you")

    def GetAction(self):
        return _("Chat with all peers")

    def GetPointToPointAction(self):
        return None
    
    def DescribeService(self, service):
        # TODO: smartly discover our own address IP
        # (this is where duplicated code starts to appear...)
        host = socket.gethostbyname(socket.gethostname())
        service.address = "%s:%d" % (host, self.port)

    def Enable(self):
        window = ChatWindow(self, self.service_api.GetDirectory())
        self.ui = UIProxy(window)
        n = NetworkLauncher(self.reactor, self, self.port)
        self.network = TwistedProxy(n, self.reactor)
        self.network.Start(self.GotMessage)
        menu = wx.Menu()
        self.service_api.SetMenu('Chat', menu)

    def Disable(self):
        self.network.Stop()
        self.network = None
        self.ui.Destroy()
        self.ui = None

    def DoAction(self):
        self.SendMessage(u"Need some wood?")
    
    def GotMessage(self, text, (host, port)):
        # This method is called in network context (i.e. Twisted thread)
        self.ui.AppendMessage(text)
    
    def SendMessage(self, text):
        # This method is called in UI context (i.e. wx Thread)
        self.network.SendMessage(text)

    def NewPeer(self, peer, service):
        #~ print "chat: NEW %s" % peer.id_
        try:
            host, port = self._ParseAddress(service.address)
        except ValueError:
            pass
        else:
            self.hosts[peer.id_] = host, port
            self.network.SetHosts(self.hosts.values())

    def ChangedPeer(self, peer, service):
        #~ print "chat: CHANGED %s" % peer.id_
        try:
            host, port = self._ParseAddress(service.address)
        except ValueError:
            if peer.id_ in self.hosts:
                del self.hosts[peer.id_]
                self.network.SetHosts(self.hosts.values())
        else:
            self.hosts[peer.id_] = host, port
            self.network.SetHosts(self.hosts.values())

    def LostPeer(self, peer_id):
        #~ print "chat: LOST %s" % peer_id
        if peer_id in self.hosts:
            del self.hosts[peer_id]
            self.network.SetHosts(self.hosts.values())

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
            print "Wrong chat address '%s'" % address
            raise
