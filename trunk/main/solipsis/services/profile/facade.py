"""Design pattern Facade: presents working API for all actions of GUI
available. This facade will be used both by GUI and unittests."""

from sys import stderr

class Facade:
    """manages user's actions & connects document and view"""

    def __init__(self, document, view):
        self.document = document
        self.view = view

    def try_connect(self, value, doc_set, gui_update):
        """tries to call function doc_set and then, if succeeded, gui_update"""
        try:
            doc_set(value)
        except TypeError, error:
            print >> stderr, str(error)
        else:
            gui_update()
        
    # PERSONAL TAB
    def change_firstname(self, value):
        """sets new value for firstname"""
        self.try_connect(value,
                         self.document.set_firstname,
                         self.viewupdate_firstname)

    def change_lastname(self, value):
        """sets new value for lastname"""
        pass

    def change_pseudo(self, value):
        """sets new value for pseudo"""
        pass

    def change_email(self, value):
        """sets new value for email"""
        pass

    def change_birthday(self, value):
        """sets new value for birthday"""
        pass

    def change_language(self, value):
        """sets new value for language"""
        pass

    def change_address(self, value):
        """sets new value for """
        pass

    def change_postcode(self, value):
        """sets new value for postcode"""
        pass

    def change_city(self, value):
        """sets new value for city"""
        pass

    def change_country(self, value):
        """sets new value for country"""
        pass

    def change_description(self, value):
        """sets new value for description"""
        pass

    # CUSTOM TAB
    def change_hobbies(self, value):
        """sets new value for hobbies"""
        pass

    def change_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        pass

    # FILE TAB
    def sets_repository(self, value):
        """sets new value for repositor"""
        pass

    def share_file(self, value):
        """sets new value for shared file"""
        pass

    def unshare_file(self, value):
        """sets new value for unshared file"""
        pass

    def tag_file(self, value):
        """sets new value for tagged file"""
        pass

    # OTHERS TAB
    def display_peer_preview(self, value):
        """sets new preview for peer"""
        pass

    def make_friend(self, value):
        """sets peer as friend """
        pass

    def black_list(self, value):
        """black list peer"""
        pass

