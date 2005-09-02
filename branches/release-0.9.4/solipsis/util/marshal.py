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


class Marshallable(object):
    """
    Marshallable is the base class for classes that are to be marshallable
    by simple protocols like XMLRPC. It means Marshallable objects can be
    converted to/from a dictionnary (which can be nested).
    """
    marshal_filters = {}

    def FromStruct(cls, struct_):
        """
        Create a Marshallable from struct (dictionnary).
        """
        obj = cls()
        if struct_ is None:
            for name, (default, cons) in obj.marshallable_fields.iteritems():
                setattr(obj, name, default)
        else:
            for name, (default, cons) in obj.marshallable_fields.iteritems():
                setattr(obj, name, cons(struct_[name]))
        return obj
    
    FromStruct = classmethod(FromStruct)

    def ToStruct(self):
        """
        Return struct (dictionnary) from Marshallable.
        """
        def _MarshalValue(v):
            assert v is not None, "Cannot marshal None!"
            if isinstance(v, Marshallable):
                return v.ToStruct()
            elif isinstance(v, list):
                return [_MarshalValue(w) for w in v]
            elif isinstance(v, dict):
                return dict([(k, _MarshalValue(w)) for k, w in v.items()])
            else:
                return v

        d = {}
        for k in self.marshallable_fields:
            v = getattr(self, k)
            #~ try:
                #~ f = self.marshal_filters[k]
            #~ except KeyError:
                #~ pass
            #~ else:
                #~ if not f(v):
                    #~ continue
            d[k] = _MarshalValue(v)
        #~ print d
        return d
