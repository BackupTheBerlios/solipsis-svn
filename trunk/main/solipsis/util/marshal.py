

from solipsis.util.address import Address


class PeerInfo:
    """
    This is a container class used to send node information to/from a navigator.
    It is marshallable as a simple structure by XML-RPC, and probably other
    protocols.
    """

    fields = {
        'id_':
            ("", str),
        'pseudo':
            (u"", unicode),
        'address':
            ("", lambda a: Address(strAddress=a)),
        'awareness_radius':
            (0.0, float),
        'position':
            ((0.0, 0.0, 0.0), lambda p: map(float, p)),
    }

    def __init__(self, struct=None):
        """
        Create a PeerInfo from struct (dictionnary).
        """
        if struct is None:
            for name, (default, cons) in self.fields.iteritems():
                setattr(self, name, default)
        else:
            for name, (default, cons) in self.fields.iteritems():
                setattr(self, name, cons(struct[name]))

    def FromPeer(self, peer):
        """
        Fill PeerInfo from peer.
        """
        self.id_ = peer.id_
        x, y = peer.position.getCoords()
        self.position = (float(x), float(y), float(peer.position.getPosZ()))
        self.pseudo = unicode(peer.pseudo)
        self.address = peer.address.toString()
        self.awareness_radius = float(peer.awareness_radius)

    def ToStruct(self):
        """
        Return struct (dictionnary) from PeerInfo.
        """
        return self.__dict__
