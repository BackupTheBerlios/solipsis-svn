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

import os

from solipsis.util.entity import Entity, ServiceData
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
        self.remote_node = None

    def Connect(self, config_data):
        """
        Connect to the node.
        """
        def _success(proxy):
            # As soon as we are connected, get all peers and ask for events
            self.proxy = proxy
            proxy.GetNodeInfo()
            proxy.GetStatus()
            proxy.GetAllPeers()
            proxy.GetEvents()
            self.ui.NodeConnectionSucceeded(proxy)
        def _failure(error):
            self.proxy = None
            self.ui.NodeConnectionFailed(error)
            #~ print "connection failure:", str(error)

        if config_data.proxy_mode != "none" and config_data.proxy_host:
            proxy_host = config_data.proxy_host
            proxy_port = config_data.proxy_port
        else:
            proxy_host = None
            proxy_port = None
        self.remote_node = XMLRPCNode(self.reactor,
            config_data.host, config_data.port, proxy_host, proxy_port)
        d = self.remote_node.Connect(self)
        d.addCallbacks(_success, _failure)

    def Disconnect(self):
        """
        Disconnect from the node.
        """
        if self.remote_node is not None:
            self.remote_node.Disconnect()
            self.remote_node = None

    def Kill(self):
        """
        Kill the node.
        """
        if self.remote_node is not None:
            self.remote_node.Quit()
            self.remote_node = None

    def Connected(self):
        """
        Returns True if connected.
        """
        return self.remote_node is not None

    def Call(self, method, *args):
        """
        Call a remote function on the node.
        """
        print "!!!Call %s" % method
        if self.proxy is not None:
            getattr(self.proxy, method)(*args)

    #
    # Method response callbacks
    #
    def success_Quit(self, reply):
        """
        Notify kill report to the UI.
        """
        if reply:
            self.ui.NodeKillSucceeded()
        else:
            self.ui.NodeKillFailed()

    def success_GetAllPeers(self, reply):
        """
        Transmit all peer information to the viewport.
        """
        self.ui.ResetWorld()
        assert isinstance(reply, list), "Bad reply to GetAllPeers()"
        for struct_ in reply:
            peer = Entity.FromStruct(struct_)
            #~ print "PEER", peer.id_
            self.ui.AddPeer(peer)
        self.ui.Redraw()

    def success_GetNodeInfo(self, reply):
        """
        Transmit node information to the viewport.
        """
        node = Entity.FromStruct(reply)
        #~ print "NODE", node.id_
        self.ui.UpdateNode(node)

    def success_GetStatus(self, reply):
        """
        Trigger visual feedback of the connection status.
        """
        print "STATUS", reply
        self.ui.SetStatus(reply)

    #
    # Notification handlers
    #
    def event_CHANGED(self, struct_):
        peer = Entity.FromStruct(struct_)
        #~ print "CHANGED", peer.id_
        self.ui.UpdatePeer(peer)
        self.ui.AskRedraw()

    def event_NEW(self, struct_):
        peer = Entity.FromStruct(struct_)
        #~ print "NEW", peer.id_
        self.ui.AddPeer(peer)
        self.ui.AskRedraw()

    def event_LOST(self, peer_id):
        #~ print "LOST", peer_id
        self.ui.RemovePeer(peer_id)
        self.ui.AskRedraw()

    def event_STATUS(self, status):
        print "STATUS", status
        self.ui.SetStatus(status)

    def event_SERVICEDATA(self, struct_):
        d = ServiceData.FromStruct(struct_)
        self.ui.ProcessServiceData(d.peer_id, d.service_id, d.data)
