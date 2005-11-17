import os, os.path
import unittest

from solipsis.services.profile import DOWNLOAD_REPO
from solipsis.services.profile.tests import GENERATED_DIR
from solipsis.services.profile.tools.prefs import Preferences

PREF_FILE = os.path.join(GENERATED_DIR, "prefs")

class ConfigTest(unittest.TestCase):

    def setUp(self):
        if os.path.exists(PREF_FILE):
            os.remove(PREF_FILE)
        self.prefs = Preferences(PREF_FILE)
        self.prefs.load()

    def tearDown(self):
        if os.path.exists(PREF_FILE):
            os.remove(PREF_FILE)

    def test_disclaimer(self):
        self.assertEquals(self.prefs.get("disclaimer"), True)
        self.prefs.set("disclaimer", False)
        self.assertEquals(self.prefs.get("disclaimer"), False)
        self.prefs.set("disclaimer")
        self.assertEquals(self.prefs.get("disclaimer"), True)
        self.assertRaises(AssertionError, self.prefs.set, "disclaimer", 3)

    def test_both(self):
        self.assertEquals(self.prefs.get("disclaimer"), True)
        self.assertEquals(self.prefs.get("display_dl"), True)
        self.prefs.set("display_dl", False)
        self.assertEquals(self.prefs.get("disclaimer"), True)
        self.assertEquals(self.prefs.get("display_dl"), False)
        self.prefs.set("disclaimer", False)
        self.assertEquals(self.prefs.get("disclaimer"), False)
        self.assertEquals(self.prefs.get("display_dl"), False)

    def test_width(self):
        self.assertEquals(self.prefs.get("profile_width"), 460)
        self.prefs.set("profile_width", 500)
        self.assertEquals(self.prefs.get("profile_width"), 500)
        self.prefs.set("profile_width")
        self.assertEquals(self.prefs.get("profile_width"), 460)
        self.assertRaises(AssertionError, self.prefs.set, "profile_width", "460")

    def test_repo(self):
        self.assertEquals(self.prefs.get("download_repo"), DOWNLOAD_REPO)
        self.prefs.set("download_repo", "dl")
        self.assertEquals(self.prefs.get("download_repo"), "dl")
        self.prefs.set("download_repo")
        self.assertEquals(self.prefs.get("download_repo"), DOWNLOAD_REPO)
        self.assertRaises(AssertionError, self.prefs.set, "download_repo", 3)
    
if __name__ == '__main__':
    unittest.main()
