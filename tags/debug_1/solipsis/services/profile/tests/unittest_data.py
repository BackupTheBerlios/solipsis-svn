#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# pylint: disable-msg=W0131,C0301,C0103
# Missing docstring, Line too long, Invalid name
"""Represents data stored in cache, especially shared file information"""

__revision__ = "$Id$"

import unittest
import os, os.path

from solipsis.services.profile.data import PeerDescriptor, Blogs, load_blogs
from solipsis.services.profile.prefs import get_prefs, set_prefs
from solipsis.services.profile.tests import get_bruce_profile, write_test_profile
from solipsis.services.profile.tests import PSEUDO, BLOG_EXT, TEST_DIR,  FILE_TEST, \
     PROFILE_DIR, PROFILE_TEST, PROFILE_BRUCE, PROFILE_010

DATA_DIR = os.path.join(TEST_DIR, "data")
SAMPLE_FILE = os.path.join(DATA_DIR, "été.txt")
SAVE_FILE = os.path.join(DATA_DIR, "sav.txt")
        
class PeerTest(unittest.TestCase):

    def setUp(self):
        write_test_profile()
    
    def test_creation(self):
        bruce = get_bruce_profile()
        self.assertEquals(bruce.node_id, PROFILE_BRUCE)
        self.assertEquals(bruce.blog[0].text, u'Hi Buddy')
        self.assertEquals(bruce.document.get_pseudo(), u'bruce')

    def test_load_and_save(self):
        peer_desc = PeerDescriptor(PROFILE_TEST)
        peer_desc.load(directory=PROFILE_DIR)
        self.assertEquals(peer_desc.blog.count_blogs(), 1)
        self.assertEquals(peer_desc.document.get_pseudo(), PSEUDO)
        # change
        peer_desc.blog.add_blog(u"second blog", PSEUDO)
        peer_desc.document.set_pseudo(u"yop la hop")
        peer_desc.save(directory=PROFILE_DIR)
        # check
        new_desc = PeerDescriptor(PROFILE_TEST)
        new_desc.load(directory=PROFILE_DIR)
        self.assertEquals(new_desc.blog.count_blogs(), 2)
        self.assertEquals(new_desc.document.get_pseudo(), u"yop la hop")
        
        
class BlogTest(unittest.TestCase):
    """Test Blog behaviour"""   
        
    def setUp(self):
        """override one in unittest.TestCase"""
        write_test_profile()
        self.blog = Blogs()
        self.blog.add_blog(u"first blog", PROFILE_TEST)
        self.blog.add_blog(u"second blog", PROFILE_TEST)
        self.blog.add_comment(0, u"commenting the first", PSEUDO)
    
    def test_blog(self):
        self.assertEquals(self.blog.count_blogs(), 2)
        self.assertEquals(self.blog.get_blog(0).text, u"first blog")
        self.assertEquals(self.blog.get_blog(0).count_blogs(), 1)
        self.assertEquals(self.blog.get_blog(1).text, u"second blog")
        self.assertEquals(self.blog.get_blog(1).count_blogs(), 0)
    
    def test_copy(self):
        copied_blog = self.blog.copy()
        # add some blogs in first
        self.blog.add_blog(u"more blog", PROFILE_TEST)
        self.blog.add_comment(0, u"commenting (again) the first", PSEUDO)
        # check result
        self.assertEquals(self.blog.count_blogs(), 3)
        self.assertEquals(self.blog.get_blog(0).count_blogs(), 2)
        # check copy
        self.assertEquals(copied_blog.count_blogs(), 2)
        self.assertEquals(copied_blog.get_blog(0).text, u"first blog")
        self.assertEquals(copied_blog.get_blog(0).count_blogs(), 1)
        self.assertEquals(copied_blog.get_blog(1).text, u"second blog")
        self.assertEquals(copied_blog.get_blog(1).count_blogs(), 0)

    def test_load(self):
        loaded_blog = load_blogs(FILE_TEST + BLOG_EXT)
        self.assertEquals(loaded_blog.count_blogs(), 1)
        self.assertEquals(loaded_blog.get_blog(0).text, u"This is a test")
        self.assertEquals(loaded_blog.get_blog(0).count_blogs(), 0)

    def test_retro_compatibility(self):
        loaded_blog = load_blogs(os.path.join(PROFILE_DIR, PROFILE_010 + BLOG_EXT))
        self.assertEquals(loaded_blog.count_blogs(), 4)
        self.assertEquals(loaded_blog.get_blog(0).text, u"Hi there! Watch my next movie... it's going to be real fun")
        self.assertEquals(loaded_blog.get_blog(0).count_blogs(), 0)
        self.assertEquals(loaded_blog.get_blog(1).text, u"I won't tell you much but this I can say: it's going to be terrific!")
        self.assertEquals(loaded_blog.get_blog(2).text, u'Watch here for its name... coming soon')
        self.assertEquals(loaded_blog.get_blog(3).text, u"A Godess' world.  What do you think?")

if __name__ == '__main__':
    unittest.main()
