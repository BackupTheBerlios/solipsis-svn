"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
from solipsis.services.profile.document import CacheDocument, PeerDescriptor


class ValidatorTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.document = CacheDocument()

    # PERSONAL TAB
    def test_title(self):
        """title as unicode"""
        self.assertRaises(TypeError, self.document.set_title, "Mr")
        self.assertRaises(TypeError, self.document.set_title, [u"Mr", ])
        self.document.set_title(u"Mr")
        
    def test_firstname(self):
        """firstname as unicode"""
        self.assertRaises(TypeError, self.document.set_firstname, "manu")
        self.assertRaises(TypeError, self.document.set_firstname, [u"manu", ])
        self.document.set_firstname(u"manu")
        
    def test_lastname(self):
        """lastname as unicode"""
        self.assertRaises(TypeError, self.document.set_lastname, "breton")
        self.assertRaises(TypeError, self.document.set_lastname, [u"breton", ])
        self.document.set_lastname(u"breton")
    
    def test_pseudo(self):
        """pseudo as unicode"""
        self.assertRaises(TypeError, self.document.set_pseudo, "emb")
        self.assertRaises(TypeError, self.document.set_pseudo, [u"manu", u"emb"])
        self.document.set_pseudo(u"emb")
    
    def test_photo(self):
        """photo as unicode"""
        self.assertRaises(TypeError, self.document.set_photo, "./dummy/dummy.jpg")
        self.document.set_photo(unittest.__file__)
        
    def test_email(self):
        """email as unicode"""
        self.assertRaises(TypeError, self.document.set_email, "manu@ft.com")
        self.assertRaises(TypeError, self.document.set_email, [u"manu@ft", ])
        self.document.set_email(u"manu@ft.com")
        
    def test_birthday(self):
        """birthday as DateTime convertable"""
        self.assertRaises(TypeError, self.document.set_birthday, "12 jan 2005")
        self.assertRaises(TypeError, self.document.set_birthday, "2005/01/12")
        self.assertRaises(TypeError, self.document.set_birthday, "12-01-2005")
        self.assertRaises(TypeError, self.document.set_birthday, "12012005")
        self.assertRaises(TypeError, self.document.set_birthday, "12/01")
        self.assertRaises(TypeError, self.document.set_birthday, ["12/01/05", ])
        self.document.set_birthday(u"12/01/2005")
        self.document.set_birthday("12/01/2005")
        
    def test_language(self):
        """language as unicode"""
        self.assertRaises(TypeError, self.document.set_language, "fr")
        self.assertRaises(TypeError, self.document.set_language, [u"fr", u"sp"])
        self.document.set_language(u"fr")
        
    def test_address(self):
        """address as unicode"""
        self.assertRaises(TypeError, self.document.set_address, "12 rue V Hugo")
        self.assertRaises(TypeError, self.document.set_address, [u"12",
                                                                u"rue V Hugo"])
        self.document.set_address(u"12 rue V Hugo")
        
    def test_postcode(self):
        """postcode as int convertable"""
        self.assertRaises(TypeError, self.document.set_postcode, "34.000")
        self.assertRaises(TypeError, self.document.set_postcode, "34 000")
        self.assertRaises(TypeError, self.document.set_postcode, "Herault")
        self.assertRaises(TypeError, self.document.set_birthday, ["34", ])
        self.document.set_postcode(u"34000")
        self.document.set_postcode("34000")
        
    def test_city(self):
        """city as unicode"""
        self.assertRaises(TypeError, self.document.set_city, "Paris")
        self.assertRaises(TypeError, self.document.set_city, [u"Paris", ])
        self.document.set_city(u"Paris")
        
    def test_country(self):
        """country as unicode"""
        self.assertRaises(TypeError, self.document.set_country, "France")
        self.assertRaises(TypeError, self.document.set_country, [u"France", ])
        self.document.set_country(u"France")
        
    def test_description(self):
        """description as unicode"""
        self.assertRaises(TypeError, self.document.set_description, "anything")
        self.assertRaises(TypeError, self.document.set_description,
                          [u"anything", ])
        self.document.set_description(u"anything")
        
    # CUSTOM TAB
    def test_hobbies(self):
        """hobbies as unicode (multiple lines)"""
        self.assertRaises(TypeError, self.document.set_hobbies,
                          "blabla\nbla bla bla\n")
        self.assertRaises(TypeError, self.document.set_hobbies,
                          u"blabla\nbla bla bla\n")
        self.document.set_hobbies([u"blabla", u"bla bla bla", u""])
        
    def test_custom_attributes(self):
        """custom_attributes as pair of key/unicode-value"""
        self.assertRaises(TypeError, self.document.add_custom_attributes,
                          "homepage: manu.com")
        self.assertRaises(TypeError, self.document.add_custom_attributes,
                          ("homepage", "manu.com", "yo"))
        self.assertRaises(TypeError, self.document.add_custom_attributes,
                          ("homepage", "manu.com"))
        self.document.add_custom_attributes((u"homepage", u"manu.com"))
        self.document.add_custom_attributes([u"homepage", u"manu.com"])
        
    # FILE TAB
    def test_repository(self):
        """repository valid path"""
        self.assertRaises(TypeError, self.document.set_repository,
                          "./dummy/dummy")
        self.document.set_repository(".")
        
    def test_adding_file(self):
        """file_path as valid file"""
        self.assertRaises(TypeError, self.document.add_file, "~/dummy/dummy")
        self.document.add_file(unittest.__file__)
        
    def test_tag_file(self):
        """tagged file as unicode"""
        self.assertRaises(TypeError, self.document.tag_file,
                          "file: tag description")
        self.assertRaises(TypeError, self.document.tag_file,
                          ("file", ))
        self.assertRaises(TypeError, self.document.tag_file,
                          ("file", "tag description"))
        self.assertRaises(TypeError, self.document.tag_file,
                          ("file", u"tag description"))
        self.document.tag_file((unittest.__file__, u"tag description"))
        self.document.tag_file([unittest.__file__, u"tag description"])
            
    # OTHERS TAB
    def test_adding_peer(self):
        """pseudo as unicode"""
        self.assertRaises(TypeError, self.document.add_peer, "nico")
        self.assertRaises(TypeError, self.document.add_peer, [u"nico", ])
        self.document.add_peer(u"nico")
    
    def test_peers_status(self):
        """action changes to accurate state"""
        self.document.make_friend(u"nico")
        self.assertEquals(PeerDescriptor.FRIEND,
                          self.document.get_peers()[u"nico"].state)
        self.document.blacklist_peer(u"nico")
        self.assertEquals(PeerDescriptor.BLACKLISTED,
                          self.document.get_peers()[u"nico"].state)
        self.document.unmark_peer(u"nico")
        self.assertEquals(PeerDescriptor.ANONYMOUS,
                          self.document.get_peers()[u"nico"].state)

if __name__ == '__main__':
    unittest.main()
