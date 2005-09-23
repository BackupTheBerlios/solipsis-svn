# pylint: disable-msg=W0201
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

import os.path
from solipsis.services.profile import QUESTION_MARK, ENCODING
from solipsis.services.profile.prefs import get_prefs
from solipsis.services.profile.data import DirContainer
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
    def set_title(self, value):
        """sets new value for title"""
        if AbstractPersonalData.set_title(self, value) is False:
            return False
        self.title = value
        return self.title
    
    def get_title(self):
        """returns value of title"""
        return self.title
        
    def set_firstname(self, value):
        """sets new value for firstname"""
        if AbstractPersonalData.set_firstname(self, value) is False:
            return False
        self.firstname = value
        return self.firstname
    
    def get_firstname(self):
        """returns value of firstname"""
        return self.firstname

    def set_lastname(self, value):
        """sets new value for lastname"""
        if AbstractPersonalData.set_lastname(self, value) is False:
            return False
        self.lastname = value
        return self.lastname
    
    def get_lastname(self):
        """returns value of lastname"""
        return self.lastname

    def set_photo(self, value):
        """sets new value for photo"""
        if AbstractPersonalData.set_photo(self, value) is False:
            return False
        self.photo = value
        return self.photo
    
    def get_photo(self):
        """returns value of photo"""
        return self.photo

    def set_email(self, value):
        """sets new value for email"""
        if AbstractPersonalData.set_email(self, value) is False:
            return False
        self.email = value
        return self.email
    
    def get_email(self):
        """returns value of email"""
        return self.email

    # CUSTOM TAB
    def has_custom_attribute(self, key):
        """return true if the key exists"""
        return self.custom_attributes.has_key(key)
    
    def add_custom_attributes(self, pair):
        """sets new value for custom_attributes"""
        AbstractPersonalData.add_custom_attributes(self, pair)
        key, value = pair
        self.custom_attributes[key] = value
        
    def remove_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        AbstractPersonalData.remove_custom_attributes(self, value)
        if self.custom_attributes.has_key(value):
            del self.custom_attributes[value]
            
    def get_custom_attributes(self):
        """returns value of custom_attributes"""
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
        
    def set_peer(self, (peer_id, peer_desc)):
        """stores Peer object"""
        self.peers[peer_id] = peer_desc
        peer_desc.set_node_id(peer_id)
        
    def remove_peer(self, peer_id):
        """del Peer object"""
        if self.peers.has_key(peer_id):
            del self.peers[peer_id]

    def has_peer(self, peer_id):
        """checks peer exists"""
        return self.peers.has_key(peer_id)
    
    def get_peer(self, peer_id):
        """returns Peer with given id"""
        return self.peers[peer_id]
    
    def get_peers(self):
        """returns Peers"""
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

    def load(self):
        """load default values if no file"""
        if not SaverMixin.load(self):
            CachePersonalMixin.load_defaults(self)
            return False
        else:
            return True
