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

from solipsis.util.wxutils import _
from solipsis.services.plugin import ServicePlugin


class Plugin(ServicePlugin):
    def GetAction(self):
        return _("Chat with people")

    def GetTitle(self):
        return _("Discussion")

    def GetDescription(self):
        return _("Talk with the people around you")

    def IsPointToPoint(self):
        return False

    def NewPeer(self, peer):
        print "chat: NEW %s" % peer.id_
        pass

    def ChangedPeer(self, peer):
        print "chat: CHANGED %s" % peer.id_
        pass

    def LostPeer(self, peer_id):
        print "chat: LOST %s" % peer_id
        pass
