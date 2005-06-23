"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest, sys
from difflib import Differ
from StringIO import StringIO
from solipsis.services.profile.document import FileDocument, CacheDocument
from solipsis.services.profile.view import PrintView, HtmlView
from solipsis.services.profile.tests import PROFILE_DIRECTORY, PROFILE_TEST, \
     PROFILE_BRUCE, PROFILE_DEMI

class ProfileTest(unittest.TestCase):
    """test interactactions between profiles"""
    
    def setUp(self):
        """override one in unittest.TestCase"""
        # bruce
        doc = FileDocument(PROFILE_BRUCE, PROFILE_DIRECTORY)
        self.assert_(doc.load())
        self.bruce_doc = CacheDocument(PROFILE_BRUCE, PROFILE_DIRECTORY)
        self.bruce_doc.import_document(doc)
        # demi
        self.demi_doc = FileDocument(PROFILE_DEMI, PROFILE_DIRECTORY)
        self.assert_(self.demi_doc.load())

    def test_bruce(self):
        """import bruce data"""
        self.assertEquals("Bruce", self.bruce_doc.get_firstname())
        self.assertEquals("Willis", self.bruce_doc.get_lastname())
        self.assertEquals("bruce.willis@stars.com", self.bruce_doc.get_email())
        self.assertEquals({'City': u'', 'Country': u'',
                           'Favourite Book': u'', 'music': u'jazz',
                           'Favourite Movie': u'', 'Sport': u'', 'Studies': u'',
                           'film': u'Die Hard'},
                          self.bruce_doc.get_custom_attributes())

    def test_peer_status(self):
        self.assertEquals(self.demi_doc.has_peer(self.bruce_doc._id), False)
        self.demi_doc.fill_data((self.bruce_doc._id, self.bruce_doc))
        self.assertEquals(self.demi_doc.has_peer(self.bruce_doc._id), False)
        self.demi_doc.make_friend(self.bruce_doc._id)
        self.assertEquals(self.demi_doc.has_peer(self.bruce_doc._id), True)
        self.demi_doc.unmark_peer(self.bruce_doc._id)
        self.assertEquals(self.demi_doc.has_peer(self.bruce_doc._id), False)
        
if __name__ == '__main__':
    unittest.main()
