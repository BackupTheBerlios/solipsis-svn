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
"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

__revision__ = "$Id$"

import re
from solipsis.services.profile import ENCODING
from solipsis.services.profile.filter_data import FilterValue, FileFilter, PeerFilter
from solipsis.services.profile.document import DocSaverMixin, ContactsMixin, \
     SECTION_PERSONAL, SECTION_CUSTOM, SECTION_FILE, \
     AbstractPersonalData

class FilterMixin:
    """Implements API for all pesonal data in cache"""
    
    def __init__(self):
        self.filters = {}
        # self.results = 
        # {name_1: {id_1: match, id_2: match},
        #  name_2: {...} ... }
        self.results = {}
        self._create_match_all()
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        for name, val in other_document.filters.items():
            self.filters[name] = val

    def _create_match_all(self):
        if u"All" not in self.filters:
            self.filters[u"All"] = PeerFilter(
                u"All", **{'pseudo': u'*'})

    def update_file_filter(self, filter_name, **props):
        if not filter_name in self.filters:
            self.filters[filter_name] = FileFilter(filter_name, **props)
        else:
            self.filters[filter_name].update_properties(**props)

    def update_profile_filter(self, filter_name, filter_or, customs, **props):
        if not filter_name in self.filters \
               or not isinstance(self.filters[filter_name], PeerFilter):
            new_filter = PeerFilter(filter_name, filter_or, **props)
            new_filter.update_customs(customs)
            self.filters[filter_name] = new_filter
        else:
            new_filter = self.filters[filter_name]
            new_filter.filter_or = filter_or
            new_filter.update_properties(**props)
            new_filter.update_customs(customs)
            
    def match(self, peer_desc, filter_names=None):
        # reduce used filters
        if not filter_names is None:
            filters = [filter_ for filter_name, filter_
                       in self.filters.items()
                       if filter_name in filter_names]
        else:
            filters = self.filters.values()
        # match
        for a_filter in filters:
            matches = []
            if isinstance(a_filter, PeerFilter):
                matches += a_filter.match(peer_desc.node_id,
                                          peer_desc.custom_as_dict(),
                                          **peer_desc.peer_as_dict())
            else:
                matches += a_filter.match(peer_desc.node_id,
                                          peer_desc.files_as_dicts())
            # order results
            if a_filter.filter_name in self.results:
                self.results[a_filter.filter_name][peer_desc.node_id] = matches
            else:
                self.results[a_filter.filter_name] = {peer_desc.node_id: matches}
        
class FilterSaverMixin(DocSaverMixin):
    """Implements API for saving & loading in a File oriented context"""

    FILTERS = [PeerFilter, FileFilter]
    
    def __init__(self, encoding=ENCODING):
        DocSaverMixin.__init__(self, encoding)

    # menu
    def save(self, path):
        for name, a_filter in self.filters.items():
            section_name = a_filter.PREFIX \
                           + (a_filter.filter_or and 'OR_' or 'AND_') \
                           + name
            if not self.config.has_section(section_name):
                self.config.add_section(section_name)
            for prop_name, value in a_filter.as_dict().items():
                self.config.set(section_name, prop_name, value)
        DocSaverMixin.save(self, path)
    
    def load(self, path):
        """fill document with information from .profile file"""
        # load config
        if not DocSaverMixin.load(self, path):
            return False
        # synchronize cache
        for section in self.config.sections():
            props = self.config.items(section)
            for filter_class in self.FILTERS:
                name, new_filter = filter_class.from_str(section, props)
                if new_filter is None:
                    continue
                else:
                    self.filters[name] = new_filter
                    break
        # add match all
        self._create_match_all()
                    
class FilterDocument(FilterMixin, FilterSaverMixin):
    """Describes all data needed in profile in a file"""

    def __init__(self):
        FilterMixin.__init__(self)
        FilterSaverMixin.__init__(self)
        
    def set_peer(self, peer_id, peer_desc):
        peer_desc.node_id = peer_id
        self.match(peer_desc)
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        FilterMixin.import_document(self, other_document)
        
