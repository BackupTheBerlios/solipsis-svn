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
import os.path

from sys import stderr
from StringIO import StringIO
from solipsis.services.profile import ENCODING, \
      PROFILE_DIR, PROFILE_FILE, BLOG_EXT
from solipsis.services.profile.data import DirContainer, \
     Blogs, load_blogs
from solipsis.services.profile.document import FileDocument

def get_facade(doc=None, view=None, blog_path=None):
    """implements pattern singleton on Facade. User may specify
    document end/or view to initialize facade with at creation"""
    if not Facade.s_facade:
        Facade.s_facade = Facade()
        # load blog
        if not blog_path:
            blog_path = os.path.join(PROFILE_DIR,
                                     PROFILE_FILE + BLOG_EXT)
        Facade.s_facade.blogs = load_blogs(blog_path)
        # import document
        doc and Facade.s_facade.add_document(doc)
        view and Facade.s_facade.add_view(view)
    else:
        doc and Facade.s_facade.reset_document(doc)
        view and Facade.s_facade.reset_view(view)
    return Facade.s_facade

class Facade:
    """manages user's actions & connects document and view"""
    
    s_facade = None

    def __init__(self):
        self.documents = {}
        self.views = {}
        self.blogs = Blogs()
        self.activated = True

    # views
    def add_view(self, view):
        """add  a view object to facade"""
        self.views[view.get_name()] = view

    def reset_view(self, view=None):
        """add  a view object to facade"""
        self.views.clear()
        if view:
            self.views[view.get_name()] = view

    # documents
    def add_document(self, doc):
        """add  a view object to facade"""
        # syncrhonize existing docs
        if "cache" in self.documents:
            doc.import_document(self.documents["cache"])
        # add new
        self.documents[doc.get_name()] = doc

    def get_document(self, name):
        """return document named 'name' if available, first otherwise"""
        if name in self.documents:
            return self.documents[name]
        else:
            return self.documents.values() \
                   and self.documents.values()[0] or None

    def reset_document(self, doc=None):
        """add  a view object to facade"""
        self.documents.clear()
        if doc:
            self.documents[doc.get_name()] = doc
        
    # blog
    def add_blog(self, text):
        """store blog in cache as wx.HtmlListBox is virtual.
        return blog's index"""
        pseudo = self.get_document('cache').get_pseudo()
        self.blogs.add_blog(text, pseudo)
        for view in self.views.values():
            view.update_blogs(self.blogs)

    def remove_blog(self, index):
        """delete blog"""
        pseudo = self.get_document('cache').get_pseudo()
        self.blogs.remove_blog(index, pseudo)
        for view in self.views.values():
            view.update_blogs(self.blogs)
        
    def add_comment(self, (index, text)):
        """store blog in cache as wx.HtmlListBox is virtual.
        return comment's index"""
        pseudo = self.get_document('cache').get_pseudo()
        self.blogs.add_comment(index, text, pseudo)
        for view in self.views.values():
            view.update_blogs(self.blogs)

    def get_blogs(self):
        """return all blogs along with their comments"""
        return self.blogs

    def get_blog(self, index):
        """return all blogs along with their comments"""
        return self.blogs.get_blog(index)

    def count_blogs(self):
        """return number of blogs"""
        return self.blogs.count_blogs()

    # proxy
    def _try_change(self, value, setter, updater):
        """tries to call function doc_set and then, if succeeded, gui_update"""
        result = {}
        for document in self.documents.values():
            try:
                result[document.name] = getattr(document, setter)(value)
            except TypeError, error:
                print >> stderr, "%s: %s"% (document.name, str(error))
                raise
        for view in self.views.values():
            getattr(view, updater)()
        return result

    def get_profile(self):
        """return a file object like on profile"""
        return self.get_document("cache").open()

    def get_blog_file(self):
        """return a file object like on blog"""
        return StringIO(pickle.dumps(self.blogs))

    def get_shared_files(self):
        """return a file object like on blog"""
        document = self.get_document("cache")
        return StringIO(pickle.dumps(document.get_shared_files()))
    
    # MENU
    def activate(self, enable=True):
        """desactivate automatic sharing"""
        self.activated = enable

    def is_activated(self):
        """getter for self.activated"""
        return self.activated
    
    def save_profile(self, path=None):
        """save .profile.solipsis"""
        if "file" in self.documents:
            file_doc = self.documents["file"]
        else:
            file_doc = FileDocument()
        # refresh file document to be sure to save updated data
        if "cache" in self.documents:
            self.documents["file"].import_document(self.documents["cache"])
        else:
            print "no cache available"
        # save
        file_doc.save(path)
        # save blog
        self.blogs.save(path + BLOG_EXT)

    def load_profile(self, path):
        """save .profile.solipsis"""
        #load profile
        if "file" in self.documents:
            self.documents["file"].load(path)
        for name, doc in self.documents.iteritems():
            name != "file" and doc.import_document(self.documents["file"])
        for view in self.views.values():
            view.import_document()

    def export_profile(self, path):
        """save .profile.solipsis"""
        html_file = open(path, "w")
        html_file.write(self.views["html"].get_view().encode(ENCODING))

    def set_auto_refresh_html(self, enable):
        """sets new preview for peer"""
        if "html" in self.views:
            self.views["html"].set_auto_refresh(enable)
    
    def refresh_html_preview(self):
        """sets new preview for peer"""
        if "html" in self.views:
            self.views["html"].update_view()
    
    # PERSONAL TAB
    def change_title(self, value):
        """sets new value for title"""
        return self._try_change(value,
                               "set_title",
                               "update_title")

    def change_firstname(self, value):
        """sets new value for firstname"""
        return self._try_change(value,
                               "set_firstname",
                               "update_firstname")

    def change_lastname(self, value):
        """sets new value for lastname"""
        return self._try_change(value,
                               "set_lastname",
                               "update_lastname")

    def change_pseudo(self, value):
        """sets new value for pseudo"""
        self.blogs.set_owner(value)
        return self._try_change(value,
                               "set_pseudo",
                               "update_pseudo")

    def change_photo(self, value):
        """sets new value for photo"""
        return self._try_change(value,
                               "set_photo",
                               "update_photo")

    def change_email(self, value):
        """sets new value for email"""
        return self._try_change(value,
                               "set_email",
                               "update_email")

    def change_birthday(self, value):
        """sets new value for birthday"""
        return self._try_change(value,
                               "set_birthday",
                               "update_birthday")

    def change_language(self, value):
        """sets new value for language"""
        return self._try_change(value,
                               "set_language",
                               "update_language")

    def change_address(self, value):
        """sets new value for """
        return self._try_change(value,
                               "set_address",
                               "update_address")

    def change_postcode(self, value):
        """sets new value for postcode"""
        return self._try_change(value,
                               "set_postcode",
                               "update_postcode")

    def change_city(self, value):
        """sets new value for city"""
        return self._try_change(value,
                               "set_city",
                               "update_city")

    def change_country(self, value):
        """sets new value for country"""
        return self._try_change(value,
                               "set_country",
                               "update_country")

    def change_description(self, value):
        """sets new value for description"""
        return self._try_change(value,
                               "set_description",
                               "update_description")

    # CUSTOM TAB
    def change_hobbies(self, value):
        """sets new value for hobbies"""
        return self._try_change(value,
                               "set_hobbies",
                               "update_hobbies")

    def add_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        return self._try_change(value,
                               "add_custom_attributes",
                               "update_custom_attributes")

    def del_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        return self._try_change(value,
                               "remove_custom_attributes",
                               "update_custom_attributes")

    # FILE TAB
    def add_repository(self, value):
        """sets new value for repositor"""
        return self._try_change(value,
                               "add_repository",
                               "update_files")
    
    def remove_repository(self, value):
        """sets new value for repositor"""
        return self._try_change(value,
                               "remove_repository",
                               "update_files")
    
    def expand_dir(self, value):
        """update doc when dir expanded"""
        return self._try_change(value,
                               "expand_dir",
                               "update_files")
    
    def share_dirs(self, pair):
        """forward command to cache"""
        return self._try_change(pair,
                               "share_dirs",
                               "update_files")

    def share_files(self, triplet):
        """forward command to cache"""
        return self._try_change(triplet,
                               "share_files",
                               "update_files")

    def share_file(self, pair):
        """forward command to cache"""
        return self._try_change(pair,
                               "share_file",
                               "update_files")

    def tag_files(self, triplet):
        """forward command to cache"""
        return self._try_change(triplet,
                               "tag_files",
                               "update_files")

    def tag_file(self, pair):
        """forward command to cache"""
        return self._try_change(pair,
                               "tag_file",
                               "update_files")
        
    def get_file_container(self, name):
        """forward command to cache"""
        if "cache" in self.documents:
            return self.documents["cache"].get_container(name)
        else:
            return self.documents.values()[0].get_container(name)
        
    def get_container(self, view, name):
        """forward command to document associated with given view"""
        return self.views[view].document.get_container(name)
    
    def expand_children(self, view, value):
        """update doc when dir expanded"""
        container = self.get_container(view, value)
        for dir_container in [cont for cont in container.values()
                              if isinstance(cont, DirContainer)]:
            self.expand_dir(dir_container.path)
        self.views[view].update_files()

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
    
    def get_peer(self, peer_id):
        """returns PeerDescriptor with given id"""
        return self.get_document('cache').get_peer(peer_id)
    
    def has_peer(self, peer_id):
        """returns PeerDescriptor with given id"""
        return self.get_document('cache').has_peer(peer_id)

    def fill_data(self, (peer_id, document)):
        """sets peer as friend """
        return self._try_change((peer_id, document),
                                "fill_data",
                                "update_peers")

    #FIXME: use _try_change
    def fill_blog(self, (peer_id, blog)):
        """sets peer as friend """
        if 'cache' in self.documents:
            self.documents["cache"].fill_blog((peer_id, blog))
        if 'gui' in self.views:
            self.views["gui"].display_blog(peer_id, blog)
    
    #FIXME: use _try_change
    def fill_shared_files(self, (peer_id, files)):
        """sets peer as friend """
        if 'cache' in self.documents:
            self.documents["cache"].fill_shared_files((peer_id, files))
        if 'gui' in self.views:
            self.views["gui"].display_files(peer_id, files)

    def make_friend(self, value):
        """sets peer as friend """
        return self._try_change(value,
                               "make_friend",
                               "update_peers")

    def blacklist_peer(self, value):
        """black list peer"""
        return self._try_change(value,
                               "blacklist_peer",
                               "update_peers")

    def unmark_peer(self, value):
        """black list peer"""
        return self._try_change(value,
                               "unmark_peer",
                               "update_peers")
