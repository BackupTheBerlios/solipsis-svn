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

from os.path import isdir, isfile
import os

DEFAULT_TAG = u"none"

class FileContainer:
    """Structure to store files info in cache"""

    def __init__(self, path, name, share=True, tag=DEFAULT_TAG):
        if not isfile(path):
            raise ValueError("%s not a valid file"% name)
        self.path = path
        self.name = name
        self._tag = tag
        self.shared = share

    def __str__(self):
        return "%s%s"% (self.name, self.shared and " [shared]" or "")

    def __repr__(self):
        return "%s %s [%s]"% (self.path, self.shared and "[shared]" or "",
                              self._tag)

    def tag(self, tag):
        """set tag"""
        self._tag = tag

    def share(self, share=True):
        """set sharing status"""
        self.shared = share
        
class DirContainer:
    """Structure to store data in cache:
    
    [item, name, #shared, [data to display on right side]"""

    def __init__(self, path, item=None):
        if not isdir(path):
            raise ValueError("%s not a valid dir"% path)
        self.path = path
        self.name = path.split(os.path.sep)[-1]
        self.item = item
        self.content = {}
        self.share_content(False)

    def __str__(self):
        return "%s [%d]"% (self.name, self.nb_shared())

    def __repr__(self):
        return "%s %s [%d]"% (self.name, str(self.content), self.nb_shared())

    def share_content(self, share=True):
        """(un)share all files of directory"""
        self.share_files([name for name in os.listdir(self.path)
                          if isfile(os.path.join(self.path, name))],
                         share)
        
    def share_files(self, names, share=True):
        """share given files of dir"""
        for name in names:
            if not self.content.has_key(name):
                self.content[name] = FileContainer(os.path.join(self.path, name),
                                              name, share)
            else:
                self.content[name].share(share)

    def tag_files(self, names, tag):
        """modify tag of shared file. Share file if not"""
        for name in names:
            if not self.content.has_key(name):
                self.content[name] = FileContainer(os.path.join(self.path, name),
                                              name, False, tag)
            else:
                self.content[name].tag(tag)

    def nb_shared(self):
        """return number of shared element"""
        result = 0
        for file_container in self.content.values():
            if file_container.shared:
                result += 1
        return result

class SharingContainer:
    """stores all DirContainer along with items"""

    def __init__(self):
        self.data = {}

    def __str__(self):
        return str(self.get_all_dirs())

    def __repr__(self):
        return self.get_all_dirs().__repr__()

    def add_dir(self, full_path):
        """add shared directory to list"""
        dir_container = DirContainer(full_path)
        # add in cache
        self.data[full_path] = dir_container
        return dir_container

    def remove_dir(self, full_path):
        """add shared directory to list"""
        del self.data[full_path]

    def expand_dir(self, full_path):
        """put into cache new information when dir expanded in tree"""
        dir_container = self.data[full_path]
        result = {}
        # add each dir of browsed dir
        for dir_name in [os.path.join(dir_container.path, name)
                         for name in os.listdir(dir_container.path)]:
            if isdir(dir_name):
                result[dir_name] = self.add_dir(dir_name)
            else:
                # not a dir, do nothing
                pass
        return result
            
    def share_dir(self, full_path, share=True):
        """forward command to cache"""
        container = self.data[full_path]
        container.share_content(share)

    def share_files(self, full_path, names, share=True):
        """forward command to cache"""
        container = self.data[full_path]
        container.share_files(names, share)

    def tag_files(self, full_path, names, tag):
        """forward command to cache"""
        self.data[full_path].tag_files(names, tag)
        
    def get_dir_content(self, full_path):
        """return data assocaited with a DirContainer"""
        return self.data[full_path].content
        
    def get_all_dirs(self):
        """return data assocaited with a DirContainer"""
        result = self.data.keys()
        result.sort()
        return result
