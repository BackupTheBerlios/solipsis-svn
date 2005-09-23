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

import ConfigParser
import os.path
import time
import sys
from solipsis.services.profile import PROFILE_EXT, ENCODING, QUESTION_MARK
from solipsis.services.profile.prefs import get_prefs
from solipsis.services.profile.path_containers import DEFAULT_TAG, \
     DirContainer, ContainerMixin
from solipsis.services.profile.data import PeerDescriptor, load_blogs
from solipsis.services.profile.filter_document import FilterSaverMixin
from solipsis.services.profile.document import CustomConfigParser, \
     AbstractPersonalData, AbstractSharingData, AbstractContactsData, \
     SECTION_PERSONAL, SECTION_CUSTOM, SECTION_OTHERS, SECTION_FILE

SHARED_TAG = "shared"

class FilePersonalMixin(AbstractPersonalData):
    """Implements API for all pesonal data in a File oriented context"""

    def __init__(self, pseudo):
        self.config.add_section(SECTION_PERSONAL)
        self.config.set(SECTION_PERSONAL, "pseudo",
                        pseudo.encode(self.encoding))
        self.config.add_section(SECTION_CUSTOM)
        AbstractPersonalData.__init__(self)
        
    # PERSONAL TAB
    def set_title(self, value):
        """sets new value for title"""
        AbstractPersonalData.set_firstname(self, value)
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
        AbstractPersonalData.set_firstname(self, value)
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
        AbstractPersonalData.set_lastname(self, value)
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
        AbstractPersonalData.set_photo(self, value)
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
        AbstractPersonalData.set_email(self, value)
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

    # CUSTOM TAB
    def has_custom_attribute(self, key):
        """return true if the key exists"""
        return self.config.has_option(SECTION_CUSTOM, key)
        
    def add_custom_attributes(self, pair):
        """sets new value for custom_attributes"""
        AbstractPersonalData.add_custom_attributes(self, pair)
        key, value = pair
        self.config.set(SECTION_CUSTOM, key, value.encode(self.encoding))

    def remove_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        AbstractPersonalData.remove_custom_attributes(self, value)
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

class FileSharingMixin(AbstractSharingData):
    """Implements API for all file data in a File oriented context"""

    def __init__(self):
        self.config.add_section(SECTION_FILE)
        AbstractSharingData.__init__(self)

    # FILE TAB
    def reset_files(self):
        """empty all information concerning files"""
        self.config.remove_section(SECTION_FILE)
        self.config.add_section(SECTION_FILE)
        AbstractSharingData.reset_files(self)

    def get_repositories(self):
        """return list of repos"""
        # lazy initialisation
        repos = AbstractSharingData.get_repositories(self)
        if len(repos) > 0:
            return repos
        # full init
        repos = self._init_repos()
        for repo in repos:
            AbstractSharingData.add_repository(self, repo)
        return AbstractSharingData.get_repositories(self)

    def _init_repos(self):
        try:
            return [repo for repo in self.config.get(
                SECTION_PERSONAL, "repositories").split(',')
                      if repo.strip() != '']
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return []
        
    def _set_repositories(self):
        """update list of repos"""
        repos_list = self.get_repositories()
        if repos_list == None:
            print "No repo to set."
            return 
        self.config.set(SECTION_PERSONAL, "repositories",
                        ",".join(repos_list))
        
    def get_files(self):
        """returns {root: DirContainer}"""
        # lazy initialisation
        if self.files != {}:
            return AbstractSharingData.get_files(self)
        # full init
        for repo in self._init_repos():
            self.files[repo] = DirContainer(repo)
        for option in self.config.options(SECTION_FILE):
            # get share & tag
            try:
                option_description = self.config.get(SECTION_FILE, option)
                option_share, option_tag = option_description.split(',')
                option_share =( option_share == SHARED_TAG)
                if isinstance(option_tag, str):
                    option_tag = unicode(option_tag, ENCODING)
            except (ValueError, ConfigParser.NoSectionError,
                    ConfigParser.NoOptionError):
                print >> sys.stderr, "option '%s' not well formated"% option_description
                option_share, option_tag = False, DEFAULT_TAG
            # add container
            container = self._get_sharing_container(option)
            container[option].share(option_share)
            container[option].tag(option_tag)
        return AbstractSharingData.get_files(self)

    def _set_files(self):
        """write in config"""
        files = self.get_files()
        for repo, dir_container in files.items():
            file_containers = dir_container.flat()
            for file_container in file_containers:
                key = os.path.join(repo, file_container.get_path())
                if file_container._shared or file_container._tag != DEFAULT_TAG:
                    value = ','.join((file_container._shared and SHARED_TAG or '',
                                      file_container._tag))
                    self.config.set(SECTION_FILE, key, value)

class FileContactMixin(AbstractContactsData):
    """Implements API for all contact data in a File oriented context"""

    def __init__(self):
        self.config.add_section(SECTION_OTHERS)
        AbstractContactsData.__init__(self)
        
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
        description = ",".join([peer_desc.pseudo.encode(self.encoding),
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
            if not isinstance(pseudo, unicode):
                pseudo = unicode(pseudo, self.encoding)
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
        peer_desc = AbstractContactsData._change_status(self, peer_id, status)
        if status != PeerDescriptor.ANONYMOUS:
            self._write_peer(peer_id, peer_desc)
        else:
            self.remove_peer(peer_id)

    def fill_data(self, (peer_id, document)):
        """stores CacheDocument associated with peer"""
        peer_desc = AbstractContactsData.fill_data(self, (peer_id, document))
        if peer_desc.state != PeerDescriptor.ANONYMOUS:
            self._write_peer(peer_id, peer_desc)

    def fill_blog(self, (peer_id, blog)):
        """stores CacheDocument associated with peer"""
        peer_desc = AbstractContactsData.fill_blog(self, (peer_id, blog))
        if peer_desc.state != PeerDescriptor.ANONYMOUS:
            blog.save()
            
    def fill_shared_files(self, (peer_id, files)):
        """connect shared files with shared files"""
        # nothing to do in FileDocuments when receiving files
        pass

class FileSaverMixin(FilterSaverMixin):
    """Implements API for saving & loading in a File oriented context"""

    def __init__(self, pseudo, directory):
        FilterSaverMixin.__init__(self, pseudo, directory)

    def get_id(self):
        """return identifiant of Document"""
        return os.path.join(self._dir, self.pseudo) + PROFILE_EXT
    
    # MENU
    def save(self):
        """fill document with information from .profile file"""
        self._set_repositories()
        self._set_files()
        FilterSaverMixin.save(self)
        
    def load(self,):
        """fill document with information from .profile file"""
        result = self._load_config()
        self.get_files()
        return result

    def to_stream(self):
        """returns a file object containing values"""
        self._set_repositories()
        self._set_files()
        return FilterSaverMixin.to_stream(self)

class FileDocument(FilePersonalMixin, FileSharingMixin,
                   FileContactMixin, FileSaverMixin):
    """Describes all data needed in profile in a file"""

    def __init__(self, pseudo, directory=None):
        assert isinstance(pseudo, unicode), "pseudo must be a unicode"
        if directory is None:
            directory = get_prefs("profile_dir")
        self.encoding = ENCODING
        self.config = CustomConfigParser(ENCODING)
        FilePersonalMixin.__init__(self, pseudo)
        FileSharingMixin.__init__(self)
        FileContactMixin.__init__(self)
        FileSaverMixin.__init__(self, pseudo, directory)

    def __str__(self):
        return "File document for %s"% self.pseudo.encode(self.encoding)
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        FilePersonalMixin.import_document(self, other_document)
        FileSharingMixin.import_document(self, other_document)
        FileContactMixin.import_document(self, other_document)

    def load(self):
        """load default values if no file"""
        if not FileSaverMixin.load(self):
            FilePersonalMixin.load_defaults(self)
            return False
        else:
            return True
    
