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

from solipsis.util.wxutils import _
from solipsis.util.uiproxy import TwistedProxy
from solipsis.services.plugin import ServicePlugin

from network import NetworkLauncher


class Plugin(ServicePlugin):
    def Init(self):
        reactor = self.service_api.GetReactor()
        port = random.randrange(7000, 7100)
        n = NetworkLauncher(reactor, self, port)
        self.network = TwistedProxy(n, reactor)

    def GetTitle(self):
        return _("Chat")

    def GetDescription(self):
        return _("Talk with the people that are currently around you")

    def GetAction(self):
        return _("Chat with all peers")

    def GetPointToPointAction(self):
        return None

    def Enable(self):
        self.network.Start()
        menu = wx.Menu()
        self.service_api.SetMenu('Chat', menu)

    def Disable(self):
        self.network.Stop()
        self.network = None

    def DoAction(self):
        self.network.SendMessage(u"Need some wood?")

    def NewPeer(self, peer, service):
        print "chat: NEW %s" % peer.id_

    def ChangedPeer(self, peer, service):
        print "chat: CHANGED %s" % peer.id_

    def LostPeer(self, peer_id):
        print "chat: LOST %s" % peer_id
