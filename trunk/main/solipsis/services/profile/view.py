"""Represents views used in model. It reads its data from a Document
(document.py) even if its independant from the structure and the inner
workings of documents"""

class AbstractView:
    """Base class for all views"""

    def __init__(self, document, name="abstract"):
        self.document = document
        self.name = name

    # PERSONAL TAB
    def update_title(self):
        """display title in view"""
        raise NotImplementedError

    def update_firstname(self):
        """display firstname in view"""
        raise NotImplementedError

    def update_lastname(self):
        """lastname"""
        raise NotImplementedError

    def update_pseudo(self):
        """pseudo"""
        raise NotImplementedError

    def update_photo(self):
        """photo"""
        raise NotImplementedError

    def update_email(self):
        """email"""
        raise NotImplementedError

    def update_birthday(self):
        """birthday"""
        raise NotImplementedError

    def update_language(self):
        """language"""
        raise NotImplementedError

    def update_address(self):
        """address"""
        raise NotImplementedError

    def update_postcode(self):
        """postcode"""
        raise NotImplementedError

    def update_city(self):
        """city"""
        raise NotImplementedError

    def update_country(self):
        """country"""
        raise NotImplementedError

    def update_description(self):
        """description"""
        raise NotImplementedError

    # CUSTOM TAB
    def update_hobbies(self):
        """hobbies"""
        raise NotImplementedError

    def update_custom_attributes(self):
        """custom_attributes"""
        raise NotImplementedError

    # FILE TAB
    def update_repository(self):
        """repository"""
        raise NotImplementedError

    def update_files(self):
        """file"""
        raise NotImplementedError

    # OTHERS TAB
    def update_peer_preview(self, value):
        """peer_preview"""
        raise NotImplementedError

    def update_peers(self):
        """peer"""
        raise NotImplementedError


class PrintView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, document, name="print"):
        AbstractView.__init__(self, document, name)

    # PERSONAL TAB
    def update_title(self):
        """title"""
        print  self.document.get_title()

    def update_firstname(self):
        """firstname"""
        print self.document.get_firstname()
        
    def update_lastname(self):
        """lastname"""
        print self.document.get_lastname()

    def update_pseudo(self):
        """pseudo"""
        print self.document.get_pseudo()  

    def update_photo(self):
        """photo"""
        print self.document.get_photo()      

    def update_email(self):
        """email"""
        print self.document.get_email()      

    def update_birthday(self):
        """DateTime birthday"""
        print self.document.get_birthday()  

    def update_language(self):
        """language"""
        print self.document.get_language()

    def update_address(self):
        """address"""
        print self.document.get_address()

    def update_postcode(self):
        """int postcode"""
        print self.document.get_postcode()

    def update_city(self):
        """city"""
        print self.document.get_city()

    def update_country(self):
        """country"""
        print self.document.get_country()

    def update_description(self):
        """description"""
        print self.document.get_description()

    # CUSTOM TAB
    def update_hobbies(self):
        """list hobbies"""
        print self.document.get_hobbies()
        
    def update_custom_attributes(self):
        """dict custom_attributes"""
        print self.document.get_custom_attributes()
        
    # FILE TAB
    def update_repository(self):
        """repository"""
        print self.document.get_repository()
        
    def update_files(self):
        """file"""
        print self.document.get_files()
        
    # OTHERS TAB
    def update_peer_preview(self, value):
        """peer_preview"""
        print self.document.get_peers()[value]
        
    def update_peers(self):
        """peer"""
        print self.document.get_peers()
        
