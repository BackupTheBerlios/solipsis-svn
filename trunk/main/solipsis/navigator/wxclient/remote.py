
import os

from solipsis.util import marshal
from solipsis.util.nodeproxy import XMLRPCNode


class RemoteConnector(object):
    """
    RemoteConnector builds the socket-based connection to the Solipsis node.
    It sends and receives data from the node through an XMLRPC connection.
    """
    def __init__(self, reactor, ui):
        self.reactor = reactor
        self.ui = ui
        self.proxy = None

    def Connect(self, host, port):
        """
        Connect to the node.
        """
        def _success(proxy):
            # As soon as we are connected, get all peers and ask for events
            self.proxy = proxy
            self.proxy.GetNodeInfo()
            self.proxy.GetStatus()
            self.proxy.GetAllPeers()
            self.proxy.GetEvents()
        def _failure(error):
            self.proxy = None
            print "connection failure:", str(error)
            
        remote_node = XMLRPCNode(self.reactor, host, port)
        d = remote_node.Connect(self)
        d.addCallbacks(_success, _failure)

    def Disconnect(self):
        """
        Disconnect from the node.
        """
        self.proxy.Disconnect()
        self.proxy = None

    def Connected(self):
        """
        Returns True if connected.
        """
        return self.proxy is not None

    def Call(self, method, *args):
        """
        Call a remote function on the node.
        """
        if self.proxy is not None:
            getattr(self.proxy, method)(*args)

    #
    # Method response callbacks
    #
    def success_GetAllPeers(self, reply):
        """
        Transmit all peer information to the viewport.
        """
        self.ui.ResetWorld()
        for struct in reply:
            peer_info = marshal.PeerInfo(struct)
            print "PEER", peer_info.id_
            self.ui.AddPeer(peer_info)
        self.ui.Redraw()

    def success_GetNodeInfo(self, reply):
        """
        Transmit node information to the viewport.
        """
        node_info = marshal.PeerInfo(reply)
        print "NODE", node_info.id_
        self.ui.UpdateNode(node_info)

    def success_GetStatus(self, reply):
        """
        Trigger visual feedback of the connection status.
        """
        print "STATUS", reply
        self.ui.SetStatus(reply)

    #
    # Notification handlers
    #
    def event_CHANGED(self, struct):
        peer_info = marshal.PeerInfo(struct)
        print "CHANGED", peer_info.id_
        self.ui.UpdatePeer(peer_info)
        self.ui.AskRedraw()

    def event_NEW(self, struct):
        peer_info = marshal.PeerInfo(struct)
        print "NEW", peer_info.id_
        self.ui.AddPeer(peer_info)
        self.ui.AskRedraw()

    def event_LOST(self, peer_id):
        print "LOST", peer_id
        self.ui.RemovePeer(peer_id)
        self.ui.AskRedraw()

    def event_STATUS(self, status):
        print "STATUS", status
        self.ui.SetStatus(status)
