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

#TODO: refactor FlieContainer/DirContainer to fatcorise share/tag

class FileContainer:
    """Structure to store files info in cache"""

    def __init__(self, path, share=False, tag=DEFAULT_TAG):
        # check validity
        if not os.path.isfile(path):
            raise KeyError("%s not a valid file"% path)
        self.path = path
        self.name = os.path.basename(path)
        self._tag = tag
        self._shared = share
        self.item = None

    def __str__(self):
        return "%s%s"% (self.name, self._shared and " [shared]" or "")

    def __repr__(self):
        return "%s %s [%s]"% (self.path, self._shared and "[shared]" or "",
                              self._tag)

    def tag(self, tag):
        """set tag"""
        self._tag = tag

    def share(self, share=True):
        """set sharing status"""
        self._shared = share

    def set_item(self, item):
        """used by GUI"""
        self.item = item

    def get_item(self):
        """used by GUI"""
        return self.item
        
class DirContainer(dict):
    """Structure to store data in cache:
    
    [item, name, #shared, [data to display on right side]"""

    def __init__(self, path, share=False, tag=DEFAULT_TAG):
        dict.__init__(self)
        # remove last '/'
        if path.endswith('/'):
            path = path[:-1]
        # check validity
        if not os.path.isdir(path):
            raise KeyError("%s not a valid dir"% path)
        # set value
        self.path = path
        self.name = os.path.basename(path)
        self._shared = share
        self._tag = tag
        self.item = None

    def __str__(self):
        return "%s [%d]"% (self.name, self.nb_shared())

    def __repr__(self):
        return "%s(%s) [%d]"\
               % (self.path, self.name, self.nb_shared())

    def keys(self):
        """overrides dict methode"""
        all_keys = []
        all_keys += [os.path.join(self.path, key) for key in dict.keys(self)]
        for container in self.values():
            if isinstance(container, dict):
                all_keys += [os.path.join(container.path, key)
                             for key in container.keys()]
        return all_keys

    def _add(self, name, share=False, tag=DEFAULT_TAG):
        """add File/DirContainer"""
        if not self.has_key(name):
            full_path = os.path.join(self.path, name)
            if os.path.isdir(full_path):
                self[name] = DirContainer(full_path, share, tag)
            elif os.path.isfile(full_path):
                self[name] = FileContainer(full_path, share, tag)
            else:
                print >> sys.stderr, "% not a valid file/dir" % full_path
        # else: already added
    
    def tag(self, tag):
        """set tag"""
        self._tag = tag

    def share(self, share=True):
        """(un)share all files of directory"""
        self._shared = share

    def set_item(self, item):
        """used by GUI"""
        self.item = item

    def get_item(self):
        """used by GUI"""
        return self.item

    def expand(self):
        """list content of directory and cache it"""
        # add each dir of browsed dir
        for dir_name in os.listdir(self.path):
            self._add(dir_name)
        
    def share_files(self, names, share=True):
        """share given files of dir"""
        for name in names:
            try:
                self[name].share(share)
            except KeyError:
                self._add(name, share)
                

    def tag_files(self, names, tag):
        """modify tag of shared file. Share file if not"""
        for name in names:
            try:
                self[name].tag(tag)
            except KeyError:
                self._add(name, tag=tag)

    def nb_shared(self):
        """return number of shared element"""
        if self._shared:
            return -1
        else:
            result = 0
            for container in self.values():
                if container._shared:
                    result += 1
            return result

class SharingContainer(dict):
    """stores all DirContainer along with items"""

    def __init__(self, path):
        dict.__init__(self)
        # remove last '/'
        if path.endswith('/'):
            path = path[:-1]
        # set value
        self.path = path

    def __str__(self):
        return str(self.keys())

    def __repr__(self):
        return repr(self.keys())

    def __getitem__(self, full_path):
        # get leaf in tree corresponding to full_path
        dir_dict, leaf = self._browse_dicts(full_path)
        return dict.__getitem__(dir_dict, leaf)

    def __setitem__(self, full_path, value):
        # check validity
        if not isinstance(value, DirContainer) \
               and not isinstance(value, FileContainer):
            raise ValueError("Adding %s not supported"\
                             % value.__class__)
        # get leaf in tree corresponding to full_path
        dir_dict, leaf = self._browse_dicts(full_path)
        # set leaf
        dict.__setitem__(dir_dict, leaf, value)
        
    def __delitem__(self, full_path):
        # get leaf in tree corresponding to full_path
        dir_dict, leaf = self._browse_dicts(full_path)
        dict.__delitem__(dir_dict, leaf)

    def has_key(self, full_path):
        """overrides dict method"""
        # get leaf in tree corresponding to full_path
        dir_dict, leaf = self._browse_dicts(full_path)
        # check
        return dict.has_key(dir_dict, leaf)

    def keys(self):
        """overrides dict method. returns all keys of all dicts"""
        all_keys = []
        all_keys += [os.path.join(self.path, key) for key in dict.keys(self)]
        for dir_container in self.values():
            if isinstance(dir_container, dict):
                all_keys += [os.path.join(dir_container.path, key)
                             for key in dir_container.keys()]
        # check
        return all_keys

    def flat(self):
        """returns {path: tag}"""
        result = {}
        all_keys = self.keys()
        for key in all_keys:
            result[key] = self[key]._tag
        return result

    def add(self, full_path):
        """calls add_dir or add_file according to nature of full_path"""
        if os.path.isdir(full_path):
            return self.add_dir(full_path)
        elif os.path.isfile(full_path):
            return self.add_file(full_path)
        else:
            raise KeyError("%s not a valid file/dir"% full_path)
        
    def add_dir(self, full_path):
        """add shared directory to list"""
        # remove last '/'
        if full_path.endswith('/'):
            full_path = full_path[:-1]
        # check validity
        if not os.path.isdir(full_path):
            raise KeyError("%s not a dir"% full_path)
        # get leaf in tree corresponding to full_path
        dir_dict, leaf = self._browse_dicts(full_path)
        # add container
        if not dir_dict.has_key(leaf):
            dir_dict[leaf] = DirContainer(full_path)
        # return final container
        return dir_dict[leaf]

    def add_file(self, full_path):
        """add shared directory to list"""
        # check validity
        if not os.path.isfile(full_path):
            raise KeyError("%s not a dir"% full_path)
        # get leaf in tree corresponding to full_path
        dir_dict, leaf = self._browse_dicts(full_path)
        # add container
        if not dir_dict.has_key(leaf):
            dir_dict[leaf] = FileContainer(full_path)
        # return final container
        return dir_dict[leaf]

    def _browse_dicts(self, full_path):
        """call os.path.split on full_path and return couple:
         - dict corresponding to dirname
         - filename"""
        # remove last '/'
        if full_path.endswith('/'):
            full_path = full_path[:-1]
        # remove root_path not to create useless DirContainers
        if full_path.startswith(self.path):
            full_path = full_path[len(self.path)+1:]
        # extract all intermediate dirs
        path, leaf = os.path.split(full_path)
        all_dirs = path.split(os.path.sep)
        # add all intermediate dirs
        current_path = ""
        current_dict = self
        for key in [a_dir for a_dir in all_dirs if a_dir]:
            current_path = os.path.join(current_path, key)
            if not dict.has_key(current_dict, key):
                current_container = DirContainer(current_path)
                current_dict[key] = current_container
                current_dict = current_container
            else:
                current_dict = current_dict[key]
        # return last created dict
        return (current_dict, leaf)

    def expand_dir(self, full_path):
        """put into cache new information when dir expanded in tree"""
        if not self.has_key(full_path):
            container = self.add(full_path)
            container.expand()
        else:
            self[full_path].expand()
            
    def share_dir(self, full_path, share=True):
        """forward command to cache"""
        if not self.has_key(full_path):
            container = self.add(full_path)
            container.share(share)
        else:
            self[full_path].share(share)

    def share_files(self, full_path, names, share=True):
        """forward command to cache"""
        if not self.has_key(full_path):
            container = self.add(full_path)
            container.share_files(names, share)
        else:
            self[full_path].share_files(names, share)

    def tag_files(self, full_path, names, tag):
        """forward command to cache"""
        """forward command to cache"""
        if not self.has_key(full_path):
            container = self.add(full_path)
            container.tag_files(names, tag)
        else:
            self[full_path].tag_files(names, tag)

    def tag_file(self, full_path, tag):
        """forward command to cache"""
        if not self.has_key(full_path):
            container = self.add(full_path)
            container.tag(tag)
        else:
            self[full_path].tag(tag)
