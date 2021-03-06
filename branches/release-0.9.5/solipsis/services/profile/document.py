# pylint: disable-msg=W0223,R0922
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

import re
import os.path
import ConfigParser
from os.path import isfile, isdir
from solipsis.services.profile import PROFILE_EXT, DEFAULT_INTERESTS, ENCODING
from solipsis.services.profile.prefs import get_prefs
from solipsis.services.profile.data import  Blogs, retro_compatibility, \
     DirContainer, SharedFiles, PeerDescriptor

SECTION_PERSONAL = "Personal"
SECTION_CUSTOM = "Custom"
SECTION_OTHERS = "Others"
SECTION_FILE = "Files"

#TODO: move download repo in option object

def read_document(stream):
    """use FileDocument to load document"""
    from solipsis.services.profile.file_document import FileDocument
    encoding = stream.readline()[1:]
    config = CustomConfigParser(encoding)
    config.readfp(stream)
    stream.close()
    try:
        pseudo = unicode(config.get(SECTION_PERSONAL,
                                    "pseudo", "Anonymous"),
                         ENCODING)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        print "Could not retreive pseudo"
        pseudo = u"Anonymous"
    doc = FileDocument(pseudo)
    doc.encoding = encoding
    doc.config = config
    return doc

def load_document(pseudo, directory=None):
    """build FileDocumentn from file"""
    assert isinstance(pseudo, unicode), "pseudo must be a unicode"
    if directory is None:
        directory = get_prefs("profile_dir")
    from solipsis.services.profile.file_document import FileDocument
    doc = FileDocument(pseudo, directory)
    if not doc.load():
        print "Could not find document"
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
            self.set_title(other_document.get_title())
            self.set_firstname(other_document.get_firstname())
            self.set_lastname(other_document.get_lastname())
            self.set_photo(other_document.get_photo())
            self.set_email(other_document.get_email())
            # custom data
            attributes = other_document.get_custom_attributes()
            for key, val in attributes.iteritems():
                self.add_custom_attributes((key, val))
        except TypeError, error:
            print error, "Using default values for personal data"

    def load_defaults(self):
        """set sample of default custom attributes"""
        for custom_interest in DEFAULT_INTERESTS:
            if not self.has_custom_attribute(custom_interest):
                self.add_custom_attributes((custom_interest, u""))
            
    # PERSONAL TAB    
    def set_title(self, value):
        """sets new value for title"""
        if value == self.get_title():
            return False
        if not isinstance(value, unicode):
            raise TypeError("title '%s' expected as unicode"% value)
    def get_title(self):
        """returns value of firstname"""
        raise NotImplementedError
        
    def set_firstname(self, value):
        """sets new value for firstname"""
        if value == self.get_firstname():
            return False
        if not isinstance(value, unicode):
            raise TypeError("firstname '%s' expected as unicode"% value)
    def get_firstname(self):
        """returns value of firstname"""
        raise NotImplementedError
        
    def set_lastname(self, value):
        """sets new value for lastname"""
        if value == self.get_lastname():
            return False
        if not isinstance(value, unicode):
            raise TypeError("lastname '%s' expected as unicode"% value)
    def get_lastname(self):
        """returns value of lastname"""
        raise NotImplementedError
    
    def set_photo(self, value):
        """sets new value for photo"""
        if value == self.get_photo():
            return False
        if not isinstance(value, unicode):
            raise TypeError("photo '%s' expected as unicode"% value)
        if not isfile(value):
            raise TypeError("photo '%s' must exist"% value)
    def get_photo(self):
        """returns value of photo"""
        raise NotImplementedError
        
    def set_email(self, value):
        """sets new value for email"""
        if value == self.get_email():
            return False
        if not isinstance(value, unicode):
            raise TypeError("email '%s' expected as unicode"% value)
    def get_email(self):
        """returns value of email"""
        raise NotImplementedError
        
    # CUSTOM TAB
    def has_custom_attribute(self, key):
        """return true if the key exists"""
        return False
    def add_custom_attributes(self, pair):
        """sets new value for custom_attributes"""
        if not isinstance(pair, list) and not isinstance(pair, tuple):
            raise TypeError("custom '%s' expected as list or tuple"% pair)
        elif len(pair) != 2:
            raise TypeError("custom expected as couple (key, value)")
        if not isinstance(pair[1], unicode):
            raise TypeError("tag '%s' expected as unicode"% pair[1])
    def remove_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        if not isinstance(value, unicode):
            raise TypeError("attribute '%s' expected as unicode"% value)
    def get_custom_attributes(self):
        """returns value of custom_attributes"""
        raise NotImplementedError

class AbstractSharingData:
    """define API for all file data"""

    def __init__(self):
        pass
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        try:
            # file data
            self.reset_files()
            for repo, sharing_cont in other_document.get_files().iteritems():
                self.add_file(repo)
                for container in sharing_cont.flat():
                    try:
                        self.share_file((container.get_path(),
                                         container._shared))
                        self.tag_file((container.get_path(),
                                       container._tag))
                    except KeyError, err:
                        print "Error on file name:", err
        except TypeError, error:
            print error, "Using default values for files"
        
    # FILE TAB
    def reset_files(self):
        """empty all information concerning files"""
        raise NotImplementedError
        
    def add_file(self, value):
        """sets new value for repository"""
        if not isinstance(value, str):
            raise TypeError("repository '%s' expected as str"% value)
        if not isdir(value):
            raise AssertionError("repository %s does not exist"% value)       
        
    def del_file(self, value):
        """remove repository"""
        if not isinstance(value, str):
            raise TypeError("repository to remove expected as str")
        
    def get_files(self):
        """returns value of files"""
        raise NotImplementedError
        
    def add(self, value):
        """add directory into  repository"""
        if not isinstance(value, str):
            raise TypeError("dir to expand expected as str")
        
    def remove(self, value):
        """remove custom value"""
        if not isinstance(value, str):
            raise TypeError("dir to expand expected as str")
        
    def expand_dir(self, value):
        """update doc when dir expanded"""
        if not isinstance(value, str):
            raise TypeError("dir to expand expected as str")
        
    def expand_children(self, value):
        """update doc when dir expanded"""
        if not isinstance(value, str):
            raise TypeError("dir to expand expected as str")
        container = self.get_container(value)
        for dir_container in [cont for cont in container.values()
                              if isinstance(cont, DirContainer)]:
            self.expand_dir(dir_container.get_path())
            
    def recursive_share(self, (path, share)):
        """forward command to cache"""
        if not isinstance(path, str):
            raise TypeError("path expected as str")
        
    def share_files(self, triplet):
        """forward command to cache"""
        if not isinstance(triplet, list) and not isinstance(triplet, tuple):
            raise TypeError("argument expected as list or tuple")
        elif len(triplet) != 3:
            raise TypeError("argument of  expected as triplet"
                            " (dir_path, file_path, share)")
        if not isinstance(triplet[0], str):
            raise TypeError("path expected as str")
        if not isinstance(triplet[1], list) \
               and not isinstance(triplet[1], tuple):
            raise TypeError("names expected as list")

    def share_file(self, pair):
        """forward command to cache"""
        if not isinstance(pair, list) and not isinstance(pair, tuple):
            raise TypeError("argument of share_file expected as list or tuple")
        elif len(pair) != 2:
            raise TypeError("argument of  expected as couple"
                            " (file_path, share)")
        if not isinstance(pair[0], str):
            raise TypeError("path expected as str")
        
    def tag_files(self, triplet):
        """sets new value for tagged files"""
        if not isinstance(triplet, list) and not isinstance(triplet, tuple):
            raise TypeError("argument of tag_file expected as list or tuple")
        elif len(triplet) != 3:
            raise TypeError("argument of  expected as couple (file_path, tag)")
        if not isinstance(triplet[0], str):
            raise TypeError("path expected as str")
        if not isinstance(triplet[1], list) \
               and not isinstance(triplet[1], tuple):
            raise TypeError("name expected as unicode")
        if not isinstance(triplet[2], unicode):
            raise TypeError("tag expected as unicode")
        
    def tag_file(self, pair):
        """sets new value for tagged file"""
        if not isinstance(pair, list) and not isinstance(pair, tuple):
            raise TypeError("argument of tag_file expected as list or tuple")
        elif len(pair) != 2:
            raise TypeError("argument of  expected as couple (file_path, tag)")
        if not isinstance(pair[0], str):
            raise TypeError("path expected as str")
        if not isinstance(pair[1], unicode):
            raise TypeError("tag expected as unicode")
        
    def get_repositories(self):
        """returns value of files"""
        raise NotImplementedError

    def get_shared_files(self):
        """return {repo: shared files}"""
        shared = SharedFiles()
        for repository in self.get_repositories():
            # copy containers wich are shared. Copy does not copy
            # callbacks, which allows pickle to work on higher levels
            copied_container = self.get_container(repository).copy(
                validator=lambda container: (isinstance(container, DirContainer)
                                             or container._shared))
            shared[repository] = [f_container
                                  for f_container in copied_container.flat()
                                  if not isinstance(f_container, DirContainer)]
        return shared
        
    def get_shared(self, repo_path):
        """returns [shared containers]"""
        raise NotImplementedError

    def get_container(self, full_path):
        """returns File/DirContainer correspondind to full_path"""
        raise NotImplementedError

    def _get_sharing_container(self, value):
        """return DirContainer which root is value"""
        files = self.get_files()
        for root_path in files:
            if value.startswith(root_path):
                return files[root_path]
        raise KeyError("%s not in %s"% (value, str(files.keys())))
            
class AbstractContactsData:
    """define API for all contacts' data"""

    def __init__(self):
        # memory
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
                self.set_peer((peer_id,
                               PeerDescriptor(peer_desc.pseudo,
                                              document=peer_desc.document,
                                              blog=peer_desc.blog,
                                              state=peer_desc.state)))
        except TypeError, error:
            print error, "Using default values for contacts"

    # OTHERS TAB
    def reset_peers(self):
        """empty all information concerning peers"""
        raise NotImplementedError
        
    def set_peer(self, (peer_id, peer_desc)):
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

    def set_connected(self, (peer_id, connected)):
        """change connected status of given peer and updates views"""
        if self.has_peer(peer_id):
            peer_desc = self.get_peer(peer_id)
            peer_desc.set_connected(connected)
    
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

    def fill_data(self, (peer_id, document)):
        """stores CacheDocument associated with peer"""
        if not self.has_peer(peer_id):
            peer_desc = PeerDescriptor(document.pseudo, document=document)
            self.set_peer((peer_id, peer_desc))
        else:
            peer_desc = self.get_peer(peer_id)
        peer_desc.set_document(document)
        self.last_downloaded_desc = peer_desc
        return peer_desc

    def fill_blog(self, (peer_id, blog)):
        """stores CacheDocument associated with peer"""
        blog = retro_compatibility(blog)
        if not isinstance(blog, Blogs):
            raise TypeError("data expected as AbstractDocument")
        if not self.has_peer(peer_id):
            peer_desc = PeerDescriptor(blog.pseudo, blog=blog)
            self.set_peer((peer_id, peer_desc))
        else:
            peer_desc = self.get_peer(peer_id)
        peer_desc.set_blog(blog)
        self.last_downloaded_desc = peer_desc
        return peer_desc
            
    def fill_shared_files(self, (peer_id, files)):
        """connect shared files with shared files"""
        if not isinstance(files, SharedFiles):
            raise TypeError("data expected as SharedFiles")
        assert self.has_peer(peer_id), "no profile for %s in %s"\
               % (peer_id, self.__class__)
        peer_desc = self.get_peer(peer_id)
        peer_desc.set_shared_files(files)
        self.last_downloaded_desc = peer_desc
        return peer_desc

class SaverMixin:
    """Take in charge saving & loading of document. Leave funciton
    import_document to be redefined."""

    def __init__(self, pseudo, directory):
        # point out file where document is saved
        self.pseudo = pseudo
        self._dir = directory

    def __repr__(self):
        return self.pseudo

    def __str__(self):
        return self.pseudo

    def get_id(self):
        """return identifiant of Document"""
        return os.path.join(self._dir, self.pseudo) + PROFILE_EXT
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        raise NotImplementedError(
            "must call import_document on base classes describing data")
    
    def copy(self):
        """return copy of this document"""
        copied_doc = self.__class__(self.pseudo, self._dir)
        copied_doc.import_document(self)
        return copied_doc

    # MENU
    def save(self):
        """fill document with information from .profile file"""
        from solipsis.services.profile.file_document import FileDocument
        doc = FileDocument(self.pseudo, self._dir)
        doc.import_document(self)
        doc.save()
        
    def load(self):
        """fill document with information from .profile file"""
        from solipsis.services.profile.file_document import FileDocument
        doc = FileDocument(self.pseudo, self._dir)
        result = doc.load()
        self.import_document(doc)
        return result
        
    def to_stream(self):
        """fill document with information from .profile file"""
        from solipsis.services.profile.file_document import FileDocument
        doc = FileDocument(self.pseudo, self._dir)
        doc.import_document(self)
        return doc.to_stream()

        
class AbstractDocument(AbstractPersonalData, AbstractSharingData,
                       AbstractContactsData, SaverMixin):
    """data container on file"""

    def __init__(self, pseudo, directory=None):
        assert isinstance(pseudo, unicode), "pseudo must be a unicode"
        if directory is None:
            directory = get_prefs("profile_dir")
        AbstractPersonalData.__init__(self)
        AbstractSharingData.__init__(self)
        AbstractContactsData.__init__(self)
        SaverMixin.__init__(self, pseudo, directory)
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        AbstractPersonalData.import_document(self, other_document)
        AbstractSharingData.import_document(self, other_document)
        AbstractContactsData.import_document(self, other_document)

    def load(self):
        """load default values if no file"""
        if not SaverMixin.load(self):
            AbstractPersonalData.load_defaults(self)
            return False
        else:
            return True
