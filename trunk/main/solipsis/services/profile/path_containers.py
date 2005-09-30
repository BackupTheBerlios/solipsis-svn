# -*- coding: iso-8859-1 -*-
# pylint: disable-msg=W0131
# Missing docstring
#
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

__revision__ = "$Id$"

import os, os.path
import stat

from solipsis.services.profile import ENCODING

DEFAULT_TAG = u"none"

def assert_file(path):
    if not os.path.isfile(path):
        raise ContainerException("[%s] not a valid file"% path)

def assert_dir(path):
    if not os.path.isdir(path):
        raise ContainerException("[%s] not a valid directory"% path)

def create_container(path, cb_share=None, checked=True,
                  share=False, tag=DEFAULT_TAG):
    """when 'checked' is True, returns asserted Contaienrs, meaning
    Container which pasth have been checked as bvalid. Otherwise,
    return simple DictContainers which may represent non existing
    files"""
    if checked:
        if os.path.isdir(path):
            return DirContainer(path, cb_share=cb_share,
                                share=share, tag=tag)
        else:
            assert_file(path)
            return FileContainer(path, cb_share=cb_share,
                                share=share, tag=tag)
    else:
        return DictContainer(path, cb_share=cb_share,
                             share=share, tag=tag)

class ContainerException(Exception):
    pass
    
class SharedFiles(dict):
    """dict wrapper (useless for now)"""

    def flatten(self):
        """convert tree of containers to array"""
        result = []
        for containers in self.values():
            result += containers
        return result

    def __str__(self):
        result = [container.name for container in self.flatten()]
        return "\n".join(result)

class ContainerMixin:
    """Factorize sharing tools on containers"""
    
    def __init__(self, path, cb_share=None, share=False, tag=DEFAULT_TAG):
        if not isinstance(path, str):
            raise ContainerException("path [%s] expected as string"% path)
        # init path
        path =  ContainerMixin._validate(self, path)
        self._paths = path.split(os.sep)
        self.name = self._paths[-1]
        # init other members
        self._tag = None
        self.tag(tag)
        self._data = None
        # sharing process
        self.on_share = cb_share
        self._shared = False
        self.share(share)

    def copy(self, validator=None):
        """deep copy of container, without callbacks"""
        if (not validator) or validator(self):
            return self.__class__(self.get_path(),
                                  share=self._shared,
                                  tag=self._tag)
        else:
            return None

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

    def get_path(self):
        """return well formated path correspondinf to file"""
        return os.sep.join(self._paths)

    def get_parent_path(self):
        """return well formated path correspondinf to file"""
        return os.sep.join(self._paths[:-1])
    
    def _validate(self, path):
        """assert path is valid"""
        if path.endswith(os.sep):
            path = path[:-1]
        return path

class DictContainer(dict, ContainerMixin):
    """Tree Structure to store data in cache in the way the explorater
    of file_system does"""

    def __init__(self, path, cb_share=None,
                 share=False, tag=DEFAULT_TAG):
        ContainerMixin.__init__(self, path, cb_share=cb_share,
                                share=share, tag=tag)
        dict.__init__(self)
        
    def __str__(self):
        return "{%s(?%s,'%s') : %s}"\
               %(self.name,
                 self._shared and "Y" or "-",
                 self._tag.encode(ENCODING)  or "-",
                 str(self.values()))
    
    def __repr__(self):
        return str(self)

    def copy(self, validator=None):
        """deep copy of container, without callbacks"""
        copied_c = ContainerMixin.copy(self, validator)
        if not copied_c is None:
            for child in self.values():
                copied_child = child.copy(validator)
                if not copied_child is None:
                    dict.__setitem__(copied_c, copied_child.name, copied_child)
        return copied_c

    def _format_path(self, path):
        """assert path exists and is a file"""
        container_path = self.get_path()
        # check included in path
        if not path.startswith(container_path):
            raise ContainerException("'%s' not in container '%s'"\
                                     % (path, container_path))
        # make path relative
        return path[len(container_path)+1:]

    def _add(self, local_key, value=None):
        """add Container"""
        path = os.path.join(self.get_path(), local_key)
        dict.__setitem__(self, local_key,
                         value or DictContainer(path))
        return dict.__getitem__(self, local_key)

    def __getitem__(self, full_path):
        full_path = ContainerMixin._validate(self, full_path)
        local_path = self._format_path(full_path)
        local_keys = [path for path in local_path.split(os.path.sep) if path]
        # walk through containers
        container = self
        for local_key in local_keys:
            if not dict.has_key(container, local_key):
                container = container._add(local_key)
            else:
                container = dict.__getitem__(container, local_key)
        return container

    def __setitem__(self, full_path, value):
        full_path = ContainerMixin._validate(self, full_path)
        if not isinstance(value, ContainerMixin):
            raise ContainerException("Added value '%s' must be a sharable" \
                                     % value)
        if not value.get_path().startswith(full_path):
            raise ContainerException("Added value '%s' not coherent with '%s'"\
                                     % (value, full_path))
        container = self
        local_path = self._format_path(full_path)
        local_keys = [path for path in local_path.split(os.path.sep) if path]
        for local_key in local_keys:
            container_path = container.get_path()
            if value and container_path == os.path.dirname(full_path):
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
        path = self.get_path()
        all_keys = []
        all_keys += [os.path.join(path, key)
                     for key in dict.keys(self)]
        # add children's ones
        for container in [dir_c for dir_c in self.values()
                          if isinstance(dir_c, DictContainer)]:
            all_keys += container.keys()
        return all_keys

    def flat(self):
        """returns {path: container}"""
        result = []
        result += self.values()
        for container in result[:]:
            if isinstance(container, DictContainer):
                result += container.flat()
        return result
            
    def add(self, full_path):
        """add Container"""
        # __getitem__ adds path if does not exist
        self[full_path]

    def recursive_share(self, share=True):
        """set sharing status"""
        ContainerMixin.share(self, share)
        for container in self.values():
            container.share(share)
        # recursive_share must returns errors which occured during
        # sharing. Which is to say: none
        return []

class FileContainer(ContainerMixin):
    """Structure to store files info in cache"""

    def __init__(self, path, cb_share=None, share=False, tag=DEFAULT_TAG):
        ContainerMixin.__init__(self, path, cb_share, share, tag)
        assert_file(self.get_path())
        self.size = os.stat(self.get_path())[stat.ST_SIZE]
        
    def __str__(self):
        return "Fc:%s(?%s,'%s')"% (self.name,
                                   self._shared and "Y" or "-",
                                   self._tag.encode(ENCODING)  or "-")
    def __repr__(self):
        return str(self)
    
    def share(self, share=True):
        """set sharing status"""
        if share != self._shared:
            if self.on_share:
                self.on_share(share)            
            ContainerMixin.share(self, share)

class DirContainer(DictContainer):
    """Enrich DictContainer with call back on sharing (counting nb
    shared) and validation of paths."""

    def __init__(self, path, cb_share=None, share=False, tag=DEFAULT_TAG):
        DictContainer.__init__(self, path, cb_share=cb_share,
                               share=share, tag=tag)
        assert_dir(self.get_path())
        self._nb_shared = 0
        
    def __str__(self):
        return "{Dc:%s(?%s,'%s',#%d) : %s}"\
               %(self.name,
                 self._shared and "Y" or "-",
                 self._tag.encode(ENCODING)  or "-",
                 self.nb_shared(),
                 str(self.values()))

    def _add(self, local_key, value=None):
        """add Container"""
        path = os.path.join(self.get_path(), local_key)
        if os.path.isdir(path):
            dict.__setitem__(self, local_key,
                             value or DirContainer(path, self.add_shared))
        elif os.path.isfile(path):
            dict.__setitem__(self, local_key,
                             value or FileContainer(path, self.add_shared))
        else:
            raise ContainerException("%s not a valid file/dir" % path)
        return dict.__getitem__(self, local_key)

    def share(self, share=True):
        """set sharing status"""
        ContainerMixin.share(self, share)
        for container in self.values():
            if isinstance(container, FileContainer):
                container.share(share)

    def recursive_share(self, share=True):
        """set sharing status of content recursively"""
        ContainerMixin.share(self, share)
        errors = self.expand_dir()
        for container in self.values():
            if isinstance(container, DirContainer):
                errors += container.expand_dir()
                errors += container.recursive_share(share)
            else:
                container.share(share)
        return errors
                
    def add_shared(self, addition=True):
        """update number of shared element"""
        self._nb_shared += addition and 1 or -1
        if self.on_share:
            self.on_share(addition)

    def nb_shared(self):
        """return number of shared element"""
        return self._nb_shared
        
    def expand_dir(self, full_path=None):
        """put into cache new information when dir expanded in tree"""
        errors = []
        if full_path:
            assert isinstance(full_path, str), "expand_dir expects a string"
            assert_dir(full_path)
            container = self[full_path]
        else:
            container = self
        container_path = container.get_path()
        for file_name in os.listdir(container_path):
            path = os.path.join(container_path, file_name)
            try:
                container.add(path)
            except ContainerException, err:
                errors.append(str(err))
        return errors
