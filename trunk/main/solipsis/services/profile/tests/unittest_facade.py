"""Design pattern Facade: presents working API for all actions of GUI
available. This facade will be used both by GUI and unittests."""

import unittest
import sys
from StringIO import StringIO

from solipsis.services.profile.document import CacheDocument
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
        self.facade.change_hobbies(u'blablabl\nbla blabla \n')
        self.assertEquals("[u'blablabl', u'bla blabla ', u'']\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_add_custom_attributes(self):
        """sets new value for custom_attributes"""
        self.facade.add_custom_attributes(("key", u"value"))
        self.assertEquals("{'key': u'value'}\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    # FILE TAB
    def test_change_repository(self):
        """sets new value for repositor"""
        self.facade.change_repository(u'.')
        self.assertEquals(".\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_add_file(self):
        """sets new value for unshared file"""
        self.facade.add_file(unittest.__file__)
        self.assertEquals("{'/usr/lib/python2.3/unittest.pyc': /usr/lib/python2.3/unittest.pyc (None)}\n",
                          sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    def test_change_file_tag(self):
        """sets new value for tagged file"""
        self.facade.change_file_tag((unittest.__file__, u'description test'))
        self.assertEquals("{'/usr/lib/python2.3/unittest.pyc': /usr/lib/python2.3/unittest.pyc (description test)}\n",
                          sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())

    # OTHERS TAB
    def test_default_peers(self):
        """sets peer as friend """
        self.facade.add_peer(u"emb")
        self.assertEquals("{u'emb': emb (0)}\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())
        
    def test_friend(self):
        """sets peer as friend """
        self.facade.make_friend(u"emb")
        self.assertEquals("{u'emb': emb (1)}\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())
        
    def test_blacklisted(self):
        """sets peer as friend """
        self.facade.blacklist_peer(u"emb")
        self.assertEquals("{u'emb': emb (2)}\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())
        
    def test_unmarked(self):
        """sets peer as friend """
        self.facade.unmark_peer(u"emb")
        self.assertEquals("{u'emb': emb (0)}\n", sys.stdout.getvalue())
        self.assertEquals("", sys.stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
