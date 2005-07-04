"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
import os.path
from ConfigParser import ConfigParser


from solipsis.services.profile import FILTER_EXT, QUESTION_MARK
from solipsis.services.profile.tests import PROFILE_DIRECTORY, PROFILE_TEST
from solipsis.services.profile.filter_document import FilterValue, FilterDocument

class ValueTest(unittest.TestCase):

    def setUp(self):
        self.title = FilterValue("title", ".*men$", True)

    def test_creation(self):
        self.title = FilterValue("title", ".*men$", True)
        self.assertEquals(str(self.title), "title")
        self.assertEquals(self.title.activated, True)
        self.assertEquals(self.title.does_match("Good Omens"), False)
        self.assertEquals(self.title.does_match("women"), True)

    def test_setters(self):
        self.title.set_value(".*men.?")
        self.assertEquals(self.title.does_match("Good Omens"), True)
        self.assertEquals(self.title.does_match("women"), True)
        self.title.activate(False)
        self.assertEquals(self.title.does_match("Good Omens"), False)
        self.assertEquals(self.title.does_match("women"), False)

    def test_default(self):
        self.title.set_value("")
        self.assertEquals(self.title.does_match("Good Omens"), False)
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
        self.assertEquals(self.document.get_firstname().description, u"")
        self.assertEquals(self.document.get_lastname().description, u"breton")
        self.assertEquals(self.document.get_photo().description, QUESTION_MARK())
        self.assertEquals(self.document.get_email().description, u"manu@ft.com")
        self.assertEquals(self.document.has_custom_attribute(u'color'), True)
        self.assertEquals(self.document.has_files_attributes(u'MP3'), True)

    def test_customs(self):
        self.document.load()
        customs = self.document.get_custom_attributes()

if __name__ == '__main__':
    unittest.main()
