"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
import sys
from difflib import Differ
from StringIO import StringIO
import os.path
from solipsis.services.profile.document import FileDocument, CacheDocument
from solipsis.services.profile.view import PrintView, HtmlView
from solipsis.services.profile import PROFILE_DIR

TEST_PROFILE = os.path.join(PROFILE_DIR, ".test.solipsis")

class ValidatorTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    expected = """#ISO-8859-1
[Personal]
city = Paris
language = fr
firstname = manu
title = Mr
lastname = breton
address = 12 rue V Hugo
pseudo = emb
birthday = 12/01/2005
postcode = 34000
photo = /usr/lib/python2.3/unittest.pyc
country = France
email = manu@ft.com
description = anything

[Others]
nico = 1

[File]
/usr/lib/python2.3/unittest.pyc = tag description
repository = .

[Custom]
color = blue
homepage = manu.com
hobbies = blabla,bla bla bla,

"""
    
    def setUp(self):
        """override one in unittest.TestCase"""
        self.document = FileDocument()

    # PERSONAL TAB
    def test_save(self):
        """Fill a full set of data"""
        self.document.set_title(u"Mr")
        self.document.set_firstname(u"manu")
        self.document.set_lastname(u"breton")
        self.document.set_pseudo(u"emb")
        self.document.set_photo(unittest.__file__)
        self.document.set_email(u"manu@ft.com")
        self.document.set_birthday(u"12/01/2005")
        self.document.set_language(u"fr")
        self.document.set_address(u"12 rue V Hugo")
        self.document.set_postcode(u"34000")
        self.document.set_city(u"Paris")
        self.document.set_country(u"France")
        self.document.set_description(u"anything")
        self.document.set_hobbies([u"blabla", u"bla bla bla", u""])
        self.document.add_custom_attributes((u"homepage", u"manu.com"))
        self.document.add_custom_attributes((u'color', u'blue'))
        self.document.set_repository(".")
        self.document.add_file(unittest.__file__)
        self.document.tag_file((unittest.__file__, u"tag description"))
        self.document.add_peer(u"nico")
        self.document.make_friend(u"nico")
        # write file
        self.document.save(TEST_PROFILE)
        differ = Differ()
        result =  differ.compare([line.replace('\n', '') for line
                                  in open(self.document.file_name).readlines()],
                                 ValidatorTest.expected.splitlines())
        for line in result:
            self.assert_(line.startswith("  "))

    def test_load(self):
        """import data"""
        self.document.load(TEST_PROFILE)
        self.assertEquals("Mr", self.document.get_title())
        self.assertEquals("manu", self.document.get_firstname())
        self.assertEquals("breton", self.document.get_lastname())
        self.assertEquals("emb", self.document.get_pseudo())
        self.assertEquals(unittest.__file__, self.document.get_photo())
        self.assertEquals("manu@ft.com", self.document.get_email())
        self.assertEquals("12/01/2005", self.document.get_birthday())
        self.assertEquals("fr", self.document.get_language())
        self.assertEquals("12 rue V Hugo", self.document.get_address())
        self.assertEquals("34000", self.document.get_postcode())
        self.assertEquals("Paris", self.document.get_city())
        self.assertEquals("France", self.document.get_country())
        self.assertEquals("anything", self.document.get_description())
        self.assertEquals([u'blabla', u'bla bla bla', u''], self.document.get_hobbies())
        self.assertEquals({"homepage": "manu.com", 'color':'blue'}, self.document.get_custom_attributes())
        self.assertEquals(".", self.document.get_repository())
        files = self.document.get_files()
        self.assertEquals("%s (tag description)"% unittest.__file__,
                          str(files[unittest.__file__]))
        peers = self.document.get_peers()
        self.assertEquals('[nico (1), None]', str(peers['nico']))


    def test_import(self):
        """import file document into cache document"""
        self.document.load(TEST_PROFILE)
        new_doc = CacheDocument()
        new_doc.import_document(self.document)
        self.assertEquals("Mr", new_doc.get_title())
        self.assertEquals("manu", new_doc.get_firstname())
        self.assertEquals("breton", new_doc.get_lastname())
        self.assertEquals("emb", new_doc.get_pseudo())
        self.assertEquals(unittest.__file__, new_doc.get_photo())
        self.assertEquals("manu@ft.com", new_doc.get_email())
        self.assertEquals("12/01/2005", new_doc.get_birthday())
        self.assertEquals("fr", new_doc.get_language())
        self.assertEquals("12 rue V Hugo", new_doc.get_address())
        self.assertEquals("34000", new_doc.get_postcode())
        self.assertEquals("Paris", new_doc.get_city())
        self.assertEquals("France", new_doc.get_country())
        self.assertEquals("anything", new_doc.get_description())
        self.assertEquals([u'blabla', u'bla bla bla', u''], new_doc.get_hobbies())
        self.assertEquals({"homepage": "manu.com", 'color':'blue'}, new_doc.get_custom_attributes())
        self.assertEquals(".", new_doc.get_repository())
        files = new_doc.get_files()
        self.assertEquals("%s (tag description)"% unittest.__file__,
                          str(files[unittest.__file__]))
        peers = new_doc.get_peers()
        self.assertEquals('[nico (1), None]', str(peers['nico']))

    def test_view(self):
        """import file document into printView"""
        self.document.load(TEST_PROFILE)
        sav_stdout = sys.stdout
        result = StringIO()
        sys.stdout = result
        view = PrintView(self.document)
        self.assertEquals(result.getvalue(), """Mr
manu
breton
emb
/usr/lib/python2.3/unittest.pyc
manu@ft.com
12/01/2005
fr
12 rue V Hugo
34000
Paris
France
anything
[u'blabla', u'bla bla bla', u'']
{'color': u'blue', 'homepage': u'manu.com'}
.
{'/usr/lib/python2.3/unittest.pyc': /usr/lib/python2.3/unittest.pyc (tag description)}
{u'nico': [nico (1), None]}
""")
        result.close()
        sys.stdout = sav_stdout

    def test_html_view(self):
        """import file document into printView"""
        self.document.load(TEST_PROFILE)
        view = HtmlView(self.document)
        result = view.get_view()
        
if __name__ == '__main__':
    unittest.main()
