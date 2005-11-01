#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# pylint: disable-msg=W0131,C0301,C0103
# Missing docstring, Line too long, Invalid name
"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

__revision__ = "$Id$"

import unittest
import os, os.path
from ConfigParser import ConfigParser
from os.path import abspath

from solipsis.services.profile import ENCODING, force_unicode
from solipsis.services.profile.prefs import get_prefs, set_prefs
from solipsis.services.profile.document import CustomConfigParser, AbstractDocument
from solipsis.services.profile.file_document import FileDocument
from solipsis.services.profile.cache_document import CacheDocument
from solipsis.services.profile.path_containers import DEFAULT_TAG, FileContainer, ContainerException
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.tests import PROFILE_DIR, PROFILE_TEST, PROFILE_BRUCE, \
     TEST_DIR, TEST_DIR
from solipsis.services.profile.tests import get_bruce_profile, write_test_profile

def tag_files(document, dir_path, file_paths, tag):
    for file_path in file_paths:
        document.tag_file(os.path.join(dir_path, file_path), tag)

class DocumentTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        write_test_profile()
        self.documents = [CacheDocument(),
                          FileDocument()]
        for document in self.documents:
            document.add_repository(TEST_DIR)
        self.abstract_doc = AbstractDocument()
        self.abstract_doc.add_repository(TEST_DIR)

    def test_config_parser(self):
        writer = CustomConfigParser(ENCODING)
        writer.add_section("TEST")
        writer.set("TEST", "Windows:path", "not a valid linux:path!")
        writer.write(open(os.path.join("generated", "config.test"), "w"))
        # standard reader
        reader = ConfigParser()
        reader.readfp(open(os.path.join("generated", "config.test")))
        self.assert_(reader.has_section("TEST"))
        self.assert_(reader.has_option("TEST", "Windows"))
        self.assertEquals(reader.get("TEST", "Windows"), "path = not a valid linux:path!")
        # custom reader
        reader = CustomConfigParser(ENCODING)
        reader.readfp(open(os.path.join("generated", "config.test")))
        self.assert_(reader.has_section("TEST"))
        self.assert_(reader.has_option("TEST", "Windows:path"))
        self.assertEquals(reader.get("TEST", "Windows:path"), "not a valid linux:path!")

    # PERSONAL TAB
    def test_pseudo(self):
        """pseudo as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_pseudo)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_pseudo, "atao")
            self.assertRaises(TypeError, document.set_pseudo, [u"atao", ])
            document.set_pseudo(u"atao")
            
    def test_title(self):
        """title as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_title)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_title, "Mr")
            self.assertRaises(TypeError, document.set_title, [u"Mr", ])
            document.set_title(u"Mr")
        
    def test_firstname(self):
        """firstname as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_firstname)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_firstname, "manu")
            self.assertRaises(TypeError, document.set_firstname, [u"manu", ])
            document.set_firstname(u"manu")
        
    def test_lastname(self):
        """lastname as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_lastname)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_lastname, "breton")
            self.assertRaises(TypeError, document.set_lastname, [u"breton", ])
            document.set_lastname(u"breton")
    
    def test_photo(self):
        """photo as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_photo)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_photo, "./dummy/dummy.jpg")
            document.set_photo(force_unicode(unittest.__file__))
        
    def test_email(self):
        """email as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_email)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_email, "manu@ft.com")
            self.assertRaises(TypeError, document.set_email, [u"manu@ft", ])
            document.set_email(u"manu@ft.com")
        
    # CUSTOM TAB
    def test_custom_attributes(self):
        """custom_attributes as pair of key", "unicode-value"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_custom_attributes)
        for document in self.documents:
            self.assertRaises(TypeError, document.add_custom_attributes,
                              "homepage", "manu.com")
            document.add_custom_attributes(u"homepage", u"manu.com")
            self.assertRaises(TypeError, document.remove_custom_attributes,
                              "homepage")
            document.remove_custom_attributes(u"homepage")
        
    # FILE TAB
    def test_reset_files(self):
        """reset files"""
        for document in self.documents:
            document.share_file(abspath("data"), True)
            self.assertEquals(document.get_container(abspath("data"))._shared, True)
            document.reset_files()
            self.assertEquals(document.get_files(), {})
        
    def test_recursive_share(self):
        """share dir giving unicode name"""
        for document in self.documents:
            self.assertRaises(TypeError, document.recursive_share, abspath(u"data"), True)
            self.assertEquals(1, len(document.recursive_share("data", True)))
            self.assertEquals([], document.recursive_share(abspath("data"), True))
        
    def test_share_files(self):
        """share files giving root & unicode names"""
        for document in self.documents:
            document.share_files(abspath("data"), [".path", "routage"], True)
        
    def test_set_container(self):
        path = os.path.join(abspath("data"), "date.txt")
        container = FileContainer(path,
                                  share=True,
                                  tag=u"Shared by set_container")
        for document in self.documents:
            self.assertEquals(document.get_container(path)._shared, False)
            self.assertEquals(document.get_container(path)._tag, DEFAULT_TAG)
            document.set_container(container)
            self.assertEquals(document.get_container(path)._shared, True)
            self.assertEquals(document.get_container(path)._tag, u"Shared by set_container")
        
    def test_add_repository(self):
        """expand dir giving unicode name"""
        for document in self.documents:
            self.assertRaises(TypeError, document.expand_dir, os.path.join(u"data", "dummy"))
            self.assertRaises(TypeError, document.expand_dir, u"data")
            document.expand_dir(abspath("data"))

    def test_get_container(self):
        for document in self.documents:
            tag_files(document, abspath(os.path.join("data", "profiles")),
                               ["bruce.prf", ".svn"], u"first")
            document.share_files(abspath(os.path.join("data", "profiles")),
                                  ["bruce.prf", "demi.prf"], True)
            # check sharing state
            self.assertEquals(document.get_container(
                abspath(os.sep.join(["data", "profiles", "bruce.prf"])))._shared, True)
            self.assertEquals(document.get_container(
                abspath(os.sep.join(["data", "profiles", "demi.prf"])))._shared, True)
            self.assertEquals(document.get_container(
                abspath(os.sep.join(["data", "profiles", ".svn"])))._shared, False)
            # check tag
            self.assertEquals(document.get_container(
                abspath(os.sep.join(["data", "profiles", "bruce.prf"])))._tag, u"first")
            self.assertEquals(document.get_container(
                abspath(os.sep.join(["data", "profiles", "demi.prf"])))._tag, DEFAULT_TAG)
            self.assertEquals(document.get_container(
                abspath(os.sep.join(["data", "profiles", ".svn"])))._tag, u"first")

    def test_get_shared_files(self):
        document = CacheDocument()
        document.add_repository(TEST_DIR)
        document.expand_dir(abspath("data"))
        document.expand_dir(abspath(os.path.join("data", "subdir1")))
        document.share_files(abspath("data"),
                              [os.sep.join([TEST_DIR, "data", ".path"]),
                               os.sep.join([TEST_DIR, "data", ".svn"]),
                               os.sep.join([TEST_DIR, "data", "date.txt"]),
                               os.sep.join([TEST_DIR, "data", "emptydir"]),
                               os.sep.join([TEST_DIR, "data", "profiles"]),
                               os.sep.join([TEST_DIR, "data", "subdir1", ".svn"]),
                               os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir"])],
                              False)
        document.share_files(abspath("data"),
                              [os.sep.join([TEST_DIR, "data"]),
                               os.sep.join([TEST_DIR, "data", ".path"]),
                               os.sep.join([TEST_DIR, "data", "date.txt"]),
                               os.sep.join([TEST_DIR, "data", "routage"]),
                               os.sep.join([TEST_DIR, "data", "subdir1"]),
                               os.sep.join([TEST_DIR, "data", "subdir1", "TOtO.txt"]),
                               os.sep.join([TEST_DIR, "data", "subdir1", "date.doc"])],
                              True)
        shared_files = [file_container.get_path() for file_container
                        in document.get_shared_files()[TEST_DIR]]
        shared_files.sort()
        self.assertEquals(shared_files, [os.sep.join([TEST_DIR, "data", ".path"]),
                                         os.sep.join([TEST_DIR, "data", "02_b_1280x1024.jpg"]),
                                         os.sep.join([TEST_DIR, "data", "Python-2.3.5.zip"]),
                                         os.sep.join([TEST_DIR, "data", "arc en ciel 6.gif"]),
                                         os.sep.join([TEST_DIR, "data", "date.txt"]),
                                         os.sep.join([TEST_DIR, "data", "pywin32-203.win32-py2.3.exe"]),
                                         os.sep.join([TEST_DIR, "data", "routage"]),
                                         os.sep.join([TEST_DIR, "data", "subdir1", "TOtO.txt"]),
                                         os.sep.join([TEST_DIR, "data", "subdir1", "date.doc"])])
        
    def test_multiple_repos(self):
        """coherency when several repos in use"""
        document = CacheDocument()
        # create 2 repos
        document.add_repository(os.sep.join([TEST_DIR, "data", "profiles"]))
        tag_files(document, os.sep.join([TEST_DIR, "data", "profiles"]), ["bruce.prf", ".svn"], u"first")
        document.share_files(os.sep.join([TEST_DIR, "data", "profiles"]), ["bruce.prf", "demi.prf"], True)
        document.add_repository(os.sep.join([TEST_DIR, "data", "subdir1"]))
        tag_files(document, os.sep.join([TEST_DIR, "data", "subdir1"]), ["date.doc", ".svn"], u"second")
        document.share_files(os.sep.join([TEST_DIR, "data", "subdir1"]), ["date.doc", "subsubdir"], True)
        # check sharing state
        self.assertEquals(document.get_container(
            abspath(os.sep.join(["data", "profiles", "bruce.prf"])))._shared, True)
        self.assertEquals(document.get_container(
            abspath(os.sep.join(["data", "profiles", "demi.prf"])))._shared, True)
        self.assertEquals(document.get_container(
            abspath(os.sep.join(["data", "profiles", ".svn"])))._shared, False)
        self.assertEquals(document.get_container(
            abspath(os.sep.join(["data", "subdir1", "date.doc"])))._shared, True)
        self.assertEquals(document.get_container(
            abspath(os.sep.join(["data", "subdir1", "subsubdir"])))._shared, True)
        self.assertEquals(document.get_container(
            abspath(os.sep.join(["data", "subdir1", ".svn"])))._shared, False)
        # check tag
        self.assertRaises(ContainerException, document.add_repository, os.sep.join([TEST_DIR, "data", "subdir1", "subsubdir"]))
        self.assertRaises(ContainerException, document.add_repository, os.sep.join([TEST_DIR, "data"]))
            
    # OTHERS TAB
    def test_reset_peers(self):
        """reset peers"""
        document = self.documents[0]
        document.set_peer(u"nico", PeerDescriptor(PROFILE_TEST))
        self.assertEquals(document.has_peer(u"nico"), True)
        document.reset_peers()
        self.assertEquals(document.has_peer(u"nico"), False)
        self.assertEquals(document.get_peers(), {})
            
    def test_getting_peer(self):
        """get peer"""
        for document in self.documents:
            document.set_peer(PROFILE_BRUCE, PeerDescriptor(PROFILE_BRUCE))
            peer_desc = self.documents[0].get_peer(PROFILE_BRUCE)
            self.assertEquals(peer_desc.node_id, PROFILE_BRUCE)
            
    def test_removing_peer(self):
        """remove peer"""
        for document in self.documents:
            document.set_peer(u"nico", PeerDescriptor(PROFILE_TEST))
            self.assertEquals(document.has_peer(u"nico"), True)
            document.remove_peer(u"nico")
            self.assertEquals(document.has_peer(u"nico"), False)
        
    def test_filling(self):
        """fill data"""
        for document in self.documents:
            self.assertEquals(document.has_peer(u"emb"), False)
            bruce = get_bruce_profile()
            document.fill_data(u"emb", bruce.document)
            document.fill_blog(u"emb", bruce.blog)
    
    def test_peers_status(self):
        """change status"""
        bruce = get_bruce_profile()
        for document in self.documents:
            self.assertRaises(AssertionError, document.make_friend, bruce.node_id)
            self.assertRaises(AssertionError, document.blacklist_peer, bruce.node_id)
            self.assertRaises(AssertionError, document.unmark_peer, bruce.node_id)
            document.set_peer(bruce.node_id, bruce)
            # friend
            document.make_friend(bruce.node_id)
            self.assertEquals(PeerDescriptor.FRIEND,
                              document.get_peer(bruce.node_id).state)
            # blacklist
            document.blacklist_peer(bruce.node_id)
            self.assertEquals(PeerDescriptor.BLACKLISTED,
                              document.get_peer(bruce.node_id).state)
            # anonmyous
            document.unmark_peer(bruce.node_id)
            self.assertEquals(PeerDescriptor.ANONYMOUS,
                              document.get_peer(bruce.node_id).state)

if __name__ == "__main__":
    unittest.main()
