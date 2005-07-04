"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
from ConfigParser import ConfigParser
from os.path import abspath

from solipsis.services.profile.filter_document import FilterValue, FilterDocument

class ValueTest(unittest.TestCase):

    def test_filter_value_object(self):
        title = FilterValue("title", ".*men$", True)
        self.assertEquals(str(title), "title")
        self.assertEquals(title.activated, True)
        self.assertEquals(title.does_match("Good Omens"), False)
        self.assertEquals(title.does_match("women"), True)
        title.set_value(".*men.?")
        self.assertEquals(title.does_match("Good Omens"), True)
        self.assertEquals(title.does_match("women"), True)
        title.activate(False)
        self.assertEquals(title.does_match("Good Omens"), False)
        self.assertEquals(title.does_match("women"), False)

class FilterTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        pass

if __name__ == '__main__':
    unittest.main()
