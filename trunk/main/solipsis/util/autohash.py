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



class Autohash1(type):
    """
    Metaclass that creates a hash function based on the attributes listed
    in the '_hash_attributes' attribute.
    """
    def __new__(cls, name, bases, d):
        try:
            l = d['_hash_attributes']
        except KeyError:
            raise KeyError("class '%s' must have the '_hash_attributes' attribute" % name)
        _hash = hash
        _xor = int.__xor__
        _reduce = reduce
        _int = int
        c = _reduce(_xor, [_hash(k) for k in l])
        def my_hash(obj):
            g = obj.__getattribute__
            return _reduce(_xor, [_hash(g(k)) for k in l], c)
        d['__hash__'] = my_hash
        t = super(Autohash1, cls).__new__(cls, name, bases, d)
        return t

class Autohash2(type):
    """
    Metametaclass that instantiates into a metaclass creating
    a hash function based on the attributes passed on instantiation.
    """
    def __new__(cls, hash_attributes):
        def class_new(cls, name, bases, d):
            print "New class", name
            l = hash_attributes
            _hash = hash
            _tuple = tuple
            c = _hash(_tuple([_hash(k) for k in l]))
            def object_hash(obj):
                g = obj.__getattribute__
                return _hash(_tuple([_hash(g(k)) for k in l]))
            d['__hash__'] = object_hash
            return super(Autohash2, cls).__new__(cls, name, bases, d)
        name = '__private'
        bases = (type,)
        d = {'__new__': class_new}
        print "New metaclass", name
        return type.__new__(cls, name, bases, d)


class Metametaclass(type):
    def __new__(cls, name, bases, dict_):
        d = { '__new__': dict_['class_new'] }
        def meta_new(cls, *args, **kargs):
            name = '__private'
            bases = (type,)
            return super(Metametaclass, cls).__new__(cls, name, bases, d)
        dict_['__new__'] = meta_new
        return type.__new__(cls, name, bases, dict_)

class Autohash(type):
    """
    Metaclass that creates a hash function based on the
    attributes passed on instantiation.
    """
    __metaclass__ = Metametaclass

    def __init__(cls, hash_attributes):
        cls.hash_attributes = hash_attributes

    def class_new(cls, name, bases, d):
        l = cls.hash_attributes
        _hash = hash
        _tuple = tuple
        c = _hash(_tuple([_hash(k) for k in l]))
        def object_hash(obj):
            g = obj.__getattribute__
            return _hash(_tuple([_hash(g(k)) for k in l]))
        d['__hash__'] = object_hash
        return super(Autohash, cls).__new__(cls, name, bases, d)
