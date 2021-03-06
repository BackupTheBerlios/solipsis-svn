# pylint: disable-msg=W0131,W0201
# Missing docstring, Attribute '%s' defined outside __init__
#
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
"""Represents data used in filter model."""

__revision__ = "$Id: filter_document.py 894 2005-10-11 18:39:43Z emb $"

import re
from solipsis.services.profile import ENCODING
    
def create_regex(input_value):
    """'input_input' is a keyword that main contain the joker char '*'.
    Te function traduces it into a regex.

    ie: *mp3 -> .*mp3
        *.gif -> .*\.gif
        bonus -> bonus
        *any(FR)* -> .*any\(FR\).*"""
    if input_value == "":
        return input_value
    # list of chars to replace (all except '*' and '\')
    sensible_chars = ".^$+?{[]|()"
    for sensible_char in sensible_chars:
        input_value = input_value.replace(sensible_char, "\\" + sensible_char)
    # add regex expression
    if not input_value.startswith('*'):
        input_value = "^" + input_value
    if not input_value.endswith('*'):
        input_value += "$"
    return input_value.replace('*', '.*')
    
def create_key_regex(input_value):
    """'input_input' is a keyword that contains no joker .
    Te function traduces it into a regex.

    ie: mp3 -> .*mp3.*
        bon.us -> .*bon\.us.*
        *any(FR)* -> .*any\(FR\).*"""
    if input_value == "":
        return input_value
    if input_value == "*":
        return ".*"
    # list of chars to replace (all except '*' and '\')
    sensible_chars = "*.^$+?{[]|()"
    for sensible_char in sensible_chars:
        input_value = input_value.replace(sensible_char, "\\" + sensible_char)
    # add regex expression
    return '.*' + input_value + '.*'

class FilterValue(object):
    """wrapper for filter: regex, description ans state"""

    def __init__(self, name="no name", value=u"", activate=False):
        self.name = name
        self.description = value
        self.activated = activate
        self.regex = re.compile(create_key_regex(value), re.IGNORECASE)

    def __eq__(self, other):
        return self.description == other.description \
               and self.activated == other.activated

    def __repr__(self):
        return ', '.join([self.name,
                          self.description,
                          self.activated and "(1)" or "(0)"])

    def __str__(self):
        return ', '.join([self.description,
                          self.activated and "(1)" or "(0)"])

    def from_str(name, desc):
        try:
            description, activated = desc.split(', ')
            return FilterValue(name=name,
                               value=description,
                               activate= activated=="(1)" and True or False)
        except ValueError:
            print "could not read filter", desc
    from_str = staticmethod(from_str)
        
    def set_value(self, value, activate=True):
        """recompile regex and (dis)activate filter"""
        self.description = value
        self.regex = re.compile(create_key_regex(value), re.IGNORECASE)
        self.activated = activate
        
    def does_match(self, peer_id, data):
        """apply regex on data and returns self if there is any match"""
        # no match -> return false
        if not self.activated or len(self.description) == 0:
            return False
        if self.regex.match(data) is None:
            return False
        # match -> return true
        return FilterResult(peer_id, self, data)

class FilterResult:
    """Structure to receive a positive result from a match"""

    def __init__(self, peer_id, filter_value, match):
        self.peer_id = peer_id
        self.filter_value = filter_value
        self.match = match

    def get_name(self):
        """return name of fhe filter (ie: personal detrails, custom
        attributes..."""
        return self.filter_value.name

    def get_description(self):
        """return regex"""
        return self.filter_value.description

class AbstractFilter:
    """description of a filter: all fields wich may be matched must be
    declared in ALL_FILTERS. They are set in __init__ and the methods
    update_field are also provided to change the description of the
    filter.

    the method match compares all fields with a dictionary which keys
    are the name of the fields. However, this dictionary does not have
    to declare all fields. If it contains any ohther fields than those
    described in ALL_FILTERS, they will be ignored"""
    
    ALL_FILTERS = []
    PREFIX = ""
    
    def __init__(self, filter_name, filter_or=True, **properties):
        """if filter_or set to True, matching will use logic OR
        between properties. Otherwise, it will use AND"""
        self.filter_name = filter_name
        self.filter_or = filter_or
        # set each properties
        for prop_name in self.ALL_FILTERS:
            # set filter value
            if prop_name in properties and properties[prop_name].strip():
                filter_value = FilterValue(name=prop_name,
                                           value=properties[prop_name],
                                           activate=True)
            else:
                filter_value = FilterValue(prop_name)
            setattr(self, prop_name, filter_value)
            # set updating method
            def set_filter(filter_value, name=prop_name):
                """set member both in cache & in file"""
                member = getattr(self, name)
                if member == filter_value:
                    return False
                else:
                    member.set_value(filter_value.description,
                                     filter_value.activated)
                    return member
            setattr(self, "update_" + prop_name, set_filter)

    def from_str(cls, name, properties):
        if not name.startswith(cls.PREFIX):
            return None, None
        name = name[len(cls.PREFIX):]
        filter_or = True
        if name.startswith("AND_"):
            filter_or = False
            name = name[4:]
        elif name.startswith("OR_"):
            name = name[3:]
        #else: do nothing, filter_or by default
        new_filter = cls(name, filter_or)
        for prop_name, value in properties:
            prop_name = prop_name.strip().lower()
            value = FilterValue.from_str(prop_name, value)
            if prop_name in new_filter.ALL_FILTERS:
                getattr(new_filter, "update_" + prop_name)(value)
            else:
                new_filter.update_dict(value)
        return name, new_filter
    from_str = classmethod(from_str)
            
    def as_dict(self):
        result = {}
        for prop_name in self.ALL_FILTERS:
            result[prop_name] = str(getattr(self, prop_name))
        return result

    def update_properties(self, **props):
        for prop_name in self.ALL_FILTERS:
            if prop_name in props and props[prop_name].strip():
                getattr(self, prop_name).set_value(props[prop_name])
            else:
                getattr(self, prop_name).activated = False

    def update_dict(self, filter_value):
        """update other fields than those specified in ALL_FILTERS"""
        raise NotImplementedError
            
    def match(self, peer_id, **properties):
        matches = []
        # match each properties
        for prop_name in self.ALL_FILTERS:
            filter_value = getattr(self, prop_name)
            if filter_value.activated and prop_name in properties:
                matches.append(filter_value.does_match(peer_id,
                                                       properties[prop_name]))
        # return only valid matches
        if False in matches and not self.filter_or:
            return []
        else:
            return [matche for matche in matches if not matche is False]

class FileFilter(AbstractFilter):
    """Implementation of AbstractFilter for files: two fields might be
    used for matches: name & size"""

    ALL_FILTERS = ["name", "size"]
    PREFIX = "file_"

    def __init__(self, filter_name, filter_or=True, **properties):
        AbstractFilter.__init__(self, filter_name, filter_or, **properties)
        
    def update_dict(self, filter_value):
        """update other fields than those specified in ALL_FILTERS"""
        print "no other field in FileFilter"
        
    def match(self, peer_id, file_dicts):
        matches = []
        for file_dict in file_dicts:
            matches += AbstractFilter.match(self, peer_id, **file_dict)
        return matches

class PeerFilter(AbstractFilter):
    """Implementation of AbstractFilter for peers: all details of a
    peer may be used for matches, plus the customs attributes"""

    ALL_FILTERS = ["title", "firstname", "lastname",
                   "pseudo", "photo", "email"]
    PREFIX = "peer_"

    def __init__(self, filter_name, filter_or=True, **properties):
        AbstractFilter.__init__(self, filter_name, filter_or, **properties)
        # set customs {name : value}
        self.customs = {}
            
    def as_dict(self):
        result = AbstractFilter.as_dict(self)
        for name, value in self.customs.items():
            result[name] = str(value)
        return result

    def update_customs(self, custom_dict):
        self.customs.clear()
        for name, value in custom_dict.items():
            filter_value = FilterValue(
                name=name,
                value=value,
                activate=True)
            self.update_dict(filter_value)

    def update_dict(self, filter_value):
        if filter_value.name in self.customs:
            self.customs[filter_value.name].set_value(
                filter_value.description,
                filter_value.activated)
        else:
            self.customs[filter_value.name] = filter_value
        
    def match(self, peer_id, customs, **properties):
        matches = AbstractFilter. match(self, peer_id, **properties)
        # match custom attributes
        merged={}
        [merged.setdefault(k,v)
         for k,v in self.customs.items() if k in customs]
        for custom_name, filter_value in merged.items():
            if filter_value.activated:
                matches.append(
                    filter_value.does_match(peer_id, customs[custom_name]))
        if False in matches and not self.filter_or:
            return []
        else:
            return [matche for matche in matches if not matche is False]
