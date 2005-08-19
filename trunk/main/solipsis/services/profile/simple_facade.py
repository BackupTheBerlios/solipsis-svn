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
from solipsis.services.profile import ENCODING
from solipsis.services.profile.prefs import get_prefs

class SimpleFacade:
    """manages user's actions & connects document and view"""
    
    def __init__(self, pseudo, directory=None):
        assert isinstance(pseudo, unicode), "pseudo must be a unicode"
        if directory is None:
            directory = get_prefs("profile_dir")
        self._desc = None
        self.pseudo = pseudo
        self._activated = True
        self.views = {}

    def get_pseudo(self):
        """return pseudo"""
        return self.pseudo

    # views
    def add_view(self, view):
        """add  a view object to facade"""
        assert self._desc, "no document associated with facade"
        self.views[view.get_name()] = view
        view.import_desc(self._desc)

    # documents
    def get_document(self):
        """return document associated with peer"""
        assert self._desc, "no document associated with facade"
        return self._desc.document

    def import_document(self, document):
        """associate given document with peer"""
        assert self._desc, "no document associated with facade"
        self._desc.document.import_document(document)
        for view in self.views:
            view.import_desc(self._desc)

    # proxy
    def _try_change(self, value, setter, updater):
        """tries to call function doc_set and then, if succeeded, gui_update"""
        assert self._desc, "no document associated with facade"
        try:
            result = getattr(self._desc.document, setter)(value)
            for view in self.views.values():
                getattr(view, updater)()
            return result
        except TypeError, error:
            print >> stderr, str(error)
            raise

    def get_profile(self):
        """return a file object like on profile"""
        assert self._desc, "no document associated with facade"
        return self._desc.document.to_stream()
   
    def get_peers(self):
        """returns PeerDescriptor with given id"""
        assert self._desc, "no document associated with facade"
        return self._desc.document.get_peers()
    
    def get_peer(self, peer_id):
        """returns PeerDescriptor with given id"""
        assert self._desc, "no document associated with facade"
        return self._desc.document.get_peer(peer_id)
    
    def has_peer(self, peer_id):
        """returns PeerDescriptor with given id"""
        assert self._desc, "no document associated with facade"
        return self._desc.document.has_peer(peer_id)
    
    # MENU
    def activate(self, enable=True):
        """desactivate automatic sharing"""
        self._activated = enable

    def is_activated(self):
        """getter for self._activated"""
        return self._activated

    def save(self):
        """save .profile.solipsis"""
        assert self._desc, "no document associated with facade"
        self._desc.save()

    def load(self):
        """load .profile.solipsis"""
        assert self._desc, "no document associated with facade"
        try:
            self._desc.load()
        except ValueError, err:
            print "Using blank one"
            # BUG: UnicodeEncodeError
#             print err, "Using blank one"
            pass
        # update
        for view in self.views.values():
            view.import_desc(self._desc)

    # PERSONAL TAB
    def change_title(self, title):
        """sets new value for title"""
        return self._try_change(title,
                                "set_title",
                                "update_title")

    def change_firstname(self, firstname):
        """sets new value for firstname"""
        return self._try_change(firstname,
                               "set_firstname",
                               "update_firstname")

    def change_lastname(self, lastname):
        """sets new value for lastname"""
        return self._try_change(lastname,
                               "set_lastname",
                               "update_lastname")

    def change_photo(self, path):
        """sets new value for photo"""
        return self._try_change(path,
                               "set_photo",
                               "update_photo")

    def change_email(self, email):
        """sets new value for email"""
        return self._try_change(email,
                               "set_email",
                               "update_email")

    # CUSTOM TAB
    def add_custom_attributes(self, (key, value)):
        """sets new value for custom_attributes"""
        return self._try_change((key, value),
                               "add_custom_attributes",
                               "update_custom_attributes")

    def del_custom_attributes(self, key):
        """sets new value for custom_attributes"""
        return self._try_change(key,
                               "remove_custom_attributes",
                               "update_custom_attributes")

    # FILE TAB
    def add_file(self, path):
        """sets new value for repositor"""
        path = path.encode(ENCODING)
        return self._try_change(path,
                               "add_file",
                               "update_files")

    def del_file(self, path):
        """sets new value for repositor"""
        path = path.encode(ENCODING)
        return self._try_change(path,
                               "del_file",
                               "update_files")

    # OTHERS TAB
    def set_peer(self, (peer_id, peer_desc)):
        """sets peer as friend """
        return self._try_change((peer_id, peer_desc),
                                "set_peer",
                                "update_peers")
    
    def remove_peer(self, value):
        """sets peer as friend """
        return self._try_change(value,
                                "remove_peer",
                                "update_peers")

    def fill_data(self, (peer_id, document)):
        """sets peer as friend """
        return self._try_change((peer_id, document),
                                "fill_data",
                                "update_peers")
