"""Design pattern Facade: presents working API for all actions of GUI
available. This facade will be used both by GUI and unittests."""

from sys import stderr

class Facade:
    """manages user's actions & connects document and view"""

    def __init__(self, document, view):
        self.document = document
        self.view = view

    def _try_change(self, value, doc_set, gui_update):
        """tries to call function doc_set and then, if succeeded, gui_update"""
        try:
            doc_set(value)
        except TypeError, error:
            print >> stderr, str(error)
            return False
        else:
            return gui_update()
        
    # PERSONAL TAB
    def change_firstname(self, value):
        """sets new value for firstname"""
        return self._try_change(value,
                               self.document.set_firstname,
                               self.view.update_firstname)

    def change_lastname(self, value):
        """sets new value for lastname"""
        return self._try_change(value,
                               self.document.set_lastname,
                               self.view.update_lastname)

    def change_pseudo(self, value):
        """sets new value for pseudo"""
        return self._try_change(value,
                               self.document.set_pseudo,
                               self.view.update_pseudo)

    def change_email(self, value):
        """sets new value for email"""
        return self._try_change(value,
                               self.document.set_email,
                               self.view.update_email)

    def change_birthday(self, value):
        """sets new value for birthday"""
        return self._try_change(value,
                               self.document.set_birthday,
                               self.view.update_birthday)

    def change_language(self, value):
        """sets new value for language"""
        return self._try_change(value,
                               self.document.set_language,
                               self.view.update_language)

    def change_address(self, value):
        """sets new value for """
        return self._try_change(value,
                               self.document.set_address,
                               self.view.update_address)

    def change_postcode(self, value):
        """sets new value for postcode"""
        return self._try_change(value,
                               self.document.set_postcode,
                               self.view.update_postcode)

    def change_city(self, value):
        """sets new value for city"""
        return self._try_change(value,
                               self.document.set_city,
                               self.view.update_city)

    def change_country(self, value):
        """sets new value for country"""
        return self._try_change(value,
                               self.document.set_country,
                               self.view.update_country)

    def change_description(self, value):
        """sets new value for description"""
        return self._try_change(value,
                               self.document.set_description,
                               self.view.update_description)

    # CUSTOM TAB
    def change_hobbies(self, value):
        """sets new value for hobbies"""
        return self._try_change(value,
                               self.document.set_hobbies,
                               self.view.update_hobbies)

    def add_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        return self._try_change(value,
                               self.document.add_custom_attributes,
                               self.view.update_custom_attributes)

    # FILE TAB
    def change_repository(self, value):
        """sets new value for repositor"""
        return self._try_change(value,
                               self.document.set_repository,
                               self.view.update_repository)

    def add_file(self, value):
        """sets new value for unshared file"""
        return self._try_change(value,
                               self.document.add_file,
                               self.view.update_file)

    def change_file_tag(self, value):
        """sets new value for tagged file"""
        return self._try_change(value,
                               self.document.tag_file,
                               self.view.update_file)

    # OTHERS TAB
    def display_peer_preview(self, value):
        """sets new preview for peer"""
        self.view.update_peer_preview(value)

    def make_friend(self, value):
        """sets peer as friend """
        return self._try_change(value,
                               self.document.make_friend,
                               self.view.update_peer)

    def blacklist_peer(self, value):
        """black list peer"""
        return self._try_change(value,
                               self.document.blacklist_peer,
                               self.view.update_peer)

    def unmark_peer(self, value):
        """black list peer"""
        return self._try_change(value,
                               self.document.unmark_peer,
                               self.view.update_peer)

