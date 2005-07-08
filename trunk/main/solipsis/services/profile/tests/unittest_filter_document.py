"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
import os.path
from ConfigParser import ConfigParser


from solipsis.services.profile import FILTER_EXT, QUESTION_MARK
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.tests import PROFILE_DIRECTORY, PROFILE_TEST
from solipsis.services.profile.filter_document import FilterValue, PeerMatch, FilterDocument
from solipsis.services.profile.file_document import FileDocument

class ValueTest(unittest.TestCase):

    def setUp(self):
        self.title = FilterValue("title", ".*men$", True)

    def test_creation(self):
        self.title = FilterValue("title", ".*men$", True)
        self.assertEquals(str(self.title), "title")
        self.assertEquals(self.title.activated, True)
        self.assertEquals(self.title.does_match("Good Omens"), False)
        self.assertEquals(self.title.does_match("men"), "men")
        self.assertEquals(self.title.does_match("women"), "women")

    def test_setters(self):
        self.title.set_value(".*men.?")
        self.assertEquals(self.title.does_match("Good Omens"), "Good Omens")
        self.assertEquals(self.title.does_match("women"), "women")
        self.title.activate(False)
        self.assertEquals(self.title.does_match("Good Omens"), False)
        self.assertEquals(self.title.does_match("women"), False)

    def test_blank(self):
        self.title.set_value("")
        self.assertEquals(self.title.activated, True)
        self.assertEquals(self.title.does_match("Good Omens"), False)
        self.assertEquals(self.title.does_match("men"), False)
        self.assertEquals(self.title.does_match("women"), False)

class MatchTest(unittest.TestCase):

    def setUp(self):
        # peer
        peer_document = FileDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        peer_document.load()
        self.peer_desc = PeerDescriptor(PROFILE_TEST, document=peer_document)
        self.peer_desc.set_shared_files()
        # filter
        self.document = FilterDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        self.document.load()

    def test_creation(self):
        match = PeerMatch(self.peer_desc, self.document)
        self.assertEquals(match.title, "Mr")
        self.assertEquals(match.firstname, False)
        self.assertEquals(match.lastname, "breton")
        self.assertEquals(match.photo, False)
        self.assertEquals(match.email, False)
        self.assertEquals(match.customs, {'color': u'blue'})
        self.assertEquals(match.files, {})

    def test_activated(self):
        # activate
        self.document.get_email().activate()
        match = PeerMatch(self.peer_desc, self.document)
        self.assertEquals(match.email, u'manu@ft.com')

    def test_files(self):
        # add filter for dummy.txt
        self.document.add_file((u'Any', FilterValue(value=u'.*\..*', activate=True)))
        match = PeerMatch(self.peer_desc, self.document)
        self.assertEquals(match.files, {u'Any': [u'dummy.txt']})

class FilterTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.document = FilterDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        # first test to call must write test file to get correct
        # execution of the others
        if not os.path.exists(os.path.join(PROFILE_DIRECTORY, PROFILE_TEST + FILTER_EXT)):
            self.test_save()

    def assert_content(self):
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
        self.assertEquals(self.document.has_file(u'MP3'), True)
            
    def test_save(self):
        # set personal data
        self.document.set_title(FilterValue(value=u"Mr", activate=True))
        self.document.set_firstname(FilterValue(value=u"", activate=True))
        self.document.set_lastname(FilterValue(value=u"breton", activate=True))
        self.document.set_photo(FilterValue(value=QUESTION_MARK(), activate=False))
        self.document.set_email(FilterValue(value=u"manu@ft.com", activate=False))
        # set custom interests, working if IGNORECASE set
        self.document.add_custom_attributes((u'color', FilterValue(value=u'BLUE', activate=True)))
        # set files
        self.document.add_file((u'MP3', FilterValue(value=u'.*\.mp3$', activate=True)))
        # write file
        self.document.save()
            
    def test_load(self):
        self.document.load()
        self.assert_content()

    def test_import(self):
        doc = FilterDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        doc.load()
        self.document.import_document(doc)
        self.assert_content()

    def test_customs(self):
        self.document.load()
        customs = self.document.get_custom_attributes()
        self.assertEquals(self.document.has_custom_attribute(u'color'), True)
        self.assertEquals(self.document.get_custom_attributes()[u'color']._name, 'color')
        self.assertEquals(self.document.get_custom_attributes()[u'color'].description, 'BLUE')
        self.assertEquals(self.document.get_custom_attributes()[u'color'].activated, True)
        self.document.add_custom_attributes((u'color', FilterValue(value=u'blue', activate=False)))
        self.assertEquals(self.document.get_custom_attributes()[u'color'].activated, False)
        customs = self.document.remove_custom_attributes(u'color')
        self.assertEquals(self.document.has_custom_attribute(u'color'), False)

if __name__ == '__main__':
    unittest.main()
