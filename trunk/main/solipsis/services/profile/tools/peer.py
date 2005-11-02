# -*- coding: iso-8859-1 -*-
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
"""Define cache structures used in profile and rendered in list widgets"""

__revision__ = "$Id$"

import os, os.path
import pickle
import time
import gettext
_ = gettext.gettext

from solipsis.services.profile import ENCODING, PROFILE_EXT, \
     BLOG_EXT, BULB_ON_IMG, BULB_OFF_IMG, VERSION
from solipsis.services.profile.tools.message import display_warning, display_error
from solipsis.services.profile.tools.prefs import get_prefs
from solipsis.services.profile.tools.blog import Blogs, Blog, load_blogs

# PEERS ##############################################################
class PeerDescriptor:
    """contains information relative to peer"""

    ANONYMOUS = 'Anonym'
    FRIEND = 'Friend'
    BLACKLISTED = 'Blacklisted'
    COLORS = {ANONYMOUS: 'black',
              FRIEND:'blue',
              BLACKLISTED:'red'}
    
    def __init__(self, node_id, document=None, blog=None,
                 state=ANONYMOUS, connected=False):
        # status
        self.node_id = node_id
        self.state = state
        self.connected = connected
        # data
        from solipsis.services.profile.editor.cache_document import CacheDocument
        self.document = document or CacheDocument()
        self.blog = blog or Blogs()

    def get_id(self):
        """NEEDED to be compliant with PeerMatch API"""
        return self.node_id

    def copy(self):
        """return copied instance of PeerDescriptor"""
        return PeerDescriptor(self.node_id,
                              self.document.copy(),
                              self.blog.copy(),
                              self.state,
                              self.connected)

    # IO #############################################################
    def load(self, directory=None, doc_extension=PROFILE_EXT):
        """load both document & blog"""
        if directory is None:
            directory = get_prefs("profile_dir")
        file_path = os.path.join(directory, self.node_id)
        self.document.load(file_path + doc_extension)
        self.blog = load_blogs(file_path + BLOG_EXT)

    def save(self, directory=None, doc_extension=PROFILE_EXT):
        """save both document & blog"""
        if directory is None:
            directory = get_prefs("profile_dir")
        file_path = os.path.join(directory, self.node_id)
        self.document.save(file_path + doc_extension)
        self.blog.save(file_path + BLOG_EXT)
        
    def html(self):
        """render peer in HTML"""
        from solipsis.services.profile.editor.facade import get_facade
        return "<img src='%s'/><font color=%s>%s</font>"\
               % (self.connected and BULB_ON_IMG() or BULB_OFF_IMG(),
                  PeerDescriptor.COLORS[self.state],
                  get_facade()._desc.document.get_pseudo().encode(ENCODING))

    # extraction #####################################################
    def custom_as_dict(self):
        return self.document.get_custom_attributes()

    def peer_as_dict(self):
        return {"title": self.document.get_title(),
                "firstname":  self.document.get_firstname(),
                "lastname":  self.document.get_lastname(),
                "pseudo":  self.document.get_pseudo(),
                "photo":  self.document.get_photo(),
                "email": self.document.get_email()}

    def files_as_dicts(self):
        result = []
        file_containers = self.document.get_shared_files().flatten()
        for file_container in file_containers:
            result.append({'name': file_container.name,
                           'size': file_container.size})
        return result
        
