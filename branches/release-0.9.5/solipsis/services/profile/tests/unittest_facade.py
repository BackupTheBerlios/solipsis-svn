"""Design pattern Facade: presents working API for all actions of GUI
available. This facade will be used both by GUI and unittests."""

import unittest
import pickle
from StringIO import StringIO

from solipsis.services.profile.document import read_document
from solipsis.services.profile.file_document import FileDocument
from solipsis.services.profile.cache_document import CacheDocument
from solipsis.services.profile.data import DEFAULT_TAG, PeerDescriptor
from solipsis.services.profile.view import PrintView
from solipsis.services.profile.facade import create_facade, get_facade, Facade, \
      create_filter_facade, get_filter_facade
from solipsis.services.profile.tests import PROFILE_DIRECTORY, PROFILE_TEST, REPO, PSEUDO
from solipsis.services.profile import ENCODING, QUESTION_MARK
from os.path import abspath

class FacadeTest(unittest.TestCase):
    """assert that facade does effectively change document and calls callback on views"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.facade = create_facade(PROFILE_TEST, PROFILE_DIRECTORY)
        self.facade.add_file(REPO)

    def test_creation(self):
        self.assert_(Facade(PROFILE_TEST, PROFILE_DIRECTORY))
        self.assert_(create_facade(PROFILE_TEST, PROFILE_DIRECTORY))

    # PERSONAL TAB
    def test_change_title(self):
        self.facade.change_title(u'Mr')
        self.assertEquals(u"Mr", self.facade.get_document().get_title())
        
    def test_change_firstname(self):
        self.facade.change_firstname(u'manu')
        self.assertEquals(u"manu", self.facade.get_document().get_firstname())

    def test_change_lastname(self):
        self.facade.change_lastname(u'breton')
        self.assertEquals(u"breton", self.facade.get_document().get_lastname())

    def test_change_photo(self):
        self.facade.change_photo(unicode(unittest.__file__, ENCODING))
        self.assertEquals(u"%s"% unittest.__file__, self.facade.get_document().get_photo())

    def test_change_email(self):
        self.facade.change_email(u'manu@ft.com')
        self.assertEquals(u"manu@ft.com", self.facade.get_document().get_email())

    # CUSTOM TAB
    def test_add_custom_attributes(self):
        self.facade.add_custom_attributes(("key", u"value"))
        self.assertEquals({'key': u'value'},
                          self.facade.get_document().get_custom_attributes())
        self.facade.load()
        self.assertEquals({'City': u'', 'key': u'value', 'Country': u'',
                           'Favourite Book': u'', 'Favourite Movie': u'',
                           'Studies': u'', 'color': u'blue', 'homepage': u'manu.com'},
                          self.facade.get_document().get_custom_attributes())

    # BLOG TAB
    def test_blog(self):
        self.facade.add_blog(u"first blog")
        self.facade.add_blog(u"second blog")
        self.facade.add_comment((0, u'first comment', 'tony'))
        blog = self.facade.get_blog(0)
        self.assertEquals(blog.text, u"first blog")
        self.assertEquals(blog.comments[0].text, u'first comment')
        self.assertEquals(self.facade.count_blogs(), 2)
        self.facade.remove_blog(0)
        self.assertEquals(self.facade.count_blogs(), 1)
        
    # FILE TAB
    def test_repository(self):
        facade = Facade(PROFILE_TEST, PROFILE_DIRECTORY)
        facade.add_file(abspath("data/profiles"))
        self.assertRaises(KeyError, facade.del_file, abspath("data"))
        self.assertRaises(ValueError, facade.add_file, abspath("data"))
        facade.add_file(abspath("data/emptydir"))
        facade.del_file(abspath("data/emptydir"))

    def test_expand_dir(self):
        self.assertEquals(self.facade.get_document().get_shared(REPO),
                          [])
        self.facade.expand_dir(abspath("data"))
        check = {}
        self.assertEquals(self._build_check_dict(self.facade.get_document(), REPO),
                          {abspath(u'data'): u'none',
                           abspath(u'data/.path'): u'none',
                           abspath(u'data/date.txt'): u'none',
                           abspath(u'data/routage'): u'none',
                           abspath(u'data/.svn'): u'none',
                           abspath(u'data/subdir1'): u'none',
                           abspath(u'data/profiles'): u'none',
                           abspath(u'data/emptydir'): u'none'})
        self.assertRaises(AssertionError, self.facade.expand_dir,
                          abspath("data/routage"))
        self.facade.expand_dir(abspath("data/emptydir"))
        self.assertEquals(self._build_check_dict(self.facade.get_document(), REPO),
                          {abspath(u'data'): u'none',
                           abspath(u'data/.path'): u'none',
                           abspath(u'data/date.txt'): u'none',
                           abspath(u'data/routage'): u'none',
                           abspath(u'data/.svn'): u'none',
                           abspath(u'data/subdir1'): u'none',
                           abspath(u'data/profiles'): u'none',
                           abspath(u'data/emptydir'): u'none',
                           abspath(u'data/emptydir/.svn'): u'none'})
        self.facade.expand_dir(abspath("data/subdir1/subsubdir"))
        self.assertEquals(self._build_check_dict(self.facade.get_document(), REPO),
                          {abspath(u'data'): u'none',
                           abspath(u'data/.path'): u'none',
                           abspath(u'data/date.txt'): u'none',
                           abspath(u'data/routage'): u'none',
                           abspath(u'data/.svn'): u'none',
                           abspath(u'data/subdir1'): u'none',
                           abspath(u'data/profiles'): u'none',
                           abspath(u'data/emptydir'): u'none',
                           abspath(u'data/emptydir/.svn'): u'none',
                           abspath(u'data/subdir1/subsubdir'): u'none',
                           abspath(u'data/subdir1/subsubdir/default.solipsis'): u'none',
                           abspath(u'data/subdir1/subsubdir/dummy.txt'): u'none',
                           abspath(u'data/subdir1/subsubdir/null'): u'none',
                           abspath(u'data/subdir1/subsubdir/.svn'): u'none'})

    def _build_check_dict(self, doc, repo_path):
        result = {}
        for container in doc.files[repo_path].flat():
            result[container.get_path()] = container._tag
        return result
        
    def test_recursive_share(self):
        self.facade.expand_dir(abspath("data"))
        # all shared
        self.assertEquals(self.facade.get_document().get_files()[REPO]
                          [abspath("data")]._shared, True)
        self.assertEquals(self.facade.get_document().get_files()[REPO]
                          [abspath("data")]._shared, True)
        self.assertEquals(self.facade.get_document().get_files()[REPO]
                          [abspath("data/subdir1")]._shared, True)
        self.assertEquals(self.facade.get_document().get_files()[REPO]
                          [abspath("data/emptydir")]._shared, True)
        self.assertEquals(self.facade.get_document().get_files()[REPO]
                          [abspath("data/subdir1/subsubdir")]._shared, True)
        # unshare deepest dir
        self.facade.recursive_share((abspath("data/subdir1/subsubdir"), False))
        self.assertEquals(self.facade.get_document().get_files()[REPO]
                          [abspath("data/subdir1/subsubdir")]._shared, False)
        self.assertEquals(self.facade.get_document().get_files()[REPO]
                          [abspath("data/subdir1")]._shared, True)
        # unshare other dir
        self.facade.recursive_share((abspath("data"), False))
        self.assertEquals(self.facade.get_document().get_files()[REPO]
                          [abspath("data/subdir1")]._shared, False)
        self.assertEquals(self.facade.get_document().get_files()[REPO]
                          [abspath("data/emptydir")]._shared, False)

    def test_share_files(self):
        files = self.facade.get_document().get_files()[REPO]
        self.facade.expand_dir(abspath("data"))
        self.facade.recursive_share((abspath("data"), False))
        self.assertEquals(files[abspath("data/routage")]._shared, False)
        self.assertEquals(files[abspath("data")]._shared, False)
        self.facade.share_files((abspath("data"),
                                 ["routage", "subdir1"], True))
        self.assertEquals(files[abspath("data/routage")]._shared, True)
        self.assertEquals(files[abspath("data/subdir1")]._shared, True)
        self.assertEquals(files[abspath("data")]._shared, False)
        self.facade.share_files((abspath("data"),
                                 ["routage"], False))
        self.assertEquals(files[abspath("data/routage")]._shared, False)

    def test_tag_files(self):
        files = self.facade.get_document().get_files()[REPO]
        self.facade.expand_dir(abspath("data"))
        self.facade.tag_files((abspath("data"),
                               ["routage", "subdir1"], u"tag desc 1"))
        self.assertEquals(files[abspath("data/routage")]._tag,
                          u"tag desc 1")
        self.assertEquals(files[abspath("data/subdir1")]._tag,
                          u"tag desc 1")
        self.assertEquals(files[abspath("data/date.txt")]._tag,
                          DEFAULT_TAG)
        self.facade.tag_files((abspath("data"),
                               ["routage", "date.txt"], u"tag desc 3"))
        self.assertEquals(files[abspath("data/routage")]._tag,
                          u"tag desc 3")
        self.assertEquals(files[abspath("data/subdir1")]._tag,
                          u"tag desc 1")
        self.assertEquals(files[abspath("data/date.txt")]._tag,
                          u"tag desc 3")

    # OTHERS TAB
    def test_set_peer(self):
        self.assertEquals(self.facade.has_peer(u"emb"), False)
        self.facade.set_peer((u"emb", PeerDescriptor(PSEUDO)))
        self.assertEquals(self.facade.has_peer(u"emb"), True)
        
    def test_fill_data(self):
        self.facade.fill_data((u"emb", FileDocument(PROFILE_TEST, PROFILE_DIRECTORY)))
        self.assert_(self.facade.get_peer(u"emb").document)
        self.facade.remove_peer(u"emb")
        self.assertEquals(self.facade.has_peer(u"emb"), False)
    
    def test_status(self):
        self.facade.set_peer((u"emb", PeerDescriptor(PSEUDO)))
        self.facade.make_friend(u"emb")
        self.assertEquals(self.facade.get_peer(u"emb").state,
                          PeerDescriptor.FRIEND)
        self.facade.blacklist_peer(u"emb")
        self.assertEquals(self.facade.get_peer(u"emb").state,
                          PeerDescriptor.BLACKLISTED)
        self.facade.unmark_peer(u"emb")
        self.assertEquals(self.facade.get_peer(u"emb").state,
                          PeerDescriptor.ANONYMOUS)

    def test_match_peer(self):
        # TODO: detail test
        filter_facade = create_filter_facade(PROFILE_TEST, PROFILE_DIRECTORY)
        filter_facade.load()
        document = FileDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        document.load()
        peer_desc = PeerDescriptor(PROFILE_TEST, document=document)
        self.facade.fill_data((PROFILE_TEST, peer_desc))
        filter_facade.set_peer((PROFILE_TEST, peer_desc))
        filter_facade.activate(False)
        filter_facade.set_peer((PROFILE_TEST, peer_desc))

class HighLevelTest(unittest.TestCase):

    def setUp(self):
        """override one in unittest.TestCase"""
        self.facade = create_facade(PROFILE_TEST, PROFILE_DIRECTORY)
        self.facade.load()
        
    def test_get_profile(self):
        doc = read_document(self.facade.get_profile())
        self.assertEquals("Mr", doc.get_title())
        self.assertEquals("manu", doc.get_firstname())
        self.assertEquals("breton", doc.get_lastname())
        self.assertEquals(QUESTION_MARK(), doc.get_photo())
        self.assertEquals("manu@ft.com", doc.get_email())
        self.assertEquals({'City': u'', 'color': u'blue', 'Country': u'',
                           'Favourite Book': u'', 'homepage': u'manu.com',
                           'Favourite Movie': u'', 'Studies': u''},
                          doc.get_custom_attributes())
        
    def test_get_blog_file(self):
        self.facade.add_blog(u"other one")
        self.facade.add_comment((2, u"whaou", "manu"))
        blog_pickle = self.facade.get_blog_file()
        blog = pickle.loads(blog_pickle.read())
        self.assertEquals(blog.blogs[0].text, u"first blog")
        self.assertEquals(blog.blogs[1].text, u"second blog")
        self.assertEquals(blog.blogs[2].text, u"other one")
        self.assertEquals(blog.blogs[2].comments[0].text, u"whaou")
        
    def test_select_files(self):
        shared_pickle = self.facade.get_shared_files()
        files = pickle.loads(shared_pickle.read())
        self.assertEquals(files.has_key(REPO), True)
        shared_files = [container.get_path() for container in files[REPO]]
        self.assertEquals(shared_files,
                          [REPO + '/data/routage',
                           REPO + '/data/subdir1/TOtO.txt',
                           REPO + '/data/subdir1/subsubdir/null',
                           REPO + '/data/subdir1/subsubdir/dummy.txt'])

if __name__ == '__main__':
    unittest.main()
