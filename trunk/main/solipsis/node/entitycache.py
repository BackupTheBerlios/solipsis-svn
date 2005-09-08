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

"""
Structure of the XML format used for storage:

<entities>
    <entity id="6010_0_6a74d073598e2c07b4ad49411b0fc3a6de0848a3">
        <address>192.34.56.70:6020</address>
        <version>1.1</version>
        <history>
            <connected>1124937580-1125137580</connected>
            <connected>1126165621-1126183604</connected>
        </history>
    </entity>
    <entity id="5800_0_76e546a71b51546c598b95901097115f44c232e8">
        ...
    </entity>
</entities>

"""

import time
from elementtree.ElementTree import Element, SubElement, ElementTree

from peer import Peer

EARLIEST_TIMESTAMP = 0

class _ConnectionInterval(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

class _PeerHistory(object):
    def __init__(self, peer=None):
        self.peer = peer
        # Keyed by end timestamp
        self.intervals = {}

    def ToElement(self):
        """
        Gets an ElementTree.Element representation.
        """
        peer = self.peer
        elt = Element("entity", id=peer.id_)
        SubElement(elt, "address").text = peer.address.ToString()
        SubElement(elt, "version").text = str(peer.protocol_version)
        hist = SubElement(elt, "history")
        keys = self.intervals.keys()
        keys.sort()
        for k in keys:
            c = SubElement(hist, "connected")
            i = self.intervals[k]
            c.text = "%s-%s" % (i.start, i.end)
        return elt

class EntityCache(object):
    max_stored_entities = 500
    max_stored_history = 5000

    def __init__(self):
        # Both dicts keyed by peer_id
        self.history_store = {}
        self.current_peers = {}

    def Evict(self):
        # All connection end timestamps
        end_timestamps = [(end, peer_id)
            for end in h.intervals()
            for (peer_id, h) in self.history_store.itervalues()]
        end_timestamps.sort()
        # Keep `max_stored_history` most recent
        evict_timestamps = end_timestamps[:-self.max_stored_history]
        for end, peer_id in evict_timestamps:
            del self.history_store[peer_id].intervals[end]
        print "flushed %d intervals" % len(evict_timestamps)
        # Freshest connection end timestamps, by peer
        end_timestamps = [(max(h.intervals, EARLIEST_TIMESTAMP), peer_id)
            for (peer_id, h) in self.history_store.itervalues()]
        end_timestamps.sort()
        # Keep `max_stored_entities` most recent
        evict_peers = end_timestamps[:-self.max_stored_entities]
        for end, peer_id in evict_peers:
            del self.history_store[peer_id]
        print "flushed %d entities" % len(evict_peers)

