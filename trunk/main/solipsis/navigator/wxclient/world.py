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

import drawable
import images


class World(object):
    """
    This class represents the navigator's view of the world.
    It receives events from the remote connector and communicates
    with the viewport to display the world on screen.
    """
    def __init__(self, viewport):
        self.viewport = viewport
        self.Reset()

    def Reset(self):
        self.peers = {}
        self.viewport.Reset()

    def AddPeer(self, peer):
        """
        Called when a new peer is discovered.
        """
        self.peers[peer.id_] = peer
        x, y, z = peer.position
        self.viewport.AddObject(peer.id_, None, position=(x, y))
        self.viewport.AddDrawable(peer.id_, drawable.Image(images.IMG_AVATAR), (0, 0), 0)
        self.viewport.AddDrawable(peer.id_, drawable.Text(peer.pseudo), (0, 20), 1)

    def RemovePeer(self, peer_id):
        """
        Called when a peer disappears.
        """
        if peer_id in self.peers:
            del self.peers[peer_id]
            self.viewport.RemoveObject(peer_id)

    def UpdateNode(self, node):
        """
        Called when the node's characteristics are updated.
        """
        x, y, z = node.position
        self.viewport.JumpTo((x, y))

    def UpdatePeer(self, peer):
        """
        Called when a peer has changed.
        """
        if peer.id_ in self.peers:
            self.peers[peer.id_] = peer
            x, y, z = peer.position
            self.viewport.MoveObject(peer.id_, position=(x, y))

