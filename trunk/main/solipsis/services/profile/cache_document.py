# pylint: disable-msg=W0131
# Missing docstring
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

from solipsis.services.profile import QUESTION_MARK, ENCODING
from solipsis.services.profile.prefs import get_prefs
from solipsis.services.profile.document import SaverMixin, \
     AbstractPersonalData, AbstractSharingData, AbstractContactsData

class CachePersonalMixin(AbstractPersonalData):
    """Implements API for all pesonal data in cache"""

    def __init__(self):
        self.title = u""
        self.firstname = u"Name"
        self.lastname = u"Lastname"
        self.photo = QUESTION_MARK()
        self.email = u"email"
        # dictionary of file. {att_name : att_value}
        self.custom_attributes = {}
        AbstractPersonalData.__init__(self)
        
    # PERSONAL TAB
    def set_title(self, title):
        if AbstractPersonalData.set_title(self, title) is False:
            return False
        self.title = title
        return self.title
    
    def get_title(self):
        return self.title
        
    def set_firstname(self, firstname):
        """sets new value for firstname"""
        if AbstractPersonalData.set_firstname(self, firstname) is False:
            return False
        self.firstname = firstname
        return self.firstname
    
    def get_firstname(self):
        return self.firstname

    def set_lastname(self, lastname):
        if AbstractPersonalData.set_lastname(self, lastname) is False:
            return False
        self.lastname = lastname
        return self.lastname
    
    def get_lastname(self):
        return self.lastname

    def set_photo(self, path):
        if AbstractPersonalData.set_photo(self, path) is False:
            return False
        self.photo = path
        return self.photo
    
    def get_photo(self):
        return self.photo

    def set_email(self, email):
        if AbstractPersonalData.set_email(self, email) is False:
            return False
        self.email = email
        return self.email
    
    def get_email(self):
        return self.email

    # CUSTOM TAB
    def has_custom_attribute(self, key):
        return self.custom_attributes.has_key(key)
    
    def add_custom_attributes(self, key, value):
        AbstractPersonalData.add_custom_attributes(self, key, value)
        self.custom_attributes[key] = value
        
    def remove_custom_attributes(self, key):
        AbstractPersonalData.remove_custom_attributes(self, key)
        if self.custom_attributes.has_key(key):
            del self.custom_attributes[key]
            
    def get_custom_attributes(self):
        return self.custom_attributes

class CacheSharingMixin(AbstractSharingData):
    """Implements API for all file data in cache"""

    def __init__(self):
        AbstractSharingData.__init__(self)

class CacheContactMixin(AbstractContactsData):
    """Implements API for all contact data in cache"""

    def __init__(self):
        # dictionary of peers. {pseudo : PeerDescriptor}
        self.peers = {}
        AbstractContactsData.__init__(self)
        
    # OTHERS TAB
    def reset_peers(self):
        """empty all information concerning peers"""
        self.peers = {}
        
    def set_peer(self, peer_id, peer_desc):
        self.peers[peer_id] = peer_desc
        peer_desc.set_node_id(peer_id)
        
    def remove_peer(self, peer_id):
        if self.peers.has_key(peer_id):
            del self.peers[peer_id]

    def has_peer(self, peer_id):
        return self.peers.has_key(peer_id)
    
    def get_peer(self, peer_id):
        return self.peers[peer_id]
    
    def get_peers(self):
        return self.peers

class CacheDocument(CachePersonalMixin, CacheSharingMixin,
                   CacheContactMixin, SaverMixin):
    """Describes all data needed in profile in a file"""

    def __init__(self, pseudo, directory=None):
        assert isinstance(pseudo, unicode), "pseudo must be a unicode"
        if directory is None:
            directory = get_prefs("profile_dir")
        CachePersonalMixin.__init__(self)
        CacheSharingMixin.__init__(self)
        CacheContactMixin.__init__(self)
        SaverMixin.__init__(self, pseudo, directory)

    def __str__(self):
        return "Cache document for %s"% self.pseudo.encode(ENCODING)
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        CachePersonalMixin.import_document(self, other_document)
        CacheSharingMixin.import_document(self, other_document)
        CacheContactMixin.import_document(self, other_document)

    def load(self, checked=True):
        """load default values if no file"""
        if not SaverMixin.load(self, checked=checked):
            CachePersonalMixin.load_defaults(self)
            return False
        else:
            return True
