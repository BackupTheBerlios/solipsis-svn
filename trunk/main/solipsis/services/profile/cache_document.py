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
from solipsis.services.profile import QUESTION_MARK, \
     PROFILE_DIR, DOWNLOAD_REPO, DEFAULT_INTERESTS
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
        self.download_repo = unicode(DOWNLOAD_REPO)
        # dictionary of file. {att_name : att_value}
        self.custom_attributes = {}
        for interest in DEFAULT_INTERESTS:
            self.custom_attributes[interest] = u""
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

    def set_download_repo(self, value):
        """sets new value for download_repo"""
        AbstractPersonalData.set_download_repo(self, value)
        self.download_repo = value
    
    def get_download_repo(self):
        """returns value of download_repo"""
        return self.download_repo

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
        # {root: DirContainers}
        self.files = {}
        AbstractSharingData.__init__(self)
        
    # FILE TAB
    def reset_files(self):
        """empty all information concerning files"""
        self.files = {}
    
    def add_file(self, value):
        """create new DirContainer"""
        AbstractSharingData.add_file(self, value)
        for existing_repo in self.files:
            if value.startswith(existing_repo):
                raise ValueError("'%s' part of existing repo %s"\
                                 %(value, existing_repo))
            if existing_repo.startswith(value):
                raise ValueError("'%s' conflicts with existing repo %s"\
                                 %(value, existing_repo))
            # else: continue
        self.files[value] = DirContainer(value)
        
    def del_file(self, value):
        """create new DirContainer"""
        AbstractSharingData.del_file(self, value)
        del self.files[value]

    def get_repositories(self):
        """return list of repos"""
        return dict.keys(self.files)
        
    def add(self, value):
        """sets new value for repository"""
        AbstractSharingData.add(self, value)
        self._get_sharing_container(value).add(value)
        
    def remove(self, value):
        """remove custom value"""
        AbstractSharingData.remove(self, value)
        container = self._get_sharing_container(value)
        if container:
            del container[value]
        else:
            print "%s already removed"% value
        
    def expand_dir(self, value):
        """update doc when dir expanded"""
        AbstractSharingData.expand_dir(self, value)
        self._get_sharing_container(value).expand_dir(value)

    def share_dirs(self, pair):
        """forward command to cache"""
        AbstractSharingData.share_dirs(self, pair)
        paths, share = pair
        for path in paths:
            self._get_sharing_container(path).share_content(path, share)

    def share_files(self, triplet):
        """forward command to cache"""
        AbstractSharingData.share_files(self, triplet)
        path, names, share = triplet
        files = [os.path.join(path, name) for name in names]
        self._get_sharing_container(path).share_container(files, share)

    def share_file(self, pair):
        """forward command to cache"""
        AbstractSharingData.share_file(self, pair)
        path, share = pair
        self._get_sharing_container(path).share_container(path, share)
        
    def tag_files(self, triplet):
        """sets new value for tagged file"""
        AbstractSharingData.tag_files(self, triplet)
        path, names, tag = triplet
        files = [os.path.join(path, name) for name in names]
        self._get_sharing_container(path).tag_container(files, tag)
        
    def tag_file(self, pair):
        """sets new value for tagged file"""
        AbstractSharingData.tag_file(self, pair)
        path, tag = pair
        self._get_sharing_container(path).tag_container(path, tag)
        
    def get_files(self):
        """returns {root: DirContainer}"""
        return self.files
        
    def get_shared(self, repo_path):
        """returns [shared containers]"""
        return [container for container
                in self.files[repo_path].flat().values()
                if container._shared]

    def get_container(self, full_path):
        """returns File/DirContainer correspondind to full_path"""
        return self._get_sharing_container(full_path)[full_path]

    def _get_sharing_container(self, value):
        """return DirContainer which root is value"""
        for root_path in self.files:
            if value.startswith(root_path):
                return self.files[root_path]
        raise KeyError("%s not in %s"% (value, str(self.files.keys())))

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

    def __init__(self, pseudo, directory=PROFILE_DIR):
        CachePersonalMixin.__init__(self)
        CacheSharingMixin.__init__(self)
        CacheContactMixin.__init__(self)
        SaverMixin.__init__(self, pseudo, directory)
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        CachePersonalMixin.import_document(self, other_document)
        CacheSharingMixin.import_document(self, other_document)
        CacheContactMixin.import_document(self, other_document)
