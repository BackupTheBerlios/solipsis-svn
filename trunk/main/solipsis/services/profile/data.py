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
import sys

DEFAULT_TAG = u"none"
SHARING_ALL = -1

def assert_file(path):
    """raise ValueError if not a file"""
    assert os.path.isfile(path), "[%s] not a valid file"% path

def assert_dir(path):
    """raise ValueError if not a file"""
    assert os.path.isdir(path), "[%s] not a valid directory"% path

class ContainerMixin:
    """Factorize sharing tools on containers"""
    
    def __init__(self, path, share=False, tag=DEFAULT_TAG):
        self._tag = tag
        self._shared = share
        self._data = None
        # init path
        self.path = ContainerMixin._validate(self, path)
        self.name = os.path.basename(path)

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
        return path
        
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
        assert os.path.exists(path), "[%s] does not exist"% path
        assert_file(path)
        return path
        
class DirContainer(dict, ContainerMixin):
    """Structure to store data in cache:
    
    [item, name, #shared, [data to display on right side]"""

    def __init__(self, path, share=False, tag=DEFAULT_TAG):
        ContainerMixin.__init__(self, path, share, tag)
        dict.__init__(self)
        
    def __str__(self):
        return "{Dc:%s(?%s,'%s',#%d) : %s}"\
               %(self.name, self._shared and "Y" or "-",
                 self._tag  or "-", self.nb_shared(), list(self.iteritems()))
    def __repr__(self):
        return str(self)

    def __getitem__(self, full_path):
        if self.path == full_path:
            return self
        #else: check children
        local_path = self._validate(full_path)
        local_key = local_path.split(os.path.sep)[0]
        if not dict.has_key(self, local_key):
            self._add(local_key)
        return dict.__getitem__(self, local_key)[full_path]

    def __setitem__(self, full_path, value):
        # remove last '/'
        if full_path.endswith('/'):
            full_path = full_path[:-1]
        print "***", full_path, value
        assert isinstance(value, ContainerMixin), \
               "Added value '%s' must be a sharable object" % value
        assert value.path.startswith(full_path), \
               "Added value '%s' not coherent with path '%s'"\
               % (value, full_path)
        local_path = self._validate(full_path)
        local_key = local_path.split(os.path.sep)[0]
        print "***", local_path, local_key
        if self.path == os.path.dirname(full_path):
            dict.__setitem__(self, local_key, value)
        else:
            dict.__getitem__(self, local_key)[full_path] = value

    def __delitem__(self, full_path):
        # remove last '/'
        if full_path.endswith('/'):
            full_path = full_path[:-1]
        if self.path == os.path.dirname(full_path):
            if dict.has_key(self, local_key):
                container = dict.__getitem__(self, os.path.basename(full_path))
                del container
            else:
                print >> sys.stderr, "%s already deleted"% full_path
        else:
            local_path = self._validate(full_path)
            local_key = local_path.split(os.path.sep)[0]
            container = dict.__getitem__(self, local_key)
            del container

    def _validate(self, path):
        """assert path exists and is a file"""
        path = ContainerMixin._validate(self, path)
        # check included in self.path
        assert path.startswith(self.path), "'%s' not in container '%s'"\
               % (path, self.path)
        # check validity
        assert os.path.exists(path), "[%s] does not exist"% path
        assert_dir(path)
        # make path relative
        return path[len(self.path):]

    def _add(self, local_key, value=None):
        """add File/DirContainer"""
        path = os.path.join(self.path, local_key)
        if os.path.isdir(path):
            self[local_key] = value or DirContainer(path)
        elif os.path.isfile(path):
            self[local_key] = value or FileContainer(path)
        else:
            print >> sys.stderr, "%s not a valid file/dir" % path

    def has_key(self, full_path):
        """overrides dict method"""
        #else: check children
        local_path = self._validate(full_path)
        local_key = local_path.split(os.path.sep)[0]
        if dict.has_key(self, local_key):
            return True
        else:
            return dict.__getitem__(self, local_key).has_key(full_path)

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
            
    def add(self, full_path, share=False, tag=DEFAULT_TAG):
        """add File/DirContainer"""
        container = self[full_path]
        container.tag(tag)
        container.share(share)
        
    def expand_dir(self, full_path):
        """put into cache new information when dir expanded in tree"""
        container = self[full_path]
        for full_path in os.listdir(self.path):
            container.add(full_path)

    def share_content(self, full_path, share=True):
        """wrapps sharing methods matching 'full_path' with list or path"""
        if isinstance(full_path, str) or isinstance(full_path, unicode):
            self._share_dir(full_path, share)
        elif isinstance(full_path, list) or isinstance(full_path, tuple):
            self._share_dirs(full_path, share)
        else:
            raise TypeError("full_path '%s' expected as list or string"\
                            % full_path)
        
    def _share_dirs(self, full_paths, share=True):
        """forward command to cache"""
        for full_path in full_paths:
            self[full_path].share_dir(share)

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
