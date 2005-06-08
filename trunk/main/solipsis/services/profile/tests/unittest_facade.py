"""Design pattern Facade: presents working API for all actions of GUI
available. This facade will be used both by GUI and unittests."""

import unittest
from StringIO import StringIO

from solipsis.services.profile.document import CacheDocument, FileDocument
from solipsis.services.profile.data import DEFAULT_TAG, PeerDescriptor
from solipsis.services.profile.view import PrintView
from solipsis.services.profile.facade import get_facade
from os.path import abspath

class FacadeTest(unittest.TestCase):
    """assert that facade does effectively change document and calls callback on views"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.repo = u"/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests"
        doc = CacheDocument()
        doc.add_repository(self.repo)
        self.result = StringIO()
        self.facade = get_facade(doc, PrintView(doc, self.result))

    # PERSONAL TAB
    def test_change_title(self):
        self.facade.change_title(u'Mr')
        self.assertEquals("Mr\n", self.result.getvalue())
        
    def test_change_firstname(self):
        self.facade.change_firstname(u'manu')
        self.assertEquals("manu\n", self.result.getvalue())

    def test_change_lastname(self):
        self.facade.change_lastname(u'breton')
        self.assertEquals("breton\n", self.result.getvalue())

    def test_change_pseudo(self):
        self.facade.change_pseudo(u'emb')
        self.assertEquals("emb", self.result.getvalue().split('\n')[-2])

    def test_change_photo(self):
        self.facade.change_photo(unittest.__file__)
        self.assertEquals("%s\n"% unittest.__file__, self.result.getvalue())

    def test_change_email(self):
        self.facade.change_email(u'manu@ft.com')
        self.assertEquals("manu@ft.com\n", self.result.getvalue())

    def test_change_birthday(self):
        self.facade.change_birthday(u'12/01/2005')
        self.assertEquals("12/01/2005\n", self.result.getvalue())

    def test_change_language(self):
        self.facade.change_language(u'fr')
        self.assertEquals("fr\n", self.result.getvalue())

    def test_change_address(self):
        self.facade.change_address(u'12 r V.Hugo')
        self.assertEquals("12 r V.Hugo\n", self.result.getvalue())

    def test_change_postcode(self):
        self.facade.change_postcode(u'03400')
        self.assertEquals("3400\n", self.result.getvalue())

    def test_change_city(self):
        self.facade.change_city(u'Paris')
        self.assertEquals("Paris\n", self.result.getvalue())

    def test_change_country(self):
        self.facade.change_country(u'France')
        self.assertEquals("France\n", self.result.getvalue())

    def test_change_description(self):
        self.facade.change_description(u'any desc')
        self.assertEquals("any desc\n", self.result.getvalue())

    def test_change_download_repo(self):
        self.facade.change_download_repo(u'any desc')
        self.assertEquals("any desc\n", self.result.getvalue())

    # CUSTOM TAB
    def test_change_hobbies(self):
        self.facade.change_hobbies([u"blabla", u"bla bla bla", u""])
        self.assertEquals("[u'blabla', u'bla bla bla', u'']\n", self.result.getvalue())

    def test_add_custom_attributes(self):
        self.facade.add_custom_attributes(("key", u"value"))
        self.assertEquals("{'key': u'value'}\n", self.result.getvalue())

    # BLOG TAB
    def test_blog(self):
        self.assertRaises(AssertionError, self.facade.add_blog, "no owner yet")
        self.facade.change_pseudo(u"manu")
        self.facade.add_blog("first blog")
        self.facade.add_blog("second blog")
        self.facade.add_comment((0, 'first comment'))
        blog = self.facade.get_blog(0)
        self.assertEquals(blog.text, "first blog")
        self.assertEquals(blog.comments[0].text, 'first comment')
        self.assertEquals(self.facade.count_blogs(), 2)
        self.facade.remove_blog(0)
        self.assertEquals(self.facade.count_blogs(), 1)
        
    # FILE TAB
    def test_repository(self):
        doc = CacheDocument()
        facade = get_facade(doc, PrintView(doc, self.result))
        facade.add_repository(abspath(u"data/profiles"))
        self.assertRaises(KeyError, facade.remove_repository, abspath(u"data"))
        self.assertRaises(ValueError, facade.add_repository, abspath(u"data"))
        facade.add_repository(abspath(u"data/emptydir"))
        facade.remove_repository(abspath(u"data/emptydir"))

    def test_expand_dir(self):
        self.assertEquals(self.facade.documents["cache"].get_shared(self.repo),
                          [])
        self.facade.expand_dir(abspath(u"data"))
        check = {}
        self.assertEquals(self._build_check_dict(self.facade.documents["cache"], self.repo),
                          {abspath(u'data'): u'none',
                           abspath(u'data/.path'): u'none',
                           abspath(u'data/date.txt'): u'none',
                           abspath(u'data/routage'): u'none',
                           abspath(u'data/.svn'): u'none',
                           abspath(u'data/subdir1'): u'none',
                           abspath(u'data/profiles'): u'none',
                           abspath(u'data/emptydir'): u'none'})
        self.assertRaises(AssertionError, self.facade.expand_dir,
                          abspath(u"data/routage"))
        self.facade.expand_dir(abspath(u"data/emptydir"))
        self.assertEquals(self._build_check_dict(self.facade.documents["cache"], self.repo),
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
        self.assertEquals(self._build_check_dict(self.facade.documents["cache"], self.repo),
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
        files = self.facade.documents["cache"].get_files()[self.repo]
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
        files = self.facade.documents["cache"].get_files()[self.repo]
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
        files = self.facade.documents["cache"].get_files()[self.repo]
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
        self.assertEquals(self.facade.get_peer(u"emb").document, None)
        self.facade.fill_data((u"emb", FileDocument()))
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
