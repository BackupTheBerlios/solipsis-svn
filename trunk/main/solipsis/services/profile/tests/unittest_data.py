#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# pylint: disable-msg=C0301
# Line too long
"""Represents data stored in cache, especially shared file information"""

import unittest
import os, os.path

from solipsis.services.profile.data import Blogs, load_blogs
from solipsis.services.profile.tests import REPO, PSEUDO, PROFILE_010, \
     PROFILE_DIRECTORY, PROFILE_TEST

DATA_DIR = os.path.join(REPO, "data")
SAMPLE_FILE = os.path.join(DATA_DIR, "été.txt")
SAVE_FILE = os.path.join(DATA_DIR, "sav.txt")
        
class PeerTest(unittest.TestCase):
    """Test PeerDescriptor behaviour"""
    
    def test_creation(self):
        blog = Blogs(PSEUDO, PROFILE_TEST)

    def test_save(self):
        pass
        
class BlogTest(unittest.TestCase):
    """Test Blog behaviour"""
        
    def setUp(self):
        """override one in unittest.TestCase"""
        self.blog = Blogs(PROFILE_TEST, directory=PROFILE_DIRECTORY)
        self.blog.add_blog(u"first blog", PROFILE_TEST)
        self.blog.add_blog(u"second blog", PROFILE_TEST)
        self.blog.add_comment(0, u"commenting the first", PSEUDO)
        self.blog.save()
    
    def test_blog(self):
        self.assertEquals(self.blog.count_blogs(), 2)
        self.assertEquals(self.blog.get_blog(0).text, u"first blog")
        self.assertEquals(self.blog.get_blog(0).count_blogs(), 1)
        self.assertEquals(self.blog.get_blog(1).text, u"second blog")
        self.assertEquals(self.blog.get_blog(1).count_blogs(), 0)
    
    def test_security(self):
        self.assertRaises(AssertionError, self.blog.add_blog, u"forbidden", 'jules')
        self.assertRaises(AssertionError, self.blog.remove_blog, 0, 'jules')
        self.assertRaises(AssertionError, self.blog.get_blog, 2)

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
        loaded_blog = load_blogs(PROFILE_TEST, directory=PROFILE_DIRECTORY)
        self.assertEquals(loaded_blog.count_blogs(), 2)
        self.assertEquals(loaded_blog.get_blog(0).text, u"first blog")
        self.assertEquals(loaded_blog.get_blog(0).count_blogs(), 1)
        self.assertEquals(loaded_blog.get_blog(1).text, u"second blog")
        self.assertEquals(loaded_blog.get_blog(1).count_blogs(), 0)

    def test_retro_compatibility(self):
        loaded_blog = load_blogs(PROFILE_010, directory=PROFILE_DIRECTORY)
        self.assertEquals(loaded_blog.count_blogs(), 4)
        self.assertEquals(loaded_blog.get_blog(0).text, u"Hi there! Watch my next movie... it's going to be real fun")
        self.assertEquals(loaded_blog.get_blog(0).count_blogs(), 0)
        self.assertEquals(loaded_blog.get_blog(1).text, u"I won't tell you much but this I can say: it's going to be terrific!")
        self.assertEquals(loaded_blog.get_blog(2).text, u'Watch here for its name... coming soon')
        self.assertEquals(loaded_blog.get_blog(3).text, u"A Godess' world.  What do you think?")

if __name__ == '__main__':
    unittest.main()
