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

import wx

import drawable
import images


class World(object):
    """
    This class represents the navigator's view of the world.
    It receives events from the remote connector and communicates
    with the viewport to display the world on screen.
    """
    class Item(object):
        def __init__(self, peer):
            self.peer = peer
            self.label_id = None
            self.avatar_id = None
    
    def __init__(self, viewport):
        self.charset = str(wx.GetLocale().GetSystemEncodingName())
        self.viewport = viewport
        self.Reset()

    def Reset(self):
        self.items = {}
        self.viewport.Reset()

    def AddPeer(self, peer):
        """
        Called when a new peer is discovered.
        """
        item = self.Item(peer)
        id_ = peer.id_
        self.items[id_] = item
        x, y, z = peer.position
        self.viewport.AddObject(id_, None, position=(x, y))
        self._CreatePeerLabel(item)
        self._CreatePeerAvatar(item)

    def RemovePeer(self, peer_id):
        """
        Called when a peer disappears.
        """
        if peer_id in self.items:
            del self.items[peer_id]
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
        id_ = peer.id_
        try:
            item = self.items[id_]
        except KeyError:
            return
        old = item.peer
        item.peer = peer
        if peer.position != old.position:
            x, y, z = peer.position
            self.viewport.MoveObject(id_, position=(x, y))
        print "%s => %s" % (old.pseudo, peer.pseudo)
        self.viewport.RemoveDrawable(id_, item.label_id)
        self._CreatePeerLabel(item)

    def _CreatePeerLabel(self, item):
        peer = item.peer
        d = drawable.Text(peer.pseudo.encode(self.charset))
        item.label_id = self.viewport.AddDrawable(peer.id_, d, (0, 20), 1)

    def _CreatePeerAvatar(self, item):
        peer = item.peer
        d = drawable.Image(images.IMG_AVATAR)
        item.avatar_id = self.viewport.AddDrawable(peer.id_, d, (0, 0), 0)
