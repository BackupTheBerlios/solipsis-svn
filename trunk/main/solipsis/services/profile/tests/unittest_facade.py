"""Design pattern Facade: presents working API for all actions of GUI
available. This facade will be used both by GUI and unittests."""

import unittest
import sys
from StringIO import StringIO

from solipsis.services.profile.document import CacheDocument, PeerDescriptor
from solipsis.services.profile.view import PrintView
from solipsis.services.profile.facade import get_facade
from mx.DateTime import DateTime

class FacadeTest(unittest.TestCase):
    """assert that facade does effectively change document and calls callback on views"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.sys_stdout = sys.stdout
        self.sys_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        doc = CacheDocument()
        self.facade = get_facade(doc, PrintView(doc))
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        """override one in unittest.TestCase"""
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self.sys_stdout
        sys.stderr = self.sys_stderr

    # PERSONAL TAB
    def test_change_title(self):
        """sets new value for title"""
        self.facade.change_title(u'Mr')
        self.assertEquals("Mr\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())
        
    def test_change_firstname(self):
        """sets new value for firstname"""
        self.facade.change_firstname(u'manu')
        self.assertEquals("manu\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_lastname(self):
        """sets new value for lastname"""
        self.facade.change_lastname(u'breton')
        self.assertEquals("breton\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_pseudo(self):
        """sets new value for pseudo"""
        self.facade.change_pseudo(u'emb')
        self.assertEquals("emb\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_photo(self):
        """sets new value for photo"""
        self.facade.change_photo(unittest.__file__)
        self.assertEquals("%s\n"% unittest.__file__, sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_email(self):
        """sets new value for email"""
        self.facade.change_email(u'manu@ft.com')
        self.assertEquals("manu@ft.com\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_birthday(self):
        """sets new value for birthday"""
        self.facade.change_birthday(u'12/01/2005')
        self.assertEquals("12/01/2005\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_language(self):
        """sets new value for language"""
        self.facade.change_language(u'fr')
        self.assertEquals("fr\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_address(self):
        """sets new value for """
        self.facade.change_address(u'12 r V.Hugo')
        self.assertEquals("12 r V.Hugo\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_postcode(self):
        """sets new value for postcode"""
        self.facade.change_postcode(u'03400')
        self.assertEquals("3400\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_city(self):
        """sets new value for city"""
        self.facade.change_city(u'Paris')
        self.assertEquals("Paris\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_country(self):
        """sets new value for country"""
        self.facade.change_country(u'France')
        self.assertEquals("France\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_description(self):
        """sets new value for description"""
        self.facade.change_description(u'any desc')
        self.assertEquals("any desc\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    # CUSTOM TAB
    def test_change_hobbies(self):
        """sets new value for hobbies"""
        self.facade.change_hobbies([u"blabla", u"bla bla bla", u""])
        self.assertEquals("[u'blabla', u'bla bla bla', u'']\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_add_custom_attributes(self):
        """sets new value for custom_attributes"""
        self.facade.add_custom_attributes(("key", u"value"))
        self.assertEquals("{'key': u'value'}\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    # FILE TAB
    def test_add_dir(self):
        """sets new value for repository"""
        self.facade.add_dir(u"data")
        self.assertRaises(KeyError, self.facade.remove_dir, u"data/subdir1")
        self.facade.add_dir(u"data/subdir1")
        self.facade.remove_dir(u"data/subdir1")

    def test_share_dir(self):
        """share all content of dir"""
        self.facade.add_dir(u"data")
        self.facade.share_dir((u"data", True))
        self.assertRaises(KeyError, self.facade.share_dir, (u"routage", True))
        self.assertRaises(KeyError, self.facade.share_dir, (u"data/subdir1", True))
        self.facade.add_dir(u"data/emptydir")
        self.facade.add_dir(u"data/subdir1/subsubdir")
        self.facade.share_dir((u"data/emptydir", True))
        self.facade.share_dir((u"data/subdir1/subsubdir", True))

    def test_share_files(self):
        """share specified files"""
        self.facade.add_dir(u"data")
        self.facade.share_files((u"data", ["routage"], True))
        self.assertRaises(ValueError, self.facade.share_files, (u"data", ["routage", "subdir1"], True))
        self.facade.share_files((u"data", ["routage"], False))

    def test_tag_files(self):
        """tag specified tags"""
        self.facade.add_dir(u"data")
        self.facade.tag_files((u"data", ["routage"], u"tag desc 1"))
        self.assertRaises(ValueError, self.facade.tag_files, (u"data", ["routage", "subdir1"], u"tag desc 2"))
        self.facade.tag_files((u"data", ["routage", "date.txt"], u"tag desc 3"))

    def test_add_files(self):
        """expand dir"""
        self.facade.add_dir(u"data")
        self.facade.expand_dir(u"data")
        self.assertRaises(KeyError, self.facade.expand_dir, u"data/routage")
        self.facade.expand_dir(u"data/emptydir")
        self.assertRaises(KeyError, self.facade.expand_dir, u"data/subdir1/subsubdir")

    # OTHERS TAB
    def test_add_peer(self):
        """sets peer as friend """
        self.facade.add_peer(u"emb")
        self.assertEquals("{u'emb': [emb (%s), None]}\n"% PeerDescriptor.ANONYMOUS,
                          sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())
        
    def test_fill_data(self):
        """fill data, then remove it"""
        self.facade.fill_data((u"emb", CacheDocument()))
        self.facade.remove_peer(u"emb")
        self.assertEquals("{u'emb': [emb (%s), cache]}\n{}\n"% PeerDescriptor.ANONYMOUS,
                          sys.stdout.getvalue())
    
    def test_friend(self):
        """sets peer as friend """
        self.facade.make_friend(u"emb")
        self.assertEquals("{u'emb': [emb (%s), None]}\n"% PeerDescriptor.FRIEND,
                          sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())
        
    def test_blacklisted(self):
        """sets peer as blacklisted """
        self.facade.blacklist_peer(u"emb")
        self.assertEquals("{u'emb': [emb (%s), None]}\n"% PeerDescriptor.BLACKLISTED,
                          sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())
        
    def test_unmarked(self):
        """sets peer as anonymous """
        self.facade.unmark_peer(u"emb")
        self.assertEquals("{u'emb': [emb (%s), None]}\n"% PeerDescriptor.ANONYMOUS,
                          sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    #TODO test fill_data


if __name__ == '__main__':
    unittest.main()
