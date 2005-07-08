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

import re
import os.path
from solipsis.services.profile import PROFILE_DIR, FILTER_EXT, \
     DEFAULT_INTERESTS, ENCODING
from solipsis.services.profile.document import AbstractPersonalData, \
     CustomConfigParser, SECTION_PERSONAL, SECTION_CUSTOM, SECTION_FILE
from solipsis.services.profile.file_document import FileSaverMixin

class FilterValue:
    """wrapper for filter: regex, description ans state"""

    def __init__(self, name="no name", value=u"", activate=False):
        self.description = value
        self.regex = re.compile(value)
        self.activated = activate
        self._name = name # name of member which is defined by FilterValue
        self._found = None # value which has been matched

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
        self.regex = re.compile(value)
        self.activated = activate

    def activate(self, activate=True):
        """change state"""
        self.activated = activate
        
    def does_match(self, data):
        """apply regex on data and returns self if there is any match"""
        # no match -> return false
        if not self.activated or len(self.description) == 0:
            return False
        if self.regex.match(data) is None:
            return False
        # match -> return true
        self._found = data
        return self

class FilterPersonalMixin(AbstractPersonalData):
    """Implements API for all pesonal data in cache"""

    def __init__(self):
        # config
        self.config.add_section(SECTION_PERSONAL)
        self.config.add_section(SECTION_CUSTOM)
        # cache
        self.title = FilterValue("title")
        self.firstname = FilterValue("firstname")
        self.lastname = FilterValue("lastname")
        self.photo = FilterValue("photo")
        self.email = FilterValue("email")
        # dictionary of file. {att_name : att_value}
        self.custom_attributes = {}
        for interest in DEFAULT_INTERESTS:
            self.custom_attributes[interest] = FilterValue(interest)
        AbstractPersonalData.__init__(self)

    def _set(self, member, filter_value):
        """set member both in cache & in file"""
        value, activate = filter_value.description, filter_value.activated
        member.set_value(value, activate)
        self.config.set(SECTION_PERSONAL, str(member),
                        ",".join((str(activate), value)))
        return member
        
    # PERSONAL TAB
    def set_title(self, filter_value):
        """sets new value for title"""
        if self.title == filter_value:
            return False
        else:
            return self._set(self.title, filter_value)
    
    def get_title(self):
        """returns value of title"""
        return self.title
        
    def set_firstname(self, filter_value):
        """sets new value for firstname"""
        if self.firstname == filter_value:
            return False
        else:
            return self._set(self.firstname, filter_value)
    
    def get_firstname(self):
        """returns value of firstname"""
        return self.firstname

    def set_lastname(self, filter_value):
        """sets new value for lastname"""
        if self.lastname == filter_value:
            return False
        else:
            return self._set(self.lastname, filter_value)
    
    def get_lastname(self):
        """returns value of lastname"""
        return self.lastname

    def set_photo(self, filter_value):
        """sets new value for photo"""
        if self.photo == filter_value:
            return False
        else:
            return self._set(self.photo, filter_value)
    
    def get_photo(self):
        """returns value of photo"""
        return self.photo

    def set_email(self, filter_value):
        """sets new value for email"""
        if self.email == filter_value:
            return False
        else:
            return self._set(self.email, filter_value)
    
    def get_email(self):
        """returns value of email"""
        return self.email

    #FIXME: remove from document and put it in options
    def set_download_repo(self, value):
        """sets new value for download_repo"""
        pass
    def get_download_repo(self):
        """returns value of download_repo"""
        return FilterValue()
    
    # CUSTOM TAB
    def has_custom_attribute(self, key):
        """return true if the key exists"""
        return self.custom_attributes.has_key(key)
    
    def add_custom_attributes(self, (key, filter_value)):
        """sets new value for custom_attributes"""
        value, activate = filter_value.description, filter_value.activated
        self.config.set(SECTION_CUSTOM, key, ",".join((str(activate), value)))
        if not self.has_custom_attribute(key):
            self.custom_attributes[key] = FilterValue(key, value, activate)
        else:
            self.custom_attributes[key].set_value(value, activate)
        
    def remove_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        AbstractPersonalData.remove_custom_attributes(self, value)
        if self.custom_attributes.has_key(value):
            self.config.remove_option(SECTION_CUSTOM, value)
            del self.custom_attributes[value]
            
    def get_custom_attributes(self):
        """returns value of custom_attributes"""
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
                self.add_file((key, val))
        except TypeError, error:
            print error, "Using default values for personal data"
        
    # FILE TAB
    def has_file(self, key):
        """return true if the key exists"""
        return self.file_filters.has_key(key)
    
    def add_file(self, (key, filter_value)):
        """sets new value for files"""
        value, activate = filter_value.description, filter_value.activated
        self.config.set(SECTION_FILE, key, ",".join((str(activate), value)))
        if not self.has_file(key):
            self.file_filters[key] = FilterValue(key, value, activate)
        else:
            self.file_filters[key].set_value(value, activate)
        
    def del_file(self, value):
        """sets new value for files"""
        if self.file_filters.has_key(value):
            self.config.remove_option(SECTION_FILE, value)
            del self.file_filters[value]
            
    def get_files(self):
        """returns value of files"""
        return self.file_filters

class FilterSaverMixin(FileSaverMixin):
    """Implements API for saving & loading in a File oriented context"""

    def get_id(self):
        """return identifiant of Document"""
        return os.path.join(self._dir, self.pseudo) + FILTER_EXT
        
    def load(self,):
        """fill document with information from .profile file"""
        # load config
        FileSaverMixin.load(self)
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
            self.add_custom_attributes((custom_option, filter_value))
        # sync files
        for file_option in self.config.options(SECTION_FILE):
            activate, description = self.config.get(
                SECTION_FILE, file_option).split(',', 1)
            filter_value = FilterValue(
                value = unicode(description, self.encoding),
                activate = activate == "True")
            self.add_file((file_option, filter_value))

class FilterDocument(FilterPersonalMixin, FilterSharingMixin, FilterSaverMixin):
    """Describes all data needed in profile in a file"""

    def __init__(self, pseudo, directory=PROFILE_DIR):
        self.encoding = ENCODING
        self.config = CustomConfigParser(ENCODING)
        self.filtered_pseudo = FilterValue("filtered_pseudo")
        # {root: DirContainers}
        self.files = {}
        # dictionary of peers. {pseudo : PeerDescriptor}
        self.peers = {}
        self.matches = []
        FilterPersonalMixin.__init__(self)
        FilterSharingMixin.__init__(self)
        FilterSaverMixin.__init__(self, pseudo, directory)
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        FilterPersonalMixin.import_document(self, other_document)
        FilterSharingMixin.import_document(self, other_document)
        
    def set_filtered_pseudo(self, filter_value):
        """sets new value for title"""
        if self.filtered_pseudo == filter_value:
            return False
        else:
            return self._set(self.filtered_pseudo, filter_value)
    
    def get_filtered_pseudo(self):
        """returns value of title"""
        return self.filtered_pseudo

    def does_match(self, peer_desc):
        """check that given peer_desc matches FilterValues"""
        self.matches = []
        if peer_desc.document:
            doc = peer_desc.document
            self.matches.append(self.title.does_match(doc.get_title()))
            self.matches.append(self.firstname.does_match(doc.get_firstname()))
            self.matches.append(self.lastname.does_match(doc.get_lastname()))
            self.matches.append(self.photo.does_match(doc.get_photo()))
            self.matches.append(self.email.does_match(doc.get_email()))
            # dictionary of custom attributes
            peer_customs = doc.get_custom_attributes()
            for custom_name, custom_filter in self.custom_attributes.iteritems():
                if peer_customs.has_key(custom_name):
                    self.matches.append(
                        custom_filter.does_match(peer_customs[custom_name]))
        if peer_desc.shared_files:
            # dictionary of files
            for filter_name, file_filter in self.file_filters.iteritems():
                for file_container in peer_desc.shared_files.flatten():
                    self.matches.append(file_filter.does_match(file_container.name))
        # remove False from matches
        self.matches = (peer_desc, [match for match in self.matches if match != False])
        return len(self.matches[1])
