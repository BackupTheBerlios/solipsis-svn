"""Design pattern Facade: presents working API for all actions of GUI
available. This facade will be used both by GUI and unittests."""

import unittest
from StringIO import StringIO

from solipsis.services.profile.document import CacheDocument, FileDocument
from solipsis.services.profile.data import DEFAULT_TAG, PeerDescriptor
from solipsis.services.profile.view import PrintView
from solipsis.services.profile.facade import get_facade, Facade
from solipsis.services.profile.tests import PROFILE_DIRECTORY, PROFILE_TEST, REPO
from solipsis.services.profile import ENCODING
from os.path import abspath

class FacadeTest(unittest.TestCase):
    """assert that facade does effectively change document and calls callback on views"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.facade = Facade(PROFILE_TEST, PROFILE_DIRECTORY)
        self.facade.add_repository(REPO)

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

    def test_change_download_repo(self):
        self.facade.change_download_repo(u'any desc')
        self.assertEquals(u"any desc", self.facade.get_document().get_download_repo())

    # CUSTOM TAB
    def test_add_custom_attributes(self):
        self.facade.add_custom_attributes(("key", u"value"))
        self.assertEquals({'City': u'', 'key': u'value', 'Country': u'',
                           'Favourite Book': u'', 'Favourite Movie': u'',
                           'Sport': u'', 'Studies': u''},
                          self.facade.get_document().get_custom_attributes())

    # BLOG TAB
    def test_blog(self):
        self.facade.add_blog("first blog")
        self.facade.add_blog("second blog")
        self.facade.add_comment((0, 'first comment', 'tony'))
        blog = self.facade.get_blog(0)
        self.assertEquals(blog.text, "first blog")
        self.assertEquals(blog.comments[0].text, 'first comment')
        self.assertEquals(self.facade.count_blogs(), 2)
        self.facade.remove_blog(0)
        self.assertEquals(self.facade.count_blogs(), 1)
        
    # FILE TAB
    def test_repository(self):
        facade = Facade(PROFILE_TEST, PROFILE_DIRECTORY)
        facade.add_repository(abspath(u"data/profiles"))
        self.assertRaises(KeyError, facade.remove_repository, abspath(u"data"))
        self.assertRaises(ValueError, facade.add_repository, abspath(u"data"))
        facade.add_repository(abspath(u"data/emptydir"))
        facade.remove_repository(abspath(u"data/emptydir"))

    def test_expand_dir(self):
        self.assertEquals(self.facade.get_document().get_shared(REPO),
                          [])
        self.facade.expand_dir(abspath(u"data"))
        check = {}
        self.assertEquals(self._build_check_dict(self.facade.get_document(), REPO),
                          {abspath(u'data'): u'none',
                           abspath(u'data/.path'): u'none',
                           abspath(u'data/date.txt'): u'none',
                           abspath(u'data/routage'): u'none',
                           abspath(u'data/.svn'): u'none',
                           abspath(u'data/subdir1'): u'none',
                           abspath(u'data/profiles'): u'none',
                           abspath(u'data/emptydir'): u'none',
                           abspath(unicode('data/élève', ENCODING)): u'none',
                           abspath(unicode('data/été.txt', ENCODING)): u'none'})
        self.assertRaises(AssertionError, self.facade.expand_dir,
                          abspath(u"data/routage"))
        self.facade.expand_dir(abspath(u"data/emptydir"))
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
        self.facade.expand_dir(abspath(u"data/subdir1/subsubdir"))
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
        for name, container in doc.files[repo_path].flat().iteritems():
            result[name] = container._tag
        return result
        
    def test_share_dir(self):
        files = self.facade.get_document().get_files()[REPO]
        self.assertRaises(AssertionError, self.facade.share_dirs,
                          ([abspath(u"data/routage")], True))
        self.assertRaises(AssertionError, self.facade.share_dirs,
                          ([abspath(u"data/ghost")], True))
        self.facade.expand_dir(abspath(u"data"))
        self.assertEquals(files[abspath(u"data")]._shared, False)
        self.facade.share_dirs(([abspath(u"data")], True))
        self.assertEquals(files[abspath(u"data")]._shared, False)
        self.assertEquals(files[abspath(u"data/subdir1")]._shared, True)
        self.assertEquals(files[abspath(u"data/emptydir")]._shared, True)
        self.facade.share_dirs(([abspath(u"data/subdir1/subsubdir")], True))
        self.assertEquals(files[abspath(u"data/subdir1/subsubdir")]._shared, False)
        self.facade.share_dirs(([abspath(u"data")], False))
        self.assertEquals(files[abspath(u"data/subdir1")]._shared, False)
        self.assertEquals(files[abspath(u"data/emptydir")]._shared, False)

    def test_share_files(self):
        files = self.facade.get_document().get_files()[REPO]
        self.facade.expand_dir(abspath(u"data"))
        self.assertEquals(files[abspath(u"data/routage")]._shared, False)
        self.assertEquals(files[abspath(u"data")]._shared, False)
        self.facade.share_files((abspath(u"data"),
                                 ["routage", "subdir1"], True))
        self.assertEquals(files[abspath(u"data/routage")]._shared, True)
        self.assertEquals(files[abspath(u"data/subdir1")]._shared, True)
        self.assertEquals(files[abspath(u"data")]._shared, False)
        self.facade.share_files((abspath(u"data"),
                                 ["routage"], False))
        self.assertEquals(files[abspath(u"data/routage")]._shared, False)

    def test_tag_files(self):
        files = self.facade.get_document().get_files()[REPO]
        self.facade.expand_dir(abspath(u"data"))
        self.facade.tag_files((abspath(u"data"),
                               ["routage", "subdir1"], u"tag desc 1"))
        self.assertEquals(files[abspath(u"data/routage")]._tag,
                          u"tag desc 1")
        self.assertEquals(files[abspath(u"data/subdir1")]._tag,
                          u"tag desc 1")
        self.assertEquals(files[abspath(u"data/date.txt")]._tag,
                          DEFAULT_TAG)
        self.facade.tag_files((abspath(u"data"),
                               ["routage", "date.txt"], u"tag desc 3"))
        self.assertEquals(files[abspath(u"data/routage")]._tag,
                          u"tag desc 3")
        self.assertEquals(files[abspath(u"data/subdir1")]._tag,
                          u"tag desc 1")
        self.assertEquals(files[abspath(u"data/date.txt")]._tag,
                          u"tag desc 3")

    # OTHERS TAB
    def test_add_peer(self):
        self.assertEquals(self.facade.has_peer(u"emb"), False)
        self.facade.add_peer(u"emb")
        self.assertEquals(self.facade.has_peer(u"emb"), True)
        
    def test_fill_data(self):
        self.facade.add_peer(u"emb")
        self.facade.fill_data((u"emb", FileDocument(PROFILE_TEST, PROFILE_DIRECTORY)))
        self.assert_(self.facade.get_peer(u"emb").document)
        self.facade.remove_peer(u"emb")
        self.assertEquals(self.facade.has_peer(u"emb"), False)
    
    def test_status(self):
        self.facade.make_friend(u"emb")
        self.assertEquals(self.facade.get_peer(u"emb").state,
                          PeerDescriptor.FRIEND)
        self.facade.blacklist_peer(u"emb")
        self.assertEquals(self.facade.get_peer(u"emb").state,
                          PeerDescriptor.BLACKLISTED)
        self.facade.unmark_peer(u"emb")
        self.assertEquals(self.facade.get_peer(u"emb").state,
                          PeerDescriptor.ANONYMOUS)

    #TODO test fill_data


if __name__ == '__main__':
    unittest.main()
