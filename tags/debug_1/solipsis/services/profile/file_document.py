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

__revision__ = "$Id$"

import ConfigParser
import os.path
import time
import sys
from solipsis.services.profile import force_unicode, ENCODING, QUESTION_MARK
from solipsis.services.profile.path_containers import DEFAULT_TAG, \
     create_container, DictContainer
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.document import \
     AbstractPersonalData, FileSharingMixin, ContactsMixin, DocSaverMixin, \
     SECTION_PERSONAL, SECTION_CUSTOM, SECTION_OTHERS, SECTION_FILE

SHARED_TAG = "shared"

class FilePersonalMixin(AbstractPersonalData):
    """Implements API for all pesonal data in a File oriented context"""

    def __init__(self):
        self.config.add_section(SECTION_PERSONAL)
        self.config.add_section(SECTION_CUSTOM)
        AbstractPersonalData.__init__(self)
        
    # PERSONAL TAB
    def set_pseudo(self, pseudo):
        AbstractPersonalData.set_pseudo(self, pseudo)
        self.config.set(SECTION_PERSONAL, "pseudo",
                        pseudo.encode(self.encoding))
        return pseudo.encode(self.encoding)
    
    def get_pseudo(self):
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "pseudo"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u""
        
    def set_title(self, value):
        AbstractPersonalData.set_title(self, value)
        self.config.set(SECTION_PERSONAL, "title",
                        value.encode(self.encoding))
        return value.encode(self.encoding)
    
    def get_title(self):
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "title"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u""
        
    def set_firstname(self, value):
        AbstractPersonalData.set_firstname(self, value)
        self.config.set(SECTION_PERSONAL, "firstname",
                        value.encode(self.encoding))
        return value.encode(self.encoding)
    
    def get_firstname(self):
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "firstname",
                                           "Emmanuel"), self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"Name"

    def set_lastname(self, value):
        AbstractPersonalData.set_lastname(self, value)
        self.config.set(SECTION_PERSONAL, "lastname",
                        value.encode(self.encoding))
        return value.encode(self.encoding)
    
    def get_lastname(self):
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "lastname"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"Lastname"

    def set_photo(self, value):
        AbstractPersonalData.set_photo(self, value)
        self.config.set(SECTION_PERSONAL, "photo",
                        value.encode(self.encoding))
        return value.encode(self.encoding)
    
    def get_photo(self):
        try:
            photo = unicode(self.config.get(SECTION_PERSONAL, "photo"),
                            self.encoding)
            if not os.path.exists(photo):
                photo = QUESTION_MARK()
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            photo = QUESTION_MARK()
        return photo

    def set_email(self, value):
        AbstractPersonalData.set_email(self, value)
        self.config.set(SECTION_PERSONAL, "email",
                        value.encode(self.encoding))
        return value.encode(self.encoding)
    
    def get_email(self):
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "email"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"email"

    # CUSTOM TAB
    def has_custom_attribute(self, key):
        """return true if the key exists"""
        return self.config.has_option(SECTION_CUSTOM, key)
        
    def add_custom_attributes(self, key, value):
        AbstractPersonalData.add_custom_attributes(self, key, value)
        self.config.set(SECTION_CUSTOM, key, value.encode(self.encoding))

    def remove_custom_attributes(self, key):
        AbstractPersonalData.remove_custom_attributes(self, key)
        if self.config.has_option(SECTION_CUSTOM, key):
            self.config.remove_option(SECTION_CUSTOM, key)

    def get_custom_attributes(self):
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

class FileFilesharingMixin(FileSharingMixin):
    """Implements API for all file data in a File oriented context"""

    def __init__(self):
        self.config.add_section(SECTION_FILE)
        FileSharingMixin.__init__(self)

    # FILE TAB
    def init_repos(self):
        try:
            return [repo for repo in self.config.get(
                SECTION_PERSONAL, "repositories").split(',')
                      if repo.strip() != '']
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return []
        
    def reset_files(self):
        """empty all information concerning files"""
        FileSharingMixin.reset_files(self)
        self.config.remove_section(SECTION_FILE)
        self.config.add_section(SECTION_FILE)

    def get_repositories(self):
        """return list of repos"""
        # lazy initialisation
        repos = FileSharingMixin.get_repositories(self)
        if len(repos) > 0:
            return repos
        # full init
        repos = self.init_repos()
        for repo in repos:
            # create repo with out checking validity of path.
            # checking might be needed at loading only => checked=False
            FileSharingMixin.add_repository(self, repo, checked=False)
        return FileSharingMixin.get_repositories(self)
        
    def get_files(self):
        """returns {root: Container}"""
        # lazy initialisation
        if self.files != {}:
            return FileSharingMixin.get_files(self)
        # full init
        for repo in self.init_repos():
            try:
                self.files[repo] = create_container(repo, checked=False)
            except AssertionError:
                print "non valid repo '%s'"% repo
        # if no valid repo found, does not try any further...
        if self.files == {}:
            return self.files
        for option in self.config.options(SECTION_FILE):
            # get share & tag
            try:
                o_description = self.config.get(SECTION_FILE, option)
                o_file, o_share, o_size, o_tag = o_description.split(',', 3)
                o_file = (o_file == 'F') and True or False
                o_share = (o_share == SHARED_TAG)
                o_tag = force_unicode(o_tag)
                o_size = int(o_size)
            except (ValueError, ConfigParser.NoSectionError,
                    ConfigParser.NoOptionError), err:
                print >> sys.stderr, "option '%s' not well formated: %s"\
                      % (o_description, err)
                o_file, o_share, o_tag, o_size = False, False, DEFAULT_TAG, 0
            # add container
            try:
                file_container = o_file and self.get_file(option) \
                                 or self.get_container(option)
                file_container.share(o_share)
                file_container.tag(o_tag)
                file_container.size = o_size
            except KeyError:
                print "non valid file '%s'"% option
        return FileSharingMixin.get_files(self)
        
    def _set_repositories(self):
        """update list of repos"""
        repos_list = self.get_repositories()
        if repos_list == None:
            print "No repo to set."
            return
        if not self.config.has_section(SECTION_PERSONAL):
            self.config.add_section(SECTION_PERSONAL)
        self.config.set(SECTION_PERSONAL, "repositories",
                        ",".join(repos_list))

    def _set_files(self):
        """write in config"""
        files = self.get_files()
        for repo, dir_container in files.items():
            f_containers = dir_container.flat()
            for f_container in f_containers:
                key = os.path.join(repo, f_container.get_path())
                if f_container._shared or f_container._tag != DEFAULT_TAG:
                    value = ','.join([isinstance(f_container, DictContainer) \
                                      and 'D' or 'F',
                                      f_container._shared and SHARED_TAG or '',
                                      str(f_container.size),
                                      f_container._tag])
                    self.config.set(SECTION_FILE, key, value)

class FileContactMixin(ContactsMixin):
    """Implements API for all contact data in a File oriented context"""

    def __init__(self):
        self.config.add_section(SECTION_OTHERS)
        ContactsMixin.__init__(self)
        
    # OTHERS TAB
    def reset_peers(self):
        """empty all information concerning peers"""
        ContactsMixin.reset_peers(self)
        self.config.remove_section(SECTION_OTHERS)
        self.config.add_section(SECTION_OTHERS)
    
    def get_peers(self):
        """returns Peers"""
        # lazy initialisation
        if self.peers != {}:
            return ContactsMixin.get_peers(self)
        # full init
        if not self.config.has_section(SECTION_OTHERS):
            self.config.add_section(SECTION_OTHERS)
        options = self.config.options(SECTION_OTHERS)
        for peer_id in options:
            # check unicode
            if isinstance(peer_id, str):
                peer_id = unicode(peer_id, self.encoding)
            # get info
            description = self.config.get(SECTION_OTHERS, peer_id)
            try:
                pseudo, state, timestamp = description.split(',')
                peer_desc =  PeerDescriptor(peer_id,
                                            state=state)
                ContactsMixin.set_peer(self, peer_id, peer_desc)
                peer_desc.load()
                # TODO: use timestamp
            except Exception, error:
                print error, ": peer %s not retreived"% description
        return ContactsMixin.get_peers(self)
        
    def _set_peers(self):
        """stores Peer object"""
        if not self.config.has_section(SECTION_OTHERS):
            self.config.add_section(SECTION_OTHERS)
        for peer_id, peer_desc in self.get_peers().items():
            if peer_desc.state == PeerDescriptor.ANONYMOUS:
                continue
            elif peer_desc.state == PeerDescriptor.FRIEND:
                peer_desc.save()
            pseudo = peer_desc.document and peer_desc.document.get_pseudo() \
                     or "Anonymous"
            description = ",".join([pseudo,
                                    peer_desc.state,
                                    time.asctime()])
            # TODO: create timestamp on peer_desc
            self.config.set(SECTION_OTHERS, peer_id, description)

class FileSaverMixin(DocSaverMixin):
    """Implements API for saving & loading in a File oriented context"""

    def __init__(self, encoding=ENCODING):
        DocSaverMixin.__init__(self, encoding)
    
    # MENU
    def save(self, path):
        """fill document with information from .profile file"""
        self._set_repositories()
        self._set_files()
        self._set_peers()
        DocSaverMixin.save(self, path)
        
    def load(self, path):
        """fill document with information from .profile file"""
        result = DocSaverMixin.load(self, path)
        self.get_files()
        self.get_peers()
        return result

    def to_stream(self):
        """returns a file object containing values"""
        self._set_repositories()
        self._set_files()
        self._set_peers()
        return DocSaverMixin.to_stream(self)

class FileDocument(FilePersonalMixin, FileFilesharingMixin,
                   FileContactMixin, FileSaverMixin):
    """Describes all data needed in profile in a file"""

    def __init__(self):
        FileSaverMixin.__init__(self)
        FilePersonalMixin.__init__(self)
        FileFilesharingMixin.__init__(self)
        FileContactMixin.__init__(self)

    def __str__(self):
        return "File document for %s"% self.get_pseudo()
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        FilePersonalMixin.import_document(self, other_document)
        FileFilesharingMixin.import_document(self, other_document)
        FileContactMixin.import_document(self, other_document)

    def load(self, path):
        """load default values if no file"""
        if not FileSaverMixin.load(self, path):
            FilePersonalMixin.load_defaults(self)
            return False
        else:
            return True
    
