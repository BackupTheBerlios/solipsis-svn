#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
"""Represents data stored in cache, especially shared file information"""

import unittest
import sys
import os, os.path

from os.path import abspath, join
from StringIO import StringIO
from solipsis.services.profile.path_containers import DEFAULT_TAG, \
     DirContainer, FileContainer
from solipsis.services.profile.data import Blogs, load_blogs, PeerDescriptor
from solipsis.services.profile.tests import REPO, PSEUDO, PROFILE_010, \
     PROFILE_DIRECTORY, PROFILE_TEST, PROFILE_BRUCE, GENERATED_DIR

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
        self.container = DirContainer(REPO)

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
        file_c = FileContainer("data/subdir1/date.doc", tag=u"my file")
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
        for file_name in [PROFILES_DIR + "/bruce.prf",
                          PROFILES_DIR + "/test.blog",
                          PROFILES_DIR + "/test.prf"]:
            copy_d[file_name].share()
        valid_copy = copy_d.copy(is_shared)
        self.assertEquals(valid_copy._shared, True)
        self.assertEquals(valid_copy._tag, u"my dir")
        self.assertEquals(valid_copy.name, "profiles")
        self.assertEquals(valid_copy.has_key(PROFILES_DIR + "/bruce.prf"), True)
        self.assertEquals(valid_copy.has_key(PROFILES_DIR + "/test.blog"), True)
        self.assertEquals(valid_copy.has_key(PROFILES_DIR + "/test.prf"), True)
        self.assertEquals(valid_copy.has_key(PROFILES_DIR + "/test.filt"), False)

    def test_setting(self):
        """set data"""
        # setting bad values
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, "youpi"))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, None))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, 1))
        self.assertRaises(AssertionError, DirContainer, u"data/emptydir")
        dir_c = DirContainer("data/emptydir")
        file_c = FileContainer("data/subdir1/date.doc", dir_c.add_shared)
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, dir_c))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, file_c))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, dir_c))
        # simple sets
        self.container[DATA_DIR] = DirContainer(DATA_DIR + os.sep)
        self.container[DATA_DIR] = DirContainer(DATA_DIR)
        self.container[join(REPO, "data/subdir1/subsubdir")] = DirContainer(join(REPO, "data/subdir1/subsubdir"))
        self.container[join(REPO, "data/subdir1/date.doc")] = FileContainer(join(REPO, "data/subdir1/date.doc"),
                                                                            dir_c.add_shared)
        self.container[join(REPO, "data/subdir1/subsubdir/null")] = FileContainer(join(REPO, "data/subdir1/subsubdir/null"),
                                                                                  dir_c.add_shared)
        self.container[join(REPO, "runtests.py")] = FileContainer(join(REPO, "runtests.py"),
                                                                  dir_c.add_shared)

    def test_getting(self):
        """get data"""
        # dir
        self.container.add(DATA_DIR)
        self.assertEquals(isinstance(self.container[DATA_DIR], DirContainer), True)
        # file
        self.container.add(join(REPO, "data/subdir1/date.doc"))
        self.container.add(join(REPO, "runtests.py"))
        self.assertEquals(isinstance(self.container[join(REPO, "data/subdir1/date.doc")], FileContainer), True)
        self.assertEquals(isinstance(self.container[join(REPO, "runtests.py")], FileContainer), True)
        # generic
        self.container.add(join(REPO, "data/profiles"))
        self.container.add(join(REPO, "data/routage"))
        self.assertEquals(isinstance(self.container[join(REPO, "data/profiles")], DirContainer), True)
        self.assertEquals(isinstance(self.container[join(REPO, "data/routage")], FileContainer), True)
        # wrapper
        dir_c = DirContainer(join(REPO, "data/emptydir"))
        file_c = FileContainer(join(REPO, "data/subdir1/subsubdir/default.solipsis"), dir_c.add_shared)
        self.container[join(REPO, "data/emptydir")] = dir_c
        self.container[join(REPO, "data/subdir1/subsubdir/default.solipsis")] = file_c
        self.assertEquals(self.container[join(REPO, "data/emptydir")].name, "emptydir")
        self.assertEquals(self.container[join(REPO, "data/subdir1/subsubdir/default.solipsis")].name, "default.solipsis")
        
    def test_deleting(self):
        """delete data"""
        # add data
        root_str = join(REPO, "runtests.py")
        dir_str = join(REPO, "data/emptydir")
        file_str = join(REPO, "data/subdir1/subsubdir/default.solipsis")
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
        self.assertRaises(AssertionError, self.container.add, join(REPO, "data/dummy"))
        self.assertRaises(AssertionError, self.container.add, join(REPO, "data/dummy.txt"))
        self.assertRaises(AssertionError, self.container.add, "data")
        self.container.add(DATA_DIR)
        self.container.add(join(REPO, "data/subdir1/subsubdir"))
        self.container.add(join(REPO, "data/subdir1/date.doc"))
        self.container.add(join(REPO, "data/subdir1/subsubdir/null"))
        self.container.add(join(REPO, "runtests.py"))
        
    def test_expanding(self):
        """expanding command"""
        self.container.add(DATA_DIR)
        self.container.add(join(REPO, "data/subdir1"))
        self.assert_(self.container.has_key(join(REPO, "data/subdir1")))
        self.assert_(not self.container.has_key(join(REPO, "data/profiles")))
        self.assert_(not self.container.has_key(join(REPO, "data/emptydir")))
        self.assert_(not self.container.has_key(join(REPO, "data/routage")))
        self.assert_(not self.container.has_key(join(REPO, "data/.path")))
        self.assert_(not self.container.has_key(join(REPO, "data/date.txt")))
        #expand
        self.container.expand_dir(DATA_DIR)
        self.assert_(self.container.has_key(DATA_DIR))
        self.assert_(self.container.has_key(join(REPO, "data/subdir1")))
        self.assert_(self.container.has_key(join(REPO, "data/profiles")))
        self.assert_(self.container.has_key(join(REPO, "data/emptydir")))
        self.assert_(self.container.has_key(join(REPO, "data/routage")))
        self.assert_(self.container.has_key(join(REPO, "data/.path")))
        self.assert_(self.container.has_key(join(REPO, "data/date.txt")))
        self.assert_(not self.container.has_key(join(REPO, "data/subdir1/subsubdir")))
        
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
        for file_path in [join(REPO, "data/routage"),
                          join(REPO, "data/date.txt"),
                          join(REPO, "data/subdir1")]:
            self.container[file_path].tag(u"tag1")
        self.assertEquals(self.container[join(REPO, "data/routage")]._tag, u"tag1")
        self.assertEquals(self.container[join(REPO, "data/date.txt")]._tag, u"tag1")
        self.assertEquals(self.container[join(REPO, "data/subdir1")]._tag, u"tag1")
        self.assertRaises(AssertionError, self.container[DATA_DIR].__getitem__, ".path")

if __name__ == '__main__':
    unittest.main()
