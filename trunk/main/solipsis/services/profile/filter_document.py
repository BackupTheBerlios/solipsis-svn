# pylint: disable-msg=W0131,W0201
# Missing docstring, Attribute '%s' defined outside __init__
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

__revision__ = "$Id: $"

import re
import os.path
import tempfile
from solipsis.services.profile import ENCODING
from solipsis.services.profile.document import AbstractPersonalData, \
     CustomConfigParser, SECTION_PERSONAL, SECTION_CUSTOM, SECTION_FILE
from solipsis.services.profile.document import SaverMixin
from solipsis.services.profile.cache_document import CacheContactMixin

class FilterValue:
    """wrapper for filter: regex, description ans state"""

    def __init__(self, name="no name", value=u"", activate=False):
        self.activated = activate
        self.description = value
        self.regex = re.compile(value, re.IGNORECASE)
        self._name = name # name of member which is defined by FilterValue

    def __repr__(self):
        return "%s, %s"% (self.description, self.activated and "(1)" or "(0)")

    def __str__(self):
        return self._name

    def __eq__(self, other):
        return self.description == other.description \
               and self.activated == other.activated

    def set_value(self, value, activate=True):
        """recompile regex and (dis)activate filter"""
        self.description = value
        self.regex = re.compile(value, re.IGNORECASE)
        self.activated = activate
        
    def does_match(self, data):
        """apply regex on data and returns self if there is any match"""
        # no match -> return false
        if not self.activated or len(self.description) == 0:
            return False
        if self.regex.match(data) is None:
            return False
        # match -> return true
        return FilterResult(self, data)

class FilterResult:
    """Structure to receive a positive result from a match"""

    def __init__(self, filter_value, match):
        self.filter_value = filter_value
        self.match = match

    def get_name(self):
        """return name of fhe filter (ie: personal detrails, custom
        attributes..."""
        return self.filter_value._name

    def get_description(self):
        """return regex"""
        return self.filter_value.description

    def get_match(self):
        """return string which matched"""
        return self.match

class PeerMatch:
    """contains all matches for given peer"""

    def __init__(self, peer_desc, filter_doc=None):
        self.peer_desc = peer_desc
        self.reset()
        self.match(filter_doc)

    def reset(self):
        self.title = False
        self.firstname = False
        self.lastname = False
        self.photo = False
        self.email = False
        self.customs = {}
        self.files = {}

    def match(self, filter_doc=None):
        """find matches for all details, attributes and files of given doc"""
        if filter_doc is None:
            from solipsis.services.profile.facade import get_filter_facade
            filter_doc = get_filter_facade()._desc.document
        if self.peer_desc.document:
            # personal data
            peer_doc = self.peer_desc.document
            self.title = filter_doc.title.does_match(peer_doc.get_title())
            self.firstname = filter_doc.firstname.does_match(
                peer_doc.get_firstname())
            self.lastname = filter_doc.lastname.does_match(
                peer_doc.get_lastname())
            self.photo = filter_doc.photo.does_match(peer_doc.get_photo())
            self.email = filter_doc.email.does_match(peer_doc.get_email())
            # custom attributes
            peer_customs = peer_doc.get_custom_attributes()
            for c_name, c_filter in filter_doc.custom_attributes.iteritems():
                if peer_customs.has_key(c_name):
                    match = c_filter.does_match(peer_customs[c_name])
                    if match:
                        self.customs[c_name] = match
        # files
        shared_files = self.peer_desc.document.get_shared_files()
        if shared_files:
            for f_name, file_filter in filter_doc.file_filters.iteritems():
                for file_container in shared_files.flatten():
                    match = file_filter.does_match(file_container.name)
                    if match:
                        if f_name not in self.files:
                            self.files[f_name] = []
                        self.files[f_name].append(match)

    def get_id(self):
        """returns peer_id associated with this match"""
        return self.peer_desc.node_id

    def has_match(self):
        """return True if any field has raised a match"""
        return self.title or self.firstname or self.lastname \
               or self.photo or self.email \
               or self.customs or self.files

class FilterPersonalMixin(AbstractPersonalData):
    """Implements API for all pesonal data in cache"""

    def __init__(self):
        # config
        self.config.add_section(SECTION_PERSONAL)
        self.config.add_section(SECTION_CUSTOM)
        # cache
        self.pseudo = FilterValue("pseudo")
        self.title = FilterValue("title")
        self.firstname = FilterValue("firstname")
        self.lastname = FilterValue("lastname")
        self.photo = FilterValue("photo")
        self.email = FilterValue("email")
        # dictionary of file. {att_name : att_value}
        self.custom_attributes = {}
        AbstractPersonalData.__init__(self)

    def _set(self, member, filter_value):
        """set member both in cache & in file"""
        value, activate = filter_value.description, filter_value.activated
        member.set_value(value, activate)
        self.config.set(SECTION_PERSONAL, str(member),
                        ",".join((str(activate), value)))
        return member
        
    # PERSONAL TAB
    def set_pseudo(self, filter_value):
        if self.pseudo == filter_value:
            return False
        else:
            return self._set(self.pseudo, filter_value)
    
    def get_pseudo(self):
        return self.pseudo
    
    def set_title(self, filter_value):
        if self.title == filter_value:
            return False
        else:
            return self._set(self.title, filter_value)
    
    def get_title(self):
        return self.title
        
    def set_firstname(self, filter_value):
        if self.firstname == filter_value:
            return False
        else:
            return self._set(self.firstname, filter_value)
    
    def get_firstname(self):
        return self.firstname

    def set_lastname(self, filter_value):
        if self.lastname == filter_value:
            return False
        else:
            return self._set(self.lastname, filter_value)
    
    def get_lastname(self):
        return self.lastname

    def set_photo(self, filter_value):
        if self.photo == filter_value:
            return False
        else:
            return self._set(self.photo, filter_value)
    
    def get_photo(self):
        return self.photo

    def set_email(self, filter_value):
        if self.email == filter_value:
            return False
        else:
            return self._set(self.email, filter_value)
    
    def get_email(self):
        return self.email
    
    # CUSTOM TAB
    def has_custom_attribute(self, key):
        return self.custom_attributes.has_key(key)
    
    def add_custom_attributes(self, key, filter_value):
        value, activate = filter_value.description, filter_value.activated
        self.config.set(SECTION_CUSTOM, key, ",".join((str(activate), value)))
        if not self.has_custom_attribute(key):
            self.custom_attributes[key] = FilterValue(key, value, activate)
        else:
            self.custom_attributes[key].set_value(value, activate)
        
    def remove_custom_attributes(self, key):
        AbstractPersonalData.remove_custom_attributes(self, key)
        if self.custom_attributes.has_key(key):
            self.config.remove_option(SECTION_CUSTOM, key)
            del self.custom_attributes[key]
            
    def get_custom_attributes(self):
        return self.custom_attributes

class FilterSharingMixin:
    """Implements API for all file data in cache"""

    def __init__(self):
        # config
        self.config.add_section(SECTION_FILE)
        # cache dictionary of file. {att_name : att_value}
        self.file_filters = {}
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        assert isinstance(other_document, FilterSharingMixin), \
               "wrong document format. Expecting FilterSharingMixin. Got %s"\
               % other_document.__class__
        try:
            file_filters = other_document.get_files()
            for key, val in file_filters.iteritems():
                self.add_repository(key, val)
        except TypeError, error:
            print error, "Using default values for personal data"
        
    # FILE TAB
    def has_file(self, key):
        return self.file_filters.has_key(key)
    
    def add_repository(self, key, filter_value):
        value, activate = filter_value.description, filter_value.activated
        self.config.set(SECTION_FILE, key, ",".join((str(activate), value)))
        if not self.has_file(key):
            self.file_filters[key] = FilterValue(key, value, activate)
        else:
            self.file_filters[key].set_value(value, activate)
        
    def del_repository(self, value):
        if self.file_filters.has_key(value):
            self.config.remove_option(SECTION_FILE, value)
            del self.file_filters[value]
            
    def get_files(self):
        return self.file_filters

class FilterContactMixin(CacheContactMixin):
    """Implements API for all contact data in cache"""

    def __init__(self):
        CacheContactMixin.__init__(self)
        
    def set_peer(self, peer_id, peer_desc):
        peer_desc.node_id = peer_id
        peer_match = PeerMatch(peer_desc)
        self.peers[peer_id] = peer_match
        
class FilterSaverMixin(SaverMixin):
    """Implements API for saving & loading in a File oriented context"""

    def __init__(self):
        SaverMixin.__init__(self)

    # MENU
    def save(self, path):
        """fill document with information from .profile file"""
        profile_file = open(path, 'w')
        profile_file.write("#%s\n"% self.encoding)
        self.config.write(profile_file)
        profile_file.close()

    def _load_config(self, path):
        if not os.path.exists(path):
            print "profile %s does not exists"% path
            return False
        else:
            profile_file = open(path)
            self.encoding = profile_file.readline()[1:]
            self.config = CustomConfigParser(self.encoding)
            self.config.readfp(profile_file)
            profile_file.close()
            return True
        
    def load(self, path):
        """fill document with information from .profile file"""
        # load config
        if not self._load_config(path):
            return False
        # synchronize cache
        for personal_option in self.config.options(SECTION_PERSONAL):
            activate, description = self.config.get(
                SECTION_PERSONAL, personal_option).split(',', 1)
            filter_value = FilterValue(
                value = unicode(description, self.encoding),
                activate = activate == "True")
            try:
                getattr(self, "set_"+personal_option)(filter_value)
            except AttributeError:
                print "Corrupted option", personal_option
                self.config.remove_option(SECTION_PERSONAL, personal_option)
        # sync custom
        for custom_option in self.config.options(SECTION_CUSTOM):
            activate, description = self.config.get(
                SECTION_CUSTOM, custom_option).split(',', 1)
            filter_value = FilterValue(
                value = unicode(description, self.encoding),
                activate = activate == "True")
            self.add_custom_attributes(custom_option, filter_value)
        # sync files
        for file_option in self.config.options(SECTION_FILE):
            activate, description = self.config.get(
                SECTION_FILE, file_option).split(',', 1)
            filter_value = FilterValue(
                value = unicode(description, self.encoding),
                activate = activate == "True")
            self.add_repository(file_option, filter_value)

    def to_stream(self):
        """returns a file object containing values"""
        file_obj = tempfile.TemporaryFile()
        file_obj.write("#%s\n"% self.encoding)
        self.config.write(file_obj)
        file_obj.seek(0)
        return file_obj

class FilterDocument(FilterPersonalMixin, FilterSharingMixin,
                     FilterContactMixin, FilterSaverMixin):
    """Describes all data needed in profile in a file"""

    def __init__(self):
        self.encoding = ENCODING
        self.config = CustomConfigParser(self.encoding)
        FilterPersonalMixin.__init__(self)
        FilterSharingMixin.__init__(self)
        FilterContactMixin.__init__(self)
        FilterSaverMixin.__init__(self)
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        FilterPersonalMixin.import_document(self, other_document)
        FilterSharingMixin.import_document(self, other_document)
        FilterContactMixin.import_document(self, other_document)
        
