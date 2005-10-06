#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# pylint: disable-msg=W0131,C0301,C0103
# Missing docstring, Line too long, Invalid name
# -*- coding:ISO-8859-1 -*-
"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

__revision__ = "$Id$"

import unittest
import os.path
from os.path import abspath
from solipsis.services.profile import QUESTION_MARK
from solipsis.services.profile.prefs import get_prefs, set_prefs
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.file_document import FileDocument
from solipsis.services.profile.cache_document import CacheDocument
from solipsis.services.profile.tests import TEST_DIR,  \
     PROFILE_DIR, PROFILE_TEST, PROFILE_BRUCE, \
     write_test_profile

class FileTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        write_test_profile()
        # load profile
        peer_desc = PeerDescriptor(PROFILE_TEST)
        peer_desc.load(directory=PROFILE_DIR)
        self.document = peer_desc.document

    def _assertContent(self, doc):
        """check validity of content"""
        self.assertEquals(u"atao", doc.get_pseudo())
        self.assertEquals(u"Mr", doc.get_title())
        self.assertEquals(u"manu", doc.get_firstname())
        self.assertEquals(u"breton", doc.get_lastname())
        self.assertEquals(QUESTION_MARK(), doc.get_photo())
        self.assertEquals(u"manu@ft.com", doc.get_email())
        self.assertEquals({'City': u'', 'color': u'blue', 'Country': u'',
                           'Favourite Book': u'', 'homepage': u'manu.com',
                           'Favourite Movie': u'', 'Studies': u''},
                          doc.get_custom_attributes())
        # assert correct file structure
        files = doc.get_files()
        self.assertEquals(files.has_key(TEST_DIR), True)
        self.assertEquals(files[TEST_DIR][os.sep.join([abspath("data"), "date.txt"])]._tag, "tagos")
        self.assertEquals(files[TEST_DIR][abspath("data")]._shared, False)
        self.assertEquals(files[TEST_DIR][os.sep.join([abspath("data"), "routage"])]._shared, True)
        self.assertEquals(files[TEST_DIR][os.sep.join([abspath("data"), "emptydir"])]._shared, True)
        self.assertEquals(files[TEST_DIR][os.sep.join([abspath("data"), "subdir1"])]._shared, True)
        self.assertEquals(files[TEST_DIR][os.sep.join([abspath("data"), "subdir1", ""])]._shared, True)
        self.assertEquals(files[TEST_DIR][os.sep.join([abspath("data"), "subdir1", "subsubdir"])]._shared, False)
        self.assertEquals(files[TEST_DIR][os.sep.join([abspath("data"), "subdir1", "subsubdir", "null"])]._shared, True)
        self.assertEquals(files[TEST_DIR][os.sep.join([abspath("data"), "subdir1", "subsubdir", "dummy.txt"])]._shared, True)
        self.assertEquals(files[TEST_DIR].has_key(os.sep.join([abspath("data"), "subdir1", "subsubdir", "default.solipsis"])), False)
        # peers
        peers = doc.get_peers()
        self.assertEquals(peers.has_key(PROFILE_BRUCE), True)
        self.assertEquals(peers[PROFILE_BRUCE].state, PeerDescriptor.FRIEND)
        self.assertEquals(peers[PROFILE_BRUCE].connected, False)

    def test_save_and_load(self):
        self._assertContent(self.document)

    def test_import(self):
        # file -> cache
        new_doc = CacheDocument()
        new_doc.import_document(self.document)
        self._assertContent(new_doc)
        # cache -> cache
        cache_doc = CacheDocument()
        cache_doc.import_document(new_doc)
        self._assertContent(cache_doc)
        # cache -> file
        file_doc = FileDocument()
        file_doc.import_document(cache_doc)
        self._assertContent(file_doc)
        # file -> file
        other_doc = FileDocument()
        other_doc.import_document(file_doc)
        self._assertContent(other_doc)
        
    def test_default(self):
        document = FileDocument()
        self.assertEquals(u"", document.get_title())
        self.assertEquals(u"Name", document.get_firstname())
        self.assertEquals(u"Lastname", document.get_lastname())
        self.assertEquals(QUESTION_MARK(),
                          document.get_photo())
        self.assertEquals(u"email", document.get_email())
        self.assertEquals({},
                          document.get_custom_attributes())
        # assert correct sharing
        self.assertEquals({}, document.get_shared_files())
        self.assertEquals({}, document.get_files())
        # peers
        self.assertEquals({}, document.get_peers())
        # load
        document.load_defaults()
        self.assertEquals({'City': u'', 'Country': u'',
                           'Favourite Book': u'', 'Favourite Movie': u'',
                           'Sport': u'', 'Studies': u''},
                          document.get_custom_attributes())
        
    def test_view(self):
        self.assertEquals(self.document.get_title(), "Mr")
        self.assertEquals(self.document.get_firstname(), "manu")
        self.assertEquals(self.document.get_lastname(), "breton")
        self.assertEquals(self.document.get_photo(), QUESTION_MARK())
        self.assertEquals(self.document.get_email(), "manu@ft.com")
        self.assertEquals(self.document.get_custom_attributes(),
                          {'City': u'', 'Studies': u'',
                           'color': u'blue', 'Country': u'',
                           'Favourite Book': u'', 'Favourite Movie': u'',
                           'homepage': u'manu.com'})
        files = [file_container.name for file_container
                 in self.document.get_files()[TEST_DIR].flat()]
        files.sort()
        self.assertEquals(files, ['TOtO.txt', 'data', 'date.doc', 'date.txt',
                                  'dummy.txt', 'emptydir', 'null', 'routage',
                                  'subdir1', 'subsubdir'])
        self.assertEquals(self.document.get_peers()[PROFILE_BRUCE].state,
                          PeerDescriptor.FRIEND)
        
if __name__ == '__main__':
    unittest.main()
