"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import mx.DateTime
import ConfigParser
import os.path
from os.path import isfile, isdir

DATE_FORMAT = "%d/%m/%Y"
ENCODING = "ISO-8859-1"
PROFILE_FILE = ".profile.solipsis"
SECTION_PERSONAL = "Personal"
SECTION_CUSTOM = "Custom"
SECTION_FILE = "File"
SECTION_OTHERS = "Others"
        

class FileDescriptor:
    """contains information relative to the sharing of one file"""

    def __init__(self, path, tag=None):
        self.path = path
        self.tag = tag

    def __repr__(self):
        return "%s (%s)"% (self.path, self.tag)

class PeerDescriptor:
    """contains information relative to peer of neioboourhood"""

    ANONYMOUS = 0
    FRIEND = 1
    BLACKLISTED = 2
    
    def __init__(self, pseudo, state=ANONYMOUS):
        self.pseudo = pseudo
        self.state = state

    def __repr__(self):
        return "%s (%s)"% (self.pseudo, self.state)
        
class AbstractDocument:
    """Base class for data container. Acts as validator.

    Setters check input type. Getters are abstract"""

    def __init__(self, name="abstract"):
        self.name = name

    def import_document(self, other_document):
        """copy data from another document into self"""
        # personal data (unicode)
        self.set_title(other_document.get_title())
        self.set_firstname(other_document.get_firstname())
        self.set_lastname(other_document.get_lastname())
        self.set_pseudo(other_document.get_pseudo())
        self.set_photo(other_document.get_photo())
        self.set_email(other_document.get_email())
        self.set_birthday(other_document.get_birthday())
        self.set_language(other_document.get_language())
        self.set_address(other_document.get_address())
        self.set_postcode(other_document.get_postcode())
        self.set_city(other_document.get_city())
        self.set_country(other_document.get_country())
        self.set_description(other_document.get_description())
        # custom data
        hobbies = other_document.get_hobbies()
        self.set_hobbies('\n'.join(hobbies))
        attributes = other_document.get_custom_attributes()
        for key, val in attributes.iteritems():
            self.add_custom_attributes((key, val))
        # file data
        self.set_repository(other_document.get_repository())
        files = other_document.get_files()
        for file_path, file_desc in files.iteritems():
            self.tag_file((file_path, file_desc.tag))
        # others' data
        peers = other_document.get_peers()
        for pseudo, peer_desc in peers.iteritems():
            self.add_peer(pseudo)
            self.peers[pseudo].state = peer_desc.state
    
    # PERSONAL TAB
    def set_title(self, value):
        """sets new value for title"""
        if not isinstance(value, unicode):
            raise TypeError("title expected as unicode")
    def get_title(self):
        """returns value of firstname"""
        raise NotImplementedError
        
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
    
    def set_photo(self, value):
        """sets new value for photo"""
        if not isfile(value):
            raise TypeError("photo must exist")
    def get_photo(self):
        """returns value of photo"""
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
    def remove_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        raise NotImplementedError
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
            raise TypeError("pseudo expected as unicode")
    
    def get_peers(self):
        """returns Peers"""
        raise NotImplementedError
    
    def make_friend(self, pseudo):
        """sets peer as friend """
        if not isinstance(pseudo, unicode):
            raise TypeError("pseudo expected as unicode")

    def blacklist_peer(self, pseudo):
        """sets new value for unshared file"""
        if not isinstance(pseudo, unicode):
            raise TypeError("pseudo expected as unicode")

    def unmark_peer(self, pseudo):
        """sets new value for unshared file"""
        if not isinstance(pseudo, unicode):
            raise TypeError("pseudo expected as unicode")
        

class CacheDocument(AbstractDocument):
    """data container on cache"""

    def __init__(self, name="cache"):
        AbstractDocument.__init__(self, name)
        self.title = u""
        self.firstname = u""
        self.lastname = u""
        self.pseudo = u""
        self.photo = ""
        self.email = u""
        self.birthday = mx.DateTime.now()
        self.language = u""
        self.address = u""
        self.postcode = 0
        self.city = u""
        self.country = u""
        self.description = u""
        self.hobbies = []
        # dictionary of file. {att_name : att_value}
        self.custom_attributes = {}
        self.repository = u""
        # dictionary of file. {fullpath : FileDescriptor}
        self.files = {}
        # dictionary of peers. {pseudo : PeerDescriptor}
        self.peers = {}

        
    # PERSONAL TAB
    def set_title(self, value):
        """sets new value for title"""
        AbstractDocument.set_title(self, value)
        self.title = value
    def get_title(self):
        """returns value of title"""
        return self.title
        
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

    def set_photo(self, value):
        """sets new value for photo"""
        AbstractDocument.set_photo(self, value)
        self.photo = value
    def get_photo(self):
        """returns value of photo"""
        return self.photo

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
        return self.birthday.strftime(DATE_FORMAT)

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
        return str(self.postcode)

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
    def remove_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        if self.custom_attributes.has_key(value):
            del self.custom_attributes[value]
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


# FILEDOCUMENT
class FileDocument(AbstractDocument):
    """data container on file"""

    def __init__(self, name="file"):
        AbstractDocument.__init__(self, name)
        self.file_name = os.path.join(os.path.expanduser('~'), PROFILE_FILE)
        self.encoding = ENCODING
        self.config = ConfigParser.ConfigParser()
        self.config.add_section(SECTION_PERSONAL)
        self.config.add_section(SECTION_CUSTOM)
        self.config.add_section(SECTION_FILE)
        self.config.add_section(SECTION_OTHERS)

    def save(self):
        """fill document with information from .profile file"""
        file_obj = open(self.file_name, 'w')
        file_obj.write("#%s\n"% self.encoding)
        self.config.write(file_obj)

    def load(self):
        """fill document with information from .profile file"""
        if os.path.exists(self.file_name):
            file_obj = open(self.file_name)
            self.encoding = file_obj.readline()[1:]
            self.config = ConfigParser.ConfigParser()
            self.config.readfp(file_obj)
            return True
        else:
            return False
        
    # PERSONAL TAB
    def set_title(self, value):
        """sets new value for title"""
        AbstractDocument.set_firstname(self, value)
        self.config.set(SECTION_PERSONAL, "title", value.encode(self.encoding))
    def get_title(self):
        """returns value of title"""
        return unicode(self.config.get(SECTION_PERSONAL, "title"), self.encoding)
        
    def set_firstname(self, value):
        """sets new value for firstname"""
        AbstractDocument.set_firstname(self, value)
        self.config.set(SECTION_PERSONAL, "firstname", value.encode(self.encoding))
    def get_firstname(self):
        """returns value of firstname"""
        return unicode(self.config.get(SECTION_PERSONAL, "firstname"), self.encoding)

    def set_lastname(self, value):
        """sets new value for lastname"""
        AbstractDocument.set_lastname(self, value)
        self.config.set(SECTION_PERSONAL, "lastname", value.encode(self.encoding))
    def get_lastname(self):
        """returns value of lastname"""
        return unicode(self.config.get(SECTION_PERSONAL, "lastname"), self.encoding)

    def set_pseudo(self, value):
        """sets new value for pseudo"""
        AbstractDocument.set_pseudo(self, value)
        self.config.set(SECTION_PERSONAL, "pseudo", value.encode(self.encoding))
    def get_pseudo(self):
        """returns value of pseudo"""
        return unicode(self.config.get(SECTION_PERSONAL, "pseudo"), self.encoding)

    def set_photo(self, value):
        """sets new value for photo"""
        AbstractDocument.set_photo(self, value)
        self.config.set(SECTION_PERSONAL, "photo", value.encode(self.encoding))
    def get_photo(self):
        """returns value of photo"""
        return self.config.get(SECTION_PERSONAL, "photo")

    def set_email(self, value):
        """sets new value for email"""
        AbstractDocument.set_email(self, value)
        self.config.set(SECTION_PERSONAL, "email", value.encode(self.encoding))
    def get_email(self):
        """returns value of email"""
        return unicode(self.config.get(SECTION_PERSONAL, "email"), self.encoding)

    def set_birthday(self, value):
        """sets new value for birthday"""
        AbstractDocument.set_birthday(self, value)
        self.config.set(SECTION_PERSONAL, "birthday", value.encode(self.encoding))
    def get_birthday(self):
        """returns value of birthday"""
        return unicode(self.config.get(SECTION_PERSONAL, "birthday"), self.encoding)

    def set_language(self, value):
        """sets new value for language"""
        AbstractDocument.set_language(self, value)
        self.config.set(SECTION_PERSONAL, "language", value.encode(self.encoding))
    def get_language(self):
        """returns value of language"""
        return unicode(self.config.get(SECTION_PERSONAL, "language"), self.encoding)

    def set_address(self, value):
        """sets new value for """
        AbstractDocument.set_address(self, value)
        self.config.set(SECTION_PERSONAL, "address", value.encode(self.encoding))
    def get_address(self):
        """returns value of address"""
        return unicode(self.config.get(SECTION_PERSONAL, "address"), self.encoding)

    def set_postcode(self, value):
        """sets new value for postcode"""
        AbstractDocument.set_postcode(self, value)
        self.config.set(SECTION_PERSONAL, "postcode", value.encode(self.encoding))
    def get_postcode(self):
        """returns value of postcode"""
        return unicode(self.config.get(SECTION_PERSONAL, "postcode"), self.encoding)

    def set_city(self, value):
        """sets new value for city"""
        AbstractDocument.set_city(self, value)
        self.config.set(SECTION_PERSONAL, "city", value.encode(self.encoding))
    def get_city(self):
        """returns value of city"""
        return unicode(self.config.get(SECTION_PERSONAL, "city"), self.encoding)

    def set_country(self, value):
        """sets new value for country"""
        AbstractDocument.set_country(self, value)
        self.config.set(SECTION_PERSONAL, "country", value.encode(self.encoding))
    def get_country(self):
        """returns value of country"""
        return unicode(self.config.get(SECTION_PERSONAL, "country"), self.encoding)

    def set_description(self, value):
        """sets new value for description"""
        AbstractDocument.set_description(self, value)
        self.config.set(SECTION_PERSONAL, "description", value.encode(self.encoding))
    def get_description(self):
        """returns value of description"""
        return unicode(self.config.get(SECTION_PERSONAL, "description"), self.encoding)

    # CUSTOM TAB
    def set_hobbies(self, value):
        """sets new value for hobbies"""
        AbstractDocument.set_hobbies(self, value)
        self.config.set(SECTION_CUSTOM, "hobbies", value.replace('\n', ',').encode(self.encoding))
    def get_hobbies(self):
        """returns value of hobbies"""
        return [unicode(hobby, self.encoding) for hobby 
                in self.config.get(SECTION_CUSTOM, "hobbies").split( ',')]

    def add_custom_attributes(self, pair):
        """sets new value for custom_attributes"""
        AbstractDocument.add_custom_attributes(self, pair)
        key, value = pair
        self.config.set(SECTION_CUSTOM, key, value.encode(self.encoding))
    def remove_custom_attributes(self, value):
        """sets new value for custom_attributes"""
        if self.config.has_option(SECTION_CUSTOM, value):
            self.config.remove_option(SECTION_CUSTOM, value)
    def get_custom_attributes(self):
        """returns value of custom_attributes"""
        options = self.config.options(SECTION_CUSTOM)
        result = {}
        for option in options:
            if option != "hobbies":
                result[option] = unicode(self.config.get(SECTION_CUSTOM, option), self.encoding)
        return result

    # FILE TAB
    def set_repository(self, value):
        """sets new value for repositor"""
        AbstractDocument.set_repository(self, value)
        self.config.set(SECTION_FILE, "repository", value.encode(self.encoding))
    def get_repository(self):
        """returns value of repository"""
        return unicode(self.config.get(SECTION_FILE, "repository"), self.encoding)
        
    def add_file(self, file_path):
        """stores File object"""
        AbstractDocument.add_file(self, file_path)
        self.config.set(SECTION_FILE, file_path, "")
        
    def get_files(self):
        """returns value of files"""
        options = self.config.options(SECTION_FILE)
        result = {}
        for option in options:
            if option != "repository":
                result[option] = FileDescriptor(option,
                                                unicode(self.config.get(SECTION_FILE, option), self.encoding))
        return result
        
    def tag_file(self, pair):
        """sets new value for tagged file"""
        AbstractDocument.tag_file(self, pair)
        file_path, tag = pair
        self.config.set(SECTION_FILE, file_path, tag.encode(self.encoding))

    # OTHERS TAB
    def add_peer(self, pseudo):
        """stores Peer object"""
        self.config.set(SECTION_OTHERS, pseudo, "")
    
    def get_peers(self):
        """returns Peers"""
        options = self.config.options(SECTION_OTHERS)
        result = {}
        for option in options:
            uoption = unicode(option, self.encoding)
            result[uoption] = PeerDescriptor(uoption,
                                             self.config.get(SECTION_OTHERS, uoption))
        return result
        
    def make_friend(self, pseudo):
        """sets peer as friend """
        AbstractDocument.make_friend(self, pseudo)
        self.config.set(SECTION_OTHERS, pseudo, PeerDescriptor.FRIEND)

    def blacklist_peer(self, pseudo):
        """sets new value for unshared file"""
        AbstractDocument.blacklist_peer(self, pseudo)
        self.config.set(SECTION_OTHERS, pseudo, PeerDescriptor.BLACKLISTED)

    def unmark_peer(self, pseudo):
        """sets new value for unshared file"""
        AbstractDocument.blacklist_peer(self, pseudo)
        self.config.set(SECTION_OTHERS, pseudo, PeerDescriptor.ANONYMOUS)

