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
    if not os.path.isfile(path):
        raise ValueError("[%s] not a valid file"% path)

def assert_dir(path):
    """raise ValueError if not a file"""
    if not os.path.isdir(path):
        raise ValueError("[%s] not a valid directory"% path)

class SharedMixin:
    """Factorize sharing tools on containers"""
    
    def __init__(self, share=False, tag=DEFAULT_TAG):
        self._tag = tag
        self._shared = share
        self._data = None

    def tag(self, tag):
        """set tag"""
        assert isinstance(tag, unicode), "tag must be unicode"
        self._tag = tag

    def share(self, share=True):
        """set sharing status"""
        assert isinstance(share, bool), "share must be bool"
        self._shared = share

    def set_data(self, data):
        """used by GUI"""
        self._data = data

    def get_data(self):
        """used by GUI"""
        return self._data
        
class FileContainer(SharedMixin):
    """Structure to store files info in cache"""

    def __init__(self, path, share=False, tag=DEFAULT_TAG):
        SharedMixin.__init__(self, share, tag)
        path = self.validate(path)
        self.path = path
        self.name = os.path.basename(path)

    def __str__(self):
        return "Fc:%s(?%s,'%s')"% (self.name, self._shared and "Y" or "-",
                                 self._tag  or "-")
    def __repr__(self):
        return str(self)

    def validate(self, path):
        """assert path exists and is a file"""
        assert os.path.exists(path), "[%s] does not exist"% path
        assert_file(path)
        return path
        
class DirContainer(dict, SharedMixin):
    """Structure to store data in cache:
    
    [item, name, #shared, [data to display on right side]"""

    def __init__(self, path, share=False, tag=DEFAULT_TAG):
        dict.__init__(self)
        SharedMixin.__init__(self, share, tag)
        path = self.validate(path)
        assert_dir(path)
        # set values
        self.path = path
        self.name = os.path.basename(path)
        
    def __str__(self):
        return "{Dc:%s(?%s,'%s',#%d) : %s}"\
               %(self.name, self._shared and "Y" or "-",
                 self._tag  or "-", self.nb_shared(), list(self.iteritems()))
    def __repr__(self):
        return str(self)

    def validate(self, path):
        """assert path exists and is a file"""
        # remove last '/'
        if path.endswith('/'):
            path = path[:-1]
        # check validity
        assert os.path.exists(path), "[%s] does not exist"% path
        return path

    def keys(self):
        """overrides dict methode"""
        # add owned keys
        all_keys = []
        all_keys += [os.path.join(self.path, key)
                     for key in dict.keys(self)]
        # add children's ones
        for container in self.values():
            if isinstance(container, dict):
                all_keys += container.keys()
        return all_keys

    def _add(self, path, share=False, tag=DEFAULT_TAG):
        """add File/DirContainer"""
        path = self.validate(path)
        name = os.path.basename(path)
        # add Container
        if not self.has_key(name):
            if os.path.isdir(path):
                self[name] = DirContainer(path, share, tag)
            elif os.path.isfile(path):
                self[name] = FileContainer(path, share, tag)
            else:
                print >> sys.stderr, "%s not a valid file/dir" % path
        # else: already added

    def expand(self):
        """list content of directory and cache it"""
        # add each dir of browsed dir
        for dir_name in os.listdir(self.path):
            self._add(os.path.join(self.path, dir_name))

    def share_content(self, share=True):
        """(un)share all files of directory; item by item"""
        for container in self.values():
            container.share(share)
        
    def share_files(self, names, share=True):
        """share given files of dir"""
        for name in names:
            try:
                self[name].share(share)
            except KeyError:
                self._add(os.path.join(self.path, name), share=share)

    def tag_files(self, names, tag):
        """modify tag of shared file. Share file if not"""
        for name in names:
            try:
                self[name].tag(tag)
            except KeyError:
                self._add(os.path.join(self.path, name), tag=tag)

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

class SharingContainer(dict, SharedMixin):
    """stores all DirContainer along with items"""

    def __init__(self, path):
        dict.__init__(self)
        SharedMixin.__init__(self)
        path = self.validate(path)
        self.path = path
        # init_content
        self.expand_root()

    def validate(self, path):
        """assert path exists and is a file"""
        assert path, "empty path '%s'"% path
        # remove last '/'
        if path.endswith('/'):
            path = path[:-1]
        # check validity
        assert os.path.exists(path), "[%s] does not exist"% path
        return path

    def __getitem__(self, full_path):
        dir_dict, leaf = self._browse_dicts(full_path)
        return dict.__getitem__(dir_dict, leaf)

    def __setitem__(self, full_path, value):
        assert isinstance(value, SharedMixin), "[%s] not a container"% value
        dir_dict, leaf = self._browse_dicts(full_path)
        dict.__setitem__(dir_dict, leaf, value)
        
    def __delitem__(self, full_path):
        dir_dict, leaf = self._browse_dicts(full_path)
        dict.__delitem__(dir_dict, leaf)

    def has_key(self, full_path):
        """overrides dict method"""
        dir_dict, leaf = self._browse_dicts(full_path)
        return dict.has_key(dir_dict, leaf)

    def keys(self):
        """overrides dict method. returns all keys of all dicts"""
        all_keys = []
        all_keys += [os.path.join(self.path, key) for key in dict.keys(self)]
        for dir_container in self.values():
            if isinstance(dir_container, dict):
                all_keys += [os.path.join(dir_container.name, key)
                             for key in dir_container.keys()]
        return all_keys

    def add(self, full_path):
        """calls add_dir or add_file according to nature of full_path"""
        full_path = self.validate(full_path)        
        if os.path.isdir(full_path):
            return self.add_dir(full_path)
        elif os.path.isfile(full_path):
            return self.add_file(full_path)
        else:
            raise ValueError("%s not a valid file/dir"% full_path)
        
    def add_dir(self, full_path):
        """add shared directory to list"""
        dir_dict, leaf = self._browse_dicts(full_path)
        assert_dir(full_path)
        # add container
        if not dict.has_key(dir_dict, leaf):
            dict.__setitem__(dir_dict, leaf, DirContainer(full_path))
        # return final container
        return dict.__getitem__(dir_dict, leaf)

    def add_file(self, full_path):
        """add shared directory to list"""
        dir_dict, leaf = self._browse_dicts(full_path)
        assert_file(full_path)
        # add container
        if not dict.has_key(dir_dict, leaf):
            dict.__setitem__(dir_dict, leaf, FileContainer(full_path))
        # return final container
        return dict.__getitem__(dir_dict, leaf)

    def _browse_dicts(self, full_path):
        """call os.path.split on full_path and return couple:
         - dict corresponding to dirname
         - filename"""
        full_path = self.validate(full_path)
        # remove root_path not to create useless DirContainers
        if full_path == self.path:
            raise AssertionError("no leaf in '%s'"% full_path)
        elif full_path.startswith(self.path):
            full_path = full_path[len(self.path)+1:]
        else:
            raise ValueError("file '%s' not in repository '%s'"\
                             %(full_path, self.path))
        # extract all intermediate dirs
        path, leaf = os.path.split(full_path)
        all_dirs = path.split(os.path.sep)
        # add all intermediate dirs
        current_path = ""
        current_dict = self
        for key in [a_dir for a_dir in all_dirs if a_dir]:
            current_path = os.path.join(current_path, key)
            if not dict.has_key(current_dict, key):
                current_container = DirContainer(os.path.join(self.path,
                                                              current_path))
                dict.__setitem__(current_dict, key, current_container)
                current_dict = current_container
            else:
                current_dict = dict.__getitem__(current_dict, key)
        # return last created dict
        return (current_dict, leaf)

    def expand_dir(self, full_path):
        """put into cache new information when dir expanded in tree"""
        full_path = self.validate(full_path)
        if full_path == self.path:
            self.expand_root()
        else:
            if not self.has_key(full_path):
                container = self.add(full_path)
                container.expand()
            else:
                self[full_path].expand()

    def expand_root(self):
        """put into cache new information when dir expanded in tree"""
        for full_name in [os.path.join(self.path, name) for name in os.listdir(self.path)]:
            if not dict.has_key(self, full_name):
                if os.path.isdir(full_name):
                    dict.__setitem__(self, os.path.basename(full_name),
                                     DirContainer(full_name))
                else:
                    dict.__setitem__(self, os.path.basename(full_name),
                                     FileContainer(full_name))
            #else already added
        
    def flat(self):
        """returns {path: tag}"""
        result = {}
        all_keys = self.keys()
        for key in all_keys:
            result[key] = self[key]
        return result
            
    def share_dirs(self, full_paths, share=True):
        """forward command to cache"""
        for full_path in full_paths:
            full_path = self.validate(full_path)
            assert_dir(full_path)
            if not self.has_key(full_path):
                container = self.add(full_path)
                container.share_content(share)
            else:
                self[full_path].share_content(share)

    def share_files(self, path, names, share=True):
        """forward command to cache"""
        path = self.validate(path)
        for full_path in [os.path.join(path, name) for name in names]:
            self.share_file(full_path, share)

    def share_file(self, full_path, share=True):
        """forward command to cache"""
        full_path = self.validate(full_path)
        if not self.has_key(full_path):
            container = self.add(full_path)
            container.share(share)
        else:
            self[full_path].share(share)

    def tag_files(self, path, names, tag):
        """forward command to cache"""
        path = self.validate(path)
        for full_path in [os.path.join(path, name) for name in names]:
            self.tag_file(full_path, tag)

    def tag_file(self, full_path, tag):
        """forward command to cache"""
        full_path = self.validate(full_path)
        if not self.has_key(full_path):
            container = self.add(full_path)
            container.tag(tag)
        else:
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

