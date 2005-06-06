"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
import time
from os.path import abspath
from solipsis.services.profile.document import \
      AbstractDocument, CacheDocument, FileDocument
from solipsis.services.profile.data import DEFAULT_TAG, PeerDescriptor

REPO = u"/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/tests"

class DocumentTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.documents = [CacheDocument(), FileDocument()]
        for document in self.documents:
            document.add_repository(REPO)
        self.abstract_doc = AbstractDocument()
        self.abstract_doc.add_repository(REPO)

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
    
    def test_pseudo(self):
        """pseudo as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_pseudo)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_pseudo, "emb")
            self.assertRaises(TypeError, document.set_pseudo, [u"manu", u"emb"])
            document.set_pseudo(u"emb")
    
    def test_photo(self):
        """photo as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_photo)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_photo, "./dummy/dummy.jpg")
            document.set_photo(unittest.__file__)
        
    def test_email(self):
        """email as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_email)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_email, "manu@ft.com")
            self.assertRaises(TypeError, document.set_email, [u"manu@ft", ])
            document.set_email(u"manu@ft.com")
        
    def test_birthday(self):
        """birthday as datetime"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_birthday)
        for document in self.documents:
            document.set_birthday(u"12/01/2005")
            birthday = document.get_birthday()
            document.set_birthday("12 jan 2005")
            self.assertEquals(document.get_birthday(), birthday)
            document.set_birthday("2005/01/12")
            self.assertEquals(document.get_birthday(), birthday)
            document.set_birthday("12-01-2005")
            self.assertEquals(document.get_birthday(), birthday)
            document.set_birthday("12012005")
            self.assertEquals(document.get_birthday(), birthday)
            document.set_birthday("12/01")
            self.assertEquals(document.get_birthday(), birthday)
            
    def test_language(self):
        """language as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_language)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_language, "fr")
            self.assertRaises(TypeError, document.set_language, [u"fr", u"sp"])
            document.set_language(u"fr")
        
    def test_address(self):
        """address as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_address)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_address, "12 rue V Hugo")
            self.assertRaises(TypeError, document.set_address, [u"12",
                                                                u"rue V Hugo"])
            document.set_address(u"12 rue V Hugo")
        
    def test_postcode(self):
        """postcode as int convertable"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_postcode)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_postcode, "34.000")
            self.assertRaises(TypeError, document.set_postcode, "34 000")
            self.assertRaises(TypeError, document.set_postcode, "Herault")
            self.assertRaises(TypeError, document.set_birthday, ["34", ])
            document.set_postcode(u"34000")
            document.set_postcode("34000")
        
    def test_city(self):
        """city as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_city)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_city, "Paris")
            self.assertRaises(TypeError, document.set_city, [u"Paris", ])
            document.set_city(u"Paris")
        
    def test_country(self):
        """country as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_country)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_country, "France")
            self.assertRaises(TypeError, document.set_country, [u"France", ])
            document.set_country(u"France")
        
    def test_description(self):
        """description as unicode"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_description)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_description, "anything")
            self.assertRaises(TypeError, document.set_description, [u"anything", ])
            document.set_description(u"anything")
        
    # CUSTOM TAB
    def test_hobbies(self):
        """hobbies as unicode (multiple lines)"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_hobbies)
        for document in self.documents:
            self.assertRaises(TypeError, document.set_hobbies,
                              "blabla\nbla bla bla\n")
            self.assertRaises(TypeError, document.set_hobbies,
                              u"blabla\nbla bla bla\n")
            document.set_hobbies([u"blabla", u"bla bla bla", u""])
        
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
            document.add((abspath(u"data")))
            document.share_file((abspath(u"data"), True))
            self.assertEquals(document.get_container(abspath(u"data"))._shared, True)
            document.reset_files()
            self.assertEquals(document.get_files(), {})
        
    def test_repository(self):
        """repository valid path"""
        for document in self.documents:
            self.assertRaises(TypeError, document.add, abspath("data/dummy"))
            document.add(abspath(u"data"))
            document.remove(abspath(u"data"))
        
    def test_share_dir(self):
        """share dir giving unicode name"""
        for document in self.documents:
            document.add((abspath(u"data")))
            self.assertRaises(TypeError, document.share_dirs, "data, True")
            self.assertRaises(TypeError, document.share_dirs, ("data", ))
            self.assertRaises(TypeError, document.share_dirs, ("data", True))
            self.assertRaises(TypeError, document.share_dirs, (abspath(u"data"), True))
            document.share_dirs(([abspath(u"data")], True))
            document.share_dirs([[abspath(u"data")], True])
        
    def test_share_files(self):
        """share files giving root & unicode names"""
        for document in self.documents:
            document.add((abspath(u"data")))
            self.assertRaises(TypeError, document.share_files,
                              "data, ['.path', 'routage'], True")
            self.assertRaises(TypeError, document.share_files,
                              ("data", "['.path', 'routage'], True"))
            self.assertRaises(TypeError, document.share_files,
                              ("data", "['.path', 'routage']", "True"))
            self.assertRaises(TypeError, document.share_files,
                              (u"data", "['.path', 'routage']", True))
            self.assertRaises(TypeError, document.share_files,
                              ("data", ['.path', 'routage'], True))
            document.share_files((abspath(u"data"), ['.path', 'routage'], True))
            document.share_files([abspath(u"data"), ['.path', 'routage'], True])
        
    def test_tag_file(self):
        """tag files giving root & unicode names"""
        for document in self.documents:
            document.add((abspath(u"data")))
            self.assertRaises(TypeError, document.tag_files,
                              "data, ['.path', 'routage'], tag desc")
            self.assertRaises(TypeError, document.tag_files,
                              ("data", "['.path', 'routage'], tag desc"))
            self.assertRaises(TypeError, document.tag_files,
                              ("data", "['.path', 'routage']", "tag desc"))
            self.assertRaises(TypeError, document.tag_files,
                              ("data", ['.path', 'routage'], "tag desc"))
            self.assertRaises(TypeError, document.tag_files,
                              (u"data", "['.path', 'routage']", "tag desc"))
            self.assertRaises(TypeError, document.tag_files,
                              (u"data", ['.path', 'routage'], "tag desc"))
            document.tag_files((abspath(u"data"), ['.path', 'routage'], u"tag desc"))
            document.tag_files([abspath(u"data"), ['.path', 'routage'], u"tag desc"])
        
    def test_add_file(self):
        """expand dir giving unicode name"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_files)
        for document in self.documents:
            document.add((abspath(u"data")))
            self.assertRaises(TypeError, document.expand_dir, "data/dummy")
            self.assertRaises(TypeError, document.expand_dir, "data")
            document.expand_dir((abspath(u"data")))

    def test_get_container(self):
        """retreive correct contaier"""
        for document in self.documents:
            document.tag_files((abspath(u"data/profiles"),
                               ["bruce.prf", ".svn"], u"first"))
            document.share_files((abspath(u"data/profiles"),
                                  ["bruce.prf", "demi.prf"], True))
            # check sharing state
            self.assertEquals(document.get_container(
                abspath(u"data/profiles/bruce.prf"))._shared, True)
            self.assertEquals(document.get_container(
                abspath(u"data/profiles/demi.prf"))._shared, True)
            self.assertEquals(document.get_container(
                abspath(u"data/profiles/.svn"))._shared, False)
            # check tag
            self.assertEquals(document.get_container(
                abspath(u"data/profiles/bruce.prf"))._tag, u"first")
            self.assertEquals(document.get_container(
                abspath(u"data/profiles/demi.prf"))._tag, DEFAULT_TAG)
            self.assertEquals(document.get_container(
                abspath(u"data/profiles/.svn"))._tag, u"first")

    def test_multiple_repos(self):
        """coherency when several repos in use"""
        document = CacheDocument()
        # create 2 repos
        document.add_repository(REPO + "/data/profiles")
        document.tag_files((REPO + "/data/profiles", ["bruce.prf", ".svn"], u"first"))
        document.share_files((REPO + "/data/profiles", ["bruce.prf", "demi.prf"], True))
        document.add_repository(REPO + "/data/subdir1")
        document.tag_files((REPO + "/data/subdir1", ["date.doc", ".svn"], u"second"))
        document.share_files((REPO + "/data/subdir1", ["date.doc", "subsubdir"], True))
        # check sharing state
        self.assertEquals(document.get_container(
            abspath("data/profiles/bruce.prf"))._shared, True)
        self.assertEquals(document.get_container(
            abspath("data/profiles/demi.prf"))._shared, True)
        self.assertEquals(document.get_container(
            abspath("data/profiles/.svn"))._shared, False)
        self.assertEquals(document.get_container(
            abspath("data/subdir1/date.doc"))._shared, True)
        self.assertEquals(document.get_container(
            abspath("data/subdir1/subsubdir"))._shared, True)
        self.assertEquals(document.get_container(
            abspath("data/subdir1/.svn"))._shared, False)
        # check tag
        self.assertRaises(ValueError, document.add_repository, REPO + "/data/subdir1/subsubdir")
        self.assertRaises(ValueError, document.add_repository, REPO + "/data")
            
    # OTHERS TAB
    def test_reset_peers(self):
        """reset peers"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_peers)
        self.assertRaises(NotImplementedError, self.abstract_doc.reset_peers)
        for document in self.documents:
            document.add_peer(u"nico")
            self.assertEquals(document.has_peer(u"nico"), True)
            document.reset_peers()
            self.assertEquals(document.has_peer(u"nico"), False)
            self.assertEquals(document.get_peers(), {})
            
    def test_adding_peer(self):
        self.assertRaises(NotImplementedError, self.abstract_doc.add_peer, "nico")
        """add peer"""
        for document in self.documents:
            self.assertEquals(document.has_peer(u"nico"), False)
            document.add_peer(u"nico")
            self.assert_(document.has_peer(u"nico"))
            
    def test_getting_peer(self):
        """get peer"""
        self.assertRaises(NotImplementedError, self.abstract_doc.get_peer, "nico")
        for document in self.documents:
            document.add_peer(u"nico")
            peer_desc = document.get_peer(u"nico")
            self.assertEquals(peer_desc.peer_id, u"nico")
            
    def test_removing_peer(self):
        """remove peer"""
        self.assertRaises(NotImplementedError, self.abstract_doc.remove_peer, "nico")
        for document in self.documents:
            document.add_peer(u"nico")
            self.assertEquals(document.has_peer(u"nico"), True)
            document.remove_peer(u"nico")
            self.assertEquals(document.has_peer(u"nico"), False)
        
    def test_filling_data(self):
        """fill data"""
        for document in self.documents:
            self.assertRaises(TypeError, document.fill_data,
                              (u"pseudo", u"tag description"))
            self.assertEquals(document.has_peer(u"emb"), False)
            abstract_doc = AbstractDocument()
            document.fill_data((u"emb", abstract_doc))
            self.assertEquals(document.has_peer(u"emb"), True)
            document.fill_data((u"emb", CacheDocument()))
            document.fill_data((u"emb", FileDocument()))
            self.assert_(document.get_peer(u"emb").document)
    
    def test_peers_status(self):
        """change status"""
        for document in self.documents:
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
