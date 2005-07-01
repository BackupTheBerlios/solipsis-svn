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

import ConfigParser
import os.path
import time
import tempfile
import sys
import re
from os.path import isfile, isdir
from solipsis.services.profile import ENCODING, QUESTION_MARK, \
     PROFILE_DIR, PROFILE_EXT, DOWNLOAD_REPO, DEFAULT_INTERESTS
from solipsis.services.profile.data import DEFAULT_TAG, \
     DirContainer, FileContainer, ContainerMixin, \
     SharedFiles, PeerDescriptor, \
     Blogs, retro_compatibility, load_blogs

DATE_FORMAT = "%d/%m/%Y"
SECTION_PERSONAL = "Personal"
SECTION_CUSTOM = "Custom"
SECTION_OTHERS = "Others"
SECTION_FILE = "Files"

SHARE_ALL = "All"
SHARE_NONE = "none"

NO_PATH = "UNKNOWN"

def read_document(stream):
    """use FileDocument to load document"""
    encoding = stream.readline()[1:]
    config = CustomConfigParser(encoding)
    config.readfp(stream)
    stream.close()
    try:
        pseudo = unicode(config.get(SECTION_PERSONAL, "pseudo", "Anonymous"),
                         encoding)
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        print "Could not retreive pseudo"
        pseudo = "Anonymous"
    doc = FileDocument(pseudo)
    doc.encoding = encoding
    doc.config = config
    return doc

def load_document(pseudo, directory=PROFILE_DIR):
    """build FileDocumentn from file"""
    doc = FileDocument(pseudo, directory)
    if not doc.load():
        print "Could not find document"
    return doc
    
class AbstractDocument:
    """Base class for data container. Acts as validator.

    Setters check input type. Getters are abstract"""

    def __init__(self, pseudo, directory=PROFILE_DIR):
        # point out file where document is saved
        self.pseudo = pseudo
        self._dir = directory
        # memory
        self.last_downloaded_desc = None
        # load default values
        for custom_interest in DEFAULT_INTERESTS:
            if not self.has_custom_attribute(custom_interest):
                self.add_custom_attributes((custom_interest, u""))

    def __repr__(self):
        return self.pseudo

    def get_id(self):
        """return identifiant of Document"""
        return os.path.join(self._dir, self.pseudo) + PROFILE_EXT

    def get_last_downloaded_desc(self):
        """return identifiant of Document"""
        return self.last_downloaded_desc

    def copy(self):
        """return copy of this document"""
        copied_doc = self.__class__(self.pseudo, self._dir)
        copied_doc.import_document(self)
        return copied_doc
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        #TODO: use better system for catching exceptions
        try:
            # personal data (unicode)
            self.set_title(other_document.get_title())
            self.set_firstname(other_document.get_firstname())
            self.set_lastname(other_document.get_lastname())
            self.set_photo(other_document.get_photo())
            self.set_email(other_document.get_email())
            self.set_download_repo(other_document.get_download_repo())
            # custom data
            attributes = other_document.get_custom_attributes()
            for key, val in attributes.iteritems():
                self.add_custom_attributes((key, val))
            # file data
            self.reset_files()
            for repo, sharing_cont in other_document.get_files().iteritems():
                self.add_repository(repo)
                for full_path, container in sharing_cont.flat().iteritems():
                    self.share_file((full_path, container._shared))
                    self.tag_file((full_path, container._tag))
            # others' data
            self.reset_peers()
            peers = other_document.get_peers()
            for peer_id, peer_desc in peers.iteritems():
                self.set_peer((peer_id, PeerDescriptor(peer_desc.pseudo,
                                                       document=peer_desc.document,
                                                       blog=peer_desc.blog,
                                                       state=peer_desc.state)))
        except TypeError, error:
            print error, "Using default values"

    # MENU
    def save(self):
        """fill document with information from .profile file"""
        doc = FileDocument(self.pseudo, self._dir)
        doc.import_document(self)
        doc.save()
        
    def load(self):
        """fill document with information from .profile file"""
        doc = FileDocument(self.pseudo, self._dir)
        result = doc.load()
        self.import_document(doc)
        return result
        
    def to_stream(self):
        """fill document with information from .profile file"""
        doc = FileDocument(self.pseudo, self._dir)
        doc.import_document(self)
        return doc.to_stream()
    
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
        
    def set_download_repo(self, value):
        """sets new value for download_repo"""
        if not isinstance(value, unicode):
            raise TypeError("download_repo '%s' expected as unicode"% value)
    def get_download_repo(self):
        """returns value of download_repo"""
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
        
    # FILE TAB
    def reset_files(self):
        """empty all information concerning files"""
        raise NotImplementedError
        
    def add_repository(self, value):
        """sets new value for repository"""
        if not isinstance(value, unicode):
            raise TypeError("repository '%s' expected as unicode"% value)
        if not isdir(value):
            raise AssertionError("repository %s does not exist"% value) 
        if not isinstance(value, unicode):
            raise TypeError("repository to add expected as unicode")       
        
    def remove_repository(self, value):
        """remove repository"""
        if not isinstance(value, unicode):
            raise TypeError("repository to remove expected as unicode")
        
    def add(self, value):
        """add directory into  repository"""
        if not isinstance(value, unicode):
            raise TypeError("dir to expand expected as unicode")
        
    def remove(self, value):
        """remove custom value"""
        if not isinstance(value, unicode):
            raise TypeError("dir to expand expected as unicode")
        
    def expand_dir(self, value):
        """update doc when dir expanded"""
        if not isinstance(value, unicode):
            raise TypeError("dir to expand expected as unicode")
        
    def expand_children(self, value):
        """update doc when dir expanded"""
        if not isinstance(value, unicode):
            raise TypeError("dir to expand expected as unicode")
        container = self.get_container(value)
        for dir_container in [cont for cont in container.values()
                              if isinstance(cont, DirContainer)]:
            self.expand_dir(dir_container.path)

    def share_dirs(self, pair):
        """forward command to cache"""
        if not isinstance(pair, list) and not isinstance(pair, tuple):
            raise TypeError("argument ofshare_dir expected as list or tuple")
        elif len(pair) != 2:
            raise TypeError("argument o fshare_dir expected as"
                            " couple (path, share)")
        if not isinstance(pair[0], list) and not isinstance(pair[0], tuple):
            raise TypeError("names expected as list or tuple")

    def share_files(self, triplet):
        """forward command to cache"""
        if not isinstance(triplet, list) and not isinstance(triplet, tuple):
            raise TypeError("argument expected as list or tuple")
        elif len(triplet) != 3:
            raise TypeError("argument of  expected as triplet"
                            " (dir_path, file_path, share)")
        if not isinstance(triplet[0], unicode):
            raise TypeError("path expected as unicode")
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
        if not isinstance(pair[0], unicode):
            raise TypeError("path expected as unicode")
        
    def tag_files(self, triplet):
        """sets new value for tagged files"""
        if not isinstance(triplet, list) and not isinstance(triplet, tuple):
            raise TypeError("argument of tag_file expected as list or tuple")
        elif len(triplet) != 3:
            raise TypeError("argument of  expected as couple (file_path, tag)")
        if not isinstance(triplet[0], unicode):
            raise TypeError("path expected as unicode")
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
        if not isinstance(pair[0], unicode):
            raise TypeError("path expected as unicode")
        if not isinstance(pair[1], unicode):
            raise TypeError("tag expected as unicode")
        
    def get_files(self):
        """returns value of files"""
        raise NotImplementedError
        
    def get_repositories(self):
        """returns value of files"""
        raise NotImplementedError

    def get_shared_files(self):
        """return {repo: shared files}"""
        shared = SharedFiles()
        for repository in self.get_repositories():
            shared_files = [file_cont for file_cont
                            in self.get_shared(repository)
                            if (isinstance(file_cont, ContainerMixin)
                                and not isinstance(file_cont, DirContainer))]
            shared_dirs = [dir_container for dir_container
                           in self.get_shared(repository)
                           if isinstance(dir_container, DirContainer)]
            for shared_dir in shared_dirs:
                shared_dir.expand_dir()
                shared_files += [file_cont for file_cont
                                 in shared_dir.values()
                                 if isinstance(file_cont, FileContainer)
                                 and not file_cont in shared_files]
            shared[repository] = shared_files
        return shared
        
    def get_shared(self, repo_path):
        """returns [shared containers]"""
        raise NotImplementedError

    def get_container(self, full_path):
        """returns File/DirContainer correspondind to full_path"""
        raise NotImplementedError
            
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
        if not isinstance(document, AbstractDocument):
            raise TypeError("data expected as AbstractDocument")
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
        

class CacheDocument(AbstractDocument):
    """data container on cache"""

    def __init__(self, pseudo, directory=PROFILE_DIR):
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
        # {root: DirContainers}
        self.files = {}
        # dictionary of peers. {pseudo : PeerDescriptor}
        self.peers = {}
        AbstractDocument.__init__(self, pseudo, directory)

    def __str__(self):
        return self.__dict__
        
    # MENU

    # used base method: saving / loading not implemented
        
    # PERSONAL TAB
    def set_title(self, value):
        """sets new value for title"""
        if AbstractDocument.set_title(self, value) is False:
            return False
        self.title = value
        return self.title
    
    def get_title(self):
        """returns value of title"""
        return self.title
        
    def set_firstname(self, value):
        """sets new value for firstname"""
        if AbstractDocument.set_firstname(self, value) is False:
            return False
        self.firstname = value
        return self.firstname
    
    def get_firstname(self):
        """returns value of firstname"""
        return self.firstname

    def set_lastname(self, value):
        """sets new value for lastname"""
        if AbstractDocument.set_lastname(self, value) is False:
            return False
        self.lastname = value
        return self.lastname
    
    def get_lastname(self):
        """returns value of lastname"""
        return self.lastname

    def set_photo(self, value):
        """sets new value for photo"""
        if AbstractDocument.set_photo(self, value) is False:
            return False
        self.photo = value
        return self.photo
    
    def get_photo(self):
        """returns value of photo"""
        return self.photo

    def set_email(self, value):
        """sets new value for email"""
        if AbstractDocument.set_email(self, value) is False:
            return False
        self.email = value
        return self.email
    
    def get_email(self):
        """returns value of email"""
        return self.email

    def set_download_repo(self, value):
        """sets new value for download_repo"""
        AbstractDocument.set_download_repo(self, value)
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
        AbstractDocument.add_custom_attributes(self, pair)
        key, value = pair
        self.custom_attributes[key] = value
        
    def remove_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        AbstractDocument.remove_custom_attributes(self, value)
        if self.custom_attributes.has_key(value):
            del self.custom_attributes[value]
            
    def get_custom_attributes(self):
        """returns value of custom_attributes"""
        return self.custom_attributes

    # FILE TAB
    def reset_files(self):
        """empty all information concerning files"""
        self.files = {}
    
    def add_repository(self, value):
        """create new DirContainer"""
        AbstractDocument.add_repository(self, value)
        for existing_repo in self.files:
            if value.startswith(existing_repo):
                raise ValueError("'%s' part of existing repo %s"\
                                 %(value, existing_repo))
            if existing_repo.startswith(value):
                raise ValueError("'%s' conflicts with existing repo %s"\
                                 %(value, existing_repo))
            # else: continue
        self.files[value] = DirContainer(value)
        
    def remove_repository(self, value):
        """create new DirContainer"""
        AbstractDocument.remove_repository(self, value)
        del self.files[value]

    def get_repositories(self):
        """return list of repos"""
        return dict.keys(self.files)
        
    def add(self, value):
        """sets new value for repository"""
        AbstractDocument.add(self, value)
        self._get_sharing_container(value).add(value)
        
    def remove(self, value):
        """remove custom value"""
        AbstractDocument.remove(self, value)
        container = self._get_sharing_container(value)
        if container:
            del container[value]
        else:
            print "%s already removed"% value
        
    def expand_dir(self, value):
        """update doc when dir expanded"""
        AbstractDocument.expand_dir(self, value)
        self._get_sharing_container(value).expand_dir(value)

    def share_dirs(self, pair):
        """forward command to cache"""
        AbstractDocument.share_dirs(self, pair)
        paths, share = pair
        for path in paths:
            self._get_sharing_container(path).share_content(path, share)

    def share_files(self, triplet):
        """forward command to cache"""
        AbstractDocument.share_files(self, triplet)
        path, names, share = triplet
        files = [os.path.join(path, name) for name in names]
        self._get_sharing_container(path).share_container(files, share)

    def share_file(self, pair):
        """forward command to cache"""
        AbstractDocument.share_file(self, pair)
        path, share = pair
        self._get_sharing_container(path).share_container(path, share)
        
    def tag_files(self, triplet):
        """sets new value for tagged file"""
        AbstractDocument.tag_files(self, triplet)
        path, names, tag = triplet
        files = [os.path.join(path, name) for name in names]
        self._get_sharing_container(path).tag_container(files, tag)
        
    def tag_file(self, pair):
        """sets new value for tagged file"""
        AbstractDocument.tag_file(self, pair)
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

# FILEDOCUMENT
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

class FileDocument(AbstractDocument):
    """data container on file"""

    def __init__(self, pseudo, directory=PROFILE_DIR):
        self.encoding = ENCODING
        self.config = CustomConfigParser(ENCODING)
        self.config.add_section(SECTION_PERSONAL)
        self.config.set(SECTION_PERSONAL, "pseudo", pseudo)
        self.config.add_section(SECTION_CUSTOM)
        self.config.add_section(SECTION_FILE)
        self.config.add_section(SECTION_OTHERS)
        AbstractDocument.__init__(self, pseudo, directory)

    def __str__(self):
        return self.pseudo
    
    # MENU

    def save(self):
        """fill document with information from .profile file"""
        profile_file = open(self.get_id(), 'w')
        profile_file.write("#%s\n"% self.encoding)
        self.config.write(profile_file)
        profile_file.close()
        
    def load(self,):
        """fill document with information from .profile file"""
        # load profile
        if not os.path.exists(self.get_id()):
            print "profile %s does not exists"% self.get_id()
            return False
        else:
            profile_file = open(self.get_id())
            self.encoding = profile_file.readline()[1:]
            self.config = CustomConfigParser(self.encoding)
            self.config.readfp(profile_file)
            profile_file.close()
            return True

    def to_stream(self):
        """returns a file object containing values"""
        file_obj = tempfile.TemporaryFile()
        file_obj.write("#%s\n"% self.encoding)
        self.config.write(file_obj)
        file_obj.seek(0)
        return file_obj
        
    # PERSONAL TAB
    def set_title(self, value):
        """sets new value for title"""
        AbstractDocument.set_firstname(self, value)
        self.config.set(SECTION_PERSONAL, "title",
                        value.encode(self.encoding))
        return value.encode(self.encoding)
    
    def get_title(self):
        """returns value of title"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "title"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u""
        
    def set_firstname(self, value):
        """sets new value for firstname"""
        AbstractDocument.set_firstname(self, value)
        self.config.set(SECTION_PERSONAL, "firstname",
                        value.encode(self.encoding))
        return value.encode(self.encoding)
    
    def get_firstname(self):
        """returns value of firstname"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "firstname",
                                           "Emmanuel"), self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"Name"

    def set_lastname(self, value):
        """sets new value for lastname"""
        AbstractDocument.set_lastname(self, value)
        self.config.set(SECTION_PERSONAL, "lastname",
                        value.encode(self.encoding))
        return value.encode(self.encoding)
    
    def get_lastname(self):
        """returns value of lastname"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "lastname"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"Lastname"

    def set_photo(self, value):
        """sets new value for photo"""
        AbstractDocument.set_photo(self, value)
        self.config.set(SECTION_PERSONAL, "photo",
                        value.encode(self.encoding))
        return value.encode(self.encoding)
    
    def get_photo(self):
        """returns value of photo"""
        try:
            photo = unicode(self.config.get(SECTION_PERSONAL, "photo"),
                            self.encoding)
            if not os.path.exists(photo):
                photo = QUESTION_MARK()
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            photo = QUESTION_MARK()
        return photo

    def set_email(self, value):
        """sets new value for email"""
        AbstractDocument.set_email(self, value)
        self.config.set(SECTION_PERSONAL, "email",
                        value.encode(self.encoding))
        return value.encode(self.encoding)
    
    def get_email(self):
        """returns value of email"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "email"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"email"

    def set_download_repo(self, value):
        """sets new value for download_repo"""
        AbstractDocument.set_download_repo(self, value)
        self.config.set(SECTION_PERSONAL, "download_repo",
                        value.encode(self.encoding))
        
    def get_download_repo(self):
        """returns value of download_repo"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "download_repo"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return unicode(DOWNLOAD_REPO)

    # CUSTOM TAB
    def has_custom_attribute(self, key):
        """return true if the key exists"""
        return self.config.has_option(SECTION_CUSTOM, key)
        
    def add_custom_attributes(self, pair):
        """sets new value for custom_attributes"""
        AbstractDocument.add_custom_attributes(self, pair)
        key, value = pair
        self.config.set(SECTION_CUSTOM, key, value.encode(self.encoding))

    def remove_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        AbstractDocument.remove_custom_attributes(self, value)
        if self.config.has_option(SECTION_CUSTOM, value):
            self.config.remove_option(SECTION_CUSTOM, value)

    def get_custom_attributes(self):
        """returns value of custom_attributes"""
        result = {}
        try:
            options = self.config.options(SECTION_CUSTOM)
            for option in options:
                if option != "hobbies":
                    result[option] = unicode(
                        self.config.get(SECTION_CUSTOM, option),
                        self.encoding)
        finally:
            return result

    # FILE TAB
    def reset_files(self):
        """empty all information concerning files"""
        self._set_repositories([])
        self.config.remove_section(SECTION_FILE)
        self.config.add_section(SECTION_FILE)
        
    def add_repository(self, value):
        """create new DirContainer"""
        AbstractDocument.add_repository(self, value)
        existing_repos = self.get_repositories()
        # update list of repositories
        for existing_repo in existing_repos:
            if value.startswith(existing_repo):
                raise ValueError("'%s' part of existing repo %s"\
                                 %(value, existing_repo))
            if existing_repo.startswith(value):
                raise ValueError("'%s' conflicts with existing repo %s"\
                                 %(value, existing_repo))
            # else: continue
        existing_repos.append(value)
        self._set_repositories(existing_repos)
        
    def remove_repository(self, value):
        """create new DirContainer"""
        AbstractDocument.remove_repository(self, value)
        # delete entry
        values = [repo for repo in self.get_repositories()
                  if repo != value]
        # update list of repositories
        self._set_repositories(values)

    def get_repositories(self):
        """return list of repos"""
        try:
            return  [unicode(repo, self.encoding) for repo
                     in  self.config.get(SECTION_PERSONAL, "repositories")\
                     .split(',')
                     if repo.strip() != '']
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return []
        
    def _set_repositories(self, repos_list):
        """update list of repos"""
        self.config.set(SECTION_PERSONAL, "repositories",
                        ",".join(repos_list).encode(self.encoding))
        
    def add(self, value):
        """sets new value for files"""
        AbstractDocument.add(self, value)
        # html only stores shared/tagged files
        
    def remove(self, value):
        """remove custom value"""
        AbstractDocument.remove(self, value)
        if self.config.has_option(SECTION_CUSTOM, value):
            self.config.remove_option(SECTION_CUSTOM, value)
        
    def expand_dir(self, value):
        """put into cache new information when dir expanded in tree"""
        AbstractDocument.expand_dir(self, value)
        # html doc does not expand anything

    def share_dirs(self, pair):
        """forward command to cache"""
        AbstractDocument.share_dirs(self, pair)
        paths, share = pair
        for path in paths:
            for file_name in os.listdir(path):
                self._set_file(os.path.join(path, file_name), share=share)

    def share_files(self, triplet):
        """forward command to cache"""
        AbstractDocument.share_files(self, triplet)
        dir_path, names, share = triplet
        for name in names:
            self._set_file(os.path.join(dir_path, name), share=share)

    def share_file(self, pair):
        """forward command to cache"""
        AbstractDocument.share_file(self, pair)
        full_path, share = pair
        self._set_file(full_path, share=share)
                
    def tag_files(self, triplet):
        """sets new value for tagged file"""
        AbstractDocument.tag_files(self, triplet)
        dir_path, names, tag = triplet
        for name in names:
            self._set_file(os.path.join(dir_path, name), tag=tag)
        
    def tag_file(self, pair):
        """sets new value for tagged file"""
        AbstractDocument.tag_file(self, pair)
        path, tag = pair
        self._set_file(path, tag=tag)

    def _set_file(self, path, tag=None, share=None):
        """write in config"""
        # check validity
        if not os.path.exists(path):
            raise KeyError("%s not a file"% path)
        # retreive existing values
        old_share, old_tag = False, DEFAULT_TAG
        if self.config.has_option(SECTION_FILE, path):
            try:
                old_share, old_tag = self.config.get(SECTION_FILE, path)\
                                     .split(',')
            except (ValueError, ConfigParser.NoSectionError,
                    ConfigParser.NoOptionError):
                old_share, old_tag = False, DEFAULT_TAG
        # merge old values & new ones
        if tag is None:
            tag = old_tag
        if share is None:
            share = old_share
        # store
        if not share:
            share = ''
        else:
            share = "shared"
        self.config.set(SECTION_FILE, path, ','.join((share, tag)))
        
    def get_files(self):
        """returns {root: DirContainer}"""
        # >> repositories
        containers = self._get_containers()
        # >> files
        if not self.config.has_section(SECTION_FILE):
            self.config.add_section(SECTION_FILE)
        for option in self.config.options(SECTION_FILE):
            if isinstance(option, str):
                option = unicode(option, self.encoding)
            try:
                option_description = self.config.get(SECTION_FILE, option)
                if isinstance(option_description, str):
                    option_description =  unicode(option_description,
                                                  self.encoding)
                option_share, option_tag = option_description.split(',')
                option_share = bool(option_share)
            except (ValueError, ConfigParser.NoSectionError,
                    ConfigParser.NoOptionError):
                print >> sys.stderr, "option %s not well formated"% option
                option_share, option_tag = False, DEFAULT_TAG
            checked_in = False
            for root_path in dict.keys(containers):
                if option.startswith(root_path):
                    try:
                        containers[root_path].share_container(option,
                                                              option_share)
                        containers[root_path].tag_container(option,
                                                            option_tag)
                    except AssertionError, error:
                        print >> sys.stderr, str(error), "Removing from profile"
                        self.config.remove_option(SECTION_FILE, option)
                    checked_in = True
                    break
                #else not this repo
            if not checked_in:
                print "could not check in", option
        return containers

    def get_shared(self, repo_path):
        """returns  [shared containerMixin]"""
        result = []
        for option in self.config.options(SECTION_FILE):
            if option.startswith(repo_path):
                if isinstance(option, str):
                    option = unicode(option, self.encoding)
                try:
                    option_description = self.config.get(SECTION_FILE, option)
                    if isinstance(option_description, str):
                        option_description =  unicode(option_description,
                                                      self.encoding)
                    option_share, option_tag = option_description.split(',')
                    option_share = bool(option_share)
                except (ValueError, ConfigParser.NoSectionError,
                        ConfigParser.NoOptionError):
                    option_share, option_tag = False, DEFAULT_TAG
                if option_share:
                    result.append(
                        ContainerMixin(option, option_share, option_tag))
            else:
                continue
        return result

    def get_container(self, full_path):
        """returns File/DirContainer correspondind to full_path"""
        files = self.get_files()
        for root_path in files:
            if full_path.startswith(root_path):
                return files[root_path][full_path]
        raise KeyError("%s not in %s"% (full_path, str(files.keys())))
    
    def _get_containers(self):
        """return list of repos"""
        repo_list = self.get_repositories()
        result = {}
        for repo in repo_list:
            result[repo] = DirContainer(repo)
        return result

        
    # OTHERS TAB
    def reset_peers(self):
        """empty all information concerning peers"""
        self.config.remove_section(SECTION_OTHERS)
        self.config.add_section(SECTION_OTHERS)
        
    def set_peer(self, (peer_id, peer_desc)):
        """stores Peer object"""
        self._write_peer(peer_id, peer_desc)
        peer_desc.set_node_id(peer_id)
        
    def _write_peer(self, peer_id, peer_desc):
        """stores Peer object"""
        # extract name of files saved on HD
        if peer_desc.document:
            peer_desc.document.save()
        description = ",".join([peer_desc.pseudo,
                                peer_desc.state,
                                peer_id,
                                time.asctime()])
        self.config.set(SECTION_OTHERS, peer_id, description)
        
    def remove_peer(self, peer_id):
        """del Peer object"""
        if self.config.has_option(SECTION_OTHERS, peer_id):
            self.config.remove_option(SECTION_OTHERS, peer_id)

    def has_peer(self, peer_id):
        """checks peer exists"""
        return self.config.has_option(SECTION_OTHERS, peer_id)
        
    def get_peer(self, peer_id):
        """retreive stored value (friendship, path) for peer_id"""
        try:
            infos = self.config.get(SECTION_OTHERS, peer_id).split(",")
            pseudo, state, p_id, creation_date = infos
            if p_id != peer_id:
                print "file corrupted: %s (%s) != %s" \
                      % (p_id, creation_date, peer_id)
                return PeerDescriptor(pseudo)
            file_doc = None
            blogs = None
            file_doc = FileDocument(pseudo, self._dir)
            if file_doc.load():
                try: 
                    blogs = load_blogs(pseudo, file_doc._dir)
                except ValueError, err:
                    print str(err)
            return PeerDescriptor(pseudo,
                                  document=file_doc,
                                  blog=blogs,
                                  state=state,
                                  connected=False)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return  PeerDescriptor(u"Anonymous")
    
    def get_peers(self):
        """returns Peers"""
        result = {}
        if self.config.has_section(SECTION_OTHERS):
            options = self.config.options(SECTION_OTHERS)
            for peer_id in options:
                # check unicode
                if isinstance(peer_id, str):
                    peer_id = unicode(peer_id, self.encoding)
                # get info
                try:
                    peer_desc = self.get_peer(peer_id)
                    result[peer_id] = peer_desc
                except ValueError, error:
                    print error
        #else return default value
        return result

    def _change_status(self, peer_id, status):
        """mark given peer as Friend, Blacklisted or Anonymous"""
        peer_desc = AbstractDocument._change_status(self, peer_id, status)
        if status != PeerDescriptor.ANONYMOUS:
            self._write_peer(peer_id, peer_desc)
        else:
            self.remove_peer(peer_id)

    def fill_data(self, (peer_id, document)):
        """stores CacheDocument associated with peer"""
        peer_desc = AbstractDocument.fill_data(self, (peer_id, document))
        if peer_desc.state != PeerDescriptor.ANONYMOUS:
            self._write_peer(peer_id, peer_desc)

    def fill_blog(self, (peer_id, blog)):
        """stores CacheDocument associated with peer"""
        peer_desc = AbstractDocument.fill_blog(self, (peer_id, blog))
        if peer_desc.state != PeerDescriptor.ANONYMOUS:
            blog.save()
            
    def fill_shared_files(self, (peer_id, files)):
        """connect shared files with shared files"""
        # nothing to do in FileDocuments when receiving files
        pass

