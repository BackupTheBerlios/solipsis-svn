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

import sys, types

class MemSizer(object):
    """
    Simple module size estimator
    ** derived from http://manatee.mojam.com/~skip/python/sizer.py **
    
    Working from the modules present in sys.modules, the Sizer class makes a
    reasonable estimate of the number of global objects reachable from each
    loaded module without traversing into other modules (more-or-less).
    
    Usage is simple:
    
        s = MemSizer()
        s.sizeall()
        for item in s.get_deltas():
            print item
    """
    dispatch = {}

    def __init__(self):
        self.oldseen = {}
        self.seen = {}
        self.unknown = {}
        self.seenids = {}

    def sizeall(self):
        self.oldseen = self.seen
        self.seen = {}
        self.seenids = {}
        for k in sys.modules.keys():
            if k.startswith('wx'):
                continue
            #~ print k
            self.seen[k] = self.rlen_module(sys.modules[k])

    def get_sizes(self):
        # Sort by descending number of objects
        result = [(-v, k) for (k, v) in self.seen.iteritems()]
        result.sort()
        s = ["%s: %d" % (k, -v) for (v, k) in result]
        return s

    def get_deltas(self):
        result = []
        _getold = self.oldseen.get
        for k, v in self.seen.iteritems():
            delta = v - _getold(k, 0)
            if delta != 0:
                result.append("%s: %d" % (k, delta))
        result.sort()
        return result

    def rlen(self, obj):
        try:
            return self.seenids[id(obj)]
        except KeyError:
            total = 0
            self.seenids[id(obj)] = 0
            # Lists and tuples
            if isinstance(obj, list) or isinstance(obj, tuple):
                total = self.rlen_seq(obj)
            # Dicts
            elif isinstance(obj, dict):
                total = self.rlen_dict(obj)
            # Objects and classes
            else:
                try:
                    total = self.rlen_dict(obj.__dict__)
                except AttributeError:
                    #self.unknown[type(obj)] = 1
                    #print "MemSizer: unknown type %s" % str(type(obj))
                    total = 1
                except:
                    print obj
                    raise
            self.seenids[id(obj)] = total
            return total

    def rlen_module(self, mod):
        if type(mod) == types.ModuleType:
            return self.rlen_dict(mod.__dict__)
        else:
            return 1

    dispatch[types.ModuleType] = rlen_module

    def rlen_dict(self, dict_):
        try:
            return self.seenids[id(dict_)]
        except KeyError:
            _rlen = self.rlen
            _modtype = types.ModuleType
            _seenids = self.seenids
            _seenids[id(dict_)] = 0
            total = 0
            for k, v in dict_.iteritems():
                if not isinstance(k, _modtype):
                    total += _rlen(k)
                if not isinstance(v, _modtype):
                    total += _rlen(v)
            _seenids[id(dict_)] = total
            return total

    def rlen_seq(self, seq):
        try:
            return self.seenids[id(seq)]
        except KeyError:
            _rlen = self.rlen
            _modtype = types.ModuleType
            _seenids = self.seenids
            _seenids[id(seq)] = 0
            total = 0
            for v in seq:
                #if id(v) not in _seenids and not isinstance(v, _modtype):
                if not isinstance(v, _modtype):
                    total += _rlen(v)
            _seenids[id(seq)] = total
            return total

    dispatch[dict] = rlen_dict
    dispatch[list] = rlen_seq
    dispatch[tuple] = rlen_seq
