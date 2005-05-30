# -*- coding:ISO-8859-1 -*-
"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
import os.path
from pprint import pprint
from os.path import abspath
from difflib import Differ
from StringIO import StringIO
from solipsis.services.profile.document import FileDocument, CacheDocument, PeerDescriptor
from solipsis.services.profile.view import PrintView, HtmlView
from solipsis.services.profile.data import DirContainer
from solipsis.services.profile import PROFILE_DIR

TEST_PROFILE = "data/profiles/test"
REPO = u"/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests"

class FileTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.document = FileDocument()
        self.document.add_repository(REPO)
        # first test to call must write test file to get correct
        # execution of the others
        if not os.path.exists(TEST_PROFILE):
            self.test_save()

    def _assertContent(self, doc):
        """check validity of content"""
        self.assertEquals("Mr", doc.get_title())
        self.assertEquals("manu", doc.get_firstname())
        self.assertEquals("breton", doc.get_lastname())
        self.assertEquals("emb", doc.get_pseudo())
        self.assertEquals(unittest.__file__, doc.get_photo())
        self.assertEquals("manu@ft.com", doc.get_email())
        self.assertEquals("12/01/2005", doc.get_birthday())
        self.assertEquals("fr", doc.get_language())
        self.assertEquals("12 rue V Hugo", doc.get_address())
        self.assertEquals("34000", doc.get_postcode())
        self.assertEquals("Paris", doc.get_city())
        self.assertEquals("France", doc.get_country())
        self.assertEquals("anything", doc.get_description())
        self.assertEquals([u'blabla', u'bla bla bla', u''], doc.get_hobbies())
        self.assertEquals({'repositories': REPO, 'color': u'blue', 'homepage': u'manu.com'},
                          doc.get_custom_attributes())
        # assert correct sharing
        self.assertEquals({REPO + u'/data/subdir1/subsubdir/null': u'empty',
                           REPO + u'/data/subdir1': u'none',
                           REPO + u'/data/subdir1/subsubdir/dummy.txt': u'empty',
                           REPO + u'/data/routage': u'none',
                           REPO + u'/data/emptydir': u'none'},
                          doc.get_shared(REPO))
        files = doc.get_files()
        self.assertEquals(files.has_key(REPO), True)
        self.assertEquals(files[REPO][abspath(u"data")]._shared, False)
        self.assertEquals(files[REPO][abspath(u"data/routage")]._shared, True)
        self.assertEquals(files[REPO][abspath(u"data/emptydir")]._shared, True)
        self.assertEquals(files[REPO][abspath(u"data/subdir1")]._shared, True)
        self.assertEquals(files[REPO][abspath(u"data/subdir1/")]._shared, True)
        self.assertEquals(files[REPO].has_key(abspath(u"data/subdir1/date.doc")), False)
        self.assertEquals(files[REPO][abspath(u"data/subdir1/subsubdir")]._shared, False)
        self.assertEquals(files[REPO][abspath(u"data/subdir1/subsubdir/null")]._shared, True)
        self.assertEquals(files[REPO][abspath(u"data/subdir1/subsubdir/dummy.txt")]._shared, True)
        self.assertEquals(files[REPO].has_key(abspath(u"data/subdir1/subsubdir/default.solipsis")), False)
        # peers
        peers = doc.get_peers()
        self.assertEquals(peers.has_key(u'nico'), True)
        self.assertEquals(peers[u'nico'][0].state, PeerDescriptor.FRIEND)
        self.assertEquals(peers[u'nico'][1], None)

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
        # set files
        self.document.add(abspath(u"data"))
        self.document.expand_dir(abspath(u"data"))
        self.document.share_files((abspath(u"data"), ["routage", u"emptydir", u"subdir1"], True))
        self.document.expand_dir(abspath(u"data/subdir1"))
        self.document.share_files((abspath(u"data/subdir1/subsubdir"), ["null", "dummy.txt"], True))
        self.document.tag_files((abspath(u"data"), ["date.txt"], u"tagos"))
        self.document.tag_files((abspath(u"data/subdir1/subsubdir"), ["null", "dummy.txt"], u"empty"))
        # set peers
        self.document.add_peer(u"nico")
        self.document.make_friend(u"nico")
        # check content
        self._assertContent(self.document)
        # write file
        self.document.save(TEST_PROFILE)

    def test_load(self):
        """import data"""
        self.document.load(TEST_PROFILE)
        self._assertContent(self.document)

    def test_import(self):
        """import file document into cache document"""
        self.document.load(TEST_PROFILE)
        new_doc = CacheDocument()
        new_doc.import_document(self.document)
        self._assertContent(new_doc)

    def test_save_and_load(self):
        """save & load"""
        self.document.load(TEST_PROFILE)
        self.document.share_file((REPO+"/data/subdir1/TOtO.txt", True))
        self.document.save("data/profiles/tata")
        new_doc = FileDocument()
        new_doc.load("data/profiles/tata")
        container = new_doc.get_container(REPO+u"/data/subdir1")
        self.assert_(dict.has_key(container, "TOtO.txt"))

    def test_load_and_save(self):
        """load & save"""
        self.document.load(TEST_PROFILE)
        new_doc = CacheDocument()
        new_doc.import_document(self.document)
        new_doc.remove_repository(REPO)
        self.assertEquals(new_doc.get_files(), {})
        new_doc.add_repository(REPO+u"/data/profiles")
        new_doc.add_repository(REPO+u"/data/subdir1")
        self.assertEquals(new_doc.get_files()[REPO+u"/data/profiles"]._shared, False)
        self.assert_(new_doc.get_files()[REPO+u"/data/subdir1"] != None)
        new_doc.save("data/profiles/toto")
        
    def test_default(self):
        """load default"""
        self.document.load(u"dummy")
        self.assertEquals(u"Mr", self.document.get_title())
        self.assertEquals(u"Emmanuel", self.document.get_firstname())
        self.assertEquals(u"Breton", self.document.get_lastname())
        self.assertEquals(u"emb", self.document.get_pseudo())
        self.assertEquals(u'/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/question_mark.gif',
                          self.document.get_photo())
        self.assertEquals(u"emb@logilab.fr", self.document.get_email())
        self.assertEquals(u"01/04/2005", self.document.get_birthday())
        self.assertEquals(u"fr", self.document.get_language())
        self.assertEquals(u"", self.document.get_address())
        self.assertEquals(u"75", self.document.get_postcode())
        self.assertEquals(u"", self.document.get_city())
        self.assertEquals(u"", self.document.get_country())
        self.assertEquals(u"Developer/Designer of this handful plugin", self.document.get_description())
        self.assertEquals([], self.document.get_hobbies())
        self.assertEquals({'repositories': REPO},
                          self.document.get_custom_attributes())
        # assert correct sharing
        self.assertEquals({}, self.document.get_shared(REPO))
        self.assertEquals({REPO: DirContainer(REPO)}, self.document.get_files())
        # peers
        self.assertEquals({}, self.document.get_peers())
        
    def test_view(self):
        """load & printView"""
        self.document.load(TEST_PROFILE)
        result = StringIO()
        view = PrintView(self.document, result, do_import=True)
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
{'color': u'blue', 'homepage': u'manu.com', 'repositories': u'/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests'}
(isolipsis.services.profile.data
Blogs
p0
(dp1
S'owner'
p2
Vemb
p3
sS'blogs'
p4
(lp5
sb.
{u'/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests': {Dc:tests(?-,'none',#0) : [{Dc:data(?-,'none',#3) : [{Dc:emptydir(?Y,'none',#-1) : []}, Fc:routage(?Y,'none'), Fc:date.txt(?-,'tagos'), {Dc:subdir1(?Y,'none',#-1) : [{Dc:subsubdir(?-,'none',#2) : [Fc:null(?Y,'empty'), Fc:dummy.txt(?Y,'empty')]}]}]}]}}
{u'nico': [nico (%s), None]}
"""% PeerDescriptor.FRIEND)
        result.close()
        
if __name__ == '__main__':
    unittest.main()
