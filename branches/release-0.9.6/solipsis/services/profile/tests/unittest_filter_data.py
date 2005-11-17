#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# pylint: disable-msg=W0131,C0301,C0103
# Missing docstring, Line too long, Invalid name
"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

__revision__ = "$Id: unittest_filter_document.py 894 2005-10-11 18:39:43Z emb $"

import unittest
import os.path

from solipsis.services.profile import FILTER_EXT, QUESTION_MARK
from solipsis.services.profile.tools.prefs import get_prefs, set_prefs
from solipsis.services.profile.tools.peer import PeerDescriptor
from solipsis.services.profile.editor.cache_document import CacheDocument
from solipsis.services.profile.filter.data import FilterValue, \
     FileFilter, PeerFilter, create_regex, create_key_regex

class ToBeMatch:
    def __init__(self, expr=None, **kwargs):
        if not expr is None:
            self.expr = expr
        for arg_name, arg_value in kwargs.items():
            setattr(self, arg_name, arg_value)

class ValuesTest(unittest.TestCase):

    def setUp(self):
        self.title = FilterValue("title", "*men", True)

    def test_conversion(self):
        self.assertEquals(create_regex("*mp3"), ".*mp3$")
        self.assertEquals(create_regex("*.gif"), ".*\.gif$")
        self.assertEquals(create_regex("bonus"), "^bonus$")
        self.assertEquals(create_regex("*any(FR)*"), ".*any\(FR\).*")

    def test_simple_conversion(self):
        self.assertEquals(create_key_regex("*mp3"), ".*\*mp3.*")
        self.assertEquals(create_key_regex(".gif"), ".*\.gif.*")
        self.assertEquals(create_key_regex("any(FR)"), ".*any\(FR\).*")

    def test_creation(self):
        self.title = FilterValue("title", "men", True)
        self.assertEquals(str(self.title), "men, (1)")
        self.assertEquals(self.title.activated, True)
        self.assertEquals(False,
            self.title.does_match("bob", ToBeMatch("Good"), "expr"))
        self.assertEquals("men",
            self.title.does_match("bob", ToBeMatch("men"), "expr").get_match())
        self.assertEquals("women",
            self.title.does_match("bob", ToBeMatch("women"), "expr").get_match())

    def test_setters(self):
        self.title.set_value("men")
        self.assert_(self.title.does_match("bob", ToBeMatch("Good Omens"), "expr"))
        self.assert_(self.title.does_match("bob", ToBeMatch("women"), "expr"))
        self.title.set_value("women")
        self.assertEquals(False, 
            self.title.does_match("bob", ToBeMatch("Good Omens"), "expr"))
        self.assert_(self.title.does_match("bob", ToBeMatch("women"), "expr"))
        self.title.activated = False
        self.assertEquals(False, 
            self.title.does_match("bob", ToBeMatch("Good Omens"), "expr"))
        self.assertEquals(False, 
            self.title.does_match("bob", ToBeMatch("women"), "expr"))

    def test_match(self):
        self.title.set_value("men")
        match = self.title.does_match("bob", ToBeMatch("Good Omens"), "expr")
        self.assertEquals(match.get_name(), "title")
        self.assertEquals(match.get_description(), "men")
        self.assertEquals(match.get_match(), "Good Omens")
        match = self.title.does_match("bob", ToBeMatch("women"), "expr")
        self.assertEquals(match.get_name(), "title")
        self.assertEquals(match.get_description(), "men")
        self.assertEquals(match.get_match(), "women")
        
    def test_blank(self):
        self.title.set_value("")
        self.assertEquals(self.title.activated, True)
        self.assertEquals(False, 
            self.title.does_match("bob", ToBeMatch("Good Omens"), "expr"))
        self.assertEquals(False, 
            self.title.does_match("bob", ToBeMatch("men"), "expr"))
        self.assertEquals(False, 
            self.title.does_match("bob", ToBeMatch("women"), "expr"))

class FiltersTest(unittest.TestCase):

    def setUp(self):
        # filters
        self.peer_filter = PeerFilter("test peer", **{
            "title": "Mr",
            "firstname": "Bob",
            "lastname": "b",
            "pseudo": "emb"})
        self.file_filter = FileFilter("test file", **{
            "name": "mp3"})
        # properties
        doc = CacheDocument()
        doc.title = "Mr"
        doc.firstname = "Emmanuel"
        doc.lastname = "Breton"
        doc.pseudo = "emb"
        doc.photo = "none"
        doc.email = "emb@logilab.fr"
        doc.add_custom_attributes(u"book", u"Harry Potter")
        doc.add_custom_attributes(u"movie", u"Leon")
        doc.add_custom_attributes(u"sport", u"biking")
        self.peer_desc = PeerDescriptor("bob", document=doc)
        self.file_props = ToBeMatch(**{
            "name": "Hero.mp3",
            "size": "3000"})

    def test_creation(self):
        name, new_filter = PeerFilter.from_str("peer_bob", [
            ("title", "Mr, (1)"),
            ("lastname", "Bob, (0)")])
        self.assertEquals("bob", name)
        self.assert_(new_filter)
        name, new_filter = FileFilter.from_str("peer_bob", [
            ("title", "Mr, (1)"),
            ("lastname", "Bob, (0)")])
        self.assertEquals(None, new_filter)
        # files
        name, new_filter = FileFilter.from_str("file_mp3", [
            ("name", "mp3, (1)")])
        self.assertEquals("mp3", name)
        self.assert_(new_filter)
        name, new_filter = PeerFilter.from_str("file_mp3", [
            ("name", "mp3, (1)")])
        self.assertEquals(None, new_filter)

    def test_file_filter(self):
        matches = self.file_filter.match("bob", [self.file_props])
        self.assertEquals(1, len(matches))
        self.assertEquals("name", matches[0].get_name())
        self.assertEquals("mp3", matches[0].get_description())
        self.assertEquals("Hero.mp3", matches[0].get_match())

    def test_peer_filter(self):
        matches =  self.peer_filter.match("bob", self.peer_desc)
        self.assertEquals(3, len(matches))
        self.assertEquals("title", matches[0].get_name())
        self.assertEquals("b", matches[1].get_description())
        self.assertEquals("emb", matches[2].get_match())

    def test_and_filters(self):
        p_filter = PeerFilter("test peer", filter_or=False, **{
            "title": "Mr",
            "firstname": "Bob",
            "lastname": "b",
            "pseudo": "emb"})
        matches =  p_filter.match("bob", self.peer_desc)
        self.assertEquals([], matches)
        # ok
        p_filter = PeerFilter("test peer", filter_or=False, **{
            "title": "Mr",
            "lastname": "b",
            "pseudo": "emb"})
        matches =  p_filter.match("bob", self.peer_desc)
        self.assertEquals(3, len(matches))

    def test_update(self):
        self.peer_filter.update_title(FilterValue("title", "Mss", True))
        self.assertEquals(2, len(
            self.peer_filter.match("bob", self.peer_desc)))
        self.peer_filter.update_email(FilterValue("email", "fr", True))
        self.assertEquals(3, len(
            self.peer_filter.match("bob", self.peer_desc)))

    def test_update_properties(self):
        self.assertEquals("Mr", self.peer_filter.title.description)
        self.assertEquals("", self.peer_filter.email.description)
        props = {"title": "Mss",
                 "email": "fr"}
        self.peer_filter.update_properties(**props)
        self.assertEquals("Mss", self.peer_filter.title.description)
        self.assertEquals("fr", self.peer_filter.email.description)
        
    def test_customs(self):
        self.peer_filter.update_dict(FilterValue("book", "potter", True))
        self.peer_filter.update_dict(FilterValue("sport", "bik", True))
        matches =  self.peer_filter.match("bob", self.peer_desc)
        self.assertEquals(5, len(matches))
        self.assertEquals("book", matches[3].get_name())
        self.assertEquals("bik", matches[4].get_description())

    def test_as_dict(self):
        peer_dict = self.peer_filter.as_dict()
        file_dict = self.file_filter.as_dict()
        self.assertEquals({'name': 'mp3, (1)',
                           'size': ', (0)'}, file_dict)
        self.assertEquals({'firstname': 'Bob, (1)',
                           'title': 'Mr, (1)',
                           'lastname': 'b, (1)',
                           'pseudo': 'emb, (1)',
                           'photo': ', (0)',
                           'email': ', (0)'}, peer_dict)
    
if __name__ == '__main__':
    unittest.main()
