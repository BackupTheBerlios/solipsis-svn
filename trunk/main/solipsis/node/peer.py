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

import time

from solipsis.util.entity import Entity
import protocol

class Peer(Entity):
    def __init__(self, *args, **kargs):
        """
        Create a new Peer (derived from Entity).
        """
        # Call parent class constructor
        super(Peer, self).__init__(*args, **kargs)

        # True if middleman needed to contact the peer
        # before a hole is punched through its NAT
        self.needs_middleman = False
        # The peer from which we know this peer
        self.middleman_address = None
        # The highest protocol version accepted by the peer
        self.protocol_version = protocol.SAFE_VERSION

        # Time of latest messages received/sent
        self.last_received_message = 0
        self.last_sent_message = 0

        # Connection hold time for this peer
        self.hold_time = None

        self.Freshen()

    def Freshen(self):
        self.last_access = time.time()

    def FromArgs(cls, args):
        """
        Returns a Peer created from the given message arguments.
        """
        peer = cls(
            address = args.address,
            awareness_radius = args.awareness_radius,
            id_ = args.id_,
            position = args.position,
        )
        try:
            peer.hold_time = args.hold_time
        except AttributeError:
            pass
        try:
            peer.needs_middleman = args.needs_middleman
        except AttributeError:
            pass
        try:
            peer.protocol_version = args.version
            peer.needs_middleman = args.needs_middleman
        except AttributeError:
            pass
        return peer

    FromArgs = classmethod(FromArgs)

    def FromRemoteArgs(cls, args):
        """
        Returns a Peer created from the given "Remote-*" message arguments.
        """
        peer = cls(
            address = args.remote_address,
            id_ = args.remote_id,
            position = args.remote_position,
        )
        try:
            peer.awareness_radius = args.remote_awareness_radius
        except AttributeError:
            pass
        try:
            peer.protocol_version = args.remote_version
            peer.needs_middleman = args.remote_needs_middleman
        except AttributeError:
            pass
        try:
            peer.middleman_address = args.address
        except AttributeError:
            pass
        return peer

    FromRemoteArgs = classmethod(FromRemoteArgs)

