# pylint: disable-msg=C0103
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

from solipsis.util.wxutils import GetCharset
from solipsis.util.uiproxy import UIProxy, UIProxyReceiver
from solipsis.navigator.world import BaseWorld
import solipsis.navigator.wxclient.drawable as drawable
import solipsis.navigator.wxclient.images as images
# This is ugly, but hey, we need it :(
from solipsis.services.avatar.repository import AvatarRepository


class World(BaseWorld, UIProxyReceiver):
    """
    This class represents the navigator's view of the world.
    It receives events from the remote connector and communicates
    with the viewport to display the world on screen.
    """

    def __init__(self, viewport):
        """
        Constructor.
        """
        BaseWorld.__init__(self, viewport)
        UIProxyReceiver.__init__(self)
        self.charset = GetCharset()
        self.repository = images.ImageRepository()
        self.avatars = AvatarRepository()
        self.avatars.AskNotify(UIProxy(self).UpdateAvatars)

    def AddPeer(self, peer):
        """
        Called when a new peer is discovered.
        """
        item = BaseWorld.AddPeer(self, peer)
        self._CreatePeerLabel(item)
        self._CreatePeerAvatar(item)

    def _UpdateNode(self, node):
        """
        Called when the node's characteristics are updated.
        """
        item = BaseWorld._UpdateNode(self, node)
        # Update node pseudo
        if item.label_id:
            self.viewport.RemoveDrawable(node.id_, item.label_id)
            item.label_id = None
        self._CreatePeerLabel(item)
        # Create avatar if necessary
        if item.avatar_id:
            self.viewport.RemoveDrawable(node.id_, item.avatar_id)
            item.avatar_id = None
        self._CreatePeerAvatar(item)

    def UpdatePeer(self, peer):
        """
        Called when a peer has changed.
        """
        item, old = BaseWorld.UpdatePeer(self, peer)
        if peer.pseudo != old.pseudo:
            self.viewport.RemoveDrawable(peer.id_, item.label_id)
            self._CreatePeerLabel(item)


    def UpdateAvatars(self, peer_list):
        """
        Called when some peers' avatars have changed.
        This function also handles the special case of the node itself.
        """
        for peer_id in peer_list:
            if peer_id == self.node_id:
                item = self.node_item
            elif peer_id in self.items:
                item = self.items[peer_id]
            else:
                continue
            if item.avatar_id:
                self.viewport.RemoveDrawable(peer_id, item.avatar_id)
                item.avatar_id = None
            self._CreatePeerAvatar(item)

    #
    # Private methods
    #

    def _CreatePeerLabel(self, item):
        """
        Add the peer's pseudo to the viewport.
        """
        peer = item.peer
        d = drawable.Text(peer.pseudo)
        item.label_id = self.viewport.AddDrawable(peer.id_, d, (0, 20), 1)

    def _CreatePeerAvatar(self, item):
        """
        Add the peer's avatar to the viewport.
        """
        peer_id = item.peer.id_
        # Try to get an existing bitmap for the peer
        bitmap = self.avatars.GetProcessedAvatarBitmap(peer_id)
        if bitmap is None:
            if 0:
                # Test code: choose random avatar if no other is available
                hash_ = self.avatars.GetRandomAvatarHash()
                self.avatars.BindHashToPeer(hash_, peer_id)
                bitmap = self.avatars.GetProcessedAvatarBitmap(peer_id)
            else:
                bitmap = self.repository.GetBitmap(images.IMG_AVATAR)
        d = drawable.Image(bitmap)
        item.avatar_id = self.viewport.AddDrawable(peer_id, d, (0, 0), 0)
