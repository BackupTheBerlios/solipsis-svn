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

import sys
import time

from twisted.internet.protocol import DatagramProtocol

from solipsis.util.utils import set
from solipsis.util.address import Address
import protocol
from parser import Parser
from peer import Peer
from delayedcaller import DelayedCaller


class NodeProtocol(DatagramProtocol):
    def __init__(self, node_connector):
        self.node_connector = node_connector

    def datagramReceived(self, data, address):
        self.node_connector.OnMessageReceived(address, data)

    def SendData(self, address, data):
        self.transport.write(data, address)


class NodeConnector(object):
    # Requests we don't want to log, even in debug mode
    no_log = set(['HEARTBEAT'])

    # Hold time
    # With local nodes, we choose a very long timeout which enables us
    # to minimize the number of HEARTBEAT messages in a mass-hosting setup
    minimum_hold_time = 30
    local_hold_time = 1200
    remote_hold_time = 30

    # Minimum time between handshakes (HELLO or CONNECT) with the same peer
    handshake_dampening_duration = 5.0
    handshake_dampening_threshold = 4

    def __init__(self, reactor, params, state_machine, logger):
        self.reactor = reactor
        self.params = params
        self.state_machine = state_machine
        self.node = state_machine.node
        self.logger = logger
        self.parser = Parser()
        self.node_protocol = NodeProtocol(self)
        self.caller = DelayedCaller(self.reactor)

        # Can be modified by bootstrap code
        self.needs_middleman = False

        # Statistics
        self.received_messages = {}
        self.sent_messages = {}

        self.Reset()

    def Reset(self):
        # Storage of peers we are currently connected to
        self.current_peers = {}
        self.known_peers = {}

        # Delayed calls for connection heartbeat and timeout
        self.dc_peer_heartbeat = {}
        self.dc_peer_timeout = {}

        # For each address, this is the timestamp of the last handshake attempts
        self.last_handshakes = {}

        self.caller.Reset()

    def Start(self, port):
        """
        Start listening to Solipsis messages.
        """
        self.listening = self.reactor.listenUDP(port, self.node_protocol)

    def Stop(self):
        """
        Stop listening.
        """
        self.listening.stopListening()

    def AcceptHandshake(self, peer):
        """
        Checks for recent connection attempts with a peer,
        and possibly other conditions.
        Returns True if connection accepted, False if refused.
        """
        now = time.time()
        try:
            last = self.last_handshakes[peer.address]
        except KeyError:
            self.last_handshakes[peer.address] = [now]
        else:
            last = [t for t in last if now - t < self.handshake_dampening_duration]
            self.last_handshakes[peer.address] = last + [now]
            if len(last) >= self.handshake_dampening_threshold:
                return False
        return True

    def AcceptPeer(self, peer):
        """
        Returns True if a peer can be accepted for connection.
        """
        return peer.hold_time >= self.minimum_hold_time

    def AddPeer(self, peer):
        """
        Add a peer to the list of connected peers.
        """
        self.current_peers[peer.id_] = peer
        self.known_peers[peer.id_] = peer

        # Setup connection heartbeat callbacks
        def msg_receive_timeout():
            self.state_machine._Verbose("timeout (%s) => closing connection with '%s'" % (str(self.node.id_), str(peer.id_)))
            self.state_machine._CloseConnection(peer)
        def msg_send_timeout():
            message = protocol.Message('HEARTBEAT')
            message.args.id_ = self.node.id_
            self.SendToPeer(peer, message)

        # Keepalive heuristic (a la BGP)
        keepalive = peer.hold_time / 3.0
        self.dc_peer_heartbeat[peer.id_] = self.caller.CallPeriodically(keepalive, msg_send_timeout)
        self.dc_peer_timeout[peer.id_] = self.caller.CallPeriodically(peer.hold_time, msg_receive_timeout)
        return True

    def RemovePeer(self, peer_id):
        """
        Remove a peer we were connected to.
        """
        del self.current_peers[peer_id]
        # Cancel delayed calls relating to the peer
        self.dc_peer_heartbeat[peer_id].Cancel()
        self.dc_peer_timeout[peer_id].Cancel()
        del self.dc_peer_heartbeat[peer_id]
        del self.dc_peer_timeout[peer_id]

    def OnMessageReceived(self, address, data):
        """
        Called when a Solipsis message is received.
        """
        host, port = address
        try:
            message = self.parser.ParseMessage(data)
            if message.request not in self.no_log:
                self.logger.debug("<<<< received from %s:%d\n%s" % (host, port, data))
        except Exception, e:
            print str(e)
            return
        # Stats
        try:
            self.received_messages[message.request] += 1
        except KeyError:
            self.received_messages[message.request] = 1
        # Reset heartbeat timeout, if applicable
        try:
            peer_id = message.args.id_
        except AttributeError:
            pass
        else:
            if peer_id in self.dc_peer_timeout:
                self.dc_peer_timeout[peer_id].Reschedule()
        self.state_machine.PeerMessageReceived(message.request, message.args)

    def SendHandshake(self, peer, message):
        """
        Say HELLO or CONNECT to a peer, adding necessary
        arguments and managing repeated connection attempts.
        Returns True if succeeded, False if cancelled.
        """
        if not self.AcceptHandshake(peer):
            return False
        message.args.hold_time = self._HoldTime(peer.address)
        message.args.version = protocol.VERSION
        message.args.needs_middleman = self.needs_middleman
        return self.SendToPeer(peer, message)

    def SendToAddress(self, address, message):
        """
        Send a Solipsis message to an address.
        """
        data = self.parser.BuildMessage(message)
        return self._SendData(address, data, log=message.request not in self.no_log)

    def SendToPeer(self, peer, message):
        """
        Send a Solipsis message to a peer, possibly using a middleman.
        """
        if peer.id_ == self.node.id_:
            self.logger.error("we tried to send a message (%s) to ourselves" % message.request)
            return False
        if peer.id_ not in self.known_peers:
            self.known_peers[peer.id_] = peer
        address = peer.address
        data = self.parser.BuildMessage(message, version=peer.protocol_version)
        # Also send message through middleman if remote NAT hole not punched yet
        if peer.id_ not in self.current_peers:
            if peer.needs_middleman:
                if not peer.middleman_address:
                    print "cannot contact '%s' without a middleman" % peer.id_
                    return False
                middleman_msg = protocol.Message('MIDDLEMAN')
                middleman_msg.args.id_ = self.node.id_
                middleman_msg.args.remote_id = peer.id_
                middleman_msg.args.payload = data
                if not self.SendToAddress(peer.middleman_address, middleman_msg):
                    return False
        else:
            address = self.current_peers[peer.id_].address
        # Update stats
        try:
            self.sent_messages[message.request] += 1
        except KeyError:
            self.sent_messages[message.request] = 1
        # Really send message
        if not self._SendData(address, data):
            return False
        # Heartbeat handling
        if peer.id_ in self.dc_peer_heartbeat:
            self.dc_peer_heartbeat[peer.id_].Reschedule()
        return True


    #
    # Statistics handling
    #
    def DumpStats(self):
        requests = self.sent_messages.keys()
        requests.extend([k for k in self.received_messages.keys() if k not in requests])
        requests.sort()
        self._Verbose("\n... Message statistics ...")
        for r in requests:
            self._Verbose("%s: %d sent, %d received" % (r, self.sent_messages.get(r, 0), self.received_messages.get(r, 0)))


    #
    # Internal methods
    #
    def _HoldTime(self, address):
        """
        Choose hold time depending on peer address.
        """
        if address.host == self.node.address.host:
            return self.local_hold_time
        else:
            return self.remote_hold_time

    def _SendData(self, address, data, log=False):
        if isinstance(address, Address):
            host, port = (address.host, address.port)
        else:
            host, port = address
        self.node_protocol.SendData((host, port), data)
        if log:
            self.logger.debug(">>>> sending to %s:%d\n%s" % (host, port, data))
        return True

