"""Represents data stored in cache, especially shared file information"""

import unittest
import sys

from os.path import abspath
from StringIO import StringIO
from solipsis.services.profile.data import DEFAULT_TAG, \
     DirContainer, FileContainer

REPO = u"/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests/"

class DataTest(unittest.TestCase):
    """Test cache coherency with following arborescency:
    
    data/
    |-- .svn
    |-- date.txt
    |-- emptydir
    |-- profiles
    |   |-- .svn
    |   |-- bruce.prf
    |   |-- demi.prf
    |   `-- test.prf
    |-- routage
    `-- subdir1
        |-- .svn
        |-- date.doc
        `-- subsubdir
            |-- .svn
            |-- default.solipsis
            |-- dummy.txt
            `-- null"""
        
    def setUp(self):
        """override one in unittest.TestCase"""
        self.container = DirContainer(REPO)

    def test_containers(self):
        """creates valid containers"""
        self.assertRaises(AssertionError, DirContainer,  REPO + "data/dummy")
        self.assertRaises(AssertionError, FileContainer,  REPO + "data/dummy.txt")

        
    def test_setting(self):
        """set data"""
        # setting bad values
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, "youpi"))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, None))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, 1))
        dir_c = DirContainer("data/emptydir")
        file_c = FileContainer("data/subdir1/date.doc")
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, dir_c))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, file_c))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, dir_c))
        # simple sets
        self.container[REPO + u"data/"] = DirContainer(REPO + u"data/")
        self.container[REPO + u"data/"] = DirContainer(REPO + u"data")
        self.container[REPO + "data/subdir1/subsubdir"] = DirContainer(REPO + u"data/subdir1/subsubdir")
        self.container[REPO + u"data/subdir1/date.doc"] = FileContainer(REPO + u"data/subdir1/date.doc")
        self.container[REPO + "data/subdir1/subsubdir/null"] = FileContainer(REPO + u"data/subdir1/subsubdir/null")
        self.container[REPO + "runtests.py"] = FileContainer(REPO + u"runtests.py")

    def test_getting(self):
        """get data"""
        # dir
        self.container.add(REPO + "data/")
        self.assertEquals(isinstance(self.container[REPO + u"data"], DirContainer), True)
        # file
        self.container.add(REPO + "data/subdir1/date.doc")
        self.container.add(REPO +"runtests.py")
        self.assertEquals(isinstance(self.container[REPO + "data/subdir1/date.doc"], FileContainer), True)
        self.assertEquals(isinstance(self.container[REPO + "runtests.py"], FileContainer), True)
        # generic
        self.container.add(REPO + "data/profiles")
        self.container.add(REPO + "data/routage")
        self.assertEquals(isinstance(self.container[REPO + "data/profiles"], DirContainer), True)
        self.assertEquals(isinstance(self.container[REPO + "data/routage"], FileContainer), True)
        # wrapper
        dir_c = DirContainer(REPO + "data/emptydir")
        file_c = FileContainer(REPO + "data/subdir1/subsubdir/default.solipsis")
        self.container[REPO + "data/emptydir"] = dir_c
        self.container[REPO + "data/subdir1/subsubdir/default.solipsis"] = file_c
        self.assertEquals(self.container[REPO + "data/emptydir"].name, "emptydir")
        self.assertEquals(self.container[REPO + "data/subdir1/subsubdir/default.solipsis"].name, "default.solipsis")
        
    def test_deleting(self):
        """delete data"""
        # add data
        root_str = REPO + "runtests.py"
        dir_str = REPO + u"data/emptydir"
        file_str = REPO + "data/subdir1/subsubdir/default.solipsis"
        self.assertEquals(self.container.has_key(root_str), False)
        self.assertEquals(self.container.has_key(dir_str), False)
        self.assertEquals(self.container.has_key(file_str), False)
        self.container[root_str] = FileContainer(root_str)
        self.container[dir_str] = DirContainer(dir_str)
        self.container[file_str] = FileContainer(file_str)
        self.assertEquals(self.container.has_key(dir_str), True)
        self.assertEquals(self.container.has_key(dir_str), True)
        self.assertEquals(self.container.has_key(file_str), True)
        del self.container[root_str]
        del self.container[dir_str]
        del self.container[file_str]
        self.assertEquals(self.container.has_key(root_str), False)
        self.assertEquals(self.container.has_key(dir_str), False)
        self.assertEquals(self.container.has_key(file_str), False)

    def test_adding(self):
        """add data"""
        # dir
        self.assertRaises(AssertionError, self.container.add, REPO + "data/dummy")
        self.assertRaises(AssertionError, self.container.add, REPO + "data/dummy.txt")
        self.assertRaises(AssertionError, self.container.add, "data")
        self.container.add(REPO + u"data/")
        self.container.add(REPO + "data/subdir1/subsubdir")
        self.container.add(REPO + u"data/subdir1/date.doc")
        self.container.add(REPO + "data/subdir1/subsubdir/null")
        self.container.add(REPO + "runtests.py")
        
    def test_expanding(self):
        """expanding command"""
        self.container.add(REPO + "data")
        self.container.add(REPO + "data/subdir1")
        self.assert_(self.container.has_key(REPO + "data/subdir1"))
        self.assert_(not self.container.has_key(REPO + "data/profiles"))
        self.assert_(not self.container.has_key(REPO + "data/emptydir"))
        self.assert_(not self.container.has_key(REPO + "data/routage"))
        self.assert_(not self.container.has_key(REPO + "data/.path"))
        self.assert_(not self.container.has_key(REPO + "data/date.txt"))
        #expand
        self.container.expand_dir(REPO + u"data")
        self.assert_(self.container.has_key(REPO + "data"))
        self.assert_(self.container.has_key(REPO + "data/subdir1"))
        self.assert_(self.container.has_key(REPO + "data/profiles"))
        self.assert_(self.container.has_key(REPO + "data/emptydir"))
        self.assert_(self.container.has_key(REPO + "data/routage"))
        self.assert_(self.container.has_key(REPO + "data/.path"))
        self.assert_(self.container.has_key(REPO + "data/date.txt"))
        self.assert_(not self.container.has_key(REPO + "data/subdir1/subsubdir"))
        
    def test_sharing(self):
        """share/unshare file and dirs"""
        self.container.share_container(REPO +"runtests.py")
        self.assertEquals(self.container[REPO + "runtests.py"]._shared, True)
        self.container.add(REPO + "data")
        self.container.expand_dir(REPO + "data")
        self.container.expand_dir(REPO + "data/subdir1")
        self.assertEquals(self.container[REPO + "data"].nb_shared(), 0)
        self.container.share_container([REPO + u"data/.path", REPO + u"data/date.txt"], True)
        self.assertEquals(self.container[REPO + "data"].nb_shared(), 2)
        self.container.share_container(REPO + u"data/subdir1/subsubdir", True)
        self.assertEquals(self.container[REPO + "data/subdir1/subsubdir"].nb_shared(), -1)
        self.container.share_container(REPO + u"data/subdir1/subsubdir", False)
        self.container.share_content([REPO + "data/subdir1/subsubdir"], True)
        self.assertEquals(self.container[REPO + "data/subdir1/subsubdir"].nb_shared(), 0)
        self.container.expand_dir(REPO + "data/subdir1/subsubdir")
        self.container.share_content([REPO + "data/subdir1/subsubdir"], True)
        self.assertEquals(self.container[REPO + "data/subdir1/subsubdir"].nb_shared(), 4)
        self.container.share_container(REPO + "data", False)
        self.assertEquals(self.container[REPO + "data"].nb_shared(), 2)
        self.container.share_content([REPO + "data"], False)
        self.assertEquals(self.container[REPO + "data"].nb_shared(), 0)
        self.container.share_content([REPO + "data/subdir1/subsubdir"], False)
        self.assertEquals(self.container[REPO + "data/subdir1/subsubdir"].nb_shared(), 0)
        self.container.share_container(REPO + "data/subdir1/subsubdir/dummy.txt", True)
        self.assertEquals(self.container[REPO + "data/subdir1/subsubdir"].nb_shared(), 1)
        
    def test_persistency(self):
        """share, expand and checks sharing info remains correct"""
        data = REPO + "data/"
        self.container.add(data)
        self.container.share_container([data + "date.txt", data + "profiles", data + "routage"], True)
        self.assertEquals(self.container[data]._shared, False)
        self.assertEquals(self.container[data + "subdir1"]._shared, False)
        self.assertEquals(self.container[data + ".svn"]._shared, False)
        self.assertEquals(self.container[data + "date.txt"]._shared, True)
        self.assertEquals(self.container[data + "profiles"]._shared, True)
        self.assertEquals(self.container[data + "routage"]._shared, True)
        # expand
        self.container.expand_dir(data)
        self.assertEquals(self.container[data]._shared, False)
        self.assertEquals(self.container[data + "subdir1"]._shared, False)
        self.assertEquals(self.container[data + ".svn"]._shared, False)
        self.assertEquals(self.container[data + "date.txt"]._shared, True)
        self.assertEquals(self.container[data + "profiles"]._shared, True)
        self.assertEquals(self.container[data + "routage"]._shared, True)

    def test_tagging(self):
        """tag data"""
        self.container.add(REPO + "data")
        self.container.tag_container([REPO + u"data/routage", REPO + u"data/date.txt", REPO + u"data/subdir1"], u"tag1")
        self.assertEquals(self.container[REPO + "data/routage"]._tag, u"tag1")
        self.assertEquals(self.container[REPO + "data/date.txt"]._tag, u"tag1")
        self.assertEquals(self.container[REPO + "data/subdir1"]._tag, u"tag1")
        self.assertRaises(AssertionError, self.container[REPO + "data"].__getitem__, ".path")

if __name__ == '__main__':
    unittest.main()
