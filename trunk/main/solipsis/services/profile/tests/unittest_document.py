"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
from solipsis.services.profile.document import PeerDescriptor, \
      AbstractDocument, CacheDocument, FileDocument


class ValidatorTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.documents = [CacheDocument(), FileDocument()]

    # PERSONAL TAB
    def test_title(self):
        """title as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_title, "Mr")
            self.assertRaises(TypeError, document.set_title, [u"Mr", ])
            document.set_title(u"Mr")
        
    def test_firstname(self):
        """firstname as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_firstname, "manu")
            self.assertRaises(TypeError, document.set_firstname, [u"manu", ])
            document.set_firstname(u"manu")
        
    def test_lastname(self):
        """lastname as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_lastname, "breton")
            self.assertRaises(TypeError, document.set_lastname, [u"breton", ])
            document.set_lastname(u"breton")
    
    def test_pseudo(self):
        """pseudo as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_pseudo, "emb")
            self.assertRaises(TypeError, document.set_pseudo, [u"manu", u"emb"])
            document.set_pseudo(u"emb")
    
    def test_photo(self):
        """photo as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_photo, "./dummy/dummy.jpg")
            document.set_photo(unittest.__file__)
        
    def test_email(self):
        """email as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_email, "manu@ft.com")
            self.assertRaises(TypeError, document.set_email, [u"manu@ft", ])
            document.set_email(u"manu@ft.com")
        
    def test_birthday(self):
        """birthday as DateTime convertable"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_birthday, "12 jan 2005")
            self.assertRaises(TypeError, document.set_birthday, "2005/01/12")
            self.assertRaises(TypeError, document.set_birthday, "12-01-2005")
            self.assertRaises(TypeError, document.set_birthday, "12012005")
            self.assertRaises(TypeError, document.set_birthday, "12/01")
            self.assertRaises(TypeError, document.set_birthday, ["12/01/05", ])
            document.set_birthday(u"12/01/2005")
            document.set_birthday("12/01/2005")
            
    def test_language(self):
        """language as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_language, "fr")
            self.assertRaises(TypeError, document.set_language, [u"fr", u"sp"])
            document.set_language(u"fr")
        
    def test_address(self):
        """address as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_address, "12 rue V Hugo")
            self.assertRaises(TypeError, document.set_address, [u"12",
                                                                u"rue V Hugo"])
            document.set_address(u"12 rue V Hugo")
        
    def test_postcode(self):
        """postcode as int convertable"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_postcode, "34.000")
            self.assertRaises(TypeError, document.set_postcode, "34 000")
            self.assertRaises(TypeError, document.set_postcode, "Herault")
            self.assertRaises(TypeError, document.set_birthday, ["34", ])
            document.set_postcode(u"34000")
            document.set_postcode("34000")
        
    def test_city(self):
        """city as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_city, "Paris")
            self.assertRaises(TypeError, document.set_city, [u"Paris", ])
            document.set_city(u"Paris")
        
    def test_country(self):
        """country as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_country, "France")
            self.assertRaises(TypeError, document.set_country, [u"France", ])
            document.set_country(u"France")
        
    def test_description(self):
        """description as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_description, "anything")
            self.assertRaises(TypeError, document.set_description, [u"anything", ])
            document.set_description(u"anything")
        
    # CUSTOM TAB
    def test_hobbies(self):
        """hobbies as unicode (multiple lines)"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_hobbies,
                              "blabla\nbla bla bla\n")
            self.assertRaises(TypeError, document.set_hobbies,
                              u"blabla\nbla bla bla\n")
            document.set_hobbies([u"blabla", u"bla bla bla", u""])
        
    def test_custom_attributes(self):
        """custom_attributes as pair of key/unicode-value"""
        for document in self.documents:
            self.assertRaises(TypeError, document.add_custom_attributes,
                              "homepage: manu.com")
            self.assertRaises(TypeError, document.add_custom_attributes,
                              ("homepage", "manu.com", "yo"))
            self.assertRaises(TypeError, document.add_custom_attributes,
                              ("homepage", "manu.com"))
            document.add_custom_attributes((u"homepage", u"manu.com"))
            document.add_custom_attributes([u"homepage", u"manu.com"])
        
    # FILE TAB
    def test_repository(self):
        """repository valid path"""
        for document in self.documents:
            self.assertRaises(TypeError, document.set_repository,
                              "./dummy/dummy")
            document.set_repository(".")
        
    def test_adding_file(self):
        """file_path as valid file"""
        for document in self.documents:
            self.assertRaises(TypeError, document.add_file, "~/dummy/dummy")
            document.add_file(unittest.__file__)
        
    def test_tag_file(self):
        """tagged file as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.tag_file,
                              "file: tag description")
            self.assertRaises(TypeError, document.tag_file,
                              ("file", ))
            self.assertRaises(TypeError, document.tag_file,
                              ("file", "tag description"))
            document.tag_file((unittest.__file__, u"tag description"))
            document.tag_file([unittest.__file__, u"tag description"])
            
    # OTHERS TAB
    def test_adding_peer(self):
        """pseudo as unicode"""
        for document in self.documents:
            self.assertRaises(TypeError, document.add_peer, "nico")
            self.assertRaises(TypeError, document.add_peer, [u"nico", ])
            document.add_peer(u"nico")
        
    def test_filling_data(self):
        """data as (pseudo, document)"""
        for document in self.documents:
            self.assertRaises(TypeError, document.fill_data,
                              "pseudo: doc")
            self.assertRaises(TypeError, document.fill_data,
                              ("pseudo", ))
            self.assertRaises(TypeError, document.fill_data,
                              ("pseudo", "doc"))
            self.assertRaises(TypeError, document.fill_data,
                              (u"pseudo", u"tag description"))
            self.assertRaises(TypeError, document.fill_data,
                              ("pseudo", AbstractDocument()))
            document.fill_data((u"emb", AbstractDocument()))
            document.fill_data((u"emb", FileDocument()))
            document.fill_data((u"emb", CacheDocument()))
    
    def test_peers_status(self):
        """action changes to accurate state"""
        for document in self.documents:
            document.make_friend(u"nico")
            self.assertEquals(PeerDescriptor.FRIEND,
                              document.get_peers()[u"nico"][0].state)
            document.blacklist_peer(u"nico")
            self.assertEquals(PeerDescriptor.BLACKLISTED,
                              document.get_peers()[u"nico"][0].state)
            document.unmark_peer(u"nico")
            self.assertEquals(PeerDescriptor.ANONYMOUS,
                              document.get_peers()[u"nico"][0].state)

    #TODO test fill data

if __name__ == '__main__':
    unittest.main()
