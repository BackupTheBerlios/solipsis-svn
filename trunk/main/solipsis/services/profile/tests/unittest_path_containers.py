#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# pylint: disable-msg=C0301
# Line too long
"""Represents data stored in cache, especially shared file information"""

import unittest
import os, os.path

from solipsis.services.profile.path_containers import \
     DirContainer, FileContainer
from solipsis.services.profile.tests import TEST_DIR

DATA_DIR = os.path.join(TEST_DIR, "data")
SAMPLE_FILE = os.path.join(DATA_DIR, "été.txt")
SAVE_FILE = os.path.join(DATA_DIR, "sav.txt")

class FileTest(unittest.TestCase):
    """Test cache coherency with following arborescency:
    
    data/
    |-- date.txt
    |-- emptydir
    |-- profiles
    |   |-- atao.prf
    |   |-- bruce.blog
    |   |-- bruce.prf
    |   |-- demi.prf
    |   |-- demi_010.blog
    |   |-- tata.prf
    |   |-- test.blog
    |   |-- test.filt
    |   `-- test.prf
    |-- routage
    `-- subdir1
        |-- TOtO.txt
        |-- date.doc
        `-- subsubdir
            |-- default.solipsis
            |-- dummy.txt
            `-- null"""
    
    def setUp(self):
        """override one in unittest.TestCase"""
        self.container = DirContainer(TEST_DIR)

    def test_file_with_accent(self):
        # specific set up
        if not os.path.exists(SAMPLE_FILE):
            sample_file = open(SAMPLE_FILE, "w")
            sample_file.write("created for testing purpose only. Should be removed after tests")
            sample_file.close()
        try:
            # raw listing
            for file_name in os.listdir(DATA_DIR):
                path = os.path.join(DATA_DIR, file_name)
                self.assert_(os.path.exists(path))
            # write
            sav = open(SAVE_FILE, 'w')
            for file_name in os.listdir(DATA_DIR):
                print >> sav, file_name
            sav.close()
            # read
            old = open(SAVE_FILE)
            lines = [line[:-1] for line in old.readlines()]
            old.close()
            # check
            for file_name in lines:
                path = os.path.join(DATA_DIR, file_name)
                self.assert_(os.path.exists(path))
        # specific tear down
        finally:
            for path in [SAMPLE_FILE, SAVE_FILE]:
                if os.path.exists(path):
                    os.remove(path)

    def test_copy(self):
        # file container, no validator
        file_c = FileContainer(os.sep.join(["data", "subdir1", "date.doc"]), tag=u"my file")
        self.assertEquals(file_c._shared, False)
        self.assertEquals(file_c._tag, u"my file")
        self.assertEquals(file_c.name, "date.doc")
        file_c.share()
        copy_f = file_c.copy()
        self.assertEquals(copy_f._shared, True)
        self.assertEquals(copy_f._tag, u"my file")
        self.assertEquals(copy_f.name, "date.doc")
        # dir container, no validator
        PROFILES_DIR = os.path.join(DATA_DIR, "profiles")
        dir_c = DirContainer(PROFILES_DIR, share=True, tag=u"my dir")
        copy_d = dir_c.copy()
        self.assertEquals(copy_d._shared, True)
        self.assertEquals(copy_d._tag, u"my dir")
        self.assertEquals(copy_d.name, "profiles")
        # validator -> no result
        not_shared = lambda container: not container._shared
        is_shared = lambda container: container._shared
        copy_d.expand_dir()
        empty_copy = copy_d.copy(not_shared)
        self.assertEquals(empty_copy, None)
        # validator -> result
        for file_name in [os.path.join(PROFILES_DIR, "bruce.prf"),
                          os.path.join(PROFILES_DIR, "test.blog"),
                          os.path.join(PROFILES_DIR, "test.prf")]:
            copy_d[file_name].share()
        valid_copy = copy_d.copy(is_shared)
        self.assertEquals(valid_copy._shared, True)
        self.assertEquals(valid_copy._tag, u"my dir")
        self.assertEquals(valid_copy.name, "profiles")
        self.assertEquals(valid_copy.has_key(os.path.join(PROFILES_DIR, "bruce.prf")), True)
        self.assertEquals(valid_copy.has_key(os.path.join(PROFILES_DIR, "test.blog")), True)
        self.assertEquals(valid_copy.has_key(os.path.join(PROFILES_DIR, "test.prf")), True)
        self.assertEquals(valid_copy.has_key(os.path.join(PROFILES_DIR, "test.filt")), False)

    def test_setting(self):
        """set data"""
        # setting bad values
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(TEST_DIR, "youpi"))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(TEST_DIR, None))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(TEST_DIR, 1))
        self.assertRaises(AssertionError, DirContainer, u"data/emptydir")
        dir_c = DirContainer("data/emptydir")
        file_c = FileContainer("data/subdir1/date.doc", dir_c.add_shared)
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(TEST_DIR, dir_c))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(TEST_DIR, file_c))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(TEST_DIR, dir_c))
        # simple sets
        self.container[DATA_DIR] = DirContainer(DATA_DIR + os.sep)
        self.container[DATA_DIR] = DirContainer(DATA_DIR)
        self.container[os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir"])] = \
                                         DirContainer(os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir"]))
        self.container[os.sep.join([TEST_DIR, "data", "subdir1", "date.doc"])] = \
                                         FileContainer(os.sep.join([TEST_DIR, "data", "subdir1", "date.doc"]), dir_c.add_shared)
        self.container[os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir", "null"])] = \
                                         FileContainer(os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir", "null"]), dir_c.add_shared)
        self.container[os.sep.join([TEST_DIR, "runtests.py"])] = \
                                         FileContainer(os.sep.join([TEST_DIR, "runtests.py"]), dir_c.add_shared)

    def test_getting(self):
        """get data"""
        # dir
        self.container.add(DATA_DIR)
        self.assertEquals(isinstance(self.container[DATA_DIR], DirContainer), True)
        # file
        self.container.add(os.sep.join([TEST_DIR, "data", "subdir1", "date.doc"]))
        self.container.add(os.sep.join([TEST_DIR, "runtests.py"]))
        self.assertEquals(isinstance(self.container[os.sep.join([TEST_DIR, "data", "subdir1", "date.doc"])], FileContainer), True)
        self.assertEquals(isinstance(self.container[os.sep.join([TEST_DIR, "runtests.py"])], FileContainer), True)
        # generic
        self.container.add(os.sep.join([TEST_DIR, "data", "profiles"]))
        self.container.add(os.sep.join([TEST_DIR, "data", "routage"]))
        self.assertEquals(isinstance(self.container[os.sep.join([TEST_DIR, "data", "profiles"])], DirContainer), True)
        self.assertEquals(isinstance(self.container[os.sep.join([TEST_DIR, "data", "routage"])], FileContainer), True)
        # wrapper
        dir_c = DirContainer(os.sep.join([TEST_DIR, "data", "emptydir"]))
        file_c = FileContainer(os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir", "default.solipsis"]), dir_c.add_shared)
        self.container[os.sep.join([TEST_DIR, "data", "emptydir"])] = dir_c
        self.container[os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir", "default.solipsis"])] = file_c
        self.assertEquals(self.container[os.sep.join([TEST_DIR, "data", "emptydir"])].name, "emptydir")
        self.assertEquals(self.container[os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir", "default.solipsis"])].name, "default.solipsis")
        
    def test_deleting(self):
        """delete data"""
        # add data
        root_str = os.sep.join([TEST_DIR, "runtests.py"])
        dir_str = os.sep.join([TEST_DIR, "data", "emptydir"])
        file_str = os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir", "default.solipsis"])
        self.assertEquals(self.container.has_key(root_str), False)
        self.assertEquals(self.container.has_key(dir_str), False)
        self.assertEquals(self.container.has_key(file_str), False)
        dir_c = DirContainer(dir_str)
        self.container[root_str] = FileContainer(root_str, dir_c.add_shared)
        self.container[dir_str] = dir_c
        self.container[file_str] = FileContainer(file_str, dir_c.add_shared)
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
        self.assertRaises(AssertionError, self.container.add, os.sep.join([TEST_DIR, "data", "dummy"]))
        self.assertRaises(AssertionError, self.container.add, os.sep.join([TEST_DIR, "data", "dummy.txt"]))
        self.assertRaises(AssertionError, self.container.add, "data")
        self.container.add(DATA_DIR)
        self.container.add(os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir"]))
        self.container.add(os.sep.join([TEST_DIR, "data", "subdir1", "date.doc"]))
        self.container.add(os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir", "null"]))
        self.container.add(os.sep.join([TEST_DIR, "runtests.py"]))
        
    def test_expanding(self):
        """expanding command"""
        self.container.add(DATA_DIR)
        self.container.add(os.sep.join([TEST_DIR, "data", "subdir1"]))
        self.assert_(self.container.has_key(os.sep.join([TEST_DIR, "data", "subdir1"])))
        self.assert_(not self.container.has_key(os.sep.join([TEST_DIR, "data", "profiles"])))
        self.assert_(not self.container.has_key(os.sep.join([TEST_DIR, "data", "emptydir"])))
        self.assert_(not self.container.has_key(os.sep.join([TEST_DIR, "data", "routage"])))
        self.assert_(not self.container.has_key(os.sep.join([TEST_DIR, "data", ".path"])))
        self.assert_(not self.container.has_key(os.sep.join([TEST_DIR, "data", "date.txt"])))
        #expand
        self.container.expand_dir(DATA_DIR)
        self.assert_(self.container.has_key(DATA_DIR))
        self.assert_(self.container.has_key(os.sep.join([TEST_DIR, "data", "subdir1"])))
        self.assert_(self.container.has_key(os.sep.join([TEST_DIR, "data", "profiles"])))
        self.assert_(self.container.has_key(os.sep.join([TEST_DIR, "data", "emptydir"])))
        self.assert_(self.container.has_key(os.sep.join([TEST_DIR, "data", "routage"])))
        self.assert_(self.container.has_key(os.sep.join([TEST_DIR, "data", ".path"])))
        self.assert_(self.container.has_key(os.sep.join([TEST_DIR, "data", "date.txt"])))
        self.assert_(not self.container.has_key(os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir"])))
        
    def test_sharing(self):
        # tests/data (containing 3 files & 3 directories
        data_container = self.container[DATA_DIR]
        self.assertEquals(data_container._shared, False)
        self.assertEquals(data_container.nb_shared(), 0)
        data_container.expand_dir()
        self.assertEquals(data_container.nb_shared(), 0)
        data_container[os.path.join(DATA_DIR, "date.txt")].share()
        self.assertEquals(data_container.nb_shared(), 1)
        data_container.share(False)
        self.assertEquals(data_container._shared, False)
        self.assertEquals(data_container.nb_shared(), 0)
        # file
        data_container[os.path.join(DATA_DIR, "date.txt")].share()
        self.assertEquals(data_container.nb_shared(), 1)
        # dirs
        data_container.expand_dir(os.path.join(DATA_DIR, "subdir1"))
        self.assertEquals(data_container[os.path.join(DATA_DIR, "subdir1")].nb_shared(), 0)
        self.assertEquals(data_container.nb_shared(), 1)
        data_container.expand_dir(os.sep.join([DATA_DIR, "subdir1", "subsubdir"]))
        data_container[os.sep.join([DATA_DIR, "subdir1", "subsubdir"])].share()
        self.assertEquals(data_container.nb_shared(), 4)
        data_container[os.path.join(DATA_DIR, "date.txt")].share(False)
        self.assertEquals(data_container.nb_shared(), 3)
        
    def test_persistency(self):
        self.container.add(DATA_DIR)
        for file_name in [os.path.join(DATA_DIR, "date.txt"),
                          os.path.join(DATA_DIR, "profiles"),
                          os.path.join(DATA_DIR, "routage")]:
            self.container[file_name].share()
        self.assertEquals(self.container[DATA_DIR]._shared, False)
        self.assertEquals(self.container[os.path.join(DATA_DIR, "subdir1")]._shared, False)
        self.assertEquals(self.container[os.path.join(DATA_DIR, ".svn")]._shared, False)
        self.assertEquals(self.container[os.path.join(DATA_DIR, "date.txt")]._shared, True)
        self.assertEquals(self.container[os.path.join(DATA_DIR, "profiles")]._shared, True)
        self.assertEquals(self.container[os.path.join(DATA_DIR, "routage")]._shared, True)
        # expand
        self.container.expand_dir(DATA_DIR)
        self.container[os.path.join(DATA_DIR, "date.txt")].tag(u"yop")
        self.assertEquals(self.container[DATA_DIR]._shared, False)
        self.assertEquals(self.container[os.path.join(DATA_DIR, "subdir1")]._shared, False)
        self.assertEquals(self.container[os.path.join(DATA_DIR, ".svn")]._shared, False)
        self.assertEquals(self.container[os.path.join(DATA_DIR, "date.txt")]._shared, True)
        self.assertEquals(self.container[os.path.join(DATA_DIR, "profiles")]._shared, True)
        self.assertEquals(self.container[os.path.join(DATA_DIR, "routage")]._shared, True)

    def test_tagging(self):
        """tag data"""
        self.container.add(DATA_DIR)
        for file_path in [os.sep.join([TEST_DIR, "data", "routage"]),
                          os.sep.join([TEST_DIR, "data", "date.txt"]),
                          os.sep.join([TEST_DIR, "data", "subdir1"])]:
            self.container[file_path].tag(u"tag1")
        self.assertEquals(self.container[os.sep.join([TEST_DIR, "data", "routage"])]._tag, u"tag1")
        self.assertEquals(self.container[os.sep.join([TEST_DIR, "data", "date.txt"])]._tag, u"tag1")
        self.assertEquals(self.container[os.sep.join([TEST_DIR, "data", "subdir1"])]._tag, u"tag1")
        self.assertRaises(AssertionError, self.container[DATA_DIR].__getitem__, ".path")

if __name__ == '__main__':
    unittest.main()
