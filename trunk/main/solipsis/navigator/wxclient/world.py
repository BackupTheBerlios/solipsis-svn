
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

