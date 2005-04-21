"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest, sys
from difflib import Differ
from StringIO import StringIO
from solipsis.services.profile.document import FileDocument, CacheDocument
from solipsis.services.profile.view import PrintView, HtmlView

TEST_PROFILE = "data/profiles/test.prf"
TEST_DEMI = "data/profiles/demi.prf"
TEST_BRUCE =  "data/profiles/bruce.prf"

class ProfileTest(unittest.TestCase):
    """test interactactions between profiles"""
    
    def setUp(self):
        """override one in unittest.TestCase"""
        # bruce
        doc = FileDocument()
        self.assert_(doc.load(TEST_BRUCE))
        self.bruce_doc = CacheDocument()
        self.bruce_doc.import_document(doc)
        # demi
        self.demi_doc = FileDocument()
        self.assert_(self.demi_doc.load(TEST_DEMI))

    def test_bruce(self):
        """import bruce data"""
        self.assertEquals("Bruce", self.bruce_doc.get_firstname())
        self.assertEquals("Willis", self.bruce_doc.get_lastname())
        self.assertEquals("john", self.bruce_doc.get_pseudo())
        self.assertEquals("bruce.willis@stars.com", self.bruce_doc.get_email())
        self.assertEquals("01/06/1947", self.bruce_doc.get_birthday())
        self.assertEquals("English", self.bruce_doc.get_language())
        self.assertEquals("Hill", self.bruce_doc.get_address())
        self.assertEquals("920", self.bruce_doc.get_postcode())
        self.assertEquals("Los Angeles", self.bruce_doc.get_city())
        self.assertEquals("US", self.bruce_doc.get_country())
        self.assertEquals("Lots of movies, quite famous, doesn't look much but very effective",
                          self.bruce_doc.get_description())
        self.assertEquals([u'cinema', u'theatre', u'cop', u'action'], self.bruce_doc.get_hobbies())
        self.assertEquals({'music': u'jazz', 'film': u'Die Hard'},
                          self.bruce_doc.get_custom_attributes())
        
if __name__ == '__main__':
    unittest.main()
