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
import weakref

from solipsis.util.compat import set

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

    def __init__(self):
        self.oldseen = {}
        self.seen = {}
        self.unknown = {}
        self.seenids = {}

        self.dispatch = {
            types.ModuleType: self.rlen_module,
            dict: self.rlen_dict,
            list: self.rlen_seq,
            tuple: self.rlen_seq,
            set: self.rlen_seq,
            # frozenset and deque do not exist in Python 2.3
            #frozenset: self.rlen_seq,
            #deque: self.rlen_seq,
        }
        self.ignores = set()
        self.ignores.add(weakref.ProxyType)
        try:
            import zope.interface.interface as i
            import zope.interface.declarations as d
            import twisted.python.components as c
        except ImportError:
            pass
        else:
            for mod in (i, d, c):
                for k in dir(mod):
                    v = getattr(mod, k)
                    if isinstance(v, type):
                        self.ignores.add(v)
            #self.ignores.add(ClassProvides)
            #self.ignores.add(Declaration)
            #self.ignores.add(Implements)

    def sizeall(self):
        self.oldseen = self.seen
        self.seen = {}
        self.seenids = {}
        for k in sys.modules.iterkeys():
            #if k != "twisted.internet.interfaces":
                #continue
            #~ if k.startswith('wx'):
                #~ continue
            self.seen[k] = self.rlen(sys.modules[k])

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
        _id = id(obj)
        try:
            return self.seenids[_id]
        except KeyError:
            total = 0
            self.seenids[_id] = 0
            t = type(obj)
            if t in self.ignores:
                return total
            try:
                d = self.dispatch[t]
            except KeyError:
                try:
                    total += self.rlen_dict(obj.__dict__)
                except AttributeError:
                    if type(obj) not in self.unknown and type(obj) not in self.dispatch:
                        self.unknown[type(obj)] = 1
                        print "MemSizer: unknown type %s" % str(type(obj))
                    total += 1
                except:
                    print "cannot memsize '%s'" % str(obj)
                    total += 0
            else:
                total += d(obj)
            self.seenids[_id] = total
            #if total > 10:
                #print total, str(obj)
            return total

    def rlen_module(self, mod):
        return self.rlen_dict(mod.__dict__)

    def rlen_dict(self, dict_):
        _rlen = self.rlen
        _modtype = types.ModuleType
        total = 0
        #print len(dict_)
        for k, v in dict_.iteritems():
            if not isinstance(k, _modtype):
                total += _rlen(k)
            if not isinstance(v, _modtype):
                total += _rlen(v)
        return total

    def rlen_seq(self, seq):
        _rlen = self.rlen
        _modtype = types.ModuleType
        total = 0
        #print len(seq)
        for v in seq:
            if not isinstance(v, _modtype):
                total += _rlen(v)
        return total

