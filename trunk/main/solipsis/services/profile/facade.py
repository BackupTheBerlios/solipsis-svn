"""Design pattern Facade: presents working API for all actions of GUI
available. This facade will be used both by GUI and unittests."""

from sys import stderr
from solipsis.services.profile import ENCODING

#TODO: add state pattern when doc modified => prompt to save

def get_facade(doc=None, view=None):
    """implements pattern singleton on Facade. User may specify
    document end/or view to initialize facade with at creation"""
    if not Facade.s_facade:
        Facade.s_facade = Facade()
        if doc:
            Facade.s_facade.add_document(doc)
        if view:
            Facade.s_facade.add_view(view)
    return Facade.s_facade

class Facade:
    """manages user's actions & connects document and view"""
    
    s_facade = None

    def __init__(self):
        self.documents = {}
        self.views = {}

    def add_view(self, view):
        """add  a view object to facade"""
        self.views[view.get_name()] = view

    def add_document(self, doc):
        """add  a view object to facade"""
        # syncrhonize existing docs
        if "cache" in self.documents:
            doc.import_document(self.documents["cache"])
        # add new
        self.documents[doc.get_name()] = doc
        
    def _try_change(self, value, setter, updater):
        """tries to call function doc_set and then, if succeeded, gui_update"""
        for document in self.documents.values():
            try:
                getattr(document, setter)(value)
            except TypeError, error:
                print >> stderr, "%s: %s"% (document.name, str(error))
            except AttributeError, error:
                print >> stderr, "%s: %s"% (document.name, str(error))
        for view in self.views.values():
            try:
                getattr(view, updater)()
            except AttributeError, error:
                print >> stderr, "%s: %s"% (view.name, str(error))
    
    # MENU
    def save_profile(self, path):
        """save .profile.solipsis"""
        if "file" in self.documents:
            self.documents["file"].save(path)

    def load_profile(self, path):
        """save .profile.solipsis"""
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
    def change_repository(self, value):
        """sets new value for repositor"""
        return self._try_change(value,
                               "set_repository",
                               "update_repository")

    def add_file(self, value):
        """sets new value for unshared file"""
        return self._try_change(value,
                               "add_file",
                               "update_files")

    def change_file_tag(self, value):
        """sets new value for tagged file"""
        return self._try_change(value,
                               "tag_file",
                               "update_files")

    # OTHERS TAB
    def display_peer_preview(self, pseudo):
        """sets new preview for peer"""
        if "gui" in self.views:
            self.views["gui"].update_peer_preview(pseudo)

    def add_peer(self, value):
        """sets peer as friend """
        return self._try_change(value,
                                "add_peer",
                                "update_peers")

    def fill_data(self, value):
        """sets peer as friend """
        return self._try_change(value,
                                "fill_data",
                                "update_peers")

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

