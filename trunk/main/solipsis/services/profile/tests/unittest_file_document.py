# -*- coding:ISO-8859-1 -*-
"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
from difflib import Differ
from StringIO import StringIO
import os.path
from os.path import abspath
from solipsis.services.profile.document import FileDocument, CacheDocument, PeerDescriptor
from solipsis.services.profile.view import PrintView, HtmlView
from solipsis.services.profile import PROFILE_DIR

TEST_PROFILE = "data/profiles/test.prf"

class FileTest(unittest.TestCase):
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

[Files]
/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests/data/date.txt = Error: doc not shared
/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests/data = none
/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests/data/subdir1/subsubdir/null = empty
/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests/data/subdir1 = none
/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests/data/subdir1/subsubdir/dummy.txt = empty
/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests/data/routage = none
/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests/data/emptydir = none

[Others]
nico = Friend,none

[Custom]
color = blue
homepage = manu.com
repositories = /home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests
hobbies = blabla,bla bla bla,

"""
    
    def setUp(self):
        """override one in unittest.TestCase"""
        self.document = FileDocument()
        self.document.add_repository(
            u"/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests")
        # first test to call must write test file to get correct
        # execution of the others
        if not os.path.exists(TEST_PROFILE):
            self.test_save()

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
        self.document.add(abspath(u"data"))
        self.document.expand_dir(abspath(u"data"))
        self.document.share_files((abspath(u"data"), ["routage"], True))
        self.document.share_dir((abspath(u"data/emptydir"), True))
        self.document.expand_dir(abspath(u"data/subdir1"))
        self.document.share_dir((abspath(u"data/subdir1"), True))
        self.document.share_files((abspath(u"data/subdir1/subsubdir"), ["null", "dummy.txt"], True))
        self.document.tag_files((abspath(u"data"), ["date.txt"], u"Error: doc not shared"))
        self.document.tag_files((abspath(u"data/subdir1/subsubdir"), ["null", "dummy.txt"], u"empty"))
        self.document.add_peer(u"nico")
        self.document.make_friend(u"nico")
        # write file
        self.document.save(TEST_PROFILE)
        differ = Differ()
        result =  list(differ.compare([line.replace('\n', '') for line
                                  in open(self.document.file_name).readlines()],
                                 FileTest.expected.splitlines()))
        for index, line in enumerate(result):
            if not line.startswith("  "):
                print '\n'.join(result)
                print "*************"
                print '\n'.join(result[index-3: index+5])
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
        self.assertEquals({'dirs': u'data,data/emptydir,data/subdir1,data/subdir1/subsubdir', 'color': u'blue', 'homepage': u'manu.com'}, self.document.get_custom_attributes())
        self.assertEquals([u'data', u'data/emptydir', u'data/subdir1', u'data/subdir1/subsubdir'], self.document.get_keys())
        self.assertEquals("[u'data', u'data/emptydir', u'data/subdir1', u'data/subdir1/subsubdir']", 
                          str(self.document.get_files()))
        peers = self.document.get_peers()
        self.assertEquals('[nico (%s), None]'% PeerDescriptor.FRIEND, str(peers['nico']))


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
        self.assertEquals({'dirs': u'data,data/emptydir,data/subdir1,data/subdir1/subsubdir', 'color': u'blue', 'homepage': u'manu.com'}, new_doc.get_custom_attributes())
        self.assertEquals([u'data', u'data/emptydir', u'data/subdir1', u'data/subdir1/subsubdir'], new_doc.get_keys())
        self.assertEquals("[u'data', u'data/emptydir', u'data/subdir1', u'data/subdir1/subsubdir']",
                          str(self.document.get_files()))
        peers = new_doc.get_peers()
        self.assertEquals('[nico (%s), None]'% PeerDescriptor.FRIEND, str(peers['nico']))
        
    def test_default(self):
        """load default"""
        self.document.load("dummy")
        result = StringIO()
        view = PrintView(self.document, result, do_import=True)
        self.assertEquals(result.getvalue(), unicode("""Mr
Emmanuel
Br�ton
emb
/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/question_mark.gif
emb@logilab.fr
01/04/2005
fr

75


Developer/Designer of this handful plugin
[]
{}
[]
{}
{}
""", "iso-8859-1"))
        result.close()
        
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
{'dirs': u'data,data/emptydir,data/subdir1,data/subdir1/subsubdir', 'color': u'blue', 'homepage': u'manu.com'}
[u'data', u'data/emptydir', u'data/subdir1', u'data/subdir1/subsubdir']
{u'data/subdir1': data/subdir1(subdir1) [1] {u'date.doc': data/subdir1/date.doc [shared] [none]}, u'data/emptydir': data/emptydir(emptydir) [0] {}, u'data/subdir1/subsubdir': data/subdir1/subsubdir(subsubdir) [3] {u'dummy.txt': data/subdir1/subsubdir/dummy.txt [shared] [empty], u'null': data/subdir1/subsubdir/null [shared] [empty], u'default.solipsis': data/subdir1/subsubdir/default.solipsis [shared] [none]}, u'data': data(data) [3] {u'routage': data/routage [shared] [none], u'.path': data/.path [shared] [none], u'date.txt': data/date.txt [shared] [none]}}
{u'nico': [nico (%s), None]}
"""% PeerDescriptor.FRIEND)
        result.close()
        
if __name__ == '__main__':
    unittest.main()
