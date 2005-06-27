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

import pickle

from sys import stderr
from StringIO import StringIO
from solipsis.services.profile import ENCODING, PROFILE_DIR
from solipsis.services.profile.data import PeerDescriptor, Blogs
from solipsis.services.profile.document import CacheDocument
from solipsis.services.profile.view import HtmlView

def get_facade(peer_id=None, directory=PROFILE_DIR, pseudo=None):
    """implements pattern singleton on Facade. User may specify
    document end/or view to initialize facade with at creation"""
    if not Facade.s_facade:
        assert peer_id, "Facade must be created with user's id"
        Facade.s_facade = Facade(pseudo, peer_id, directory)
    else:
        if peer_id:
            f_id = Facade.s_facade._desc.peer_id
            assert f_id == peer_id,  "given pseudo %s does not match id %s" \
                   % (peer_id, f_id)
        #else: nothing to do but returning facade
    return Facade.s_facade

class Facade:
    """manages user's actions & connects document and view"""
    
    s_facade = None

    def __init__(self, pseudo, peer_id, directory=PROFILE_DIR):
        self._desc = PeerDescriptor(peer_id,
                                    document=CacheDocument(peer_id, directory),
                                    blog=Blogs(pseudo, peer_id, directory),
                                    pseudo=pseudo)
        self._activated = True
        self.views = {}

    def get_pseudo(self):
        """return pseudo"""
        return self._desc.get_pseudo()

    def get_id(self):
        """return pseudo"""
        return self._desc.peer_id

    # views
    def add_view(self, view):
        """add  a view object to facade"""
        self.views[view.get_name()] = view
        view.import_document(self._desc.document)
        view.update_blogs(self._desc.blog)

    # documents
    def get_document(self):
        """return document associated with peer"""
        return self._desc.document

    def import_document(self, document):
        """associate given document with peer"""
        self._desc.document.import_document(document)
        for view in self.views:
            view.import_document(document)

    # blog
    def add_blog(self, text):
        """store blog in cache as wx.HtmlListBox is virtual.
        return blog's index"""
        self._desc.blog.add_blog(text, self._desc.peer_id)
        self.update_blogs()

    def remove_blog(self, index):
        """delete blog"""
        self._desc.blog.remove_blog(index, self._desc.peer_id)
        self.update_blogs()
        
    def add_comment(self, (index, text, author)):
        """store blog in cache as wx.HtmlListBox is virtual.
        return comment's index"""
        self._desc.blog.add_comment(index, text, author)
        self.update_blogs()

    def get_blogs(self):
        """return all blogs along with their comments"""
        return self._desc.blog

    def get_blog(self, index):
        """return all blogs along with their comments"""
        return self._desc.blog.get_blog(index)

    def count_blogs(self):
        """return number of blogs"""
        return self._desc.blog.count_blogs()

    def update_blogs(self):
        """trigger update of views with new blogs"""
        for view in self.views.values():
            view.update_blogs(self._desc.blog)

    # proxy
    def _try_change(self, value, setter, updater):
        """tries to call function doc_set and then, if succeeded, gui_update"""
        try:
            result = getattr(self._desc.document, setter)(value)
            for view in self.views.values():
                getattr(view, updater)()
            return result
        except TypeError, error:
            print >> stderr, str(error)
            raise

    def get_profile(self):
        """return a file object like on profile"""
        return self._desc.document.open()

    def get_blog_file(self):
        """return a file object like on blog"""
        return StringIO(pickle.dumps(self._desc.blog))

    def get_shared_files(self):
        """return a file object like on blog"""
        return StringIO(pickle.dumps(self._desc.document.get_shared_files()))
        
    def get_file_container(self, name):
        """forward command to cache"""
        return self._desc.document.get_container(name)
    
    def get_peer(self, peer_id):
        """returns PeerDescriptor with given id"""
        return self._desc.document.get_peer(peer_id)
    
    def has_peer(self, peer_id):
        """returns PeerDescriptor with given id"""
        return self._desc.document.has_peer(peer_id)
    
    # MENU
    def activate(self, enable=True):
        """desactivate automatic sharing"""
        self._activated = enable

    def is_activated(self):
        """getter for self._activated"""
        return self._activated

    def export_profile(self, path):
        """write profile in html format"""
        html_file = open(path, "w")
        html_view = HtmlView(self._desc.document)
        html_file.write(html_view.get_view(True).encode(ENCODING))
    
    def save_profile(self):
        """save .profile.solipsis"""
        self._desc.save()

    def load_profile(self):
        """load .profile.solipsis"""
        # clean
        for view in self.views.values():
            view.reset_files()
        # load
        try:
            self._desc.load()
        except ValueError, err:
            print err, "Using blank one"
        # update
        for view in self.views.values():
            view.import_document(self._desc.document)
        self.update_blogs()

    # PERSONAL TAB
    def change_title(self, title):
        """sets new value for title"""
        return self._try_change(title,
                                "set_title",
                                "update_title")

    def change_firstname(self, firstname):
        """sets new value for firstname"""
        return self._try_change(firstname,
                               "set_firstname",
                               "update_firstname")

    def change_lastname(self, lastname):
        """sets new value for lastname"""
        return self._try_change(lastname,
                               "set_lastname",
                               "update_lastname")

    def change_photo(self, path):
        """sets new value for photo"""
        return self._try_change(path,
                               "set_photo",
                               "update_photo")

    def change_email(self, email):
        """sets new value for email"""
        return self._try_change(email,
                               "set_email",
                               "update_email")

    def change_download_repo(self, path):
        """sets new value for description"""
        return self._try_change(path,
                               "set_download_repo",
                               "update_download_repo")

    # CUSTOM TAB
    def add_custom_attributes(self, (key, value)):
        """sets new value for custom_attributes"""
        return self._try_change((key, value),
                               "add_custom_attributes",
                               "update_custom_attributes")

    def del_custom_attributes(self, key):
        """sets new value for custom_attributes"""
        return self._try_change(key,
                               "remove_custom_attributes",
                               "update_custom_attributes")

    # FILE TAB
    def add_repository(self, path):
        """sets new value for repositor"""
        return self._try_change(path,
                               "add_repository",
                               "update_files")
    
    def remove_repository(self, path):
        """sets new value for repositor"""
        return self._try_change(path,
                               "remove_repository",
                               "update_files")
    
    def expand_dir(self, path):
        """update doc when dir expanded"""
        return self._try_change(path,
                               "expand_dir",
                               "update_files")
        
    def expand_children(self, path):
        """update doc when dir expanded"""
        return self._try_change(path,
                               "expand_children",
                               "update_files")
    
    def share_dirs(self, (path, share)):
        """forward command to cache"""
        return self._try_change((path, share),
                               "share_dirs",
                               "update_files")

    def share_files(self, (path, names, share)):
        """forward command to cache"""
        return self._try_change((path, names, share),
                               "share_files",
                               "update_files")

    def share_file(self, (path, share)):
        """forward command to cache"""
        return self._try_change((path, share),
                               "share_file",
                               "update_files")

    def tag_files(self, (path, names, tag)):
        """forward command to cache"""
        return self._try_change((path, names, tag),
                               "tag_files",
                               "update_files")

    def tag_file(self, (path, tag)):
        """forward command to cache"""
        return self._try_change((path, tag),
                               "tag_file",
                               "update_files")

    # OTHERS TAB
    def add_peer(self, value):
        """sets peer as friend """
        return self._try_change(value,
                                "add_peer",
                                "update_peers")
    
    def remove_peer(self, value):
        """sets peer as friend """
        return self._try_change(value,
                                "remove_peer",
                                "update_peers")

    def set_connected(self, (peer_id, connected)):
        """change connected status of given peer and updates views"""
        return self._try_change((peer_id, connected),
                                "set_connected",
                                "update_peers")

    def fill_data(self, (peer_id, document)):
        """sets peer as friend """
        return self._try_change((peer_id, document),
                                "fill_data",
                                "update_peers")

    def fill_blog(self, (peer_id, blog)):
        """sets peer as friend """
        return self._try_change((peer_id, blog),
                                "fill_blog",
                                "display_blog")
    
    def fill_shared_files(self, (peer_id, files)):
        """sets peer as friend """
        return self._try_change((peer_id, files),
                                "fill_shared_files",
                                "display_files")

    def make_friend(self, peer_id):
        """sets peer as friend """
        return self._try_change(peer_id,
                               "make_friend",
                               "update_peers")

    def blacklist_peer(self, peer_id):
        """black list peer"""
        return self._try_change(peer_id,
                               "blacklist_peer",
                               "update_peers")

    def unmark_peer(self, peer_id):
        """black list peer"""
        return self._try_change(peer_id,
                               "unmark_peer",
                               "update_peers")
