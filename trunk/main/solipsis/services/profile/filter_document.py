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
from solipsis.services.profile import PROFILE_DIR, FILTER_EXT, DEFAULT_INTERESTS, ENCODING
from solipsis.services.profile.document import AbstractPersonalData, \
     CustomConfigParser, SECTION_PERSONAL, SECTION_CUSTOM, SECTION_FILE
from solipsis.services.profile.file_document import FileSaverMixin

class FilterValue:
    """wrapper for filter: regex, description ans state"""

    def __init__(self, name, value=u"", activate=False):
        self.name = name
        self.description = value
        self.regex = re.compile(value)
        self.activated = activate

    def __str__(self):
        return self.name

    def set_value(self, value, activate=True):
        """recompile regex and (dis)activate filter"""
        self.description = value
        self.regex = re.compile(value)
        self.activated = activate

    def activate(self, activate=True):
        """change state"""
        self.activated = activate
        
    def does_match(self, data):
        """apply regex on data and returns True if there is any match"""
        if not self.activated or len(self.description) == 0:
            return False
        if self.regex.match(data) is None:
            return False
        else:
            return True

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

    def _set(self, member, value, activate):
        """set member both in cache & in file"""
        member.set_value(value, activate)
        self.config.set(SECTION_PERSONAL, str(member),
                        ",".join((str(activate), value)))
        return member
        
    # PERSONAL TAB
    def set_title(self, (value, activate)):
        """sets new value for title"""
        if AbstractPersonalData.set_title(self, value) is False:
            return False
        else:
            return self._set(self.title, value, activate)
    
    def get_title(self):
        """returns value of title"""
        return self.title
        
    def set_firstname(self, (value, activate)):
        """sets new value for firstname"""
        if AbstractPersonalData.set_firstname(self, value) is False:
            return False
        else:
            return self._set(self.firstname, value, activate)
    
    def get_firstname(self):
        """returns value of firstname"""
        return self.firstname

    def set_lastname(self, (value, activate)):
        """sets new value for lastname"""
        if AbstractPersonalData.set_lastname(self, value) is False:
            return False
        else:
            return self._set(self.lastname, value, activate)
    
    def get_lastname(self):
        """returns value of lastname"""
        return self.lastname

    def set_photo(self, (value, activate)):
        """sets new value for photo"""
        if AbstractPersonalData.set_photo(self, value) is False:
            return False
        else:
            return self._set(self.photo, value, activate)
    
    def get_photo(self):
        """returns value of photo"""
        return self.photo

    def set_email(self, (value, activate)):
        """sets new value for email"""
        if AbstractPersonalData.set_email(self, value) is False:
            return False
        else:
            return self._set(self.email, value, activate)
    
    def get_email(self):
        """returns value of email"""
        return self.email

    # CUSTOM TAB
    def has_custom_attribute(self, key):
        """return true if the key exists"""
        return self.custom_attributes.has_key(key)
    
    def add_custom_attributes(self, (key, value, activate)):
        """sets new value for custom_attributes"""
        AbstractPersonalData.add_custom_attributes(self, (key, value))
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
        self.files_attributess = {}
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        assert isinstance(FilterSharingMixin, other_document), \
               "wrong document format. Expecting FilterSharingMixin. Got %s"\
               % other_document.__class__
        try:
            file_filters = other_document.get_files_attributess()
            for key, val in file_filters.iteritems():
                self.add_files_attributess((key, val.description, val.activate))
        except TypeError, error:
            print error, "Using default values for personal data"
        
    # FILE TAB
    def has_files_attributes(self, key):
        """return true if the key exists"""
        return self.files_attributess.has_key(key)
    
    def add_files_attributes(self, (key, value, activate)):
        """sets new value for files_attributess"""
        self.config.set(SECTION_FILE, key, ",".join((str(activate), value)))
        if not self.has_files_attributes(key):
            self.files_attributess[key] = FilterValue(key, value, activate)
        else:
            self.files_attributess[key].set_value(value, activate)
        
    def remove_files_attributes(self, value):
        """sets new value for files_attributess"""
        if self.files_attributess.has_key(value):
            self.config.remove_option(SECTION_FILE, value)
            del self.files_attributess[value]
            
    def get_files_attributes(self):
        """returns value of files_attributess"""
        return self.files_attributess

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
            getattr(self, "set_"+personal_option)(
                (unicode(description, self.encoding), bool(activate)))
        # sync custom
        for custom_option in self.config.options(SECTION_CUSTOM):
            activate, description = self.config.get(
                SECTION_CUSTOM, custom_option).split(',', 1)
            self.add_custom_attributes(
                (custom_option, unicode(description, self.encoding), bool(activate)))
        # sync files
        for file_option in self.config.options(SECTION_FILE):
            activate, description = self.config.get(
                SECTION_FILE, file_option).split(',', 1)
            self.add_files_attributes((
                file_option, unicode(description, self.encoding), bool(activate)))

class FilterDocument(FilterPersonalMixin, FilterSharingMixin, FilterSaverMixin):
    """Describes all data needed in profile in a file"""

    def __init__(self, pseudo, directory=PROFILE_DIR):
        self.encoding = ENCODING
        self.config = CustomConfigParser(ENCODING)
        # {root: DirContainers}
        self.files = {}
        # dictionary of peers. {pseudo : PeerDescriptor}
        self.peers = {}
        FilterPersonalMixin.__init__(self)
        FilterSharingMixin.__init__(self)
        FilterSaverMixin.__init__(self, pseudo, directory)
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        FilterPersonalMixin.import_document(self, other_document)
        FilterSharingMixin.import_document(self, other_document)
