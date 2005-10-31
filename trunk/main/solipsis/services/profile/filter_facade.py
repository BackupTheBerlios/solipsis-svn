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
"""Design pattern Facade: presents working API for all actions of GUI
available. This facade will be used both by GUI and unittests."""

__revision__ = "$Id: simple_facade.py 864 2005-09-30 07:27:23Z emb $"

from sys import stderr
from solipsis.services.profile import FILTER_EXT
from solipsis.services.profile.facade import AbstractFacade
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.filter_document import FilterDocument

def create_filter_facade(node_id):
    """implements pattern singleton on FilterFacade"""
    FilterFacade.filter_facade = FilterFacade(node_id)
    return FilterFacade.filter_facade

def get_filter_facade():
    """implements pattern singleton on FilterFacade"""
    if FilterFacade.filter_facade == None and get_facade() != None:
        create_filter_facade(get_facade()._desc.node_id)
    return FilterFacade.filter_facade

class FilterFacade(AbstractFacade):
    """facade associating a FilterDocument and a FilterView"""

    filter_facade = None

    def __init__(self, node_id):
        AbstractFacade.__init__(self, node_id, FilterDocument())

    # menu
    def save(self, directory=None):
        """save .profile.solipsis"""
        AbstractFacade.save(self, directory=directory,
                            doc_extension=FILTER_EXT)

    def load(self, directory=None):
        """load .profile.solipsis"""
        AbstractFacade.load(self, directory=directory,
                            doc_extension=FILTER_EXT)

    # filters
    def get_filter(self, filter_name):
        return self._desc.document.filters[filter_name]
    
    def get_results(self, filter_name):
        return self._desc.document.results[filter_name]
        
    def update_file_filter(self, filter_name, **props):
        self._desc.document.update_file_filter(filter_name, **props)
        for view in self.views.values():
            view.update_filter(filter_name)
        
    def update_profile_filter(self, filter_name, filter_or, customs, **props):
        self._desc.document.update_profile_filter(
            filter_name, filter_or, customs, **props)
        for view in self.views.values():
            view.update_filter(filter_name)

    def match(self, peer_desc, filter_names=None):
        self._desc.document.match(peer_desc, filter_names)
        for view in self.views.values():
            if filter_names is None:
                filter_names = self._desc.document.filters.keys()
            for filter_name in filter_names:
                view.update_filter(filter_name)

    def delete_filters(self, filter_names):
        for filter_name in filter_names:
            if filter_name in  self._desc.document.filters:
                del self._desc.document.filters[filter_name]
            if filter_name in self._desc.document.results:
                del self._desc.document.results[filter_name]
            for view in self.views.values():
                view.delete_filter(filter_name)
