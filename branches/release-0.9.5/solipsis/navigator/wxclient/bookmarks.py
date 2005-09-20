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
    """
    I contain a list of bookmarked peers.
    """

    def __init__(self):
        self.peers = []

    def AddPeer(self, peer):
        """
        Add a peer.
        """
        self.RemoveByPseudo(peer.pseudo)
        self.RemoveById(peer.id_)
        self.peers.append(peer)

    def RemoveByPseudo(self, pseudo):
        """
        Remove all peers with the given pseudo.
        """
        self.peers = [p for p in self.peers if p.pseudo != pseudo]

    def RemoveById(self, peer_id):
        """
        Remove all peers with the given ID.
        """
        self.peers = [p for p in self.peers if p.id_ != peer_id]

    def RemoveDuplicates(self, peer):
        """
        Remove duplicates of the given peer.
        """
        self.RemoveByPseudo(peer.pseudo)
        self.RemoveById(peer.id_)

    def GetPeerByPseudo(self, pseudo):
        """
        Get a peer by its pseudo, or None.
        """
        l = [p for p in self.peers if p.pseudo == pseudo]
        assert len(l) < 2
        return len(l) and l[0] or None

    def GetPeerById(self, peer_id):
        """
        Get a peer by its ID, or None.
        """
        l = [p for p in self.peers if p.id_ == peer_id]
        assert len(l) < 2
        return len(l) and l[0] or None

    def GetAllPeers(self):
        """
        Returns a copy of the list of peers.
        """
        return list(self.peers)
