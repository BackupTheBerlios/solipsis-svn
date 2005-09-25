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

import os, os.path
import pickle
import time

from solipsis.services.profile import ENCODING, \
     BLOG_EXT, BULB_ON_IMG, BULB_OFF_IMG, VERSION
from solipsis.services.profile.prefs import get_prefs

# PEERS
#######

class PeerDescriptor:
    """contains information relative to peer"""

    ANONYMOUS = 'Anonym'
    FRIEND = 'Friend'
    BLACKLISTED = 'Blacklisted'
    COLORS = {ANONYMOUS: 'black',
              FRIEND:'blue',
              BLACKLISTED:'red'}
    
    def __init__(self, pseudo, document=None, blog=None,
                 state=ANONYMOUS, connected=False):
        assert isinstance(pseudo, unicode), "pseudo must be a unicode"
        # status
        self.pseudo = pseudo
        self.state = state
        self.connected = connected
        # data
        from solipsis.services.profile.cache_document import CacheDocument
        self.document = document or CacheDocument(pseudo)
        self.blog = blog or Blogs(pseudo)
        # node_id
        self.node_id = None

    def __str__(self):
        return "PeerDescriptor %s"% self.pseudo.encode(ENCODING)

    def __repr__(self):
        return "%s (%s)"% (self.pseudo, self.state)

    def get_id(self):
        """return id associated with peer (id of node)"""
        return self.node_id

    def copy(self):
        """return copied instance of PeerDescriptor"""
        return PeerDescriptor(self.pseudo,
                              self.document.copy(),
                              self.blog.copy(),
                              self.state,
                              self.connected)

    def load(self, checked=True):
        """load both document & blog"""
        self.document.load(checked=checked)
        self.set_blog(load_blogs(self.pseudo, self.document._dir))

    def save(self):
        """save both document & blog"""
        self.document.save()
        self.blog.save()

    def set_connected(self, enable):
        """change user's connected status"""
        self.connected = enable

    def set_blog(self, blog):
        """blog is instance Blogs"""
        self.blog = blog

    def set_document(self, document):
        """set member of type AbstractDocument"""
        self.document = document

    def set_node_id(self, node_id):
        """set when peer_desc is assciated with a node"""
        self.node_id = node_id
        
    def html(self):
        """render peer in HTML"""
        return "<img src='%s'/><font color=%s>%s</font>"\
               % (self.connected and BULB_ON_IMG() or BULB_OFF_IMG(),
                  PeerDescriptor.COLORS[self.state],
                  self.pseudo)
    
# BLOGS
#######

def load_blogs(pseudo, directory=None):
    """use pickle to loas blogs. file name given without extension
    (same model as profile"""
    if directory is None:
        directory = get_prefs("profile_dir")
    # reformating name
    file_name =  os.path.join(directory, pseudo)
    file_name += BLOG_EXT
    # loading
    if os.path.exists(file_name):
        blog_file = open(file_name, "rb")
        blogs = pickle.load(blog_file)
        blog_file.close()
        return retro_compatibility(blogs)
    else:
        raise ValueError("blog file %s not found"% file_name)

def retro_compatibility(blogs):
    """make sure that downloaded version is the good one"""
    if not hasattr(blogs, "version"):
        # v 0.1.0: owner only
        blogs.pseudo = blogs.owner
        blogs._dir = get_prefs("profile_dir")
        return blogs.copy()
    elif blogs.version == "0.2.0":
        # v 0.2.0: path derived from _id & _dir. owner becomes pseudo
        blogs.pseudo = blogs._id
        return blogs.copy()
    elif blogs.version in ["0.2.1", "0.2.2"]:
        # v 0.2.1: path derived from pseudo & dir. _id removed
        return blogs
    else:
        raise ValueError("blog format not recognized.")
        
    
class Blogs:
    """container for all blogs, responsible for authentification"""

    def __init__(self, pseudo, directory=None):
        assert isinstance(pseudo, unicode), "pseudo must be a unicode"
        if directory is None:
            directory = get_prefs("profile_dir")
        self.pseudo = pseudo 
        self._dir = directory
        self.blogs = []
        # tag class to be enable retro-compatibility
        self.version = VERSION

    def __str__(self):
        return str(self.blogs)

    def __getitem__(self, index):
        return self.blogs[index]

    def get_id(self):
        """return file name of blog"""
        return os.path.join(self._dir, self.pseudo) + BLOG_EXT

    def save(self):
        """use pickle to save to blog_file"""
        # saving
        blog_file = open(self.get_id(), 'wb')
        pickle.dump(self, file=blog_file, protocol=pickle.HIGHEST_PROTOCOL)
        blog_file.close()

    def copy(self):
        """return new instance of Blogs with same attributes"""
        copied = Blogs(self.pseudo, self._dir)
        for index, blog in enumerate(self.blogs):
            copied.add_blog(blog.text, blog.author, blog.date)
            for comment in blog.comments:
                copied.add_comment(index, comment.text, blog.author, blog.date)
        return copied

    def add_blog(self, text, author, date=None):
        """store blog in cache as wx.HtmlListBox is virtual.
        return blog's id"""
        if author != self.pseudo:
            raise AssertionError("not authorized")
        else:
            self.blogs.append(Blog(text, author, date))

    def add_comment(self, index, text, author=None, date=None):
        """get blog at given index and delegate add_comment to it"""
        blog = self.get_blog(index)
        blog.add_comment(text, author, date)

    def remove_blog(self, index, pseudo):
        """delete blog"""
        if pseudo != self.pseudo:
            raise AssertionError("not authorized")
        else:
            if index < len(self.blogs):
                del self.blogs[index]
            else:
                raise AssertionError('blog id %s not valid'% index)
        
    def get_blog(self, index):
        """return all blogs along with their comments"""
        if index < len(self.blogs):
            return self.blogs[index]
        else:
            raise AssertionError('blog id %s not valid'% index)

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
               % (self.text.encode(ENCODING), self.author, self.date)
    
    def _html_text(self):
        """return blog as main entry"""
        return "<p'>%s</p><p align='right'><cite>%s, %s</cite></p>"\
               % (self.text.encode(ENCODING), self.author, self.date)
