
import twisted.web.xmlrpc as xmlrpc

from solipsis.util import marshal


class RemoteConnector(object):
    """
    RemoteConnector builds the socket-based connection to the Solipsis node.
    It handles sending and receiving data from the node.
    """
    def __init__(self, reactor, ui):
        self.reactor = reactor
        self.ui = ui
        self.xmlrpc_control = None
        self.connect_id = None

    def Connect(self, host, port):
        """
        Connect to the node.
        """
        control_url = 'http://%s:%d/RPC2' % (host, port)
        xmlrpc_control = xmlrpc.Proxy(control_url)

        def _success(connect_id):
            # As soon as we are connected, get all peers and ask for events
            self.xmlrpc_control = xmlrpc_control
            self.connect_id = connect_id
            print "connect_id:", connect_id
            self.Call('GetNodeInfo')
            self.Call('GetStatus')
            self.Call('GetAllPeers')
            self._AskEvents()
        def _failure(error):
            print "connection failure:", str(error)
        xmlrpc_control.callRemote('Connect').addCallbacks(_success, _failure)

    def Disconnect(self):
        """
        Disconnect from the node.
        """
        self.Call('Disconnect')
        self.xmlrpc_control = None
        self.connect_id = None

    def Connected(self):
        """
        Returns True if connected.
        """
        return self.xmlrpc_control is not None

    def Call(self, method, *args):
        """
        Call a remote function on the node.
        """
        if self.xmlrpc_control is not None:
            d = self.xmlrpc_control.callRemote(method, self.connect_id, *args)
            _success = getattr(self, "success_" + method, self.success_default)
            _failure = getattr(self, "failure_" + method, self.failure_default)
            d.addCallbacks(_success, _failure)

    #
    # XML RPC callbacks
    #
    def success_default(self, reply):
        pass

    def failure_default(self, error):
        print "failure:", str(error)

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

    def success_GetEvents(self, reply):
        """
        Process events, then ask for more.
        """
        for notif in reply:
            t, request, payload = notif
            try:
                attr = getattr(self, 'event_' + request)
            except:
                print "Unrecognized notification '%s'" % request
            else:
                attr(payload)
        self._AskEvents()

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

    #
    # Private methods
    #
    def _AskEvents(self):
        self.Call('GetEvents')

