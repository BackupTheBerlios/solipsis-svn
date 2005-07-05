"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
import os.path
from ConfigParser import ConfigParser


from solipsis.services.profile import FILTER_EXT, QUESTION_MARK
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.tests import PROFILE_DIRECTORY, PROFILE_TEST
from solipsis.services.profile.filter_document import FilterValue, FilterDocument
from solipsis.services.profile.file_document import FileDocument

class ValueTest(unittest.TestCase):

    def setUp(self):
        self.title = FilterValue("title", ".*men$", True)

    def test_creation(self):
        self.title = FilterValue("title", ".*men$", True)
        self.assertEquals(str(self.title), "title")
        self.assertEquals(self.title.activated, True)
        self.assertEquals(self.title.does_match("Good Omens"), False)
        self.assertEquals(self.title.does_match("men")._name, "title")
        self.assertEquals(self.title.does_match("women")._name, "title")

    def test_setters(self):
        self.title.set_value(".*men.?")
        self.assertEquals(self.title.does_match("Good Omens")._name, "title")
        self.assertEquals(self.title.does_match("women")._name, "title")
        self.title.activate(False)
        self.assertEquals(self.title.does_match("Good Omens"), False)
        self.assertEquals(self.title.does_match("women"), False)

    def test_blank(self):
        self.title.set_value("")
        self.assertEquals(self.title.activated, True)
        self.assertEquals(self.title.does_match("Good Omens"), False)
        self.assertEquals(self.title.does_match("men"), False)
        self.assertEquals(self.title.does_match("women"), False)

class FilterTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.document = FilterDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        # first test to call must write test file to get correct
        # execution of the others
        if not os.path.exists(os.path.join(PROFILE_DIRECTORY, PROFILE_TEST + FILTER_EXT)):
            self.test_save()
            
    def test_save(self):
        # set personal data
        self.document.set_title((u"Mr", True))
        self.document.set_firstname((u"", True))
        self.document.set_lastname((u"breton", True))
        self.document.set_photo((QUESTION_MARK(), False))
        self.document.set_email((u"manu@ft.com", False))
        # set custom interests
        self.document.add_custom_attributes((u'color', u'blue', True))
        # set files
        self.document.add_files_attributes((u'MP3', u'.*\.mp3$', True))
        # write file
        self.document.save()
            
    def test_load(self):
        self.document.load()
        self.assertEquals(self.document.get_title().description, u"Mr")
        self.assertEquals(self.document.get_title().activated, True)
        self.assertEquals(self.document.get_firstname().description, u"")
        self.assertEquals(self.document.get_firstname().activated, True)
        self.assertEquals(self.document.get_lastname().description, u"breton")
        self.assertEquals(self.document.get_lastname().activated, True)
        self.assertEquals(self.document.get_photo().description, QUESTION_MARK())
        self.assertEquals(self.document.get_photo().activated, False)
        self.assertEquals(self.document.get_email().description, u"manu@ft.com")
        self.assertEquals(self.document.get_email().activated, False)
        self.assertEquals(self.document.has_custom_attribute(u'color'), True)
        self.assertEquals(self.document.has_files_attributes(u'MP3'), True)

    def test_customs(self):
        self.document.load()
        customs = self.document.get_custom_attributes()
        self.assertEquals(self.document.has_custom_attribute(u'color'), True)
        self.assertEquals(self.document.get_custom_attributes()[u'color']._name, 'color')
        self.assertEquals(self.document.get_custom_attributes()[u'color'].description, 'blue')
        self.assertEquals(self.document.get_custom_attributes()[u'color'].activated, True)
        self.document.add_custom_attributes((u'color', u'blue', False))
        self.assertEquals(self.document.get_custom_attributes()[u'color'].activated, False)
        customs = self.document.remove_custom_attributes(u'color')
        self.assertEquals(self.document.has_custom_attribute(u'color'), False)

    def test_does_match(self):
        # peer
        peer_document = FileDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        peer_document.load()
        peer_desc = PeerDescriptor(PROFILE_TEST, document=peer_document)
        peer_desc.set_shared_files()
        # filter
        self.document.load()
        self.assertEquals(len(self.document.does_match(peer_desc)), 3)
        # activate
        self.document.get_email().activate()
        self.assertEquals(len(self.document.does_match(peer_desc)), 4)
        # add filter for dummy.txt
        self.document.add_files_attributes((u'Any', u'.*\..*', True))
        self.assertEquals(len(self.document.does_match(peer_desc)), 5)

if __name__ == '__main__':
    unittest.main()
