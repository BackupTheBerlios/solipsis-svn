"""Represents views used in model. It reads its data from a Document
(document.py) even if its independant from the structure and the inner
workings of documents"""

class AbstractView:
    """Base class for all views"""

    def __init__(self, document):
        self.document = document

    # PERSONAL TAB
    def update_firstname(self, value):
        """sets new value for firstname"""
        raise NotImplementedError

    def update_lastname(self, value):
        """sets new value for lastname"""
        raise NotImplementedError

    def update_pseudo(self, value):
        """sets new value for pseudo"""
        raise NotImplementedError

    def update_email(self, value):
        """sets new value for email"""
        raise NotImplementedError

    def update_birthday(self, value):
        """sets new value for birthday"""
        raise NotImplementedError

    def update_language(self, value):
        """sets new value for language"""
        raise NotImplementedError

    def update_address(self, value):
        """sets new value for """
        raise NotImplementedError

    def update_postcode(self, value):
        """sets new value for """
        raise NotImplementedError

    def update_city(self, value):
        """sets new value for """
        raise NotImplementedError

    def update_country(self, value):
        """sets new value for """
        raise NotImplementedError

    def update_description(self, value):
        """sets new value for """
        raise NotImplementedError

    # CUSTOM TAB
    def update_hobbies(self, value):
        """sets new value for """
        raise NotImplementedError

    def update_custom_attributes(self, value):
        """sets new value for """
        raise NotImplementedError

    # FILE TAB
    def update_repository(self, value):
        """sets new value for """
        raise NotImplementedError

    def update_share_file(self, value):
        """sets new value for """
        raise NotImplementedError

    def update_unshare_file(self, value):
        """sets new value for """
        raise NotImplementedError

    def update_tag_file(self, value):
        """sets new value for """
        raise NotImplementedError

    # OTHERS TAB
    def update_peer_preview(self, value):
        """sets new value for """
        raise NotImplementedError

    def update_friend(self, value):
        """sets new value for """
        raise NotImplementedError

    def update_black_list(self, value):
        """sets new value for """
        raise NotImplementedError


class GuiView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, document):
        AbstractView.__init__(self, document)

    def update_all_view(self):
        """trigger called on a modification of the document"""
        pass

    # PERSONAL TAB
    def update_firstname(self, value):
        """sets new value for firstname"""
        self.document.get_firstname()
        

    def update_lastname(self, value):
        """sets new value for lastname"""
        

    def update_pseudo(self, value):
        """sets new value for pseudo"""
        

    def update_email(self, value):
        """sets new value for email"""
        

    def update_birthday(self, value):
        """sets new value for birthday"""
        

    def update_language(self, value):
        """sets new value for language"""
        

    def update_address(self, value):
        """sets new value for """
        

    def update_postcode(self, value):
        """sets new value for """
        

    def update_city(self, value):
        """sets new value for """
        

    def update_country(self, value):
        """sets new value for """
        

    def update_description(self, value):
        """sets new value for """
        

    # CUSTOM TAB
    def update_hobbies(self, value):
        """sets new value for """
        

    def update_custom_attributes(self, value):
        """sets new value for """
        

    # FILE TAB
    def update_repository(self, value):
        """sets new value for """
        

    def update_share_file(self, value):
        """sets new value for """
        

    def update_unshare_file(self, value):
        """sets new value for """
        

    def update_tag_file(self, value):
        """sets new value for """
        

    # OTHERS TAB
    def update_peer_preview(self, value):
        """sets new value for """
        

    def update_friend(self, value):
        """sets new value for """
        

    def update_black_list(self, value):
        """sets new value for """
        
