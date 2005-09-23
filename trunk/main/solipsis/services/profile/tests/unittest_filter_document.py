"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
import os.path
from ConfigParser import ConfigParser


from solipsis.services.profile import FILTER_EXT, QUESTION_MARK
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.filter_document import FilterValue, PeerMatch, FilterDocument
from solipsis.services.profile.file_document import FileDocument
from solipsis.services.profile.tests import PROFILE_DIRECTORY, PROFILE_TEST, REPO
from solipsis.services.profile.tests.unittest_file_document import write_test_profile, FILE_TEST

class ValueTest(unittest.TestCase):

    def setUp(self):
        self.title = FilterValue("title", ".*men$", True)

    def test_creation(self):
        self.title = FilterValue("title", ".*men$", True)
        self.assertEquals(str(self.title), "title")
        self.assertEquals(self.title.activated, True)
        self.assertEquals(self.title.does_match("Good Omens"), False)
        self.assertEquals(self.title.does_match("men").get_match(), "men")
        self.assertEquals(self.title.does_match("women").get_match(), "women")

    def test_setters(self):
        self.title.set_value(".*men.?")
        self.assertEquals(self.title.does_match("Good Omens").get_match(), "Good Omens")
        self.assertEquals(self.title.does_match("women").get_match(), "women")
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
        peer_document.share_files((REPO, [os.path.join("data", "date.txt"), os.path.join("data", "subdir1")], True))
        self.peer_desc = PeerDescriptor(PROFILE_TEST, document=peer_document)
        # filter
        self.document = FilterDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        self.document.load()

    def test_creation(self):
        match = PeerMatch(self.peer_desc, self.document)
        self.assertEquals(match.title.get_match(), "Mr")
        self.assertEquals(match.firstname, False)
        self.assertEquals(match.lastname.get_match(), "breton")
        self.assertEquals(match.photo, False)
        self.assertEquals(match.email, False)
        self.assertEquals(match.customs['color'].get_match(), u'blue')
        self.assertEquals(match.files, {})

    def test_activated(self):
        # activate
        self.document.get_email().activate()
        match = PeerMatch(self.peer_desc, self.document)
        self.assertEquals(match.email.get_match(), u'manu@ft.com')

    def test_files(self):
        # add filter for dummy.txt
        self.document.add_repository((u'Any', FilterValue(value=u'.*\..*', activate=True)))
        match = PeerMatch(self.peer_desc, self.document)
        match_files = [file_container.match for file_container in match.files[u'Any']]
        match_files.sort()
        self.assertEquals(match_files, ['TOtO.txt', 'date.doc', 'date.txt', "dummy.txt"])

def write_test_filter():
    document = FilterDocument(PROFILE_TEST, PROFILE_DIRECTORY)
    # set personal data
    document.set_title(FilterValue(value=u"Mr", activate=True))
    document.set_firstname(FilterValue(value=u"", activate=True))
    document.set_lastname(FilterValue(value=u"breton", activate=True))
    document.set_photo(FilterValue(value=QUESTION_MARK(), activate=False))
    document.set_email(FilterValue(value=u"manu@ft.com", activate=False))
    # set custom interests, working if IGNORECASE set
    document.add_custom_attributes((u'color', FilterValue(value=u'BLUE', activate=True)))
    # set files
    document.add_repository((u'MP3', FilterValue(value=u'.*\.mp3$', activate=True)))
    # write file
    document.save()
    
FILTER_TEST = os.path.join(PROFILE_DIRECTORY, PROFILE_TEST + FILTER_EXT)

class FilterTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        # write test profile
        if os.path.exists(FILTER_TEST):
            os.remove(FILTER_TEST)
        write_test_filter()
        # write test profile
        if os.path.exists(FILE_TEST):
            os.remove(FILE_TEST)
        write_test_profile()
        # load profile
        self.document = FilterDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        self.document.load()

    def assert_content(self, document):
        self.assertEquals(document.get_title().description, u"Mr")
        self.assertEquals(document.get_title().activated, True)
        self.assertEquals(document.get_firstname().description, u"")
        self.assertEquals(document.get_firstname().activated, True)
        self.assertEquals(document.get_lastname().description, u"breton")
        self.assertEquals(document.get_lastname().activated, True)
        self.assertEquals(document.get_photo().description, QUESTION_MARK())
        self.assertEquals(document.get_photo().activated, False)
        self.assertEquals(document.get_email().description, u"manu@ft.com")
        self.assertEquals(document.get_email().activated, False)
        self.assertEquals(document.has_custom_attribute(u'color'), True)
        self.assertEquals(document.has_file(u'MP3'), True)
            
    def test_save(self):
        self.assert_content(self.document)

    def test_import(self):
        doc = FilterDocument(PROFILE_TEST, PROFILE_DIRECTORY)
        doc.import_document(self.document)
        self.assert_content(doc)

    def test_customs(self):
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
