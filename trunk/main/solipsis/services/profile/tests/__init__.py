#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>
"""Constants used by tests"""

__revision__ = "$Id$"

import os, os.path
import solipsis

from solipsis.services.profile import QUESTION_MARK, \
     PROFILE_EXT, BLOG_EXT, FILTER_EXT
from solipsis.services.profile.file_document import FileDocument
from solipsis.services.profile.filter_document import FilterDocument
from solipsis.services.profile.filter_data import FilterValue, \
     PeerFilter, FileFilter
from solipsis.services.profile.data import PeerDescriptor, Blogs, load_blogs

TEST_DIR = os.path.sep.join([os.path.dirname(solipsis.__file__),
                             "services", "profile", "tests"])
GENERATED_DIR = os.path.join(TEST_DIR, "generated")
DATA_DIR = os.path.join(TEST_DIR, "data")
PROFILE_DIR = os.path.sep.join([TEST_DIR, "data", "profiles"])

PROFILE_TEST = u"test_030_736537"
PROFILE_BRUCE = u"bruce_030_09484"
PROFILE_UNICODE = u"zoé_030_154343"
PROFILE_TATA = u"tata_030_094664"
PROFILE_DEMI = u"demi_030_057890"
PROFILE_010 = u"demi_010"

FILE_TEST = os.path.join(PROFILE_DIR, PROFILE_TEST)
FILE_BRUCE = os.path.join(PROFILE_DIR, PROFILE_BRUCE)

PSEUDO = u"atao"

def get_bruce_profile():
    """return PeerDescriptor filled with:
    
    node_id = PROFILE_BRUCE
    
    Blog:
    `````
      'Hi Buddy'

    Files:
    ``````
      data/
      |-- date.txt           Shared
      |-- ...
      `-- subdir1
          |-- date.doc       Shared
          `-- ...
    """
    # write bruce blog
    bruce_blog = Blogs()
    bruce_blog.add_blog(u"Hi Buddy", u"bruce")
    # write bruce profile
    bruce_doc = FileDocument()
    bruce_doc.set_pseudo(u"bruce")
    bruce_doc.set_title(u"Mr")
    bruce_doc.set_firstname(u"bruce")
    bruce_doc.set_lastname(u"willis")
    bruce_doc.set_photo(QUESTION_MARK())
    bruce_doc.set_email(u"bruce@stars.com")
    bruce_doc.add_custom_attributes(u"Homepage", u"bruce.com")
    bruce_doc.add_custom_attributes(u'Color', u'gray')
    bruce_doc.add_custom_attributes(u'Movie', u'6th Sense')
    bruce_doc.add_custom_attributes(u'Actor', u'Robin Williams')
    bruce_doc.add_repository(TEST_DIR)
    bruce_doc.share_file(os.path.join(DATA_DIR, "date.txt"))
    bruce_doc.share_file(os.sep.join([DATA_DIR,
                                      "subdir1",
                                      "date.doc"]))
    return PeerDescriptor(PROFILE_BRUCE, document=bruce_doc, blog=bruce_blog)

def write_test_profile():
    """write testing profile & blogs into test.prf & test.blog
    
    node_id = PROFILE_BRUCE
    
    Blog:
    `````
      'This is a test'

    Files:
    ``````
      data/
      |-- date.txt                  - tagos
      |-- emptydir           Shared
      |-- profiles
      |   `-- ...
      |-- routage            Shared
      `-- subdir1            Shared
          |-- TOtO.txt
          |-- date.doc
          `-- subsubdir
              |-- dummy.txt  Shared - tag2
              |-- null       Shared - tag1
              `-- ..."""
    # write filter
    filter_document = FilterDocument()
    peer_filter = PeerFilter("Mr_B", filter_or=False,**{
        "pseudo" : "*",
        "title": "Mr",
        "lastname": "b*"})
    peer_filter.update_dict(FilterValue(name='color',
                                        value="blue",
                                        activate=True))
    file_filter = FileFilter("MP3", **{"name": "*.mp3"})
    filter_document.filters[peer_filter.filter_name] = peer_filter
    filter_document.filters[file_filter.filter_name] = file_filter
    if os.path.exists(FILE_TEST + FILTER_EXT):
        os.remove(FILE_TEST + FILTER_EXT)
    filter_document.save(FILE_TEST + FILTER_EXT)
    # write blog
    blog = Blogs()
    blog.add_blog(u"This is a test", PSEUDO)
    if os.path.exists(FILE_TEST + BLOG_EXT):
        os.remove(FILE_TEST + BLOG_EXT)
    blog.save(FILE_TEST + BLOG_EXT)
    # write profile
    document = FileDocument()
    document.set_pseudo(PSEUDO)
    document.set_title(u"Mr")
    document.set_firstname(u"manu")
    document.set_lastname(u"breton")
    document.set_photo(QUESTION_MARK())
    document.set_email(u"manu@ft.com")
    document.load_defaults()
    document.add_custom_attributes(u"homepage", u"manu.com")
    document.add_custom_attributes(u'color', u'blue')
    document.remove_custom_attributes(u'Sport')
    document.add_repository(TEST_DIR)
    document.expand_dir(DATA_DIR)
    document.expand_dir(os.path.join(DATA_DIR,
                                     "subdir1"))
    document.share_files(DATA_DIR,
                         ["routage", "emptydir", "subdir1"])
    document.share_files(os.sep.join([DATA_DIR,
                                      "subdir1",
                                      "subsubdir"]),
                         ["null", "dummy.txt"])
    document.tag_file(os.path.join(DATA_DIR,
                                   "date.txt"),
                      u"tagos")
    document.tag_file(os.sep.join([DATA_DIR,
                                   "subdir1",
                                   "subsubdir",
                                   "null"]),
                      u"tag1")
    document.tag_file(os.sep.join([DATA_DIR,
                                   "subdir1",
                                   "subsubdir",
                                   "dummy.txt"]),
                      u"tag2")
    # set peers
    bruce = get_bruce_profile()
    bruce_doc = bruce.document
    bruce_blog = bruce.blog
    document.fill_data(PROFILE_BRUCE, bruce_doc)
    document.fill_blog(PROFILE_BRUCE, bruce_blog)
    document.make_friend(PROFILE_BRUCE)
    # write file
    if os.path.exists(FILE_TEST + PROFILE_EXT):
        os.remove(FILE_TEST + PROFILE_EXT)
    document.save(FILE_TEST + PROFILE_EXT)
