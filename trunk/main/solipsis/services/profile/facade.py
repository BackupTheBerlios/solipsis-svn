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

__revision__ = "$Id$"

import pickle

from StringIO import StringIO
from solipsis.services.profile import ENCODING, PROFILE_EXT
from solipsis.services.profile.view import HtmlView
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.blog import Blogs
from solipsis.services.profile.cache_document import CacheDocument

def create_facade(node_id):
    """implements pattern singleton on Facade. User may specify
    document end/or view to initialize facade with at creation"""
    Facade.s_facade = Facade(node_id)
    return Facade.s_facade

def get_facade():
    """implements pattern singleton on Facade. User may specify
    document end/or view to initialize facade with at creation"""
    return Facade.s_facade
    
class AbstractFacade:
    """manages user's actions & connects document and view"""
    
    def __init__(self, node_id, document):
        self._desc = PeerDescriptor(node_id,
                                    document=document,
                                    blog=Blogs())
        self.views = {}
        self._activated = True

    # views
    def add_view(self, view):
        """add  a view object to facade"""
        self.views[view.get_name()] = view
        view.import_desc(self._desc)

    # documents
    def import_document(self, document):
        """associate given document with peer"""
        self._desc.document.import_document(document)
        for view in self.views:
            view.import_desc(self._desc)

    # proxy
    def _try_change(self, setter, updater, *args, **kwargs):
        """Calls the setting function on a document (wich can be
        passed in **kwargs with the key 'document'), and calls the
        getting function on all views linked to the facade.

        returns value returned by setter"""
        if not 'document' in kwargs:
            document = self._desc.document
        else:
            document = kwargs['document']
        try:
            result = getattr(document, setter)(*args)
            for view in self.views.values():
                getattr(view, updater)()
            return result
        except TypeError, error:
            print >> stderr, str(error)
            raise
   
    def get_peers(self):
        """returns PeerDescriptor with given id"""
        return self._desc.document.get_peers()
   
    def get_peer(self, peer_id):
        """returns PeerDescriptor with given id"""
        return self._desc.document.get_peer(peer_id)
    
    # menu
    def save(self, doc_extension, directory=None):
        """save .profile.solipsis"""
        self._desc.save(directory=directory,
                        doc_extension=doc_extension)
            
    def load(self, doc_extension, directory=None):
        """load .profile.solipsis"""
        try:
            self._desc.load(directory=directory,
                            doc_extension=doc_extension)
        except ValueError, err:
            print err, ": Using blank one"
        # update
        for view in self.views.values():
            view.import_desc(self._desc)

class Facade(AbstractFacade):
    """manages user's actions & connects document and view"""
    
    s_facade = None

    def __init__(self, node_id):
        AbstractFacade.__init__(self, node_id, CacheDocument())

    # views
    def add_view(self, view):
        """add  a view object to facade"""
        AbstractFacade.add_view(self, view)
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
    
    # menu
    def export_profile(self, path):
        """write profile in html format"""
        html_file = open(path, "w")
        html_view = HtmlView(self._desc)
        html_file.write(html_view.get_view(True).encode(ENCODING))

    def save(self, directory=None):
        """save .profile.solipsis"""
        AbstractFacade.save(self, directory=directory, doc_extension=PROFILE_EXT)

    def load(self, directory=None):
        """load .profile.solipsis"""
        AbstractFacade.load(self, directory=directory, doc_extension=PROFILE_EXT)
        for view in self.views.values():
            view.update_blogs()

    # personal
    def change_pseudo(self, pseudo):
        """sets peer as friend """
        return self._try_change("set_pseudo",
                                "update_pseudo",
                                pseudo)
    
    def change_title(self, title):
        """sets new value for title"""
        return self._try_change("set_title",
                                "update_title",
                                title)

    def change_firstname(self, firstname):
        """sets new value for firstname"""
        return self._try_change("set_firstname",
                                "update_firstname",
                                firstname)

    def change_lastname(self, lastname):
        """sets new value for lastname"""
        return self._try_change("set_lastname",
                                "update_lastname",
                                lastname)

    def change_photo(self, path):
        """sets new value for photo"""
        return self._try_change("set_photo",
                                "update_photo",
                                path)

    def change_email(self, email):
        """sets new value for email"""
        return self._try_change("set_email",
                                "update_email",
                                email)

    # custom
    def add_custom_attributes(self, key, value):
        """sets new value for custom_attributes"""
        return self._try_change("add_custom_attributes",
                                "update_custom_attributes",
                                key, value)

    def del_custom_attributes(self, key):
        """sets new value for custom_attributes"""
        return self._try_change("remove_custom_attributes",
                                "update_custom_attributes",
                                key)

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
                              index)
        
    def add_comment(self, index, text, author):
        """store blog in cache as wx.HtmlListBox is virtual.
        return comment's index"""
        self._try_blog_change('add_comment',
                              'update_blogs',
                              index, text, author)
    
    # file
    def add_repository(self, path):
        """sets new value for repositor"""
        path = path.encode(ENCODING)
        return self._try_change("add_repository",
                                "build_files",
                                path)

    def del_repository(self, path):
        """sets new value for repositor"""
        path = path.encode(ENCODING)
        return self._try_change("del_repository",
                                "build_files",
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
        
    def recursive_expand(self, path):
        """update doc when dir expanded"""
        path = path.encode(ENCODING)
        return self._try_change("recursive_expand",
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

    # peer management   
    def set_data(self, peer_id, document, flag_update=True):
        """same as fill data but without updating views"""
        self._desc.document.fill_data(peer_id, document, flag_update)
        
    def set_connected(self, peer_id, connected):
        """change connected status of given peer and updates views"""
        return self._try_change("set_connected",
                                "update_peers",
                                peer_id, connected)
    
    def remove_peer(self, peer_id):
        """sets peer as friend """
        return self._try_change("remove_peer",
                                "update_peers",
                                peer_id)

    def fill_data(self, peer_id, document):
        """sets peer as friend """
        return self._try_change("fill_data",
                                "update_peers",
                                peer_id, document)

    def fill_blog(self, peer_id, blog):
        """sets peer as friend """
        return self._try_change("fill_blog",
                                "update_blogs",
                                peer_id, blog)
    
    def fill_shared_files(self, peer_id, files):
        """sets peer as friend """
        return self._try_change("fill_shared_files",
                                "build_files",
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

