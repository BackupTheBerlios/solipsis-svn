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
from solipsis.services.profile.filter_data import create_regex, FilterValue 
from solipsis.services.profile.filter_document import FilterDocument
from solipsis.services.profile.tests import PROFILE_DIR, PROFILE_TEST, TEST_DIR
from solipsis.services.profile.tests import write_test_profile, FILE_TEST
    
FILTER_TEST = os.path.join(PROFILE_DIR, PROFILE_TEST + FILTER_EXT)

class FilterTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        write_test_profile()
        # load profile
        self.document = FilterDocument()
        self.document.load(FILTER_TEST)

    def assert_content(self, document):
        self.assertEquals(3, len(self.document.filters))
        all_dict = self.document.filters["All"].as_dict()
        peer_dict = self.document.filters["Mr_B"].as_dict()
        file_dict = self.document.filters["MP3"].as_dict()
        self.assertEquals('*, (1)', all_dict['pseudo'])
        self.assertEquals('*.mp3, (1)', file_dict['name'])
        self.assertEquals('*, (1)', peer_dict['pseudo'])
        self.assertEquals('Mr, (1)', peer_dict['title'])
        self.assertEquals('b*, (1)', peer_dict['lastname'])
        self.assertEquals('blue, (1)', peer_dict['color'])
            
    def test_load(self):
        self.assert_content(self.document)

    def test_import(self):
        doc = FilterDocument()
        doc.import_document(self.document)
        self.assert_content(doc)

    def test_match(self):
        peer_desc = PeerDescriptor(PROFILE_TEST)
        peer_desc.load(directory=PROFILE_DIR)
        self.document.match(peer_desc)
        # check results
        self.assertEquals(3, len(self.document.results))
        self.assert_('All' in self.document.results)
        self.assert_('Mr_B' in self.document.results)
        self.assert_('MP3' in self.document.results)
        results = [(result.get_name(), result.match)
                   for result in self.document.results['Mr_B'][PROFILE_TEST]]
        results.sort()
        self.assertEquals([('color', 'blue'),
                           ('lastname', 'breton'),
                           ('pseudo', 'atao'),
                           ('title', 'Mr')],
                          results)

if __name__ == '__main__':
    unittest.main()
