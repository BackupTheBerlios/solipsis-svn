#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# pylint: disable-msg=W0131,C0301,C0103
# Missing docstring, Line too long, Invalid name
"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

__revision__ = "$Id$"

import unittest
import os.path

from solipsis.services.profile import FILTER_EXT, QUESTION_MARK
from solipsis.services.profile.prefs import get_prefs, set_prefs
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.filter_document import FilterValue, PeerMatch, \
     FilterDocument, create_regex
from solipsis.services.profile.tests import PROFILE_DIR, PROFILE_TEST, TEST_DIR
from solipsis.services.profile.tests import write_test_profile, FILE_TEST

class ValueTest(unittest.TestCase):

    def setUp(self):
        self.title = FilterValue("title", "*men", True)

    def test_conversion(self):
        self.assertEquals(create_regex("*mp3"), ".*mp3$")
        self.assertEquals(create_regex("*.gif"), ".*\.gif$")
        self.assertEquals(create_regex("bonus"), "^bonus$")
        self.assertEquals(create_regex("*any(FR)*"), ".*any\(FR\).*")

    def test_creation(self):
        self.title = FilterValue("title", "*men", True)
        self.assertEquals(str(self.title), "title")
        self.assertEquals(self.title.activated, True)
        self.assertEquals(self.title.does_match("Good Omens"), False)
        self.assertEquals(self.title.does_match("men").get_match(), "men")
        self.assertEquals(self.title.does_match("women").get_match(), "women")

    def test_setters(self):
        self.title.set_value("*men*")
        self.assertEquals(self.title.does_match("Good Omens").get_match(), "Good Omens")
        self.assertEquals(self.title.does_match("women").get_match(), "women")
        self.title.activated = False
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
        write_test_profile()
        # peer
        self.peer_desc = PeerDescriptor(PROFILE_TEST)
        self.peer_desc.load(directory=PROFILE_DIR)
        self.peer_desc.document.share_files(TEST_DIR,
                                            [os.path.join("data", "date.txt"),
                                             os.path.join("data", "subdir1")],
                                            True)
        # filter
        self.document = FilterDocument()
        self.document.load(FILTER_TEST)

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
        self.document.get_email().activated = True
        match = PeerMatch(self.peer_desc, self.document)
        self.assertEquals(match.lastname.get_match(), u'breton')

    def test_files(self):
        # add filter for dummy.txt
        filter_value =  FilterValue(value=u'*.*', activate=True)
        self.document.add_repository(u'Any', filter_value)
        match = PeerMatch(self.peer_desc, self.document)
        match_files = [file_container.match for file_container
                       in match.files[u'Any']]
        match_files.sort()
        self.assertEquals(
            match_files, ['TOtO.txt', 'date.doc', 'date.txt', "dummy.txt"])
    
FILTER_TEST = os.path.join(PROFILE_DIR, PROFILE_TEST + FILTER_EXT)

class FilterTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        # write test profile
        if os.path.exists(FILE_TEST):
            os.remove(FILE_TEST)
        write_test_profile()
        # load profile
        self.document = FilterDocument()
        self.document.load(FILTER_TEST)

    def assert_content(self, document):
        self.assertEquals(document.get_title().description, u"Mr")
        self.assertEquals(document.get_title().activated, True)
        self.assertEquals(document.get_firstname().description, u"")
        self.assertEquals(document.get_firstname().activated, False)
        self.assertEquals(document.get_lastname().description, u"b*")
        self.assertEquals(document.get_lastname().activated, True)
        self.assertEquals(document.get_photo().description, u"")
        self.assertEquals(document.get_photo().activated, False)
        self.assertEquals(document.get_email().description, u"")
        self.assertEquals(document.get_email().activated, False)
        self.assertEquals(document.has_custom_attribute(u'color'), True)
        self.assertEquals(document.has_file(u'MP3'), True)
            
    def test_save(self):
        self.assert_content(self.document)

    def test_import(self):
        doc = FilterDocument()
        doc.import_document(self.document)
        self.assert_content(doc)

    def test_customs(self):
        self.assertEquals(self.document.has_custom_attribute(u'color'), True)
        self.assertEquals(self.document.get_custom_attributes()[u'color']._name, 'color')
        self.assertEquals(self.document.get_custom_attributes()[u'color'].description, 'blue')
        self.assertEquals(self.document.get_custom_attributes()[u'color'].activated, True)
        self.document.add_custom_attributes(u'color', FilterValue(value=u'blue', activate=False))
        self.assertEquals(self.document.get_custom_attributes()[u'color'].activated, False)
        self.document.remove_custom_attributes(u'color')
        self.assertEquals(self.document.has_custom_attribute(u'color'), False)

if __name__ == '__main__':
    unittest.main()
