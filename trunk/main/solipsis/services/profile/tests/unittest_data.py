"""Represents data stored in cache, especially shared file information"""

import unittest
import sys

from StringIO import StringIO
from solipsis.services.profile.data import SharingContainer, DEFAULT_TAG

class SimpleView:
    """utility class to emulate real widget (wx.ListCtrl)"""
    def __init__(self, iostring):
        self.content = {}
        self.iostring = iostring
        self.item = 0

    def __str__(self):
        return self.iostring.getvalue()

    def append_item(self, parent, name):
        self.item += 1
        self.content[self.item] = name
        return self.item

    def delete_item(self, item):
        del self.content[item]

    def display(self, container):
        print >> self.iostring, container


class CacheTest(unittest.TestCase):
    """test that cache coherency with following arborescency
         data
         data/routage
         data/date.txt
         data/.path
         data/emptydir
         data/subdir1
         data/subdir1/date.doc
         data/subdir1/subsubdir
         data/subdir1/subsubdir/default.solipsis
         data/subdir1/subsubdir/dummy.txt
         data/subdir1/subsubdir/null"""
        
    def setUp(self):
        """override one in unittest.TestCase"""
        self.container = SharingContainer()

    def test_repository(self):
        """add and remove repo"""
        self.container.add_dir("data")
        self.container.add_dir("data/subdir1/subsubdir")
        self.container.add_dir("data/emptydir")
        self.assert_(self.container.data.has_key("data"))
        self.assert_(self.container.data.has_key("data/subdir1/subsubdir"))
        self.assert_(self.container.data.has_key("data/emptydir"))
        
        self.container.remove_dir("data/subdir1/subsubdir")
        self.container.remove_dir("data")
        self.assert_(not self.container.data.has_key("data"))
        self.assert_(not self.container.data.has_key("data/subdir1/subsubdir"))
        self.assert_(self.container.data.has_key("data/emptydir"))

    def test_expanding(self):
        """good completion of dirs on expanding command"""
        self.container.add_dir("data")
        self.container.expand_dir("data")
        self.assert_(self.container.data.has_key("data"))
        self.assert_(self.container.data.has_key("data/subdir1"))
        self.assert_(self.container.data.has_key("data/emptydir"))
        self.assert_(not self.container.data.has_key("data/subdir1/subsubdir"))
        self.assert_(not self.container.data.has_key("data/routage"))
        self.assert_(not self.container.data.has_key("data/.path"))
        self.assert_(not self.container.data.has_key("data/date.txt"))
        
    def test_sharing(self):
        """share/unshare file and dirs"""
        self.container.add_dir("data")
        self.container.expand_dir("data")
        self.container.expand_dir("data/subdir1")
        self.assertEquals(self.container.data["data"].nb_shared(), 0)
        self.container.share_files("data", [".path", "date.txt"])
        self.assertEquals(self.container.data["data"].nb_shared(), 2)
        self.container.share_dir("data/subdir1/subsubdir")
        self.assertEquals(self.container.data["data/subdir1/subsubdir"].nb_shared(), 3)
        self.container.share_dir("data", False)
        self.assertEquals(self.container.data["data"].nb_shared(), 0)
        self.container.share_files("data/subdir1/subsubdir", ["dummy.txt"], False)
        self.assertEquals(self.container.data["data/subdir1/subsubdir"].nb_shared(), 2)

    def test_tagging(self):
        """coherent listing of content"""
        self.container.add_dir("data")
        self.container.tag_files("data", ["routage", "date.txt"], u"tag1")
        self.assertEquals(self.container.data["data"].content["routage"]._tag, u"tag1")
        self.assertEquals(self.container.data["data"].content["date.txt"]._tag, u"tag1")
        self.assertEquals(self.container.data["data"].content[".path"]._tag, DEFAULT_TAG)
        self.assertRaises(ValueError, self.container.tag_files, *("data", ["subdir1"], u"tag1"))

    def test_listing(self):
        """coherent listing of content"""
        self.container.add_dir("data")
        self.container.expand_dir("data")
        self.container.share_files("data", [".path", "date.txt"])
        self.container.tag_files("data", ["routage", "date.txt"], u"tag1")
        content = self.container.get_dir_content("data")
        self.assertEquals(str(content), "{'routage': data/routage  [tag1], '.path': data/.path [shared] [none], 'test.prf': data/test.prf  [none], 'date.txt': data/date.txt [shared] [tag1]}")
    
if __name__ == '__main__':
    unittest.main()
