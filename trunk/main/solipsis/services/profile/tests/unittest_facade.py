"""Design pattern Facade: presents working API for all actions of GUI
available. This facade will be used both by GUI and unittests."""

import unittest
from StringIO import StringIO

from solipsis.services.profile.document import CacheDocument, PeerDescriptor
from solipsis.services.profile.data import DEFAULT_TAG
from solipsis.services.profile.view import PrintView
from solipsis.services.profile.facade import get_facade
from mx.DateTime import DateTime
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
        """sets new value for title"""
        self.facade.change_title(u'Mr')
        self.assertEquals("Mr\n", self.result.getvalue())
        
    def test_change_firstname(self):
        """sets new value for firstname"""
        self.facade.change_firstname(u'manu')
        self.assertEquals("manu\n", self.result.getvalue())

    def test_change_lastname(self):
        """sets new value for lastname"""
        self.facade.change_lastname(u'breton')
        self.assertEquals("breton\n", self.result.getvalue())

    def test_change_pseudo(self):
        """sets new value for pseudo"""
        self.facade.change_pseudo(u'emb')
        self.assertEquals("emb\n", self.result.getvalue())

    def test_change_photo(self):
        """sets new value for photo"""
        self.facade.change_photo(unittest.__file__)
        self.assertEquals("%s\n"% unittest.__file__, self.result.getvalue())

    def test_change_email(self):
        """sets new value for email"""
        self.facade.change_email(u'manu@ft.com')
        self.assertEquals("manu@ft.com\n", self.result.getvalue())

    def test_change_birthday(self):
        """sets new value for birthday"""
        self.facade.change_birthday(u'12/01/2005')
        self.assertEquals("12/01/2005\n", self.result.getvalue())

    def test_change_language(self):
        """sets new value for language"""
        self.facade.change_language(u'fr')
        self.assertEquals("fr\n", self.result.getvalue())

    def test_change_address(self):
        """sets new value for """
        self.facade.change_address(u'12 r V.Hugo')
        self.assertEquals("12 r V.Hugo\n", self.result.getvalue())

    def test_change_postcode(self):
        """sets new value for postcode"""
        self.facade.change_postcode(u'03400')
        self.assertEquals("3400\n", self.result.getvalue())

    def test_change_city(self):
        """sets new value for city"""
        self.facade.change_city(u'Paris')
        self.assertEquals("Paris\n", self.result.getvalue())

    def test_change_country(self):
        """sets new value for country"""
        self.facade.change_country(u'France')
        self.assertEquals("France\n", self.result.getvalue())

    def test_change_description(self):
        """sets new value for description"""
        self.facade.change_description(u'any desc')
        self.assertEquals("any desc\n", self.result.getvalue())

    # CUSTOM TAB
    def test_change_hobbies(self):
        """sets new value for hobbies"""
        self.facade.change_hobbies([u"blabla", u"bla bla bla", u""])
        self.assertEquals("[u'blabla', u'bla bla bla', u'']\n", self.result.getvalue())

    def test_add_custom_attributes(self):
        """sets new value for custom_attributes"""
        self.facade.add_custom_attributes(("key", u"value"))
        self.assertEquals("{'key': u'value'}\n", self.result.getvalue())

    # BLOG TAB
    def test_blog(self):
        """set message and comments in blog"""
        self.assertRaises(AssertionError, self.facade.add_blog, "no owner yet")
        self.facade.change_pseudo(u"manu")
        self.facade.add_blog("first blog")
        self.facade.add_blog("second blog")
        self.facade.add_comment((0, 'first comment'))
        blog = self.facade.get_blog(0)
        self.assertEquals(blog.text, "first blog")
        self.assertEquals(blog.comments[0].text, 'first comment')
        
    # FILE TAB
    def test_repository(self):
        """sets new value for repository"""
        doc = CacheDocument()
        facade = get_facade(doc, PrintView(doc, self.result))
        facade.add_repository(abspath(u"data/profiles"))
        self.assertRaises(KeyError, facade.remove_repository, abspath(u"data"))
        self.assertRaises(ValueError, facade.add_repository, abspath(u"data"))
        facade.add_repository(abspath(u"data/emptydir"))
        facade.remove_repository(abspath(u"data/emptydir"))

    def test_expand_dir(self):
        """expand dir"""
        self.assertEquals(self.facade.documents["cache"].get_shared(self.repo),
                          {})
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
        """format list of existing dir"""
        result = {}
        for name, container in doc.files[repo_path].flat().iteritems():
            result[name] = container._tag
        return result
        
    def test_share_dir(self):
        """share all content of dir"""
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
        """share specified files"""
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
        """tag specified tags"""
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
        """sets peer as friend """
        self.facade.add_peer(u"emb")
        self.assertEquals("{u'emb': [emb (%s), None]}\n"% PeerDescriptor.ANONYMOUS,
                          self.result.getvalue())
        
    def test_fill_data(self):
        """fill data, then remove it"""
        self.facade.fill_data((u"emb", CacheDocument()))
        self.facade.remove_peer(u"emb")
        self.assertEquals("{u'emb': [emb (%s), cache]}\n{}\n"% PeerDescriptor.ANONYMOUS,
                          self.result.getvalue())
    
    def test_friend(self):
        """sets peer as friend """
        self.facade.make_friend(u"emb")
        self.assertEquals("{u'emb': [emb (%s), None]}\n"% PeerDescriptor.FRIEND,
                          self.result.getvalue())
        
    def test_blacklisted(self):
        """sets peer as blacklisted """
        self.facade.blacklist_peer(u"emb")
        self.assertEquals("{u'emb': [emb (%s), None]}\n"% PeerDescriptor.BLACKLISTED,
                          self.result.getvalue())
        
    def test_unmarked(self):
        """sets peer as anonymous """
        self.facade.unmark_peer(u"emb")
        self.assertEquals("{u'emb': [emb (%s), None]}\n"% PeerDescriptor.ANONYMOUS,
                          self.result.getvalue())

    #TODO test fill_data


if __name__ == '__main__':
    unittest.main()
