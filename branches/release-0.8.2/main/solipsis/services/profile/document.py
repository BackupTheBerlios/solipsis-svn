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

import mx.DateTime
import ConfigParser
import os.path
import sys
from os.path import isfile, isdir
from StringIO import StringIO
from solipsis.services.profile.data import DirContainer
from solipsis.services.profile import ENCODING, \
     PROFILE_DIR, PROFILE_FILE
from solipsis.services.profile.images import DEFAULT_PIC
from solipsis.services.profile.data import DEFAULT_TAG

DATE_FORMAT = "%d/%m/%Y"
SECTION_PERSONAL = "Personal"
SECTION_CUSTOM = "Custom"
SECTION_OTHERS = "Others"
SECTION_FILE = "Files"
BULB_ON_IMG = "../images/bulb.gif"      
BULB_OFF_IMG = "../images/bulb_off.gif"

SHARE_ALL = "All"
SHARE_NONE = "none"

NO_PATH = "none"

class FileDescriptor:
    """contains information relative to the sharing of one file"""

    def __init__(self, path, tag=None):
        self.path = path
        self.tag = tag

    def __repr__(self):
        return "%s (%s)"% (self.path, self.tag)

class PeerDescriptor:
    """contains information relative to peer of neibourhood"""

    ANONYMOUS = 'Anonym'
    FRIEND = 'Friend'
    BLACKLISTED = 'Blacklisted'
    COLORS = {ANONYMOUS: 'black',
              FRIEND:'blue',
              BLACKLISTED:'red'}
    
    def __init__(self, pseudo, state=ANONYMOUS, connected=False):
        self.pseudo = pseudo
        self.state = state
        self.connected = connected

    def __repr__(self):
        return "%s (%s)"% (self.pseudo, self.state)

    def set_connected(self, enable):
        """change user's connected status"""
        self.connected = enable
        
    def html(self):
        """render peer in HTML"""
        return "<img src='%s'/><font color=%s>%s</font>"\
               % (self.connected and BULB_ON_IMG or BULB_OFF_IMG,
                  PeerDescriptor.COLORS[self.state], self.pseudo)
        
class AbstractDocument:
    """Base class for data container. Acts as validator.

    Setters check input type. Getters are abstract"""

    def __init__(self, name="abstract"):
        self.name = name

    def __repr__(self):
        return self.name

    def get_name(self):
        """used as key in index"""
        return self.name

    def get_id(self):
        """return identifiant of Document"""
        return self.name

    def import_document(self, other_document):
        """copy data from another document into self"""
        # personal data (unicode)
        self.set_title(other_document.get_title())
        self.set_firstname(other_document.get_firstname())
        self.set_lastname(other_document.get_lastname())
        self.set_pseudo(other_document.get_pseudo())
        self.set_photo(other_document.get_photo())
        self.set_email(other_document.get_email())
        self.set_birthday(other_document.get_birthday())
        self.set_language(other_document.get_language())
        self.set_address(other_document.get_address())
        self.set_postcode(other_document.get_postcode())
        self.set_city(other_document.get_city())
        self.set_country(other_document.get_country())
        self.set_description(other_document.get_description())
        # custom data
        self.set_hobbies(other_document.get_hobbies())
        attributes = other_document.get_custom_attributes()
        for key, val in attributes.iteritems():
            self.add_custom_attributes((key, val))
        # file data
        self.reset_files()
        for repo, sharing_container in other_document.get_files().iteritems():
            self.add_repository(repo)
            for full_path, container in sharing_container.flat().iteritems():
                self.share_file((full_path, container._shared))
                self.tag_file((full_path, container._tag))
        # others' data
        self.reset_peers()
        peers = other_document.get_peers()
        for pseudo, (peer_desc, peer_doc) in peers.iteritems():
            self.add_peer(pseudo)
            peer_doc and self.fill_data((pseudo, peer_doc))
            if peer_desc.state == PeerDescriptor.ANONYMOUS:
                self.unmark_peer(pseudo)
            elif peer_desc.state == PeerDescriptor.FRIEND:
                self.make_friend(pseudo)
            elif peer_desc.state == PeerDescriptor.BLACKLISTED:
                self.blacklist_peer(pseudo)
            else:
                print >> sys.stderr, "state %s not recognised"% peer_desc.state
    
    # MENU
    def save(self, path=None):
        """fill document with information from .profile file"""
        doc = FileDocument()
        doc.import_document(self)
        doc.save(path)

    def load(self, path=None):
        """fill document with information from .profile file"""
        doc = FileDocument()
        doc.load(path)
        self.import_document(doc)
    
    # PERSONAL TAB
    def set_title(self, value):
        """sets new value for title"""
        if not isinstance(value, unicode):
            raise TypeError("title expected as unicode")
    def get_title(self):
        """returns value of firstname"""
        raise NotImplementedError
        
    def set_firstname(self, value):
        """sets new value for firstname"""
        if not isinstance(value, unicode):
            raise TypeError("firstname expected as unicode")
    def get_firstname(self):
        """returns value of firstname"""
        raise NotImplementedError
        
    def set_lastname(self, value):
        """sets new value for lastname"""
        if not isinstance(value, unicode):
            raise TypeError("lastname expected as unicode")
    def get_lastname(self):
        """returns value of lastname"""
        raise NotImplementedError
    
    def set_pseudo(self, value):
        """sets new value for pseudo"""
        if not isinstance(value, unicode):
            raise TypeError("pseudo expected as unicode")
    def get_pseudo(self):
        """returns value of pseudo"""
        raise NotImplementedError
    
    def set_photo(self, value):
        """sets new value for photo"""
        if not isfile(value):
            raise TypeError("photo must exist")
    def get_photo(self):
        """returns value of photo"""
        raise NotImplementedError
        
    def set_email(self, value):
        """sets new value for email"""
        if not isinstance(value, unicode):
            raise TypeError("email expected as unicode")
    def get_email(self):
        """returns value of email"""
        raise NotImplementedError
        
    def set_birthday(self, value):
        """sets new value for birthday"""
        try:
            mx.DateTime.strptime(value, DATE_FORMAT)
        except mx.DateTime.Error, error:
            raise TypeError("birthday expected in format %s. %s"\
                            % (DATE_FORMAT, str(error)))
    def get_birthday(self):
        """returns value of birthday"""
        raise NotImplementedError
        
    def set_language(self, value):
        """sets new value for language"""
        if not isinstance(value, unicode):
            raise TypeError("language expected as unicode")
    def get_language(self):
        """returns value of language"""
        raise NotImplementedError
        
    def set_address(self, value):
        """sets new value for address"""
        if not isinstance(value, unicode):
            raise TypeError("address expected as unicode")
    def get_address(self):
        """returns value of address"""
        raise NotImplementedError
        
    def set_postcode(self, value):
        """sets new value for postcode"""
        try:
            int(value)
        except ValueError, error:
            raise TypeError("postcode expected as int. "+ str(error))
    def get_postcode(self):
        """returns value of postcode"""
        raise NotImplementedError
        
    def set_city(self, value):
        """sets new value for city"""
        if not isinstance(value, unicode):
            raise TypeError("city expected as unicode")
    def get_city(self):
        """returns value of city"""
        raise NotImplementedError
        
    def set_country(self, value):
        """sets new value for country"""
        if not isinstance(value, unicode):
            raise TypeError("country expected as unicode")
    def get_country(self):
        """returns value of country"""
        raise NotImplementedError
        
    def set_description(self, value):
        """sets new value for description"""
        if not isinstance(value, unicode):
            raise TypeError("description expected as unicode")
    def get_description(self):
        """returns value of description"""
        raise NotImplementedError
        
    # CUSTOM TAB
    def set_hobbies(self, value):
        """sets new value for hobbies"""
        if not isinstance(value, list) and not isinstance(value, tuple):
            raise TypeError("hobbies expected as list or tuple")
    def get_hobbies(self):
        """returns value of hobbies"""
        raise NotImplementedError
        
    def add_custom_attributes(self, pair):
        """sets new value for custom_attributes"""
        if not isinstance(pair, list) and not isinstance(pair, tuple):
            raise TypeError("custom_attribute expected as list or tuple")
        elif len(pair) != 2:
            raise TypeError("custom_attribute expected as couple (key, value)")
        if not isinstance(pair[1], unicode):
            raise TypeError("tag expected as unicode")
    def remove_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        if not isinstance(value, unicode):
            raise TypeError("attribute expected as unicode")
    def get_custom_attributes(self):
        """returns value of custom_attributes"""
        raise NotImplementedError
        
    # FILE TAB
    def reset_files(self):
        """empty all information concerning files"""
        raise NotImplementedError
        
    def add_repository(self, value):
        """sets new value for repository"""
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
        """remove directory from repository"""
        if not isinstance(value, unicode):
            raise TypeError("dir to expand expected as unicode")
        
    def expand_dir(self, value):
        """update doc when dir expanded"""
        if not isinstance(value, unicode):
            raise TypeError("dir to expand expected as unicode")

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
            raise TypeError("argument of tag_container expected as list or tuple")
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
        
    def get_shared(self, repo_path):
        """returns list of all dirs"""
        raise NotImplementedError

    def get_container(self, full_path):
        """returns File/DirContainer correspondind to full_path"""
        raise NotImplementedError
            
    # OTHERS TAB
    def reset_peers(self):
        """empty all information concerning peers"""
        raise NotImplementedError
        
    def add_peer(self, pseudo):
        """stores Peer object"""
        if not isinstance(pseudo, unicode):
            raise TypeError("pseudo expected as unicode")
        
    def remove_peer(self, pseudo):
        """del Peer object"""
        if not isinstance(pseudo, unicode):
            raise TypeError("pseudo expected as unicode")
    
    def get_peers(self):
        """returns Peers"""
        raise NotImplementedError
    
    def get_ordered_peers(self):
        """returns Peers"""
        peers = self.get_peers()
        peers_name = peers.keys()
        peers_name.sort()
        return [(name, peers[name]) for name in peers_name]

    def fill_data(self, pair):
        """stores CacheDocument associated with peer"""
        if not isinstance(pair, list) and not isinstance(pair, tuple):
            raise TypeError("argument of tag_file expected as list or tuple")
        elif len(pair) != 2:
            raise TypeError("argument of  expected as couple (file_path, tag)")
        pseudo, document = pair
        if not isinstance(pseudo, unicode):
            raise TypeError("pseudo expected as unicode")
        if not isinstance(document, AbstractDocument):
            raise TypeError("data expected as AbstractDocument")
    
    def make_friend(self, pseudo):
        """sets peer as friend """
        if not isinstance(pseudo, unicode):
            raise TypeError("pseudo expected as unicode")

    def blacklist_peer(self, pseudo):
        """sets new value for unshared file"""
        if not isinstance(pseudo, unicode):
            raise TypeError("pseudo expected as unicode")

    def unmark_peer(self, pseudo):
        """sets new value for unshared file"""
        if not isinstance(pseudo, unicode):
            raise TypeError("pseudo expected as unicode")
        

class CacheDocument(AbstractDocument):
    """data container on cache"""

    def __init__(self, name="cache"):
        AbstractDocument.__init__(self, name)
        self.title = u""
        self.firstname = u""
        self.lastname = u""
        self.pseudo = u""
        self.photo = ""
        self.email = u""
        self.birthday = mx.DateTime.now()
        self.language = u""
        self.address = u""
        self.postcode = 0
        self.city = u""
        self.country = u""
        self.description = u""
        self.hobbies = []
        # dictionary of file. {att_name : att_value}
        self.custom_attributes = {}
        # {root: DirContainers}
        self.files = {}
        # dictionary of peers. {pseudo : PeerDescriptor}
        self.peers = {}

    def __str__(self):
        from solipsis.services.profile.view import PrintView
        result = StringIO()
        PrintView(self, result, do_import=True)
        return result.getvalue()
        
    # MENU

    # used base method: saving / loading not implemented
        
    # PERSONAL TAB
    def set_title(self, value):
        """sets new value for title"""
        AbstractDocument.set_title(self, value)
        self.title = value
    def get_title(self):
        """returns value of title"""
        return self.title
        
    def set_firstname(self, value):
        """sets new value for firstname"""
        AbstractDocument.set_firstname(self, value)
        self.firstname = value
    def get_firstname(self):
        """returns value of firstname"""
        return self.firstname

    def set_lastname(self, value):
        """sets new value for lastname"""
        AbstractDocument.set_lastname(self, value)
        self.lastname = value
    def get_lastname(self):
        """returns value of lastname"""
        return self.lastname

    def set_pseudo(self, value):
        """sets new value for pseudo"""
        AbstractDocument.set_pseudo(self, value)
        self.pseudo = value
    def get_pseudo(self):
        """returns value of pseudo"""
        return self.pseudo

    def set_photo(self, value):
        """sets new value for photo"""
        AbstractDocument.set_photo(self, value)
        self.photo = value
    def get_photo(self):
        """returns value of photo"""
        return self.photo

    def set_email(self, value):
        """sets new value for email"""
        AbstractDocument.set_email(self, value)
        self.email = value
    def get_email(self):
        """returns value of email"""
        return self.email

    def set_birthday(self, value):
        """sets new value for birthday"""
        AbstractDocument.set_birthday(self, value)
        self.birthday = mx.DateTime.strptime(value, DATE_FORMAT)
    def get_birthday(self):
        """returns value of birthday"""
        return self.birthday.strftime(DATE_FORMAT)

    def set_language(self, value):
        """sets new value for language"""
        AbstractDocument.set_language(self, value)
        self.language = value
    def get_language(self):
        """returns value of language"""
        return self.language

    def set_address(self, value):
        """sets new value for """
        AbstractDocument.set_address(self, value)
        self.address = value
    def get_address(self):
        """returns value of address"""
        return self.address

    def set_postcode(self, value):
        """sets new value for postcode"""
        AbstractDocument.set_postcode(self, value)
        self.postcode = int(value)
    def get_postcode(self):
        """returns value of postcode"""
        return str(self.postcode)

    def set_city(self, value):
        """sets new value for city"""
        AbstractDocument.set_city(self, value)
        self.city = value
    def get_city(self):
        """returns value of city"""
        return self.city

    def set_country(self, value):
        """sets new value for country"""
        AbstractDocument.set_country(self, value)
        self.country = value
    def get_country(self):
        """returns value of country"""
        return self.country

    def set_description(self, value):
        """sets new value for description"""
        AbstractDocument.set_description(self, value)
        self.description = value
    def get_description(self):
        """returns value of description"""
        return self.description

    # CUSTOM TAB
    def set_hobbies(self, value):
        """sets new value for hobbies"""
        AbstractDocument.set_hobbies(self, value)
        self.hobbies = value
    def get_hobbies(self):
        """returns value of hobbies"""
        return self.hobbies

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
        """sets new value for repository"""
        AbstractDocument.remove(self, value)
        container = self._get_sharing_container(value)
        del self._get_sharing_container(value)[value]
        
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
        """returns  {full_path: tag}"""
        result = {}
        for name, container in self.files[repo_path].flat().iteritems():
            if container._shared:
                result[name] = container._tag
        return result

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
        
    def add_peer(self, pseudo):
        """stores Peer object"""
        AbstractDocument.add_peer(self, pseudo)
        self.peers[pseudo] = [PeerDescriptor(pseudo), None]
        
    def remove_peer(self, pseudo):
        """del Peer object"""
        AbstractDocument.remove_peer(self, pseudo)
        if self.peers.has_key(pseudo):
            del self.peers[pseudo]
    
    def get_peers(self):
        """returns Peers"""
        return self.peers

    def fill_data(self, pair):
        """stores CacheDocument associated with peer"""
        AbstractDocument.fill_data(self, pair)
        pseudo, document = pair
        if not self.peers.has_key(pseudo):
            self.add_peer(pseudo)
        self.peers[pseudo][1] = document
    
    def make_friend(self, pseudo):
        """sets peer as friend """
        AbstractDocument.make_friend(self, pseudo)
        if not self.peers.has_key(pseudo):
            self.add_peer(pseudo)
        peer_obj = self.peers[pseudo][0]
        peer_obj.state = PeerDescriptor.FRIEND

    def blacklist_peer(self, pseudo):
        """sets new value for unshared file"""
        AbstractDocument.blacklist_peer(self, pseudo)
        if not self.peers.has_key(pseudo):
            self.add_peer(pseudo)
        peer_obj = self.peers[pseudo][0]
        peer_obj.state = PeerDescriptor.BLACKLISTED

    def unmark_peer(self, pseudo):
        """sets new value for unshared file"""
        AbstractDocument.unmark_peer(self, pseudo)
        if not self.peers.has_key(pseudo):
            self.add_peer(pseudo)
        peer_obj = self.peers[pseudo][0]
        peer_obj.state = PeerDescriptor.ANONYMOUS


# FILEDOCUMENT
class CustomConfigParser(ConfigParser.ConfigParser):

    def optionxform(self, option):
        """override default implementation to make it case sensitive"""
        return str(option)

class FileDocument(AbstractDocument):
    """data container on file"""

    def __init__(self, name="file"):
        AbstractDocument.__init__(self, name)
        self.file_name = os.path.join(PROFILE_DIR, PROFILE_FILE)
        self.encoding = ENCODING
        self.config = CustomConfigParser()
        self.config.add_section(SECTION_PERSONAL)
        self.config.add_section(SECTION_CUSTOM)
        self.config.add_section(SECTION_FILE)
        self.config.add_section(SECTION_OTHERS)

    def __str__(self):
        result = StringIO()
        self.config.write(result)
        return result.getvalue()

    def get_id(self):
        """return identifiant of Document"""
        return self.file_name
    
    # MENU

    def save(self, path=None):
        """fill document with information from .profile file"""
        if path:
            self.file_name = path
        file_obj = open(self.file_name, 'w')
        file_obj.write("#%s\n"% self.encoding)
        self.config.write(file_obj)
        file_obj.close()

    def read(self, stream):
        """import profile from given stream (file object like)"""
        self.encoding = stream.readline()[1:]
        self.config = CustomConfigParser()
        self.config.readfp(stream)

    def load(self, path=None):
        """fill document with information from .profile file"""
        if path and os.path.exists(path):
            self.file_name = path
        else:
            return False
        # else: continue
        file_obj = open(self.file_name)
        self.read(file_obj)
        file_obj.close()
        return True
        
    # PERSONAL TAB
    def set_title(self, value):
        """sets new value for title"""
        AbstractDocument.set_firstname(self, value)
        self.config.set(SECTION_PERSONAL, "title",
                        value.encode(self.encoding))
    def get_title(self):
        """returns value of title"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "title"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"Mr"
        
    def set_firstname(self, value):
        """sets new value for firstname"""
        AbstractDocument.set_firstname(self, value)
        self.config.set(SECTION_PERSONAL, "firstname",
                        value.encode(self.encoding))
    def get_firstname(self):
        """returns value of firstname"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "firstname",
                                           "Emmanuel"), self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"Emmanuel"

    def set_lastname(self, value):
        """sets new value for lastname"""
        AbstractDocument.set_lastname(self, value)
        self.config.set(SECTION_PERSONAL, "lastname",
                        value.encode(self.encoding))
    def get_lastname(self):
        """returns value of lastname"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "lastname"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"Breton"

    def set_pseudo(self, value):
        """sets new value for pseudo"""
        AbstractDocument.set_pseudo(self, value)
        self.config.set(SECTION_PERSONAL, "pseudo",
                        value.encode(self.encoding))
    def get_pseudo(self):
        """returns value of pseudo"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "pseudo"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"emb"

    def set_photo(self, value):
        """sets new value for photo"""
        AbstractDocument.set_photo(self, value)
        self.config.set(SECTION_PERSONAL, "photo",
                        value.encode(self.encoding))
    def get_photo(self):
        """returns value of photo"""
        try:
            return self.config.get(SECTION_PERSONAL, "photo")
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return DEFAULT_PIC

    def set_email(self, value):
        """sets new value for email"""
        AbstractDocument.set_email(self, value)
        self.config.set(SECTION_PERSONAL, "email",
                        value.encode(self.encoding))
    def get_email(self):
        """returns value of email"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "email"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"emb@logilab.fr"

    def set_birthday(self, value):
        """sets new value for birthday"""
        AbstractDocument.set_birthday(self, value)
        self.config.set(SECTION_PERSONAL, "birthday",
                        value.encode(self.encoding))
    def get_birthday(self):
        """returns value of birthday"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "birthday"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"01/04/2005"
            

    def set_language(self, value):
        """sets new value for language"""
        AbstractDocument.set_language(self, value)
        self.config.set(SECTION_PERSONAL, "language",
                        value.encode(self.encoding))
    def get_language(self):
        """returns value of language"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "language"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"fr"

    def set_address(self, value):
        """sets new value for """
        AbstractDocument.set_address(self, value)
        self.config.set(SECTION_PERSONAL, "address",
                        value.encode(self.encoding))
    def get_address(self):
        """returns value of address"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "address"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u""

    def set_postcode(self, value):
        """sets new value for postcode"""
        AbstractDocument.set_postcode(self, value)
        self.config.set(SECTION_PERSONAL, "postcode",
                        value.encode(self.encoding))
    def get_postcode(self):
        """returns value of postcode"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "postcode"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"75"

    def set_city(self, value):
        """sets new value for city"""
        AbstractDocument.set_city(self, value)
        self.config.set(SECTION_PERSONAL, "city",
                        value.encode(self.encoding))
    def get_city(self):
        """returns value of city"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "city"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u""

    def set_country(self, value):
        """sets new value for country"""
        AbstractDocument.set_country(self, value)
        self.config.set(SECTION_PERSONAL, "country",
                        value.encode(self.encoding))
    def get_country(self):
        """returns value of country"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "country"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u""

    def set_description(self, value):
        """sets new value for description"""
        AbstractDocument.set_description(self, value)
        self.config.set(SECTION_PERSONAL, "description",
                        value.encode(self.encoding))
    def get_description(self):
        """returns value of description"""
        try:
            return unicode(self.config.get(SECTION_PERSONAL, "description"),
                           self.encoding)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return u"Developer/Designer of this handful plugin"

    # CUSTOM TAB
    def set_hobbies(self, value):
        """sets new value for hobbies"""
        AbstractDocument.set_hobbies(self, value)
        self.config.set(SECTION_CUSTOM, "hobbies",
                        ",".join(value).encode(self.encoding))
    def get_hobbies(self):
        """returns value of hobbies"""
        try:
            return [unicode(hobby, self.encoding) for hobby 
                    in self.config.get(SECTION_CUSTOM, "hobbies").split( ',')]
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return []

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
                    result[option] = unicode(self.config.get(SECTION_CUSTOM,
                                                             option),
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
                     in  self.config.get(SECTION_CUSTOM, "repositories")\
                     .split(',')
                     if repo.strip() != '']
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return []
        
    def _set_repositories(self, repos_list):
        """update list of repos"""
        self.config.set(SECTION_CUSTOM, "repositories",
                        ",".join(repos_list).encode(self.encoding))
        
    def add(self, value):
        """sets new value for files"""
        AbstractDocument.add(self, value)
        # html only stores shared/tagged files
        
    def remove(self, value):
        """sets new value for repository"""
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
            print >> sys.stderr, "profile file corrupted: "\
                  "does not has [FILES] section"
            return {}
        for option in self.config.options(SECTION_FILE):
            try:
                option_description = self.config.get(SECTION_FILE, option)
                if isinstance(option_description, str):
                    option_description =  unicode(option_description,
                                                  self.encoding)
                option_share, option_tag = option_description.split(',')
                option_share = bool(option_share)
            except (ValueError, ConfigParser.NoSectionError,
                    ConfigParser.NoOptionError):
                print >> stderr, "option %s not well formated"% option
                option_share, option_tag = False, DEFAULT_TAG
            for root_path in dict.keys(containers):
                if option.startswith(root_path):
                    containers[root_path].share_container(option,
                                                     option_share)
                    containers[root_path].tag_container(option,
                                                   option_tag)
                    break
        return containers
    
    def get_shared(self, repo_path):
        """returns  {root: tag}"""
        result = {}
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
                    result[option] = option_tag
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
        
    def add_peer(self, pseudo):
        """stores Peer object"""
        AbstractDocument.add_peer(self, pseudo)
        self.config.set(SECTION_OTHERS, pseudo, ","\
                        .join([PeerDescriptor.ANONYMOUS, NO_PATH]))
        
    def remove_peer(self, pseudo):
        """del Peer object"""
        AbstractDocument.remove_peer(self, pseudo)
        if self.config.has_option(SECTION_OTHERS, pseudo):
            self.config.remove_option(SECTION_OTHERS, pseudo)
    
    def get_peers(self):
        """returns Peers"""
        result = {}
        try:
            options = self.config.options(SECTION_OTHERS)
            for opt in options:
                # get info
                if isinstance(opt, str):
                    opt = unicode(opt, self.encoding)
                try:
                    # expected format is friend, path
                    friend, path = self.config.get(SECTION_OTHERS, opt)\
                                   .split(",")
                except ValueError:
                    # if format does not match, guess for path or friend
                    value = unicode(self.config.get(SECTION_OTHERS, opt),
                                    self.encoding)
                    if value in [PeerDescriptor.ANONYMOUS,
                                 PeerDescriptor.FRIEND,
                                 PeerDescriptor.BLACKLISTED]:
                        friend, path = value, NO_PATH
                    elif os.path.exists(value):
                        friend, path = PeerDescriptor.ANONYMOUS, value
                    else:
                        friend, path = PeerDescriptor.ANONYMOUS, NO_PATH
                # load doc
                if path != NO_PATH:
                    doc = FileDocument()
                    if not doc.load(path):
                        doc = None
                else:
                    doc = None
                result[opt] = [PeerDescriptor(opt, friend), doc]
            return result
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return result
        

    def fill_data(self, pair):
        """stores CacheDocument associated with peer"""
        AbstractDocument.fill_data(self, pair)
        pseudo, doc = pair
        friendship = self._get_peer_info(pseudo)[0]
        self.config.set(SECTION_OTHERS, pseudo, "%s,%s"\
                        % (friendship, doc.get_id()))   
        
    def make_friend(self, pseudo):
        """sets peer as friend """
        AbstractDocument.make_friend(self, pseudo)
        path = self._get_peer_info(pseudo)[1]
        self.config.set(SECTION_OTHERS, pseudo, "%s,%s"\
                        % (PeerDescriptor.FRIEND, path))

    def blacklist_peer(self, pseudo):
        """sets new value for unshared file"""
        AbstractDocument.blacklist_peer(self, pseudo)
        path = self._get_peer_info(pseudo)[1]
        self.config.set(SECTION_OTHERS, pseudo, "%s,%s"\
                        % (PeerDescriptor.BLACKLISTED, path))

    def unmark_peer(self, pseudo):
        """sets new value for unshared file"""
        AbstractDocument.unmark_peer(self, pseudo)
        path = self._get_peer_info(pseudo)[1]
        self.config.set(SECTION_OTHERS, pseudo, "%s,%s"\
                        % (PeerDescriptor.ANONYMOUS, path))

    def _get_peer_info(self, pseudo):
        """retreive stored value (friendship, path) for pseudo"""
        try:
            return self.config.get(SECTION_OTHERS, pseudo).split(",")
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            return [PeerDescriptor.ANONYMOUS, NO_PATH]

