
import drawable
import images


class World:
    def __init__(self, viewport):
        self.viewport = viewport
        self.peers = {}

    def AddPeer(self, peer):
        self.peers[peer.id_] = peer
        self.viewport.AddObject(peer.id_, None, position=peer.position)
        self.viewport.AddDrawable(peer.id_, drawable.Image(images.IMG_AVATAR), (0, 0), 0)
        self.viewport.AddDrawable(peer.id_, drawable.Text(peer.pseudo), (0, 20), 1)

    def RemovePeer(self, peer_id):
        if peer_id in self.peers:
            del self.peers[peer_id]
            self.viewport.RemoveObject(peer_id)
