"""Represents data stored in cache, especially shared file information"""

import unittest
import sys

from StringIO import StringIO
from solipsis.services.profile.data import DEFAULT_TAG, \
     SharingContainer, DirContainer, FileContainer

class DataTest(unittest.TestCase):
    """Test cache coherency with following arborescency:
    
    data/
    |-- date.txt
    |-- emptydir
    |-- profiles
    |   |-- bruce.prf
    |   |-- demi.prf
    |   `-- test.prf
    |-- routage
    `-- subdir1
        |-- date.doc
        `-- subsubdir
            |-- default.solipsis
            |-- dummy.txt
            `-- null"""
        
    def setUp(self):
        """override one in unittest.TestCase"""
        self.container = SharingContainer()

    def test_setting(self):
        """get data"""
        # dir
        self.container.add_dir("data/")
        self.container.add_dir("data/subdir1/subsubdir")
        self.assertRaises(KeyError, self.container.add_dir, "data/date.txt")
        # file
        self.container.add_file("data/subdir1/date.doc")
        self.container.add_file("data/subdir1/subsubdir/null")
        self.assertRaises(KeyError, self.container.add_file, "data/emptydir")
        # generic
        self.container.add("data/profiles")
        self.container.add("data/routage")
        # wrapper
        dir_c = DirContainer("data/emptydir")
        file_c = FileContainer("data/subdir1/subsubdir/default.solipsis")
        self.container["data/emptydir"] = dir_c
        self.container["data/subdir1/subsubdir/default.solipsis"] = file_c
        self.assertRaises(KeyError, self.container.__setitem__, *("data/false", DirContainer("data")))
        self.assertRaises(KeyError, self.container.__setitem__, *("data/false", FileContainer("data/date.txt")))
        self.assertRaises(ValueError, self.container.__setitem__, *("data", None))
        self.assertRaises(ValueError, self.container.__setitem__, *("data", "false"))
        self.assertRaises(ValueError, self.container.__setitem__, *("data", 1))

    def test_getting(self):
        """get data"""
        # dir
        self.container.add_dir("data/")
        self.assertEquals(isinstance(self.container["data"], DirContainer), True)
        # file
        self.container.add_file("data/subdir1/date.doc")
        self.assertEquals(isinstance(self.container["data/subdir1/date.doc"], FileContainer), True)
        # generic
        self.container.add("data/profiles")
        self.container.add("data/routage")
        self.assertEquals(isinstance(self.container["data/profiles"], DirContainer), True)
        self.assertEquals(isinstance(self.container["data/routage"], FileContainer), True)
        # wrapper
        dir_c = DirContainer("data/emptydir")
        file_c = FileContainer("data/subdir1/subsubdir/default.solipsis")
        self.container["data/emptydir"] = dir_c
        self.container["data/subdir1/subsubdir/default.solipsis"] = file_c
        self.assertEquals(self.container["data/emptydir"], dir_c)
        self.assertEquals(self.container["data/subdir1/subsubdir/default.solipsis"], file_c)
        
    def test_deleting(self):
        """get data"""
        # add data
        dir_str = "data/emptydir"
        file_str = "data/subdir1/subsubdir/default.solipsis"
        self.container[dir_str] = DirContainer(dir_str)
        self.container[file_str] = FileContainer(file_str)
        self.assertEquals(self.container.has_key(dir_str), True)
        self.assertEquals(self.container.has_key(file_str), True)
        del self.container[dir_str]
        del self.container[file_str]
        self.assertEquals(self.container.has_key(dir_str), False)
        self.assertEquals(self.container.has_key(file_str), False)
        
    def test_expanding(self):
        """good completion of dirs on expanding command"""
        self.container.add_dir("data")
        self.container.add_dir("data/subdir1")
        self.assert_(self.container.has_key("data/subdir1"))
        self.assert_(not self.container.has_key("data/profiles"))
        self.assert_(not self.container.has_key("data/emptydir"))
        self.assert_(not self.container.has_key("data/routage"))
        self.assert_(not self.container.has_key("data/.path"))
        self.assert_(not self.container.has_key("data/date.txt"))
        #expand
        self.container.expand_dir("data")
        self.assert_(self.container.has_key("data"))
        self.assert_(self.container.has_key("data/subdir1"))
        self.assert_(self.container.has_key("data/profiles"))
        self.assert_(self.container.has_key("data/emptydir"))
        self.assert_(self.container.has_key("data/routage"))
        self.assert_(self.container.has_key("data/.path"))
        self.assert_(self.container.has_key("data/date.txt"))
        self.assert_(not self.container.has_key("data/subdir1/subsubdir"))
        
    def test_sharing(self):
        """share/unshare file and dirs"""
        self.container.add_dir("data")
        self.container.expand_dir("data")
        self.container.expand_dir("data/subdir1")
        self.assertEquals(self.container["data"].nb_shared(), 0)
        self.container.share_files("data", [".path", "date.txt"])
        self.assertEquals(self.container["data"].nb_shared(), 2)
        self.container.share_dir("data/subdir1/subsubdir")
        self.assertEquals(self.container["data/subdir1/subsubdir"].nb_shared(), -1)
        self.container.share_dir("data", False)
        self.assertEquals(self.container["data"].nb_shared(), 2)
        self.container.share_dir("data/subdir1/subsubdir", False)
        self.assertEquals(self.container["data/subdir1/subsubdir"].nb_shared(), 0)
        self.container.share_files("data/subdir1/subsubdir", ["dummy.txt"], True)
        self.assertEquals(self.container["data/subdir1/subsubdir"].nb_shared(), 1)

    def test_tagging(self):
        """coherent listing of content"""
        self.container.add_dir("data")
        self.container.tag_files("data", ["routage", "date.txt", "subdir1"], u"tag1")
        self.assertEquals(self.container["data"]["routage"]._tag, u"tag1")
        self.assertEquals(self.container["data"]["date.txt"]._tag, u"tag1")
        self.assertEquals(self.container["data"]["subdir1"]._tag, u"tag1")
        self.assertEquals(self.container["data"][".path"]._tag, DEFAULT_TAG)

if __name__ == '__main__':
    unittest.main()
