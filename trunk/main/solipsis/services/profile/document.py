"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import mx.DateTime
from os.path import isfile, isdir

DATE_FORMAT = "%d/%m/%Y"

class FileDescriptor:
    """contains information relative to the sharing of one file"""

    def __init__(self, path):
        self.path = path
        self.tag = None

class PeerDescriptor:
    """contains information relative to peer of neioboourhood"""

    ANONYMOUS = 0
    FRIEND = 1
    BLACKLISTED = 2
    
    def __init__(self, pseudo):
        self.pseudo = pseudo
        self.state = PeerDescriptor.ANONYMOUS
        
class AbstractDocument:
    """Base class for data container. Acts as validator.

    Setters check input type. Getters are abstract"""
    
    # PERSONAL TAB
    def set_firstname(self, value):
        """sets new value for firstname"""
        if not isinstance(value, unicode):
            raise TypeError("firstname expected as unicode")
    def get_firstname(self):
        """returns value of firstname"""
        raise NotImplementedError
        
    def set_lastname(self, value):
        """sets new value for lastname"""
        if not isinstance(value, unicode):
            raise TypeError("lastname expected as unicode")
    def get_lastname(self):
        """returns value of lastname"""
        raise NotImplementedError
    
    def set_pseudo(self, value):
        """sets new value for pseudo"""
        if not isinstance(value, unicode):
            raise TypeError("pseudo expected as unicode")
    def get_pseudo(self):
        """returns value of pseudo"""
        raise NotImplementedError
        
    def set_email(self, value):
        """sets new value for email"""
        if not isinstance(value, unicode):
            raise TypeError("email expected as unicode")
    def get_email(self):
        """returns value of email"""
        raise NotImplementedError
        
    def set_birthday(self, value):
        """sets new value for birthday"""
        try:
            birthday = mx.DateTime.strptime(value, DATE_FORMAT)
        except mx.DateTime.Error, error:
            raise TypeError("birthday expected in format %s. %s"\
                            % (DATE_FORMAT, str(error)))
    def get_birthday(self):
        """returns value of birthday"""
        raise NotImplementedError
        
    def set_language(self, value):
        """sets new value for language"""
        if not isinstance(value, unicode):
            raise TypeError("language expected as unicode")
    def get_language(self):
        """returns value of language"""
        raise NotImplementedError
        
    def set_address(self, value):
        """sets new value for address"""
        if not isinstance(value, unicode):
            raise TypeError("address expected as unicode")
    def get_address(self):
        """returns value of address"""
        raise NotImplementedError
        
    def set_postcode(self, value):
        """sets new value for postcode"""
        try:
            postcode = int(value)
        except ValueError, error:
            raise TypeError("postcode expected as int. "+ str(error))
    def get_postcode(self):
        """returns value of postcode"""
        raise NotImplementedError
        
    def set_city(self, value):
        """sets new value for city"""
        if not isinstance(value, unicode):
            raise TypeError("city expected as unicode")
    def get_city(self):
        """returns value of city"""
        raise NotImplementedError
        
    def set_country(self, value):
        """sets new value for country"""
        if not isinstance(value, unicode):
            raise TypeError("country expected as unicode")
    def get_country(self):
        """returns value of country"""
        raise NotImplementedError
        
    def set_description(self, value):
        """sets new value for description"""
        if not isinstance(value, unicode):
            raise TypeError("description expected as unicode")
    def get_description(self):
        """returns value of description"""
        raise NotImplementedError
        
    # CUSTOM TAB
    def set_hobbies(self, value):
        """sets new value for hobbies"""
        if not isinstance(value, unicode):
            raise TypeError("hobbies expected as unicode")
    def get_hobbies(self):
        """returns value of hobbies"""
        raise NotImplementedError
        
    def add_custom_attributes(self, pair):
        """sets new value for custom_attributes"""
        if not isinstance(pair, list) and not isinstance(pair, tuple):
            raise TypeError("custom_attribute expected as list or tuple")
        elif len(pair) != 2:
            raise TypeError("custom_attribute expected as couple (key, value)")
        if not isinstance(pair[1], unicode):
            raise TypeError("tag expected as unicode")
    def get_custom_attributes(self):
        """returns value of custom_attributes"""
        raise NotImplementedError
        
    # FILE TAB
    def set_repository(self, value):
        """sets new value for repository"""
        if not isdir(value):
            raise TypeError("repository directory must exist")
    def get_repository(self):
        """returns value of repository"""
        raise NotImplementedError
        
    def add_file(self, file_path):
        """stores File object"""
        if not isfile(file_path):
            raise TypeError("file must exist")
        
    def get_files(self):
        """returns value of files"""
        raise NotImplementedError
        
    def tag_file(self, pair):
        """sets new value for tagged file"""
        if not isinstance(pair, list) and not isinstance(pair, tuple):
            raise TypeError("argument of tag_file expected as list or tuple")
        elif len(pair) != 2:
            raise TypeError("argument of  expected as couple (file_path, tag)")
        if not isinstance(pair[1], unicode):
            raise TypeError("tag expected as unicode")
            
    # OTHERS TAB
    def add_peer(self, pseudo):
        """stores Peer object"""
        if not isinstance(pseudo, unicode):
            raise TypeError("hobbies expected as unicode")
    
    def get_peers(self):
        """returns Peers"""
        raise NotImplementedError
    
    def make_friend(self, pseudo):
        """sets peer as friend """
        if not isinstance(pseudo, unicode):
            raise TypeError("hobbies expected as unicode")

    def blacklist_peer(self, pseudo):
        """sets new value for unshared file"""
        if not isinstance(pseudo, unicode):
            raise TypeError("hobbies expected as unicode")

    def unmark_peer(self, pseudo):
        """sets new value for unshared file"""
        if not isinstance(pseudo, unicode):
            raise TypeError("hobbies expected as unicode")
        

class CacheDocument(AbstractDocument):
    """data container on cache"""

    def __init__(self):
        self.firstname = u""
        self.lastname = u""
        self.pseudo = u""
        self.email = u""
        self.birthday = mx.DateTime.now()
        self.language = u""
        self.address = u""
        self.postcode = 0
        self.city = u""
        self.country = u""
        self.description = u""
        self.hobbies = []
        self.custom_attributes = {}
        self.repository = u""
        # dictionary of file. keys=fullpath
        self.files = {}
        # dictionary of peers. keys=pseudo(?)
        self.peers = {}

        
    # PERSONAL TAB
    def set_firstname(self, value):
        """sets new value for firstname"""
        AbstractDocument.set_firstname(self, value)
        self.firstname = value
    def get_firstname(self):
        """returns value of firstname"""
        return self.firstname

    def set_lastname(self, value):
        """sets new value for lastname"""
        AbstractDocument.set_lastname(self, value)
        self.lastname = value
    def get_lastname(self):
        """returns value of lastname"""
        return self.lastname

    def set_pseudo(self, value):
        """sets new value for pseudo"""
        AbstractDocument.set_pseudo(self, value)
        self.pseudo = value
    def get_pseudo(self):
        """returns value of pseudo"""
        return self.pseudo

    def set_email(self, value):
        """sets new value for email"""
        AbstractDocument.set_email(self, value)
        self.email = value
    def get_email(self):
        """returns value of email"""
        return self.email

    def set_birthday(self, value):
        """sets new value for birthday"""
        AbstractDocument.set_birthday(self, value)
        self.birthday = mx.DateTime.strptime(value, DATE_FORMAT)
    def get_birthday(self):
        """returns value of birthday"""
        return self.birthday

    def set_language(self, value):
        """sets new value for language"""
        AbstractDocument.set_language(self, value)
        self.language = value
    def get_language(self):
        """returns value of language"""
        return self.language

    def set_address(self, value):
        """sets new value for """
        AbstractDocument.set_address(self, value)
        self.address = value
    def get_address(self):
        """returns value of address"""
        return self.address

    def set_postcode(self, value):
        """sets new value for postcode"""
        AbstractDocument.set_postcode(self, value)
        self.postcode = int(value)
    def get_postcode(self):
        """returns value of postcode"""
        return self.postcode

    def set_city(self, value):
        """sets new value for city"""
        AbstractDocument.set_city(self, value)
        self.city = value
    def get_city(self):
        """returns value of city"""
        return self.city

    def set_country(self, value):
        """sets new value for country"""
        AbstractDocument.set_country(self, value)
        self.country = value
    def get_country(self):
        """returns value of country"""
        return self.country

    def set_description(self, value):
        """sets new value for description"""
        AbstractDocument.set_description(self, value)
        self.description = value
    def get_description(self):
        """returns value of description"""
        return self.description

    # CUSTOM TAB
    def set_hobbies(self, value):
        """sets new value for hobbies"""
        AbstractDocument.set_hobbies(self, value)
        self.hobbies = value.split('\n')
    def get_hobbies(self):
        """returns value of hobbies"""
        return self.hobbies

    def add_custom_attributes(self, pair):
        """sets new value for custom_attributes"""
        AbstractDocument.add_custom_attributes(self, pair)
        key, value = pair
        self.custom_attributes[key] = value
    def get_custom_attributes(self):
        """returns value of custom_attributes"""
        return self.custom_attributes

    # FILE TAB
    def set_repository(self, value):
        """sets new value for repositor"""
        AbstractDocument.set_repository(self, value)
        self.repository = value
    def get_repository(self):
        """returns value of repository"""
        return self.repository
        
    def add_file(self, file_path):
        """stores File object"""
        AbstractDocument.add_file(self, file_path)
        self.files[file_path] = FileDescriptor(file_path)
        
    def get_files(self):
        """returns value of files"""
        return self.files
        
    def tag_file(self, pair):
        """sets new value for tagged file"""
        AbstractDocument.tag_file(self, pair)
        file_path, tag = pair
        if not self.files.has_key(file_path):
            self.add_file(file_path)
        file_obj = self.files[file_path]
        file_obj.tag = tag

    # OTHERS TAB
    def add_peer(self, pseudo):
        """stores Peer object"""
        AbstractDocument.add_peer(self, pseudo)
        self.peers[pseudo] = PeerDescriptor(pseudo)
    
    def get_peers(self):
        """returns Peers"""
        return self.peers
    
    def make_friend(self, pseudo):
        """sets peer as friend """
        AbstractDocument.make_friend(self, pseudo)
        if not self.peers.has_key(pseudo):
            self.add_peer(pseudo)
        peer_obj = self.peers[pseudo]
        peer_obj.state = PeerDescriptor.FRIEND

    def blacklist_peer(self, pseudo):
        """sets new value for unshared file"""
        AbstractDocument.blacklist_peer(self, pseudo)
        if not self.peers.has_key(pseudo):
            self.add_peer(pseudo)
        peer_obj = self.peers[pseudo]
        peer_obj.state = PeerDescriptor.BLACKLISTED

    def unmark_peer(self, pseudo):
        """sets new value for unshared file"""
        AbstractDocument.blacklist_peer(self, pseudo)
        if not self.peers.has_key(pseudo):
            self.add_peer(pseudo)
        peer_obj = self.peers[pseudo]
        peer_obj.state = PeerDescriptor.ANONYMOUS


#TODO: FILEDOCUMENT
