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
import tempfile
import sys
from solipsis.services.profile import ENCODING, QUESTION_MARK, \
     PROFILE_DIR, DOWNLOAD_REPO
from solipsis.services.profile.data import DEFAULT_TAG, \
     DirContainer, ContainerMixin, \
     PeerDescriptor, load_blogs
from solipsis.services.profile.document import CustomConfigParser, SaverMixin, \
     AbstractPersonalData, AbstractSharingData, AbstractContactsData, \
     SECTION_PERSONAL, SECTION_CUSTOM, SECTION_OTHERS, SECTION_FILE

class FilePersonalMixin(AbstractPersonalData):
    """Implements API for all pesonal data in a File oriented context"""

    def __init__(self, pseudo):
        self.config.add_section(SECTION_PERSONAL)
        self.config.set(SECTION_PERSONAL, "pseudo", pseudo)
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

    def set_download_repo(self, value):
        """sets new value for download_repo"""
        AbstractPersonalData.set_download_repo(self, value)
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
        self._set_repositories([])
        self.config.remove_section(SECTION_FILE)
        self.config.add_section(SECTION_FILE)
        
    def add_file(self, value):
        """create new DirContainer"""
        AbstractSharingData.add_file(self, value)
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
        
    def del_file(self, value):
        """create new DirContainer"""
        AbstractSharingData.del_file(self, value)
        # delete entry
        values = [repo for repo in self.get_repositories()
                  if repo != value]
        # update list of repositories
        self._set_repositories(values)

    def get_repositories(self):
        """return list of repos"""
        try:
            return  [repo for repo
                     in  self.config.get(SECTION_PERSONAL, "repositories")\
                     .split(',')
                     if repo.strip() != '']
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return []
        
    def _set_repositories(self, repos_list):
        """update list of repos"""
        self.config.set(SECTION_PERSONAL, "repositories",
                        ",".join(repos_list))
        
    def add(self, value):
        """sets new value for files"""
        AbstractSharingData.add(self, value)
        # html only stores shared/tagged files
        
    def remove(self, value):
        """remove custom value"""
        AbstractSharingData.remove(self, value)
        if self.config.has_option(SECTION_CUSTOM, value):
            self.config.remove_option(SECTION_CUSTOM, value)
        
    def expand_dir(self, value):
        """put into cache new information when dir expanded in tree"""
        AbstractSharingData.expand_dir(self, value)
        # html doc does not expand anything

    def share_dirs(self, pair):
        """forward command to cache"""
        AbstractSharingData.share_dirs(self, pair)
        paths, share = pair
        for path in paths:
            for file_name in os.listdir(path):
                self._set_file(os.path.join(path, file_name), share=share)

    def share_files(self, triplet):
        """forward command to cache"""
        AbstractSharingData.share_files(self, triplet)
        dir_path, names, share = triplet
        for name in names:
            self._set_file(os.path.join(dir_path, name), share=share)

    def share_file(self, pair):
        """forward command to cache"""
        AbstractSharingData.share_file(self, pair)
        full_path, share = pair
        self._set_file(full_path, share=share)
                
    def tag_files(self, triplet):
        """sets new value for tagged file"""
        AbstractSharingData.tag_files(self, triplet)
        dir_path, names, tag = triplet
        for name in names:
            self._set_file(os.path.join(dir_path, name), tag=tag)
        
    def tag_file(self, pair):
        """sets new value for tagged file"""
        AbstractSharingData.tag_file(self, pair)
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
            try:
                option_description = self.config.get(SECTION_FILE, option)
                option_share, option_tag = option_description.split(',')
                option_share = bool(option_share)
                if isinstance(option_tag, str):
                    option_tag = unicode(option_tag, ENCODING)
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
                try:
                    option_description = self.config.get(SECTION_FILE, option)
                    option_share, option_tag = option_description.split(',')
                    option_share = bool(option_share)
                    if isinstance(option_tag, str):
                        option_tag = unicode(option_tag, ENCODING)
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

class FileSaverMixin(SaverMixin):
    """Implements API for saving & loading in a File oriented context"""

    def __init__(self, pseudo, directory=PROFILE_DIR):
        SaverMixin.__init__(self, pseudo, directory)
    
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

class FileDocument(FilePersonalMixin, FileSharingMixin,
                   FileContactMixin, FileSaverMixin):
    """Describes all data needed in profile in a file"""

    def __init__(self, pseudo, directory=PROFILE_DIR):
        self.encoding = ENCODING
        self.config = CustomConfigParser(ENCODING)
        FilePersonalMixin.__init__(self, pseudo)
        FileSharingMixin.__init__(self)
        FileContactMixin.__init__(self)
        FileSaverMixin.__init__(self, pseudo, directory)
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        FilePersonalMixin.import_document(self, other_document)
        FileSharingMixin.import_document(self, other_document)
        FileContactMixin.import_document(self, other_document)
    
