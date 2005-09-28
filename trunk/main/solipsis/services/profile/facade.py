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
"""Design pattern Facade: presents working API for all actions of GUI
available. This facade will be used both by GUI and unittests."""

__revision__ = "$Id: $"

import pickle

from StringIO import StringIO
from solipsis.services.profile import ENCODING, PROFILE_EXT, FILTER_EXT
from solipsis.services.profile.view import HtmlView
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.simple_facade import SimpleFacade
from solipsis.services.profile.filter_document import FilterDocument

def create_facade(node_id):
    """implements pattern singleton on Facade. User may specify
    document end/or view to initialize facade with at creation"""
    Facade.s_facade = Facade(node_id)
    return Facade.s_facade

def get_facade():
    """implements pattern singleton on Facade. User may specify
    document end/or view to initialize facade with at creation"""
    return Facade.s_facade

def create_filter_facade(node_id):
    """implements pattern singleton on FilterFacade"""
    FilterFacade.filter_facade = FilterFacade(node_id)
    return FilterFacade.filter_facade

def get_filter_facade():
    """implements pattern singleton on FilterFacade"""
    return FilterFacade.filter_facade

class FilterFacade(SimpleFacade):
    """facade associating a FilterDocument and a FilterView"""

    filter_facade = None

    def __init__(self, node_id):
        SimpleFacade.__init__(self, node_id)
        self._desc = PeerDescriptor(node_id,
                                    document=FilterDocument())

    def save(self, directory=None):
        """save .profile.solipsis"""
        SimpleFacade.save(self, directory=directory, doc_extension=FILTER_EXT)

    def load(self, directory=None):
        """load .profile.solipsis"""
        SimpleFacade.load(self, directory=directory, doc_extension=FILTER_EXT)
    
    def add_repository(self, key, filter_value):
        """sets new value for repositor"""
        return self._try_change("add_repository",
                                "update_files",
                                key, filter_value)

class Facade(SimpleFacade):
    """manages user's actions & connects document and view"""
    
    s_facade = None

    def __init__(self, node_id):
        SimpleFacade.__init__(self, node_id)

    # views
    def add_view(self, view):
        """add  a view object to facade"""
        SimpleFacade.add_view(self, view)
        view.update_blogs()

    # proxy
    def _try_blog_change(self, setter, updater, *args):
        """tries to call function doc_set and then, if succeeded, gui_update"""
        return self._try_change(setter, updater,
                                *args,
                                **{'document':self._desc.blog})
    
    def get_blog_file(self):
        """return a file object like on blog"""
        return StringIO(pickle.dumps(self._desc.blog))

    def get_shared_files(self):
        """return a file object like on blog"""
        return StringIO(pickle.dumps(self._desc.document.get_shared_files()))
        
    def get_file_container(self, name):
        """forward command to cache"""
        if isinstance(name, unicode):
            name = name.encode(ENCODING)
        return self._desc.document.get_container(name)
    
    # MENU
    def export_profile(self, path):
        """write profile in html format"""
        html_file = open(path, "w")
        html_view = HtmlView(self._desc)
        html_file.write(html_view.get_view(True).encode(ENCODING))

    def save(self, directory=None):
        """save .profile.solipsis"""
        SimpleFacade.save(self, directory=directory, doc_extension=PROFILE_EXT)

    def load(self, directory=None):
        """load .profile.solipsis"""
        SimpleFacade.load(self, directory=directory, doc_extension=PROFILE_EXT)
        for view in self.views.values():
            view.update_blogs()

    # blog
    def add_blog(self, text):
        """store blog in cache as wx.HtmlListBox is virtual.
        return blog's index"""
        self._try_blog_change('add_blog',
                              'update_blogs',
                              text, self._desc.document.get_pseudo())

    def remove_blog(self, index):
        """delete blog"""
        self._try_blog_change('remove_blog',
                              'update_blogs',
                              index, self._desc.document.get_pseudo())
        
    def add_comment(self, index, text, author):
        """store blog in cache as wx.HtmlListBox is virtual.
        return comment's index"""
        self._try_blog_change('add_comment',
                              'update_blogs',
                              index, text, author)
    
    # FILE TAB
    def add_repository(self, path):
        """sets new value for repositor"""
        path = path.encode(ENCODING)
        return self._try_change("add_repository",
                                "update_files",
                                path)

    def del_repository(self, path):
        """sets new value for repositor"""
        path = path.encode(ENCODING)
        return self._try_change("del_repository",
                                "update_files",
                                path)
    
    def expand_dir(self, path):
        """update doc when dir expanded"""
        path = path.encode(ENCODING)
        return self._try_change("expand_dir",
                                "update_files",
                                path)
        
    def expand_children(self, path):
        """update doc when dir expanded"""
        path = path.encode(ENCODING)
        return self._try_change("expand_children",
                               "update_files",
                                path)
    
    def recursive_share(self, path, share):
        """forward command to cache"""
        path = path.encode(ENCODING)
        return self._try_change("recursive_share",
                                "update_files",
                                path, share)

    def share_files(self, path, names, share):
        """forward command to cache"""
        path = path.encode(ENCODING)
        names = [name.encode(ENCODING) for name in names]
        return self._try_change("share_files",
                                "update_files",
                                path, names, share)

    def share_file(self, path, share):
        """forward command to cache"""
        path = path.encode(ENCODING)
        return self._try_change("share_file",
                                "update_files",
                                path, share)

    def tag_file(self, path, tag):
        """forward command to cache"""
        path = path.encode(ENCODING)
        return self._try_change("tag_file",
                                "update_files",
                                path, tag)

    # PEER MANAGEMENT   
    def set_connected(self, peer_id, connected):
        """change connected status of given peer and updates views"""
        return self._try_change("set_connected",
                                "update_peers",
                                peer_id, connected)

    def fill_blog(self, peer_id, blog):
        """sets peer as friend """
        return self._try_change("fill_blog",
                                "update_blogs",
                                peer_id, blog)
    
    def fill_shared_files(self, peer_id, files):
        """sets peer as friend """
        return self._try_change("fill_shared_files",
                                "update_files",
                                peer_id, files)

    def make_friend(self, peer_id):
        """sets peer as friend """
        return self._try_change("make_friend",
                                "update_peers",
                                peer_id)

    def blacklist_peer(self, peer_id):
        """black list peer"""
        return self._try_change("blacklist_peer",
                                "update_peers",
                                peer_id)

    def unmark_peer(self, peer_id):
        """black list peer"""
        return self._try_change("unmark_peer",
                                "update_peers",
                                peer_id)
