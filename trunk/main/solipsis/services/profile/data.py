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
import time
import sys

DEFAULT_TAG = u"none"
SHARING_ALL = -1

def assert_file(path):
    """raise ValueError if not a file"""
    assert os.path.isfile(path), "[%s] not a valid file"% path

def assert_dir(path):
    """raise ValueError if not a file"""
    assert os.path.isdir(path), "[%s] not a valid directory"% path

class Blogs:
    """container for all blogs, responsible for authentification"""

    def __init__(self, owner=None):
        self.owner = owner
        self.blogs = []

    def __str__(self):
        return str(self.blogs)

    def __getitem__(self, index):
        return self.blogs[index]

    def set_owner(self, pseudo):
        for blog in self.blogs:
            for comment in blog.comments:
                if comment.author == self.owner:
                    comment.set_author(pseudo)
            blog.set_author(pseudo)
        self.owner = pseudo

    def add_blog(self, text, author):
        """store blog in cache as wx.HtmlListBox is virtual.
        return blog's id"""
        if author != self.owner:
            raise AssertionError("not authorized")
        else:
            self.blogs.append(Blog(text, author))

    def remove_blog(self, index, pseudo):
        """delete blog"""
        if pseudo != self.owner:
            raise AssertionError("not authorized")
        else:
            if index<len(self.blogs):
                del self.blogs[index]
            else:
                raise AssertionError('blog id %s not valid'% index)
        
    def get_blog(self, index):
        """return all blogs along with their comments"""
        if index<len(self.blogs):
            return self.blogs[index]
        else:
            raise AssertionError('blog id %s not valid'% index)

    def count_blogs(self):
        """return number of blogs"""
        return len(self.blogs)

        
class Blog:

    def __init__(self, text, author):
        self.text = text
        self.date = time.asctime()
        self.author = author
        self.comments = []

    def __repr__(self):
        return "%s (%d)"% (self.text, len(self.comments))

    def set_author(self, author):
        self.author = author

    def add_comment(self, text, pseudo):
        self.comments.append(Blog(text, pseudo))
        
    def html(self):
        blog_html = self._html_text()
        for comment in self.comments:
            blog_html += comment._html_comment()
        return blog_html
    
    def _html_comment(self):
        return "<font color='silver' size='-1'><p>%s</p><p align='right'><cite>%s, %s</cite></font></p>"\
               % (self.text, self.author, self.date)
    
    def _html_text(self):
        return "<p'>%s</p><p align='right'><cite>%s, %s</cite></p>"\
               % (self.text, self.author, self.date)

class ContainerMixin:
    """Factorize sharing tools on containers"""
    
    def __init__(self, path, share=False, tag=DEFAULT_TAG):
        self._tag = tag
        self._shared = share
        self._data = None
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
        self._data = data

    def get_data(self):
        """used by GUI"""
        return self._data
    
    def _validate(self, path):
        """assert path is valid"""
        if path.endswith('/'):
            path = path[:-1]
        assert os.path.exists(path), "[%s] does not exist"% path
        return path

    def import_data(self, container):
        """copy data from container"""
        assert self.path == container.path, "containers %s & %s not compatible"% (self, container)
        self._tag = container._tag
        self._shared = container._shared
        self._data = container._data
        
class FileContainer(ContainerMixin):
    """Structure to store files info in cache"""

    def __str__(self):
        return "Fc:%s(?%s,'%s')"% (self.name, self._shared and "Y" or "-",
                                 self._tag  or "-")
    def __repr__(self):
        return str(self)

    def _validate(self, path):
        """assert path exists and is a file"""
        path = ContainerMixin._validate(self, path)
        assert_file(path)
        return path
        
class DirContainer(dict, ContainerMixin):
    """Structure to store data in cache:
    
    [item, name, #shared, [data to display on right side]"""

    def __init__(self, path, share=False, tag=DEFAULT_TAG):
        ContainerMixin.__init__(self, path, share, tag)
        assert_dir(path)
        dict.__init__(self)
        
    def __str__(self):
        return "{Dc:%s(?%s,'%s',#%d) : %s}"\
               %(self.name, self._shared and "Y" or "-",
                 self._tag  or "-", self.nb_shared(), str(self.values()))
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
        assert_dir(path)
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
        if os.path.isdir(path):
            dict.__setitem__(self, local_key, value or DirContainer(path))
        elif os.path.isfile(path):
            dict.__setitem__(self, local_key, value or FileContainer(path))
        else:
            print >> sys.stderr, "%s not a valid file/dir" % path
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
        """returns {path: tag}"""
        result = {}
        all_keys = self.keys()
        for key in all_keys:
            result[key] = self[key]
        return result
            
    def add(self, full_path):
        """add File/DirContainer"""
        container = self[full_path]
        
    def expand_dir(self, full_path):
        """put into cache new information when dir expanded in tree"""
        assert_dir(full_path)
        container = self[full_path]
        for full_path in [os.path.join(container.path, path) for path in os.listdir(container.path)]:
            container.add(full_path)

    def share_content(self, full_path, share=True):
        """wrapps sharing methods matching 'full_path' with list or path"""
        if isinstance(full_path, str) or isinstance(full_path, unicode):
            assert_dir(full_path)
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
        if isinstance(full_path, str) or isinstance(full_path, unicode):
            self._share_file(full_path, share)
        elif isinstance(full_path, list) or isinstance(full_path, tuple):
            self._share_files(full_path, share)
        else:
            raise TypeError("full_path '%s' expected as list or string"\
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
        if isinstance(full_path, str) or isinstance(full_path, unicode):
            self._tag_file(full_path, tag)
        elif isinstance(full_path, list) or isinstance(full_path, tuple):
            self._tag_files(full_path, tag)
        else:
            raise TypeError("full_path '%s' expected as list or string"\
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
