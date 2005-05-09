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


class BookmarkList(object):

    def __init__(self):
        raise NotImplementedError

    def AddPeer(self, peer):
        raise NotImplementedError

    def RemoveByPseudo(self, pseudo):
        raise NotImplementedError

    def RemoveById(self, peer_id):
        raise NotImplementedError

    def RemoveDuplicates(self, peer):
        raise NotImplementedError

    def GetPeerByPseudo(self, pseudo):
        raise NotImplementedError

    def GetPeerById(self, peer_id):
        raise NotImplementedError

    def GetAllPeers(self):
        raise NotImplementedError
