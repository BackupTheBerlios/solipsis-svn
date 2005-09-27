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

from sys import stderr
from solipsis.services.profile.data import PeerDescriptor, Blogs
from solipsis.services.profile.cache_document import CacheDocument
from solipsis.services.profile.prefs import get_prefs

class SimpleFacade:
    """manages user's actions & connects document and view"""
    
    def __init__(self, pseudo, directory=None):
        assert isinstance(pseudo, unicode), "pseudo must be a unicode"
        if directory is None:
            directory = get_prefs("profile_dir")
        self._desc = PeerDescriptor(pseudo,
                                    document=CacheDocument(pseudo, directory),
                                    blog=Blogs(pseudo, directory))
        self._activated = True
        self.views = {}

    # views
    def add_view(self, view):
        """add  a view object to facade"""
        self.views[view.get_name()] = view
        view.import_desc(self._desc)

    # documents
    def import_document(self, document):
        """associate given document with peer"""
        self._desc.document.import_document(document)
        for view in self.views:
            view.import_desc(self._desc)

    # proxy
    def _try_change(self, setter, updater, *args, **kwargs):
        """Calls the setting function on a document (wich can be
        passed in **kwargs with the key 'document'), and calls the
        getting function on all views linked to the facade.

        returns value returned by setter"""
        if not 'document' in kwargs:
            document = self._desc.document
        else:
            document = kwargs['document']
        try:
            result = getattr(document, setter)(*args)
            for view in self.views.values():
                getattr(view, updater)()
            return result
        except TypeError, error:
            print >> stderr, str(error)
            raise
   
    def get_peer(self, peer_id):
        """returns PeerDescriptor with given id"""
        return self._desc.document.get_peer(peer_id)
    
    # MENU
    def load(self):
        """load .profile.solipsis"""
        try:
            self._desc.load(checked=True)
        except ValueError:
            print "Using blank one"
        # update
        for view in self.views.values():
            view.import_desc(self._desc)

    # PERSONAL TAB
    def change_title(self, title):
        """sets new value for title"""
        return self._try_change("set_title",
                                "update_title",
                                title)

    def change_firstname(self, firstname):
        """sets new value for firstname"""
        return self._try_change("set_firstname",
                                "update_firstname",
                                firstname)

    def change_lastname(self, lastname):
        """sets new value for lastname"""
        return self._try_change("set_lastname",
                                "update_lastname",
                                lastname)

    def change_photo(self, path):
        """sets new value for photo"""
        return self._try_change("set_photo",
                                "update_photo",
                                path)

    def change_email(self, email):
        """sets new value for email"""
        return self._try_change("set_email",
                                "update_email",
                                email)

    # CUSTOM TAB
    def add_custom_attributes(self, key, value):
        """sets new value for custom_attributes"""
        return self._try_change("add_custom_attributes",
                                "update_custom_attributes",
                                key, value)

    def del_custom_attributes(self, key):
        """sets new value for custom_attributes"""
        return self._try_change("remove_custom_attributes",
                                "update_custom_attributes",
                                key)

    # FILE TAB
    def add_repository(self, path):
        """sets new path for repositor"""
        return self._try_change("add_repository",
                                "update_files",
                                path)

    def del_repository(self, path):
        """sets new path for repositor"""
        return self._try_change("del_repository",
                                "update_files",
                                path)

    # OTHERS TAB
    def set_peer(self, peer_id, peer_desc):
        """sets peer as friend """
        return self._try_change("set_peer",
                                "update_peers",
                                peer_id, peer_desc)
    
    def remove_peer(self, peer_id):
        """sets peer as friend """
        return self._try_change("remove_peer",
                                "update_peers",
                                peer_id)

    def fill_data(self, peer_id, document):
        """sets peer as friend """
        return self._try_change("fill_data",
                                "update_peers",
                                peer_id, document)
