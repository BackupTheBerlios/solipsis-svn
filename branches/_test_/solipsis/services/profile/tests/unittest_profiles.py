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
        bruce_doc = CacheDocument()
        bruce_doc.import_document(doc)
        self.bruce = HtmlView(bruce_doc)
        # demi
        demi_doc = FileDocument()
        self.assert_(demi_doc.load(TEST_DEMI))
        result = StringIO()
        self.demi = PrintView(demi_doc, result)

    def test_bruce(self):
        """import bruce data"""
        self.assertEquals(str(self.bruce.document),"""Mr
Bruce
Willis
john
/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/profile_male.gif
bruce.willis@stars.com
01/06/1947
English
Hill
920
Los Angeles
US
Lots of movies, quite famous, doesn't look much but very effective
[u'cinema', u'theatre', u'cop', u'action']
{'music': u'jazz', 'film': u'Die Hard'}
[]
{}
{}
""")
        
    def test_demi(self):
        """import demi data"""
        self.assertEquals(str(self.demi.document),"""[Personal]
city = Los Angeles
language = English
firstname = Demi
title = Mrs
photo = /home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/profile_female.gif
address = Hill
pseudo = demi
birthday = 01/02/1949
postcode = 920
lastname = Moore
country = US
email = demi.moore@stars.com
description = Big star, connected with Bruce

[Others]
john = Friend

[File]

[Custom]
book = Harry Potter
music = classic
film = Des hommes d'Honneurs
hobbies = cinema,theatre,striptease

""")        
        
        
if __name__ == '__main__':
    unittest.main()
