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
"""testing high level functionalities"""

# TODO: Fill tests

import unittest
import os.path
import socket
import solipsis.services.profile

from solipsis.services.profile.tests import PROFILE_DIRECTORY, PROFILE_TEST
from solipsis.services.profile.plugin import Plugin
from solipsis.services.profile.facade import create_facade, get_facade, \
     create_filter_facade, get_filter_facade

def get_plugin():
    if PluginTest.plugin is None:
        PluginTest.plugin = Plugin(DumbServiceApi())
        PluginTest.plugin.Init(socket.gethostbyname(socket.gethostname()))
        PluginTest.plugin.EnableBasic()
        create_facade(PROFILE_TEST)
        create_filter_facade(PROFILE_TEST)
    return PluginTest.plugin

class DumbServiceApi(object):

    def SendData(self, data):
        print "sent:", data

    def GetDirectory(self):
        return os.path.dirname(solipsis.services.profile.__file__)

class PluginTest(unittest.TestCase):

    plugin = None

    def setUp(self):
        self.plugin = get_plugin()
        self.facade = create_facade(PROFILE_TEST, PROFILE_DIRECTORY)
        self.filter_facade = create_filter_facade(PROFILE_TEST, PROFILE_DIRECTORY)
        self.facade.load()
        self.filter_facade.load()
        
    def test_get_profile(self):
        pass
        
    def test_get_blog_file(self):
        pass
        
    def test_select_files(self):
        pass
        
    def test_get_files(self):
        pass
    
if __name__ == '__main__':
    unittest.main()
