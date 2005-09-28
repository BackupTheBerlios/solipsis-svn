# pylint: disable-msg=W0131,W0223
# Missing docstring, not overriden
#
# <copyright>
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
"""Represents data used in model. Three pool of data;
 - personal data
 - file data
 - contacts' data"""

__revision__ = "$Id: $"

import re
import os.path
import ConfigParser
from os.path import isfile
from solipsis.services.profile import DEFAULT_INTERESTS
from solipsis.services.profile.path_containers import ContainerMixin,  \
     create_container, DictContainer, SharedFiles
from solipsis.services.profile.data import  Blogs, retro_compatibility, \
     PeerDescriptor

SECTION_PERSONAL = "Personal"
SECTION_CUSTOM = "Custom"
SECTION_OTHERS = "Others"
SECTION_FILE = "Files"

def read_document(stream):
    """use FileDocument to load document"""
    from solipsis.services.profile.file_document import FileDocument
    encoding = stream.readline()[1:]
    config = CustomConfigParser(encoding)
    config.readfp(stream)
    stream.close()
    doc = FileDocument()
    doc.encoding = encoding
    doc.config = config
    return doc
    
class CustomConfigParser(ConfigParser.ConfigParser):
    """simple wrapper to make config file case sensitive"""

    def __init__(self, encoding):
        ConfigParser.ConfigParser.__init__(self)
        self.encoding = encoding
    
    # only allow '=' to split key and value
    OPTCRE =  re.compile(
    r'(?P<option>[^=][^=]*)'              # very permissive!
    r'\s*(?P<vi>[=])\s*'                  # any number of space/tab,
                                          # followed by separator
                                          # (either : or =), followed
                                          # by any # space/tab
    r'(?P<value>.*)$'                     # everything up to eol
    )
    
    def optionxform(self, option):
        """override default implementation to make it case sensitive"""
        if isinstance(option, unicode):
            return option.encode(self.encoding)
        else:
            return str(option)

class AbstractPersonalData:
    """define API for all pesonal data"""

    def __init__(self):
        pass
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        try:
            # personal data (unicode)
            self.set_pseudo(other_document.get_pseudo())
            self.set_title(other_document.get_title())
            self.set_firstname(other_document.get_firstname())
            self.set_lastname(other_document.get_lastname())
            self.set_photo(other_document.get_photo())
            self.set_email(other_document.get_email())
            # custom data
            attributes = other_document.get_custom_attributes()
            for key, val in attributes.iteritems():
                self.add_custom_attributes(key, val)
        except TypeError, error:
            print error, "Using default values for personal data"

    def load_defaults(self):
        """set sample of default custom attributes"""
        for custom_interest in DEFAULT_INTERESTS:
            if not self.has_custom_attribute(custom_interest):
                self.add_custom_attributes(custom_interest, u"")
            
    # PERSONAL TAB    
    def set_pseudo(self, pseudo):
        if pseudo == self.get_pseudo():
            return False
        if not isinstance(pseudo, unicode):
            raise TypeError("pseudo '%s' expected as unicode"% pseudo)
        
    def get_pseudo(self):
        raise NotImplementedError
    
    def set_title(self, title):
        if title == self.get_title():
            return False
        if not isinstance(title, unicode):
            raise TypeError("title '%s' expected as unicode"% title)
        
    def get_title(self):
        raise NotImplementedError
        
    def set_firstname(self, firstname):
        if firstname == self.get_firstname():
            return False
        if not isinstance(firstname, unicode):
            raise TypeError("firstname '%s' expected as unicode"% firstname)
        
    def get_firstname(self):
        raise NotImplementedError
        
    def set_lastname(self, lastname):
        if lastname == self.get_lastname():
            return False
        if not isinstance(lastname, unicode):
            raise TypeError("lastname '%s' expected as unicode"% lastname)
        
    def get_lastname(self):
        raise NotImplementedError
    
    def set_photo(self, path):
        if path == self.get_photo():
            return False
        if not isinstance(path, unicode):
            raise TypeError("photo '%s' expected as unicode"% path)
        if not isfile(path):
            raise TypeError("photo '%s' must exist"% path)
        
    def get_photo(self):
        raise NotImplementedError
        
    def set_email(self, email):
        if email == self.get_email():
            return False
        if not isinstance(email, unicode):
            raise TypeError("email '%s' expected as unicode"% email)
        
    def get_email(self):
        raise NotImplementedError
        
    # CUSTOM TAB
    def has_custom_attribute(self, key):
        raise NotImplementedError
    
    def add_custom_attributes(self, key, value):
        if not (isinstance(key, unicode) or isinstance(key, str)) :
            raise TypeError("key '%s' expected as unicode"% key)
        if not isinstance(value, unicode):
            raise TypeError("tag '%s' expected as unicode"% value)
        
    def remove_custom_attributes(self, key):
        if not isinstance(key, unicode):
            raise TypeError("attribute '%s' expected as unicode"% key)
        
    def get_custom_attributes(self):
        raise NotImplementedError

class AbstractSharingData:
    """define API for all file data"""

    def __init__(self):
        # {root: Containers}
        self.files = {}
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        try:
            # file data
            self.reset_files()
            for repo, sharing_cont in \
                    other_document.get_files().iteritems():
                self.add_repository(repo)
                for container in sharing_cont.flat():
                    try:
                        self.share_file(container.get_path(), container._shared)
                        self.tag_file(container.get_path(), container._tag)
                    except KeyError, err:
                        print "Error on file name:", err
        except TypeError, error:
            print error, "Using default values for files"

    # FILE TAB
    def reset_files(self):
        """empty all information concerning files"""
        self.files = {}
        
    def get_repositories(self):
        return dict.keys(self.files)
        
    def add_repository(self, path, share=True, checked=True):
        """create a Container pointing to 'path' to directory"""
        # check type
        if not isinstance(path, str):
            raise TypeError("repository '%s' expected as str"% path)
        # already added?
        if path in self.files:
            return
        # included or including existing path?
        for repo in self.files:
            if path.startswith(repo):
                raise ValueError("'%s' part of existing repo %s"\
                                 %(path, repo))
            if repo.startswith(path):
                raise ValueError("'%s' conflicts with existing repo %s"\
                                 %(path, repo))
            # else: continue
        self.files[path] = create_container(path,
                                            share=share,
                                            checked=checked)      
        
    def del_repository(self, path):
        if not isinstance(path, str):
            raise TypeError("repository to remove expected as str")
        del self.files[path]
        
    def get_files(self):
        """returns {root: Container}"""
        return self.files
        
    def expand_dir(self, path):
        if not isinstance(path, str):
            raise TypeError("dir to expand expected as str")
        self._get_sharing_container(path).expand_dir(path)
        
    def expand_children(self, path):
        if not isinstance(path, str):
            raise TypeError("dir to expand expected as str")
        container = self.get_container(path)
        for dir_container in [cont for cont in container.values()
                              if isinstance(cont, DictContainer)]:
            self.expand_dir(dir_container.get_path())
        
    def share_files(self, path, names, share=True):
        if not isinstance(path, str):
            raise TypeError("path expected as str")
        if not isinstance(names, list) \
               and not isinstance(names, tuple):
            raise TypeError("names expected as list")
        if not isinstance(share, bool):
            raise TypeError("share expected as bool")
        files = [os.path.join(path, name) for name in names]
        for file_name in files:
            container = self.get_container(file_name)
            container.share(share)

    def share_file(self, path, share=True):
        if not isinstance(path, str):
            raise TypeError("path expected as str")
        if not isinstance(share, bool):
            raise TypeError("share expected as bool")
        self.get_container(path).share(share)

    def set_container(self, container):
        assert isinstance(container, ContainerMixin)
        parent_path = container.get_parent_path()
        parent_container = self.get_container(parent_path)
        parent_container[container.get_path()] = container
            
    def recursive_share(self, path, share):
        if not isinstance(path, str):
            raise TypeError("path expected as str")
        if not isinstance(share, bool):
            raise TypeError("share expected as bool")
        self.get_container(path).recursive_share(share)
        
    def tag_file(self, path, tag):
        if not isinstance(path, str):
            raise TypeError("path expected as str")
        if not isinstance(tag, unicode):
            raise TypeError("tag expected as unicode")
        self.get_container(path).tag(tag)

    def get_shared_files(self):
        """return {repo: shared files}"""
        shared = SharedFiles()
        for repository in self.get_repositories():
            # copy containers wich are shared. Copy does not copy
            # callbacks, which allows pickle to work on higher levels
            copied_container = self.get_container(repository).copy(
                validator=lambda container: (isinstance(container, DictContainer)
                                             or container._shared))
            shared[repository] = [f_container
                                  for f_container in copied_container.flat()
                                  if not isinstance(f_container, DictContainer)
                                  and f_container._shared]
        return shared
        
    def get_container(self, full_path):
        """returns Container correspondind to full_path"""
        return self._get_sharing_container(full_path)[full_path]

    def _get_sharing_container(self, path):
        """return Container which root is path"""
        for root_path in self.files:
            if path.startswith(root_path):
                return self.files[root_path]
        raise KeyError("%s not in %s"% (path, str(self.files.keys())))
            
class AbstractContactsData:
    """define API for all contacts' data"""

    def __init__(self):
        self.last_downloaded_desc = None

    def get_last_downloaded_desc(self):
        """return identifiant of Document"""
        return self.last_downloaded_desc

    def reset_last_downloaded_desc(self):
        """return identifiant of Document"""
        self.last_downloaded_desc = None
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        try:
            # others' data
            self.reset_peers()
            peers = other_document.get_peers()
            for peer_id, peer_desc in peers.iteritems():
                self.set_peer(peer_id,
                              PeerDescriptor(peer_id,
                                             document=peer_desc.document,
                                             blog=peer_desc.blog,
                                             state=peer_desc.state))
        except TypeError, error:
            print error, "Using default values for contacts"

    # OTHERS TAB
    def reset_peers(self):
        """empty all information concerning peers"""
        raise NotImplementedError
        
    def set_peer(self, peer_id, peer_desc):
        """stores Peer object"""
        raise NotImplementedError
        
    def remove_peer(self, peer_id):
        """del Peer object"""
        raise NotImplementedError

    def has_peer(self, peer_id):
        """checks peer exists"""
        raise NotImplementedError
    
    def get_peer(self, peer_id):
        """returns PeerDescriptor with given id"""
        raise NotImplementedError
    
    def get_peers(self):
        """returns Peers"""
        raise NotImplementedError
    
    def get_ordered_peers(self):
        """returns Peers"""
        peers = self.get_peers()
        peers_name = peers.keys()
        peers_name.sort()
        return [peers[name] for name in peers_name]

    def set_connected(self, peer_id, connected):
        """change connected status of given peer and updates views"""
        if self.has_peer(peer_id):
            peer_desc = self.get_peer(peer_id)
            peer_desc.connected = connected
    
    def make_friend(self, peer_id):
        """sets peer as friend """
        self._change_status(peer_id, PeerDescriptor.FRIEND)

    def blacklist_peer(self, peer_id):
        """sets new value for unshared file"""
        self._change_status(peer_id, PeerDescriptor.BLACKLISTED)

    def unmark_peer(self, peer_id):
        """sets new value for unshared file"""
        self._change_status(peer_id, PeerDescriptor.ANONYMOUS)      

    def _change_status(self, peer_id, status):
        """mark given peer as Friend, Blacklisted or Anonymous"""
        assert self.has_peer(peer_id), "no profile for %s"% peer_id
        peer_desc = self.get_peer(peer_id)
        peer_desc.state = status
        return peer_desc

    def fill_data(self, peer_id, document, flag_update=True):
        """stores CacheDocument associated with peer"""
        # set peer_desc
        if not self.has_peer(peer_id):
            peer_desc = PeerDescriptor(peer_id, document=document)
            self.set_peer(peer_id, peer_desc)
        else:
            peer_desc = self.get_peer(peer_id)
        # set data
        peer_desc.document = document
        if flag_update:
            self.last_downloaded_desc = peer_desc
        else:
            self.reset_last_downloaded_desc()
        return peer_desc

    def fill_blog(self, peer_id, blog, flag_update=True):
        """stores CacheDocument associated with peer"""
        blog = retro_compatibility(blog)
        if not isinstance(blog, Blogs):
            raise TypeError("data expected as AbstractDocument")
        # set peer_desc
        if not self.has_peer(peer_id):
            peer_desc = PeerDescriptor(peer_id, blog=blog)
            self.set_peer(peer_id, peer_desc)
        else:
            peer_desc = self.get_peer(peer_id)
        # set blog
        peer_desc.blog = blog
        if flag_update:
            self.last_downloaded_desc = peer_desc
        else:
            self.reset_last_downloaded_desc()
        return peer_desc
            
    def fill_shared_files(self, peer_id, files, flag_update=True):
        """connect shared files with shared files"""
        if not isinstance(files, SharedFiles):
            raise TypeError("data expected as SharedFiles")
        assert self.has_peer(peer_id), "no profile for %s in %s"\
               % (peer_id, self.__class__)
        peer_desc = self.get_peer(peer_id)
        # set repositories
        for repo in files:
            # do not check validity of path since files are located on
            # remote computer => checked=False
            peer_desc.document.add_repository(repo, checked=False)
        # set files
        for file_container in files.flatten():
            peer_desc.document.set_container(file_container)
        if flag_update:
            self.last_downloaded_desc = peer_desc
        else:
            self.reset_last_downloaded_desc()
        return peer_desc

class SaverMixin:
    """Take in charge saving & loading of document. Leave funciton
    import_document to be redefined."""

    def __init__(self):
        pass

    def import_document(self, other_document):
        """copy data from another document into self"""
        raise NotImplementedError(
            "import_document must be overridden")
    
    def copy(self):
        """return copy of this document"""
        copied_doc = self.__class__()
        copied_doc.import_document(self)
        return copied_doc

    # MENU
    def save(self, path):
        """fill document with information from .profile file"""
        from solipsis.services.profile.file_document import FileDocument
        doc = FileDocument()
        doc.import_document(self)
        doc.save(path)
        
    def load(self, path):
        """fill document with information from .profile file"""
        from solipsis.services.profile.file_document import FileDocument
        doc = FileDocument()
        result = doc.load(path)
        self.import_document(doc)
        return result
        
    def to_stream(self):
        """fill document with information from .profile file"""
        from solipsis.services.profile.file_document import FileDocument
        doc = FileDocument()
        doc.import_document(self)
        return doc.to_stream()

        
class AbstractDocument(AbstractPersonalData, AbstractSharingData,
                       AbstractContactsData, SaverMixin):
    """data container on file"""

    def __init__(self):
        AbstractPersonalData.__init__(self)
        AbstractSharingData.__init__(self)
        AbstractContactsData.__init__(self)
        SaverMixin.__init__(self)
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        AbstractPersonalData.import_document(self, other_document)
        AbstractSharingData.import_document(self, other_document)
        AbstractContactsData.import_document(self, other_document)

    def load(self, path):
        """load default values if no file"""
        if not SaverMixin.load(self, path):
            AbstractPersonalData.load_defaults(self)
            return False
        else:
            return True
