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

from solipsis.services.profile import ENCODING, PROFILE_DIR, \
     BLOG_EXT, BULB_ON_IMG, BULB_OFF_IMG, VERSION

DEFAULT_TAG = u"none"
SHARING_ALL = -1

def assert_file(path):
    """raise ValueError if not a file"""
    assert os.path.isfile(path), \
           "[%s] not a valid file"% path

def assert_dir(path):
    """raise ValueError if not a file"""
    assert os.path.isdir(path), \
           "[%s] not a valid directory"% path
    
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
        # status
        self.pseudo = pseudo
        self.state = state
        self.connected = connected
        # data
        from solipsis.services.profile.document import CacheDocument
        self.document = document or CacheDocument(pseudo)
        self.blog = blog or Blogs(pseudo)
        self.shared_files = None
        # node_id
        self.node_id = None

    def __repr__(self):
        return "%s (%s)"% (self.pseudo, self.state)

    def copy(self):
        """return copied instance of PeerDescriptor"""
        return PeerDescriptor(self.pseudo,
                              self.document.copy(),
                              self.blog.copy(),
                              self.state,
                              self.connected)

    def load(self):
        """load both document & blog"""
        self.document.load()
        self.set_blog(load_blogs(self.pseudo))

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

    def set_shared_files(self, files):
        """blog is instance Blogs"""
        self.shared_files = files

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

def load_blogs(pseudo, directory=PROFILE_DIR):
    """use pickle to loas blogs. file name given without extension
    (same model as profile"""
    # reformating name
    file_name =  os.path.join(directory, pseudo)
    file_name += BLOG_EXT
    # loading
    if os.path.exists(file_name):
        blog_file = open(file_name)
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
        blogs._dir = PROFILE_DIR
        return blogs.copy()
    elif blogs.version == "0.2.0":
        # v 0.2.0: path derived from _id & _dir. owner becomes pseudo
        blogs.pseudo = blogs._id
        return blogs.copy()
    elif blogs.version == "0.2.1":
        # v 0.2.1: path derived from pseudo & dir. _id removed
        return blogs
    else:
        raise ValueError("blog format not recognized.")
        
    
class Blogs:
    """container for all blogs, responsible for authentification"""


    def __init__(self, pseudo, directory=PROFILE_DIR):
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
        blog_file = open(self.get_id(), 'w')
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
        self.text = text
        if not date:
            self.date = time.asctime()
        else:
            self.date = date
        self.author = author
        self.comments = []

    def __repr__(self):
        return "%s (%d)"% (self.text, len(self.comments))

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
               % (self.text, self.author, self.date)
    
    def _html_text(self):
        """return blog as main entry"""
        return "<p'>%s</p><p align='right'><cite>%s, %s</cite></p>"\
               % (self.text, self.author, self.date)
        
# FILES
#######

class SharedFiles(dict):
    """dict wrapper (useless for now)"""
    pass

class ContainerMixin:
    """Factorize sharing tools on containers"""
    
    def __init__(self, path, share=False, tag=DEFAULT_TAG):
        if not isinstance(path, unicode):
            raise TypeError("path [%s] expected as unicode"% path)
        self._tag = None
        self._shared = None
        self._data = None
        self.tag(tag)
        self.share(share)
        # init path
        self.path = ContainerMixin._validate(self, path)
        self.name = os.path.basename(self.path)

    def tag(self, tag):
        """set tag"""
        assert isinstance(tag, unicode), "tag '%s' must be unicode"% tag
        self._tag = tag

    def share(self, share=True):
        """set sharing status"""
        assert isinstance(share, bool), "share '%s' must be bool"% share
        self._shared = share

    def set_data(self, data):
        """used by GUI"""
        assert data, "data associated is None"
        self._data = data

    def get_data(self):
        """used by GUI"""
        return self._data
    
    def _validate(self, path):
        """assert path is valid"""
        if path.endswith(os.sep):
            path = path[:-1]
        return path

    def import_data(self, container):
        """copy data from container"""
        assert self.path == container.path, \
               "containers %s & %s not compatible"% (self, container)
        self.tag(container._tag)
        self.shared(container._shared)
        self._data = container._data
        
class FileContainer(ContainerMixin):
    """Structure to store files info in cache"""

    def __init__(self, path, share=False, tag=DEFAULT_TAG):
        ContainerMixin.__init__(self, path, share, tag)
        assert_file(path.encode(ENCODING))
        
    def __str__(self):
        return "Fc:%s(?%s,'%s')"% (self.name.encode(ENCODING),
                                   self._shared and "Y" or "-",
                                   self._tag.encode(ENCODING)  or "-")
    def __repr__(self):
        return str(self)

    def _validate(self, path):
        """assert path exists and is a file"""
        path = ContainerMixin._validate(self, path)
        assert_file(path.encode(ENCODING))
        return path
        
class DirContainer(dict, ContainerMixin):
    """Structure to store data in cache:
    
    [item, name, #shared, [data to display on right side]"""

    def __init__(self, path, share=False, tag=DEFAULT_TAG):
        ContainerMixin.__init__(self, path, share, tag)
        assert_dir(path.encode(ENCODING))
        dict.__init__(self)
        
    def __str__(self):
        return "{Dc:%s(?%s,'%s',#%d) : %s}"\
               %(self.name.encode(ENCODING),
                 self._shared and "Y" or "-",
                 self._tag.encode(ENCODING)  or "-",
                 self.nb_shared(),
                 str(self.values()))
    def __repr__(self):
        return str(self)

    def __getitem__(self, full_path):
        full_path = ContainerMixin._validate(self, full_path)
        container = self
        local_path = self._format_path(full_path)
        local_keys = [path for path in local_path.split(os.path.sep) if path]
        for local_key in local_keys:
            if not dict.has_key(container, local_key):
                container = container._add(local_key)
            else:
                container = dict.__getitem__(container, local_key)
        return container

    def __setitem__(self, full_path, value):
        full_path = ContainerMixin._validate(self, full_path)
        assert isinstance(value, ContainerMixin), \
               "Added value '%s' must be a sharable object" % value
        assert value.path.startswith(full_path), \
               "Added value '%s' not coherent with path '%s'"\
               % (value, full_path)
        container = self
        local_path = self._format_path(full_path)
        local_keys = [path for path in local_path.split(os.path.sep) if path]
        for local_key in local_keys:
            if value and container.path == os.path.dirname(full_path):
                # add value if defined AND right place to do so
                dict.__setitem__(container, os.path.basename(full_path), value)
            else:
                # create intermediary containers
                if not dict.has_key(container, local_key):
                    container = container._add(local_key)
                else:
                    container = dict.__getitem__(container, local_key)

    def __delitem__(self, full_path):
        full_path = ContainerMixin._validate(self, full_path)
        container = self[os.path.dirname(full_path)]
        dict.__delitem__(container, os.path.basename(full_path))

    def _validate(self, path):
        """assert path exists and is a file"""
        path = ContainerMixin._validate(self, path)
        # check included in self.path
        assert path.startswith(self.path), "'%s' not in container '%s'"\
               % (path, self.path)
        # check validity
        assert_dir(path.encode(ENCODING))
        # make path relative
        return path

    def _format_path(self, path):
        """assert path exists and is a file"""
        # check included in self.path
        assert path.startswith(self.path), "'%s' not in container '%s'"\
               % (path, self.path)
        # make path relative
        return path[len(self.path)+1:]

    def _add(self, local_key, value=None):
        """add File/DirContainer"""
        path = os.path.join(self.path, local_key)
        if os.path.isdir(path.encode(ENCODING)):
            dict.__setitem__(self, local_key, value or DirContainer(path))
        elif os.path.isfile(path.encode(ENCODING)):
            dict.__setitem__(self, local_key, value or FileContainer(path))
        else:
            raise AssertionError("%s not a valid file/dir" \
                                 % path.encode(ENCODING))
        return dict.__getitem__(self, local_key)

    def has_key(self, full_path):
        """overrides dict method"""
        full_path = ContainerMixin._validate(self, full_path)
        container = self
        local_path = self._format_path(full_path)
        local_keys = local_path.split(os.path.sep)
        for local_key in local_keys:
            if not dict.has_key(container, local_key):
                return False
            else:
                container = dict.__getitem__(container, local_key)
        return True

    def keys(self):
        """overrides dict methode"""
        # add owned keys
        all_keys = []
        all_keys += [os.path.join(self.path, key)
                     for key in dict.keys(self)]
        # add children's ones
        for container in [dir_c for dir_c in self.values()
                          if isinstance(dir_c, DirContainer)]:
            all_keys += container.keys()
        return all_keys

    def flat(self):
        """returns {path: container}"""
        result = {}
        all_keys = self.keys()
        for key in all_keys:
            result[key] = self[key]
        return result
            
    def add(self, full_path):
        """add File/DirContainer"""
        # __getitem__ adds path if does not exist
        self[full_path]
        
    def expand_dir(self, full_path=None):
        """put into cache new information when dir expanded in tree"""
        if full_path:
            assert_dir(full_path.encode(ENCODING))
            container = self[full_path]
        else:
            container = self
        for path in [os.path.join(container.path, path)
                     for path in os.listdir(container.path)]:
            container.add(path)

    def share_content(self, full_path, share=True):
        """wrapps sharing methods matching 'full_path' with list or path"""
        if isinstance(full_path, str) or isinstance(full_path, unicode):
            assert_dir(full_path.encode(ENCODING))
            self[full_path]._share_dir(share)
        elif isinstance(full_path, list) or isinstance(full_path, tuple):
            self._share_dirs(full_path, share)
        else:
            raise TypeError("full_path '%s' expected as list or string"\
                            % full_path)
        
    def _share_dirs(self, full_paths, share=True):
        """forward command to cache"""
        for full_path in full_paths:
            self[full_path]._share_dir(share)

    def _share_dir(self, share=True):
        """(un)share all files of directory; item by item"""
        for container in self.values():
            container.share(share)

    def share_container(self, full_path, share=True):
        """wrapps sharing methods matching 'full_path' with list or path"""
        if isinstance(full_path, unicode):
            self._share_file(full_path, share)
        elif isinstance(full_path, list) or isinstance(full_path, tuple):
            self._share_files(full_path, share)
        else:
            raise TypeError("full_path '%s' expected as list or unicode"\
                            % full_path)
        
    def _share_file(self, full_path, share=True):
        """share given files of dir"""
        self[full_path].share(share)
        
    def _share_files(self, full_paths, share=True):
        """share given files of dir"""
        for full_path in full_paths:
            self[full_path].share(share)

    def tag_container(self, full_path, tag=DEFAULT_TAG):
        """wrapps sharing methods matching 'full_path' with list or path"""
        if isinstance(full_path, unicode):
            self._tag_file(full_path, tag)
        elif isinstance(full_path, list) or isinstance(full_path, tuple):
            self._tag_files(full_path, tag)
        else:
            raise TypeError("full_path '%s' expected as list or unicode"\
                            % full_path)

    def _tag_files(self, full_paths, tag):
        """modify tag of shared file. Share file if not"""
        for full_path in full_paths:
            self[full_path].tag(tag)

    def _tag_file(self, full_path, tag):
        """modify tag of shared file. Share file if not"""
        self[full_path].tag(tag)

    def nb_shared(self):
        """return number of shared element"""
        if self._shared:
            return SHARING_ALL
        else:
            result = 0
            for container in self.values():
                if container._shared:
                    result += 1
            return result
