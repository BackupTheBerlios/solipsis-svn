"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
from ConfigParser import ConfigParser
from os.path import abspath
from pprint import pprint

from solipsis.services.profile.document import CustomConfigParser, AbstractDocument
from solipsis.services.profile.file_document import FileDocument
from solipsis.services.profile.cache_document import CacheDocument
from solipsis.services.profile.data import DEFAULT_TAG, PeerDescriptor
from solipsis.services.profile.tests import PROFILE_DIRECTORY, PROFILE_TEST, \
     REPO, PSEUDO, TEST_DIR
from solipsis.services.profile import ENCODING

class DocumentTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.documents = [CacheDocument(PROFILE_TEST, PROFILE_DIRECTORY),
                          FileDocument(PROFILE_TEST, PROFILE_DIRECTORY)]
        for document in self.documents:
            document.add_file(REPO)
        self.abstract_doc = AbstractDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        self.abstract_doc.add_file(REPO)

    def test_config_parser(self):
        writer = CustomConfigParser(ENCODING)
        writer.add_section('TEST')
        writer.set('TEST', "Windows:path", "not a valid linux:path!")
        writer.write(open("generated/config.test", "w"))
        # standard reader
        reader = ConfigParser()
        reader.readfp(open("generated/config.test"))
        self.assert_(reader.has_section('TEST'))
        self.assert_(reader.has_option('TEST', "Windows"))
        self.assertEquals(reader.get('TEST', "Windows"), "path = not a valid linux:path!")
        # custom reader
        reader = CustomConfigParser(ENCODING)
        reader.readfp(open("generated/config.test"))
        self.assert_(reader.has_section('TEST'))
        self.assert_(reader.has_option('TEST', "Windows:path"))
        self.assertEquals(reader.get('TEST', "Windows:path"), "not a valid linux:path!")

    # PERSONAL TAB
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
            document.set_photo(unicode(unittest.__file__, ENCODING))
        
    def test_email(self):
        """email as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_email)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_email, "manu@ft.com")
            self.assertRaises(TypeError, document.set_email, [u"manu@ft", ])
            document.set_email(u"manu@ft.com")
        
    # CUSTOM TAB
    def test_custom_attributes(self):
        """custom_attributes as pair of key/unicode-value"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_custom_attributes)
        for document in self.documents:
            self.assertRaises(TypeError, document.add_custom_attributes,
                              "homepage: manu.com")
            self.assertRaises(TypeError, document.add_custom_attributes,
                              ("homepage", "manu.com", "yo"))
            self.assertRaises(TypeError, document.add_custom_attributes,
                              ("homepage", "manu.com"))
            document.add_custom_attributes((u"homepage", u"manu.com"))
            self.assertRaises(TypeError, document.remove_custom_attributes,
                              "homepage")
            document.remove_custom_attributes(u"homepage")
        
    # FILE TAB
    def test_reset_files(self):
        """reset files"""
        for document in self.documents:
            document.add((abspath("data")))
            document.share_file((abspath("data"), True))
            self.assertEquals(document.get_container(abspath("data"))._shared, True)
            document.reset_files()
            self.assertEquals(document.get_files(), {})
        
    def test_repository(self):
        """repository valid path"""
        for document in self.documents:
            self.assertRaises(TypeError, document.add, abspath(u"data/dummy"))
            document.add(abspath("data"))
            document.remove(abspath("data"))
        
    def test_recursive_share(self):
        """share dir giving unicode name"""
        for document in self.documents:
            document.add((abspath("data")))
            self.assertRaises(KeyError, document.recursive_share, ("data", True))
            self.assertRaises(TypeError, document.recursive_share, (abspath(u"data"), True))
            document.recursive_share((abspath("data"), True))
        
    def test_share_files(self):
        """share files giving root & unicode names"""
        for document in self.documents:
            document.add((abspath("data")))
            self.assertRaises(TypeError, document.share_files,
                              "data, ['.path', 'routage'], True")
            self.assertRaises(TypeError, document.share_files,
                              ("data", "['.path', 'routage'], True"))
            self.assertRaises(TypeError, document.share_files,
                              ("data", "['.path', 'routage']", "True"))
            self.assertRaises(TypeError, document.share_files,
                              ("data", "['.path', 'routage']", True))
            document.share_files((abspath("data"), ['.path', 'routage'], True))
            document.share_files([abspath("data"), ['.path', 'routage'], True])
        
    def test_tag_file(self):
        """tag files giving root & unicode names"""
        for document in self.documents:
            document.add((abspath("data")))
            self.assertRaises(TypeError, document.tag_files,
                              "data, ['.path', 'routage'], tag desc")
            self.assertRaises(TypeError, document.tag_files,
                              ("data", "['.path', 'routage'], tag desc"))
            self.assertRaises(TypeError, document.tag_files,
                              ("data", "['.path', 'routage']", "tag desc"))
            self.assertRaises(TypeError, document.tag_files,
                              ("data", ['.path', 'routage'], "tag desc"))
            self.assertRaises(TypeError, document.tag_files,
                              ("data", "['.path', 'routage']", "tag desc"))
            self.assertRaises(TypeError, document.tag_files,
                              ("data", ['.path', 'routage'], "tag desc"))
            document.tag_files((abspath("data"), ['.path', 'routage'], u"tag desc"))
            document.tag_files([abspath("data"), ['.path', 'routage'], u"tag desc"])
        
    def test_add_file(self):
        """expand dir giving unicode name"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_files)
        for document in self.documents:
            document.add((abspath("data")))
            self.assertRaises(TypeError, document.expand_dir, u"data/dummy")
            self.assertRaises(TypeError, document.expand_dir, u"data")
            document.expand_dir((abspath("data")))

    def test_get_container(self):
        for document in self.documents:
            document.tag_files((abspath("data/profiles"),
                               ["bruce.prf", ".svn"], u"first"))
            document.share_files((abspath("data/profiles"),
                                  ["bruce.prf", "demi.prf"], False))
            # check sharing state
            self.assertEquals(document.get_container(
                abspath("data/profiles/bruce.prf"))._shared, False)
            self.assertEquals(document.get_container(
                abspath("data/profiles/demi.prf"))._shared, False)
            self.assertEquals(document.get_container(
                abspath("data/profiles/.svn"))._shared, True)
            # check tag
            self.assertEquals(document.get_container(
                abspath("data/profiles/bruce.prf"))._tag, u"first")
            self.assertEquals(document.get_container(
                abspath("data/profiles/demi.prf"))._tag, DEFAULT_TAG)
            self.assertEquals(document.get_container(
                abspath("data/profiles/.svn"))._tag, u"first")

    def test_get_shared_files(self):
        document = CacheDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        document.add_file(REPO)
        document.expand_dir(abspath("data"))
        document.expand_dir(abspath("data/subdir1"))
        document.share_files((abspath("data"),
                              [REPO + '/data/.path',
                               REPO + '/data/.svn',
                               REPO + '/data/date.txt',
                               REPO + '/data/emptydir',
                               REPO + '/data/profiles',
                               REPO + '/data/subdir1/.svn',
                               REPO + '/data/subdir1/subsubdir'],
                              False))
        document.share_files((abspath("data"),
                              [REPO + '/data',
                               REPO + "/data/.path",
                               REPO + "/data/date.txt",
                               REPO + "/data/routage",
                               REPO + '/data/subdir1',
                               REPO + "/data/subdir1/TOtO.txt",
                               REPO + "/data/subdir1/date.doc"],
                              True))
        shared_files = [file_container.get_path() for file_container
                        in document.get_shared_files()[REPO]]
        shared_files.sort()
        self.assertEquals(shared_files, [REPO + "/data/.path",
                                         REPO + "/data/date.txt",
                                         REPO + "/data/routage",
                                         REPO + "/data/subdir1/TOtO.txt",
                                         REPO + "/data/subdir1/date.doc"])
        
    def test_multiple_repos(self):
        """coherency when several repos in use"""
        document = CacheDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        # create 2 repos
        document.add_file(REPO + "/data/profiles")
        document.tag_files((REPO + "/data/profiles", ["bruce.prf", ".svn"], u"first"))
        document.share_files((REPO + "/data/profiles", ["bruce.prf", "demi.prf"], False))
        document.add_file(REPO + "/data/subdir1")
        document.tag_files((REPO + "/data/subdir1", ["date.doc", ".svn"], u"second"))
        document.share_files((REPO + "/data/subdir1", ["date.doc", "subsubdir"], False))
        # check sharing state
        self.assertEquals(document.get_container(
            abspath("data/profiles/bruce.prf"))._shared, False)
        self.assertEquals(document.get_container(
            abspath("data/profiles/demi.prf"))._shared, False)
        self.assertEquals(document.get_container(
            abspath("data/profiles/.svn"))._shared, True)
        self.assertEquals(document.get_container(
            abspath("data/subdir1/date.doc"))._shared, False)
        self.assertEquals(document.get_container(
            abspath("data/subdir1/subsubdir"))._shared, False)
        self.assertEquals(document.get_container(
            abspath("data/subdir1/.svn"))._shared, True)
        # check tag
        self.assertRaises(ValueError, document.add_file, REPO + "/data/subdir1/subsubdir")
        self.assertRaises(ValueError, document.add_file, REPO + "/data")
            
    # OTHERS TAB
    def test_reset_peers(self):
        """reset peers"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_peers)
        self.assertRaises(NotImplementedError, self.abstract_doc.reset_peers)
        document = self.documents[0]
        document.set_peer((u"nico", PeerDescriptor(PSEUDO)))
        self.assertEquals(document.has_peer(u"nico"), True)
        document.reset_peers()
        self.assertEquals(document.has_peer(u"nico"), False)
        self.assertEquals(document.get_peers(), {})
            
    def test_getting_peer(self):
        """get peer"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_peer, "nico")
        for document in self.documents:
            document.set_peer((u"nico", PeerDescriptor(PSEUDO)))
            peer_desc = self.documents[0].get_peer(u"nico")
            self.assertEquals(peer_desc.pseudo, PSEUDO)
            
    def test_removing_peer(self):
        """remove peer"""
        self.assertRaises(NotImplementedError, self.abstract_doc.remove_peer, "nico")
        for document in self.documents:
            document.set_peer((u"nico", PeerDescriptor(PSEUDO)))
            self.assertEquals(document.has_peer(u"nico"), True)
            document.remove_peer(u"nico")
            self.assertEquals(document.has_peer(u"nico"), False)
        
    def test_filling_data(self):
        """fill data"""
        for document in self.documents:
            self.assertEquals(document.has_peer(u"emb"), False)
            file_doc = FileDocument(PROFILE_TEST, PROFILE_DIRECTORY)
            file_doc.load()
            document.fill_data((u"emb", file_doc))
    
    def test_peers_status(self):
        """change status"""
        for document in self.documents:
            self.assertRaises(AssertionError, document.make_friend, u"nico")
            self.assertRaises(AssertionError, document.blacklist_peer, u"nico")
            self.assertRaises(AssertionError, document.unmark_peer, u"nico")
            document.set_peer((u"nico", PeerDescriptor(PROFILE_TEST)))
            # friend
            document.make_friend(u"nico")
            self.assertEquals(PeerDescriptor.FRIEND,
                              document.get_peer(u"nico").state)
            # blacklist
            document.blacklist_peer(u"nico")
            self.assertEquals(PeerDescriptor.BLACKLISTED,
                              document.get_peer(u"nico").state)
            # anonmyous
            document.unmark_peer(u"nico")
            self.assertEquals(PeerDescriptor.ANONYMOUS,
                              document.get_peer(u"nico").state)

if __name__ == '__main__':
    unittest.main()
