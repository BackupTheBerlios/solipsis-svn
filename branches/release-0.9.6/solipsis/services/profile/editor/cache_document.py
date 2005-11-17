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

from solipsis.services.profile.editor.document import SaverMixin, \
     AbstractPersonalData, FileSharingMixin, ContactsMixin

class CachePersonalMixin(AbstractPersonalData):
    """Implements API for all pesonal data in cache"""

    def __init__(self):
        AbstractPersonalData.__init__(self)
        # dictionary of file. {att_name : att_value}
        self.custom_attributes = {}
        
    # CUSTOM TAB
    def has_custom_attribute(self, key):
        return self.custom_attributes.has_key(key)
    
    def add_custom_attributes(self, key, value):
        AbstractPersonalData.add_custom_attributes(self, key, value)
        self.custom_attributes[key] = value
        
    def remove_custom_attributes(self, key):
        AbstractPersonalData.remove_custom_attributes(self, key)
        if self.custom_attributes.has_key(key):
            del self.custom_attributes[key]
            
    def get_custom_attributes(self):
        return self.custom_attributes

class CacheDocument(CachePersonalMixin, FileSharingMixin,
                   ContactsMixin, SaverMixin):
    """Describes all data needed in profile in a file"""

    def __init__(self):
        CachePersonalMixin.__init__(self)
        FileSharingMixin.__init__(self)
        ContactsMixin.__init__(self)
        SaverMixin.__init__(self)
        
    def import_document(self, other_document):
        """copy data from another document into self"""
        CachePersonalMixin.import_document(self, other_document)
        FileSharingMixin.import_document(self, other_document)
        ContactsMixin.import_document(self, other_document)

    def load(self, path):
        """load default values if no file"""
        if not SaverMixin.load(self, path):
            CachePersonalMixin.load_defaults(self)
            return False
        else:
            return True
