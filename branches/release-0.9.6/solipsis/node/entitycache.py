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
import copy
import os
import bisect
import random
import math
from elementtree.ElementTree import Element, SubElement, ElementTree

from solipsis.util.compat import set
from solipsis.util.utils import CreateSecureId
from solipsis.util.address import Address
from peer import Peer


EARLIEST_TIMESTAMP = 0

def _timestamp():
    return int(time.time())

class _ConnectionInterval(object):
    def __init__(self, start, end=None):
        self.start = start
        self.end = end

class _PeerHistory(object):
    def __init__(self, peer=None):
        self.peer = peer
        # Keyed by end timestamp
        self.intervals = {}
        self.last_interval = None

    def Copy(self):
        other = copy.copy(self)
        # When a copy is asked, produce a distinct interval dict
        other.intervals = self.intervals.copy()
        other.last_interval = None
        return other

    def Open(self):
        """
        Open new connection interval.
        """
        assert self.last_interval is None, "Already open"
        self.last_interval = _ConnectionInterval(_timestamp())

    def Close(self):
        """
        Close current interval.
        """
        assert self.last_interval is not None, "Not open"
        i = self.last_interval
        i.end = _timestamp()
        self.intervals[i.end] = i
        self.last_interval = None

    def Merge(self, other):
        """
        Merge with other (fresher) history entry.
        """
        assert self.last_interval is None, "Cannot merge while open"
        # Flush history if address has changed
        if self.peer.address == other.peer.address:
            self.intervals.update(other.intervals)
        else:
            self.intervals = other.intervals.copy()
        self.peer = other.peer

    def Flush(self):
        """
        Flush past data.
        """
        self.intervals.clear()

    def GetTotalDuration(self):
        """
        Return summed duration of history intervals.
        """
        return sum([i.end - i.start for i in self.intervals.itervalues()])

    def GetLatestEnd(self):
        """
        Return end timestamp of latest interval.
        """
        return max(self.intervals.keys() + [EARLIEST_TIMESTAMP])

    #
    # I/O
    #
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

    def FromElement(cls, elt):
        """
        Creates a peer history from an ElementTree.Element.
        """
        obj = cls()
        peer_id = elt.get('id')
        address = Address.FromString(elt.findtext('address'))
        obj.peer = Peer(id_=peer_id, address=address)
        obj.peer.protocol_version = float(elt.findtext('version'))
        hist = elt.find('history')
        intervals = hist.findall('connected')
        for i in intervals:
            start, end = map(int, i.text.split('-'))
            obj.intervals[end] = _ConnectionInterval(start, end)
        return obj

    FromElement = classmethod(FromElement)


class _HistoryStore(object):
    max_stored_entities = 500
    max_stored_history = 2000

    def __init__(self):
        # Keyed by peer_id
        self.entries = {}

    def OnPeerConnected(self, peer):
        """
        Update store data when a peer is connected.
        """
        if peer.needs_middleman:
            return
        peer_id = peer.id_
        try:
            entry = self.entries[peer_id]
        except KeyError:
            entry = _PeerHistory(peer)
            self.entries[peer_id] = entry
        else:
            # Forget history if address has changed
            if peer.address != entry.peer.address:
                entry.Flush()
            entry.peer = peer
        entry.Open()

    def OnPeerDisconnected(self, peer_id):
        """
        Update store data when a peer is disconnected.
        """
        try:
            self.entries[peer_id].Close()
        except KeyError:
            # This simply means the peer was ignored because it needs a middleman
            pass

    def EvictIntervals(self):
        # All connection end timestamps
        end_timestamps = [(end, peer_id)
            for (peer_id, h) in self.entries.iteritems()
            for end in h.intervals]
        end_timestamps.sort()
        # Keep `max_stored_history` most recent
        evict_timestamps = end_timestamps[:-self.max_stored_history]
        for end, peer_id in evict_timestamps:
            del self.entries[peer_id].intervals[end]
#         print "flushed %d intervals" % len(evict_timestamps)

    def EvictEntities(self):
        # Evict empty entries
        evict_peers = [peer_id
            for peer_id, h in self.entries.iteritems()
            if not h.last_interval and not h.intervals]
        for peer_id in evict_peers:
            del self.entries[peer_id]
        # Freshest connection end timestamps, by peer
        end_timestamps = [(max(h.intervals.keys() + [EARLIEST_TIMESTAMP]), peer_id)
            for (peer_id, h) in self.entries.iteritems()]
        end_timestamps.sort()
        # Keep `max_stored_entities` most recent
        evict_peers = end_timestamps[:-self.max_stored_entities]
        for end, peer_id in evict_peers:
            del self.entries[peer_id]
#         print "flushed %d entities" % len(evict_peers)

    def Evict(self):
        """
        Evict superfluous data, to maintain a sensible size.
        """
        self.EvictIntervals()
        self.EvictEntities()

    def FlushHistory(self):
        """
        Flush all non-present data.
        """
        for entry in self.entries.itervalues():
            entry.Flush()

    def Merge(self, other):
        """
        Merges the other history store into this one.
        The other history store takes precedence when there is a conflict.
        """
        this_peers = set(self.entries)
        other_peers = set(other.entries)
        for peer_id in other_peers - this_peers:
#             print "new", peer_id
            self.entries[peer_id] = other.entries[peer_id].Copy()
        for peer_id in other_peers & this_peers:
#             print "merge", peer_id
            self.entries[peer_id].Merge(other.entries[peer_id])

    def WeightedEntities(self):
        """
        Return a list of (w, peer) tuples where 'w' is
        a numeric weight of the peer according to the peer history.
        """
        l = []
        for entry in self.entries.itervalues():
            w = float(entry.GetTotalDuration())
            l.append((w, entry.peer))
        return l

    #
    # I/O
    #
    def ToElement(self, it=None):
        """
        Represents the store contents as an ElementTree.Element.
        """
        if it is None:
            it = self.entries.iteritems()
        elt = Element("entities")
        for peer_id, entry in it:
            elt.append(entry.ToElement())
        return elt

    def FromElement(cls, elt):
        """
        Creates a history store from an ElementTree.Element.
        """
        obj = cls()
        entities = elt.findall('.//entity')
        for e in entities:
            entry = _PeerHistory.FromElement(e)
            obj.entries[entry.peer.id_] = entry
        return obj

    FromElement = classmethod(FromElement)


class EntityCache(object):
    def __init__(self):
        self.history = _HistoryStore()
        self.current_peers = _HistoryStore()
        self.default_entities = []

    def Fortify(self):
        """
        Perform useful maintenance tasks.
        """
        self.history.Merge(self.current_peers)
        self.history.Evict()
        self.current_peers.FlushHistory()
        self.current_peers.Evict()

    def OnPeerConnected(self, peer):
        """
        Call this method when a peer is connected.
        """
        self.current_peers.OnPeerConnected(peer)

    def OnPeerDisconnected(self, peer_id):
        """
        Call this method when a peer is disconnected.
        """
        self.current_peers.OnPeerDisconnected(peer_id)

    def Write(self, outfile):
        """
        Write the entity cache to an open file object.
        """
        self.Fortify()
        et = ElementTree(self.history.ToElement())
        et.write(outfile)

    def Read(self, infile):
        """
        Read the entity cache from an open file object.
        """
        try:
            et = ElementTree(file=infile)
        except (IOError, EOFError), e:
            print "failed loading entity cache: %s" % str(e)
            return
        self.history = _HistoryStore.FromElement(et)
        self.current_peers = _HistoryStore()

    def Load(self, path):
        """
        Load the entity cache from the given file path.
        """
        if not os.path.isfile(path):
            print "entities file '%s' not found" % path
            return False
        f = file(path, 'rb')
        try:
            self.Read(f)
        finally:
            f.close()
        return True

# ** this routine needs an overlap check when merging intervals
#     def Merge(self, path):
#         """
#         Merge information from the given file path.
#         """
#         other = type(self)()
#         if other.Load(path):
#             self.Fortify()
#             self.history.Merge(other.history)

    def SetDefaultEntities(self, addresses):
        """
        Sets the list of default entities.
        """
        self.default_entities = [Peer(address=address) for address in addresses]

    def IterChoose(self, loop=True, other_entities=None):
        """
        An iterator that will return
        entities to connect to.
        """
        self.Fortify()
        iter_count = 0
        if other_entities is None:
            other_entities = self.default_entities
        # Build weighted decision tree
        choices = self.history.WeightedEntities()
        choices.sort()
        choices.reverse()
        total = sum([w for (w, e) in choices])
        current_other_entities = other_entities[:]
        current_list = choices[:]
        current_total = total
        while loop or current_list or current_other_entities:
            iter_count += 1
            if loop and choices and not current_list:
                # Re-start with a fresh item choice list
                current_list = choices[:]
                current_total = total
                print "!! rewinding entity choice list"
            if loop and other_entities and not current_other_entities:
                # Re-populate additional entities
                current_other_entities = other_entities[:]
            w = len(current_other_entities) * (current_total or 1.0) * (1.0 - math.exp(-iter_count / 60.0))
            r = random.random() * (current_total + w)
            # Uniform choice amongst additional entities
            if r < w:
                i = int(len(current_other_entities) * r / w)
                e = current_other_entities.pop(i)
                yield e
                continue
            r -= w
            # This is O(N), but N is bound by max_stored_entities,
            # and also we will statistically stop in the first slots
            # (due to the reverse sort above)
            for i, (w, e) in enumerate(current_list):
                if r <= w:
                    break
                r -= w
            else:
                raise AssertionError("weighted search exhausted")
            # Remove the chosen item from future choices
            current_total -= w
            current_list.pop(i)
            yield e


#         # Huffman algorithm to optimize average tree traversing length
#         while len(l) > 1:
#             left = l.pop()
#             right = l.pop()
#             bisect.insort(l, (left[0] + right[0], (left, right)))
#         print l[0][0]
#         # Build decision tree
#         def _build_dec(item):
#             w, e = item
#             if not isinstance(e, tuple):
#                 return [w, 1, e]
#             left, right = e
#             left = _build_dec(left)
#             right = _build_dec(right)
#             return [left[0], left[1] + right[1], left, right]
#         decision_tree = _build_dec(l[0])

    def SaveAtomic(self, path):
        """
        Atomically save the entity cache to the given file path.
        """
        tmppath = path + '.'
        tmppath += CreateSecureId("%s %s" % (hash(self), time.time()))
        f = file(tmppath, 'wb')
        try:
            self.Write(f)
            f.close()
            try:
                os.rename(tmppath, path)
            except OSError:
                try:
                    os.unlink(path)
                except OSError:
                    # We may get there when concurrency is tight
                    pass
                try:
                    os.rename(tmppath, path)
                except OSError:
                    # We may get there when concurrency is tight
                    pass
        finally:
            try:
                os.unlink(tmppath)
            except OSError:
                pass

