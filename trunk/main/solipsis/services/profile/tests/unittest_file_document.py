# -*- coding:ISO-8859-1 -*-
"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import sys
import unittest
import os.path
from pprint import pprint
from os.path import abspath
from difflib import Differ
from solipsis.services.profile import QUESTION_MARK, PROFILE_EXT
from solipsis.services.profile.data import PeerDescriptor, load_blogs
from solipsis.services.profile.file_document import FileDocument
from solipsis.services.profile.cache_document import CacheDocument
from solipsis.services.profile.data import DirContainer, Blogs
from solipsis.services.profile import ENCODING, PROFILE_DIR
from solipsis.services.profile.tests import REPO, PROFILE_UNICODE, \
     PROFILE_DIRECTORY, PROFILE_TEST, PROFILE_BRUCE, PROFILE_TATA


class FileTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.document = FileDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        self.document.add_file(REPO)
        # first test to call must write test file to get correct
        # execution of the others
        if not os.path.exists(os.path.join(PROFILE_DIRECTORY, PROFILE_TEST + PROFILE_EXT)):
            self.test_save()

    def _assertContent(self, doc):
        """check validity of content"""
        self.assertEquals("Mr", doc.get_title())
        self.assertEquals("manu", doc.get_firstname())
        self.assertEquals("breton", doc.get_lastname())
        self.assertEquals(QUESTION_MARK(), doc.get_photo())
        self.assertEquals("manu@ft.com", doc.get_email())
        self.assertEquals({'City': u'', 'color': u'blue', 'Country': u'',
                           'Favourite Book': u'', 'homepage': u'manu.com',
                           'Favourite Movie': u'', 'Studies': u''},
                          doc.get_custom_attributes())
        # assert correct sharing
        shared_dict = {}
        for container in  doc.get_shared(REPO):
            shared_dict[container.get_path()] = container
        expected_files = {REPO + '/data/subdir1/subsubdir/null': u'empty',
                          REPO + '/data/subdir1': u'none',
                          REPO + '/data/subdir1/subsubdir/dummy.txt': u'empty',
                          REPO + '/data/routage': u'none',
                          REPO + '/data/emptydir': u'none'}
        for expected, tag in expected_files.iteritems():
            self.assert_(shared_dict.has_key(expected))
            self.assertEquals(shared_dict[expected]._tag, tag)
        files = doc.get_files()
        self.assertEquals(files.has_key(REPO), True)
        self.assertEquals(files[REPO][abspath("data")]._shared, False)
        self.assertEquals(files[REPO][abspath("data/routage")]._shared, True)
        self.assertEquals(files[REPO][abspath("data/emptydir")]._shared, True)
        self.assertEquals(files[REPO][abspath("data/subdir1")]._shared, True)
        self.assertEquals(files[REPO][abspath("data/subdir1/")]._shared, True)
        self.assertEquals(files[REPO][abspath("data/subdir1/subsubdir")]._shared, False)
        self.assertEquals(files[REPO][abspath("data/subdir1/subsubdir/null")]._shared, True)
        self.assertEquals(files[REPO][abspath("data/subdir1/subsubdir/dummy.txt")]._shared, True)
        self.assertEquals(files[REPO].has_key(abspath("data/subdir1/subsubdir/default.solipsis")), False)
        # peers
        peers = doc.get_peers()
        self.assertEquals(peers.has_key(u'bruce'), True)
        self.assertEquals(peers[u'bruce'].state, PeerDescriptor.FRIEND)
        self.assertEquals(peers[u'bruce'].connected, False)

    # PERSONAL TAB
    def test_save(self):
        # write bruce blog
        try:
            bruce_blog = load_blogs(PROFILE_BRUCE, PROFILE_DIRECTORY)
        except ValueError:
            bruce_blog = Blogs(PROFILE_BRUCE, PROFILE_DIRECTORY)
            bruce_blog.add_blog("Hi Buddy", PROFILE_BRUCE)
            bruce_blog.save()
        # write data
        self.document.set_title(u"Mr")
        self.document.set_firstname(u"manu")
        self.document.set_lastname(u"breton")
        self.document.set_photo(QUESTION_MARK())
        self.document.set_email(u"manu@ft.com")
        self.document.load_defaults()
        self.document.add_custom_attributes((u"homepage", u"manu.com"))
        self.document.add_custom_attributes((u'color', u'blue'))
        self.document.remove_custom_attributes(u'Sport')
        # set files
        self.document.add(abspath("data"))
        self.document.expand_dir(abspath("data"))
        self.document.expand_dir(abspath("data/subdir1"))
        self.document.recursive_share((abspath("data"), False))
        self.assertEquals(self.document.get_files()[REPO][abspath("data")]._shared, False)
        self.document.share_files((abspath("data"), ["routage", "emptydir", "subdir1"], True))
        self.document.share_files((abspath("data/subdir1/subsubdir"), ["null", "dummy.txt"], True))
        self.document.tag_files((abspath("data"), ["date.txt"], u"tagos"))
        self.document.tag_files((abspath("data/subdir1/subsubdir"), ["null", "dummy.txt"], u"empty"))
        # set peers
        bruce_doc = FileDocument(PROFILE_BRUCE, PROFILE_DIRECTORY)
        bruce_doc.load()
        self.document.fill_data((u"bruce", bruce_doc))
        self.document.fill_blog((u"bruce", load_blogs(PROFILE_BRUCE, PROFILE_DIRECTORY)))
        self.document.make_friend(u"bruce")
        # write file
        self.assertEquals(self.document.get_files()[REPO][abspath("data")]._shared, False)
        self.document.save()
        # check content
        self.assertEquals(self.document.get_files()[REPO][abspath("data")]._shared, False)
        self._assertContent(self.document)

    def test_unicode(self):
        # blog
        unicode_blog = Blogs(PROFILE_UNICODE, PROFILE_DIRECTORY)
        unicode_blog.add_blog(u"Enchanté", PROFILE_UNICODE)
        unicode_blog.save()
        # doc
        unicode_doc = FileDocument(PROFILE_UNICODE, PROFILE_DIRECTORY)
        # write data
        unicode_doc.set_title(u"Mr")
        unicode_doc.set_firstname(u"Zoé")
        unicode_doc.set_lastname(u"Bréton")
        unicode_doc.set_photo(QUESTION_MARK())
        unicode_doc.set_email(u"manu@ft.com")
        unicode_doc.load_defaults()
        unicode_doc.add_custom_attributes((u"été", u"chôô"))
        unicode_doc.remove_custom_attributes(u'Sport')
        # save
        unicode_doc.save()
        # check content
        blog = load_blogs(PROFILE_UNICODE, PROFILE_DIRECTORY)
        self.assertEquals(blog.blogs[0].text, u"Enchanté")
        doc = FileDocument(PROFILE_UNICODE, PROFILE_DIRECTORY)
        doc.load()
        self.assertEquals(u"Mr", doc.get_title())
        self.assertEquals(u"Zoé", doc.get_firstname())
        self.assertEquals(u"Bréton", doc.get_lastname())
        self.assertEquals(QUESTION_MARK(), doc.get_photo())
        self.assertEquals(u"manu@ft.com", doc.get_email())
        self.assertEquals({'City': u'', 'été': u'chôô', 'Country': u'',
                           'Favourite Book': u'',
                           'Favourite Movie': u'', 'Studies': u''},
                          doc.get_custom_attributes())

    def test_load(self):
        self.document.load()
        self._assertContent(self.document)

    def test_import(self):
        self.document.load()
        new_doc = CacheDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        new_doc.import_document(self.document)
        self._assertContent(new_doc)

    def test_save_and_load(self):
        self.document.load()
        self.document.share_file((REPO+"/data/subdir1/TOtO.txt", True))
        sav_doc = FileDocument(PROFILE_TATA, PROFILE_DIRECTORY)
        sav_doc.import_document(self.document)
        sav_doc.save()
        new_doc = FileDocument(PROFILE_TATA, PROFILE_DIRECTORY)
        new_doc.load()
        container = new_doc.get_container(REPO+"/data/subdir1")
        self.assert_(dict.has_key(container, "TOtO.txt"))

    def test_load_and_save(self):
        self.document.load()
        new_doc = CacheDocument(PROFILE_TATA, PROFILE_DIRECTORY)
        new_doc.import_document(self.document)
        new_doc.del_file(REPO)
        self.assertEquals(new_doc.get_files(), {})
        new_doc.add_file(REPO+"/data/profiles")
        new_doc.add_file(REPO+"/data/subdir1")
        self.assertEquals(new_doc.get_files()[REPO+"/data/profiles"]._shared, True)
        self.assert_(new_doc.get_files()[REPO+"/data/subdir1"] != None)
        new_doc.save()
        check_doc = FileDocument(PROFILE_TATA, PROFILE_DIRECTORY)
        check_doc.load()
        self.assertEquals(check_doc.get_files()[REPO+"/data/profiles"]._shared, True)
        self.assert_(check_doc.get_files()[REPO+"/data/subdir1"] != None)
        
        
    def test_default(self):
        document = FileDocument(u"dummy", PROFILE_DIRECTORY)
        self.assertEquals(u"", document.get_title())
        self.assertEquals(u"Name", document.get_firstname())
        self.assertEquals(u"Lastname", document.get_lastname())
        self.assertEquals(u'/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/question_mark.gif',
                          document.get_photo())
        self.assertEquals(u"email", document.get_email())
        self.assertEquals({},
                          document.get_custom_attributes())
        # assert correct sharing
        self.assertEquals([], document.get_shared(REPO))
        self.assertEquals({}, document.get_files())
        # peers
        self.assertEquals({}, document.get_peers())
        # load
        document.load()
        self.assertEquals({'City': u'', 'Country': u'',
                           'Favourite Book': u'', 'Favourite Movie': u'',
                           'Sport': u'', 'Studies': u''},
                          document.get_custom_attributes())
        
    def test_view(self):
        self.document.load()
        self.assertEquals(self.document.get_title(), "Mr")
        self.assertEquals(self.document.get_firstname(), "manu")
        self.assertEquals(self.document.get_lastname(), "breton")
        self.assertEquals(self.document.get_photo(), QUESTION_MARK())
        self.assertEquals(self.document.get_email(), "manu@ft.com")
        self.assertEquals(self.document.get_custom_attributes(), {'City': u'', 'Studies': u'',
                                                            'color': u'blue', 'Country': u'',
                                                            'Favourite Book': u'', 'Favourite Movie': u'',
                                                            'homepage': u'manu.com'})
        self.assertEquals(str(self.document.get_files()),
                          "{'/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests': {Dc:tests(?Y,'none',#4) : [{Dc:data(?-,'none',#4) : [Fc:.path(?-,'none'), {Dc:profiles(?-,'none',#0) : []}, {Dc:subdir1(?Y,'none',#3) : [Fc:date.doc(?-,'none'), Fc:TOtO.txt(?Y,'none'), {Dc:subsubdir(?-,'none',#2) : [Fc:null(?Y,'empty'), Fc:dummy.txt(?Y,'empty')]}, {Dc:.svn(?-,'none',#0) : []}]}, Fc:routage(?Y,'none'), {Dc:emptydir(?Y,'none',#0) : []}, {Dc:.svn(?-,'none',#0) : []}, Fc:date.txt(?-,'tagos')]}]}}")
        self.assertEquals(str(self.document.get_peers()),
                          "{u'bruce': bruce (%s)}"% PeerDescriptor.FRIEND)
        
if __name__ == '__main__':
    unittest.main()
