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
"""Define cache structures used in profile and rendered in list widgets"""

__revision__ = "$Id: data.py 894 2005-10-11 18:39:43Z emb $"

import os, os.path
import pickle
import time
import gettext
_ = gettext.gettext

from solipsis.services.profile.message import display_warning, display_error
from solipsis.services.profile import ENCODING, PROFILE_EXT, \
     BLOG_EXT, BULB_ON_IMG, BULB_OFF_IMG, VERSION
from solipsis.services.profile.prefs import get_prefs

class Blogs:
    """container for all blogs, responsible for authentification"""

    def __init__(self, blogs=None):
        if blogs is None:
            self.blogs = []
        else:
            self.blogs = blogs
        # tag class to be enable retro-compatibility
        self.version = VERSION

    def __str__(self):
        return str(self.blogs)

    def __getitem__(self, index):
        return self.blogs[index]

    def save(self, path):
        """use pickle to save to blog_file"""
        # saving
        blog_file = open(path, 'wb')
        pickle.dump(self, file=blog_file, protocol=pickle.HIGHEST_PROTOCOL)
        blog_file.close()

    def copy(self):
        """return new instance of Blogs with same attributes"""
        copied = Blogs()
        for index, blog in enumerate(self.blogs):
            copied.add_blog(blog.text, blog.author, blog.date)
            for comment in blog.comments:
                copied.add_comment(index, comment.text, blog.author, blog.date)
        return copied

    def add_blog(self, text, author, date=None):
        """store blog in cache as wx.HtmlListBox is virtual.
        return blog's id"""
        self.blogs.append(Blog(text, author, date))

    def add_comment(self, index, text, author=None, date=None):
        """get blog at given index and delegate add_comment to it"""
        try:
            blog = self.get_blog(index)
            blog.add_comment(text, author, date)
        except IndexError, err:
            display_error(_("Could not add comment: blog not valid"),
                          error=err)

    def remove_blog(self, index):
        """delete blog"""
        try:
            del self.blogs[index]
        except IndexError, err:
            display_warning(_("Blog already deleted."),
                            error=err)
        
    def get_blog(self, index):
        """return all blogs along with their comments"""
        return self.blogs[index]

    def count_blogs(self):
        """return number of blogs"""
        return len(self.blogs)
        
class Blog:
    """Entry of a blog, including comments"""

    def __init__(self, text, author, date=None):
        assert isinstance(text, unicode)
        self.text = text
        if not date:
            self.date = time.asctime()
        else:
            self.date = date
        self.author = author
        self.comments = []

    def __repr__(self):
        return "%s (%d)"% (self.text.encode(ENCODING), len(self.comments))

    def add_comment(self, text, pseudo, date=None):
        """add sub blog (comment) to blog"""
        self.comments.append(Blog(text, pseudo, date))

    def count_blogs(self):
        """return number of blogs"""
        return len(self.comments)
        
    def html(self):
        """return html view of blog"""
        blog_html = self._html_text()
        for comment in self.comments:
            blog_html += comment._html_comment()
        return blog_html
    
    def _html_comment(self):
        """format blog as comment"""
        return """<font color='silver' size='-1'>
  <p>%s</p>
  <p align='right'><cite>%s, %s</cite></p>
</font>"""\
               % (self.text.encode(ENCODING),
                  self.author.encode(ENCODING),
                  self.date)
    
    def _html_text(self):
        """return blog as main entry"""
        return "<p>%s</p><p align='right'><cite>%s, %s</cite></p>"\
               % (self.text.encode(ENCODING),
                  self.author.encode(ENCODING),
                  self.date)

# high level functions ###############################################
def load_blogs(path):
    """use pickle to load blogs. file name given without extension
    (same model as profile"""
    # loading
    if os.path.exists(path):
        blog_file = open(path, "rb")
        blogs = pickle.load(blog_file)
        blog_file.close()
        return retro_compatibility(blogs)
    else:
        return Blogs()

def retro_compatibility(blogs):
    """make sure that downloaded version is the good one"""
    if not hasattr(blogs, "version"):
        # v 0.1.0: self.owner & self.blogs only
        return Blogs(blogs.blogs)
    elif blogs.version == "0.2.0":
        # v 0.2.0: + self._id & self._dir added
        #            self.owner becomes self.pseudo
        return Blogs(blogs.blogs)
    elif blogs.version in ["0.2.1", "0.2.2"]:
        # v 0.2.1: - self._id removed
        return Blogs(blogs.blogs)
    elif blogs.version == "0.3.0":
        # v 0.3.0: - self.pseudo & self._dir removed 
        return blogs
    elif blogs.version == "0.4.0":
        # v 0.4.0: - moved classes in module blog.py
        return blogs
    else:
        display_warning(_("Could not read blog file. Using a blank one."))
        
