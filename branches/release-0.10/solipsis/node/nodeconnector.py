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
import traceback

from twisted.internet.protocol import DatagramProtocol

from solipsis.util.compat import set
from solipsis.util.address import Address
from solipsis.node.discovery import stun
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
        try:
            self.transport.write(data, address)
            return True
        except Exception, e:
            print "failed sending message to %s:" % str(address)
            print traceback.format_tb(e)
            return False

class NodeConnector(object):
    # Requests we don't want to log, even in debug mode
    no_log = set(['HEARTBEAT'])

    # Connection hold time
    # With local nodes, we choose a very long timeout which enables us
    # to minimize the number of HEARTBEAT messages in a mass-hosting setup
    minimum_hold_time = 25
    local_hold_time = 1200
    remote_hold_time = 30

    # Minimum time between handshakes (HELLO or CONNECT) with the same peer
    handshake_dampening_duration = 6.0
    handshake_dampening_threshold = 10
    outgoing_handshake_duration = 1.5

    # Delay between attempts at protocol version negotiation
    version_negotiation_delay = 3.0

    def __init__(self, reactor, params, state_machine, logger):
        self.reactor = reactor
        self.params = params
        self.state_machine = state_machine
        self.node = state_machine.node
        self.logger = logger
        self.parser = Parser()
        self.node_protocol = NodeProtocol(self)
        self.caller = DelayedCaller(self.reactor)

        # This flag will be updated by NAT detection code
        self.needs_middleman = True

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
        # Delayed calls for version negotiation
        self.dc_peer_negotiate = {}

        # For each address, this is the timestamp of the last handshake attempts
        self.last_handshakes = {}
        self.outgoing_handshakes = {}

        self.caller.Reset()

    def Start(self, port):
        """
        Start listening to Solipsis messages.
        """
        self.needs_middleman = stun.NeedsMiddleman()
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
                print "*** refusing handshake with '%s'" % peer.id_
                return False
        return True

    def AcceptPeer(self, peer):
        """
        Returns True if a peer can be accepted for connection.
        """
        return peer.hold_time is None or (peer.hold_time >= self.minimum_hold_time)

    def AddPeer(self, peer):
        """
        Add a peer to the list of connected peers.
        """
        self.current_peers[peer.id_] = peer
        self.known_peers[peer.id_] = peer
#         print "adding peer with protocol %s" % str(peer.protocol_version)

        # Setup connection heartbeat callbacks
        def msg_receive_timeout():
            self.state_machine._Verbose("timeout (%s) => closing connection with '%s'" % (str(self.node.id_), str(peer.id_)))
            self.state_machine._CloseConnection(peer)
        def msg_send_timeout():
            message = protocol.Message('HEARTBEAT')
            message.args.id_ = self.node.id_
            self.SendToPeer(peer, message)

        # Keepalive heuristic (a la BGP)
#         keepalive = peer.hold_time / 3.0
        keepalive = self._HoldTime(peer.address) / 3.0
        self.dc_peer_heartbeat[peer.id_] = self.caller.CallPeriodically(keepalive, msg_send_timeout)
        self.dc_peer_timeout[peer.id_] = self.caller.CallPeriodically(self._HoldTime(peer.address), msg_receive_timeout)

        # Negotiation is done
        self._CancelPeerDCs(peer.id_, [self.dc_peer_negotiate])
        try:
            del self.outgoing_handshakes[peer.address]
        except KeyError:
            pass
        return True

    def RemovePeer(self, peer_id):
        """
        Remove a peer we were connected to.
        """
        del self.current_peers[peer_id]
        # Cancel delayed calls related to the peer
        self._CancelPeerDCs(peer_id, [self.dc_peer_heartbeat, self.dc_peer_timeout, self.dc_peer_negotiate])

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
#         print "  <", message.request, "%s:%d" % (host, port)
        self.state_machine.PeerMessageReceived(message.request, message.args)

    def FillHandshake(self, peer, message):
        """
        Fill handshake parameters in a Solipsis message.
        (e.g. protocol version, hold time...)
        """
        message.args.hold_time = self._HoldTime(peer.address)
        message.args.version = protocol.VERSION
        message.args.needs_middleman = self.needs_middleman

    def SendHandshake(self, peer, message):
        """
        Special method for sending HELLO and CONNECT messages.
        In addition to proper message sending, this method also
        manages version negotiation.
        Returns True if succeeded, False otherwise.
        """
        now = time.time()
        try:
            last = self.outgoing_handshakes[peer.address]
        except KeyError:
            pass
        else:
            # If we already tried an outgoing handshake
            # recently, pretend we have sent the message
            if now - last < self.outgoing_handshake_duration:
#                 print "* handshake already sent to", peer.id_
                return True
        self.outgoing_handshakes[peer.address] = now
        self.FillHandshake(peer, message)

        # Explanation:
        # - 'can_ignore_middleman': this a special case since the NAT hole
        #   may already have been punched by a previous message (e.g. HELLO),
        #   but the peer is not yet in our current list
        # - 'version_override': we first try to with the 'better' version and
        #   fall back to the lower version we know the peer supports
        better_version = protocol.BETTER_VERSION
        def safe_attempt():
            return self.SendToPeer(peer, message, can_ignore_middleman=True)
        def negotiation_attempt():
            return self.SendToPeer(peer, message, version_override=better_version, can_ignore_middleman=True)

        use_negotiation = peer.protocol_version < better_version
        if use_negotiation:
#             print "using negotiation for %s instead of %s" % (str(better_version), str(peer.protocol_version))
            dc = self.caller.CallLater(self.version_negotiation_delay, safe_attempt)
            self.dc_peer_negotiate[peer.id_] = dc
            return negotiation_attempt()
        else:
            return safe_attempt()

    def SendToAddress(self, address, message):
        """
        Send a Solipsis message to an address.
        """
        data = self.parser.BuildMessage(message)
        return self._SendData(address, data, log=message.request not in self.no_log)

    def SendToPeer(self, peer, message, version_override=None, can_ignore_middleman=False):
        """
        Send a Solipsis message to a peer, possibly using a middleman.
        """
        if peer.id_ == self.node.id_:
            self.logger.error("we tried to send a message (%s) to ourselves" % message.request)
            return False
        if peer.id_ not in self.known_peers:
            self.known_peers[peer.id_] = peer
        version = version_override or peer.protocol_version
        data = self.parser.BuildMessage(message, version)
        try_middleman = False
        try_directly = True
        our_address = self.node.address
        # Special treatment when we seem to be behind the same NAT
        if peer.address.host == our_address.host and \
            peer.address.private_host is not None and our_address.private_host is not None:
            address = Address(peer.address.private_host, peer.address.private_port)
        # Send message through middleman if remote NAT hole not punched yet
        elif peer.id_ not in self.current_peers:
            address = peer.address
            if peer.needs_middleman:
                if not peer.middleman_address:
                    if not can_ignore_middleman:
                        print "cannot contact '%s' without a middleman ('%s')" % (peer.id_, message.request)
                        return False
                else:
                    try_middleman = True
                    # There's no need to also send the message directly
                    # except if we have to punch a hole in our own NAT.
                    if not self.needs_middleman:
                        try_directly = False
        else:
            address = self.current_peers[peer.id_].address
        # Really send message
        if try_middleman:
            middleman_msg = protocol.Message('MIDDLEMAN')
            middleman_msg.args.id_ = self.node.id_
            middleman_msg.args.remote_id = peer.id_
            middleman_msg.args.payload = data
            # MIDDLEMAN doesn't exist in old protocol versions
            middleman_msg.version = protocol.BETTER_VERSION
            if not self.SendToAddress(peer.middleman_address, middleman_msg):
                return False
        if try_directly:
            if not self._SendData(address, data, log=message.request not in self.no_log):
                return False
            # Heartbeat handling
            if peer.id_ in self.dc_peer_heartbeat:
                self.dc_peer_heartbeat[peer.id_].Reschedule()
        # Update stats
        try:
            self.sent_messages[message.request] += 1
        except KeyError:
            self.sent_messages[message.request] = 1
        return True

    def DoMiddleman(self, source_id, target_id, data):
        """
        Relay a Solipsis message on behalf of a peer to another peer.
        """
        try:
            target = self.known_peers[target_id]
        except KeyError:
            print "cannot do middleman for %s" % target_id
            return False
#         print "doing middleman %s -> %s" % (source_id, target_id)
        return self._SendData(target.address, data, log=True)

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

    def _SendData(self, address, data, log=True):
        """
        Send raw data to a destination address, and optionally log it.
        """
        our_address = self.node.address
        # Special treatment when we seem to be behind the same NAT
        if address.host == our_address.host and \
            address.private_host is not None and our_address.private_host is not None:
            host, port = address.private_host, address.private_port
        else:
            host, port = address.host, address.port
        r = self.node_protocol.SendData((host, port), data)
        if log:
            self.logger.debug(">>>> sending to %s:%d\n%s" % (host, port, data))
        return r

    def _CancelPeerDCs(self, peer_id, dc_tables):
        """
        Cancel delayed calls for the given peer in the given tables.
        """
        for t in dc_tables:
            try:
                dc = t.pop(peer_id)
            except KeyError:
                pass
            else:
                dc.Cancel()
