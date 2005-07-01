"""Represents data stored in cache, especially shared file information"""

import unittest
import sys

from os.path import abspath, join
from StringIO import StringIO
from solipsis.services.profile.data import DEFAULT_TAG, \
     DirContainer, FileContainer, Blogs, load_blogs, PeerDescriptor
from solipsis.services.profile.tests import REPO, PSEUDO, PROFILE_010, \
     PROFILE_DIRECTORY, PROFILE_TEST, PROFILE_BRUCE, GENERATED_DIR

        
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
        self.blog.add_blog("first blog", PROFILE_TEST)
        self.blog.add_blog("second blog", PROFILE_TEST)
        self.blog.add_comment(0, "commenting the first", PSEUDO)
        self.blog.save()
    
    def test_blog(self):
        self.assertEquals(self.blog.count_blogs(), 2)
        self.assertEquals(self.blog.get_blog(0).text, "first blog")
        self.assertEquals(self.blog.get_blog(0).count_blogs(), 1)
        self.assertEquals(self.blog.get_blog(1).text, "second blog")
        self.assertEquals(self.blog.get_blog(1).count_blogs(), 0)
    
    def test_security(self):
        self.assertRaises(AssertionError, self.blog.add_blog, "forbidden", 'jules')
        self.assertRaises(AssertionError, self.blog.remove_blog, 0, 'jules')
        self.assertRaises(AssertionError, self.blog.get_blog, 2)

    def test_copy(self):
        copied_blog = self.blog.copy()
        # add some blogs in first
        self.blog.add_blog("more blog", PROFILE_TEST)
        self.blog.add_comment(0, "commenting (again) the first", PSEUDO)
        # check result
        self.assertEquals(self.blog.count_blogs(), 3)
        self.assertEquals(self.blog.get_blog(0).count_blogs(), 2)
        # check copy
        self.assertEquals(copied_blog.count_blogs(), 2)
        self.assertEquals(copied_blog.get_blog(0).text, "first blog")
        self.assertEquals(copied_blog.get_blog(0).count_blogs(), 1)
        self.assertEquals(copied_blog.get_blog(1).text, "second blog")
        self.assertEquals(copied_blog.get_blog(1).count_blogs(), 0)

    def test_load(self):
        loaded_blog = load_blogs(PROFILE_TEST, directory=PROFILE_DIRECTORY)
        self.assertEquals(loaded_blog.count_blogs(), 2)
        self.assertEquals(loaded_blog.get_blog(0).text, "first blog")
        self.assertEquals(loaded_blog.get_blog(0).count_blogs(), 1)
        self.assertEquals(loaded_blog.get_blog(1).text, "second blog")
        self.assertEquals(loaded_blog.get_blog(1).count_blogs(), 0)

    def test_retro_compatibility(self):
        loaded_blog = load_blogs(PROFILE_010, directory=PROFILE_DIRECTORY)
        self.assertEquals(loaded_blog.count_blogs(), 4)
        self.assertEquals(loaded_blog.get_blog(0).text, u"Hi there! Watch my next movie... it's going to be real fun")
        self.assertEquals(loaded_blog.get_blog(0).count_blogs(), 0)
        self.assertEquals(loaded_blog.get_blog(1).text, u"I won't tell you much but this I can say: it's going to be terrific!")
        self.assertEquals(loaded_blog.get_blog(2).text, u'Watch here for its name... coming soon')
        self.assertEquals(loaded_blog.get_blog(3).text, u"A Godess' world.  What do you think?")

        
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
        self.assertRaises(AssertionError, DirContainer,  join(REPO, "data/dummy"))
        self.assertRaises(AssertionError, FileContainer,  join(REPO, "data/dummy.txt"))

        
    def test_setting(self):
        """set data"""
        # setting bad values
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, "youpi"))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, None))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, 1))
        self.assertRaises(TypeError, DirContainer, "data/emptydir")
        dir_c = DirContainer(u"data/emptydir")
        file_c = FileContainer(u"data/subdir1/date.doc")
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, dir_c))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, file_c))
        self.assertRaises(AssertionError, self.container.__setitem__, \
                          *(REPO, dir_c))
        # simple sets
        self.container[join(REPO, u"data/")] = DirContainer(join(REPO, u"data/"))
        self.container[join(REPO, u"data/")] = DirContainer(join(REPO, u"data"))
        self.container[join(REPO, "data/subdir1/subsubdir")] = DirContainer(join(REPO, u"data/subdir1/subsubdir"))
        self.container[join(REPO, u"data/subdir1/date.doc")] = FileContainer(join(REPO, u"data/subdir1/date.doc"))
        self.container[join(REPO, "data/subdir1/subsubdir/null")] = FileContainer(join(REPO, u"data/subdir1/subsubdir/null"))
        self.container[join(REPO, "runtests.py")] = FileContainer(join(REPO, u"runtests.py"))

    def test_getting(self):
        """get data"""
        # dir
        self.container.add(join(REPO, "data/"))
        self.assertEquals(isinstance(self.container[join(REPO, u"data")], DirContainer), True)
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
        file_c = FileContainer(join(REPO, "data/subdir1/subsubdir/default.solipsis"))
        self.container[join(REPO, "data/emptydir")] = dir_c
        self.container[join(REPO, "data/subdir1/subsubdir/default.solipsis")] = file_c
        self.assertEquals(self.container[join(REPO, "data/emptydir")].name, "emptydir")
        self.assertEquals(self.container[join(REPO, "data/subdir1/subsubdir/default.solipsis")].name, "default.solipsis")
        
    def test_deleting(self):
        """delete data"""
        # add data
        root_str = join(REPO, "runtests.py")
        dir_str = join(REPO, u"data/emptydir")
        file_str = join(REPO, "data/subdir1/subsubdir/default.solipsis")
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
        self.assertRaises(AssertionError, self.container.add, join(REPO, "data/dummy"))
        self.assertRaises(AssertionError, self.container.add, join(REPO, "data/dummy.txt"))
        self.assertRaises(AssertionError, self.container.add, "data")
        self.container.add(join(REPO, u"data/"))
        self.container.add(join(REPO, "data/subdir1/subsubdir"))
        self.container.add(join(REPO, u"data/subdir1/date.doc"))
        self.container.add(join(REPO, "data/subdir1/subsubdir/null"))
        self.container.add(join(REPO, "runtests.py"))
        
    def test_expanding(self):
        """expanding command"""
        self.container.add(join(REPO, "data"))
        self.container.add(join(REPO, "data/subdir1"))
        self.assert_(self.container.has_key(join(REPO, "data/subdir1")))
        self.assert_(not self.container.has_key(join(REPO, "data/profiles")))
        self.assert_(not self.container.has_key(join(REPO, "data/emptydir")))
        self.assert_(not self.container.has_key(join(REPO, "data/routage")))
        self.assert_(not self.container.has_key(join(REPO, "data/.path")))
        self.assert_(not self.container.has_key(join(REPO, "data/date.txt")))
        #expand
        self.container.expand_dir(join(REPO, u"data"))
        self.assert_(self.container.has_key(join(REPO, "data")))
        self.assert_(self.container.has_key(join(REPO, "data/subdir1")))
        self.assert_(self.container.has_key(join(REPO, "data/profiles")))
        self.assert_(self.container.has_key(join(REPO, "data/emptydir")))
        self.assert_(self.container.has_key(join(REPO, "data/routage")))
        self.assert_(self.container.has_key(join(REPO, "data/.path")))
        self.assert_(self.container.has_key(join(REPO, "data/date.txt")))
        self.assert_(not self.container.has_key(join(REPO, "data/subdir1/subsubdir")))
        
    def test_sharing(self):
        """share/unshare file and dirs"""
        self.container.share_container(join(REPO, "runtests.py"))
        self.assertEquals(self.container[join(REPO, "runtests.py")]._shared, True)
        self.container.add(join(REPO, "data"))
        self.container.expand_dir(join(REPO, "data"))
        self.container.expand_dir(join(REPO, "data/subdir1"))
        self.assertEquals(self.container[join(REPO, "data")].nb_shared(), 0)
        self.container.share_container([join(REPO, u"data/.path"), join(REPO, u"data/date.txt")], True)
        self.assertEquals(self.container[join(REPO, "data")].nb_shared(), 2)
        self.container.share_container(join(REPO, u"data/subdir1/subsubdir"), True)
        self.assertEquals(self.container[join(REPO, "data/subdir1/subsubdir")].nb_shared(), -1)
        self.container.share_container(join(REPO, u"data/subdir1/subsubdir"), False)
        self.container.share_content([join(REPO, "data/subdir1/subsubdir")], True)
        self.assertEquals(self.container[join(REPO, "data/subdir1/subsubdir")].nb_shared(), 0)
        self.container.expand_dir(join(REPO, "data/subdir1/subsubdir"))
        self.container.share_content([join(REPO, "data/subdir1/subsubdir")], True)
        self.assertEquals(self.container[join(REPO, "data/subdir1/subsubdir")].nb_shared(), 4)
        self.container.share_container(join(REPO, "data"), False)
        self.assertEquals(self.container[join(REPO, "data")].nb_shared(), 2)
        self.container.share_content([join(REPO, "data")], False)
        self.assertEquals(self.container[join(REPO, "data")].nb_shared(), 0)
        self.container.share_content([join(REPO, "data/subdir1/subsubdir")], False)
        self.assertEquals(self.container[join(REPO, "data/subdir1/subsubdir")].nb_shared(), 0)
        self.container.share_container(join(REPO, "data/subdir1/subsubdir/dummy.txt"), True)
        self.assertEquals(self.container[join(REPO, "data/subdir1/subsubdir")].nb_shared(), 1)
        
    def test_persistency(self):
        """share, expand and checks sharing info remains correct"""
        data = join(REPO, "data/")
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
        self.container.add(join(REPO, "data"))
        self.container.tag_container([join(REPO, u"data/routage"),
                                      join(REPO, u"data/date.txt"),
                                      join(REPO, u"data/subdir1")], u"tag1")
        self.assertEquals(self.container[join(REPO, "data/routage")]._tag, u"tag1")
        self.assertEquals(self.container[join(REPO, "data/date.txt")]._tag, u"tag1")
        self.assertEquals(self.container[join(REPO, "data/subdir1")]._tag, u"tag1")
        self.assertRaises(AssertionError, self.container[join(REPO, "data")].__getitem__, ".path")

if __name__ == '__main__':
    unittest.main()
