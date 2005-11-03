# pylint: disable-msg=W0131
# Missing docstring
"""client server module for file sharing"""

__revision__ = "$Id: network.py 902 2005-10-14 16:18:06Z emb $"

import datetime
import tempfile
import gettext
_ = gettext.gettext

from solipsis.util.network import parse_address
from solipsis.services.profile.tools.message import display_status

# Alerts #############################################################
class SecurityAlert(Exception):

    def __init__(self, key, *args, **kwargs):
        Exception. __init__(self, *args, **kwargs)
        SecurityWarnings.instance()[key] = self
        SecurityWarnings.instance().display(key)

class SecurityWarnings(dict):

    _instance = None
    def instance(cls, *args, **kwargs):
        """Mise en oeuvre du pattern singleton"""
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance
    instance = classmethod(instance)
        
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def __setitem__(self, key, value):
        if key in self:
            self[key].append(value)
        else:
            dict.__setitem__(self, key, [value])

    def count(self, key):
        if key in self:
            return len(self[key])
        else:
            return 0

    def display(self, key):
        if key in self:
            nb_tries = self.count(key)
            if nb_tries > 1:
                display_status(_("%d retries of potential hacker '%s'"\
                                 % (nb_tries, key)))
            elif nb_tries == 1:
                display_status(_("'%s' has not registered properly: %s"\
                                  % (key, self[key][0])))
        #else no warning...

# Messages ###########################################################
MESSAGE_HELLO = "HELLO"
MESSAGE_ERROR = "ERROR"
MESSAGE_PROFILE = "REQUEST_PROFILE"
MESSAGE_BLOG = "REQUEST_BLOG"
MESSAGE_SHARED = "REQUEST_SHARED"
MESSAGE_FILES = "REQUEST_FILES"

SERVICES_MESSAGES = [MESSAGE_HELLO, MESSAGE_ERROR, MESSAGE_PROFILE,
                     MESSAGE_BLOG, MESSAGE_SHARED, MESSAGE_FILES]

class Message(object):
    """Simple wrapper for a communication message"""

    def __init__(self, command):
        if command not in SERVICES_MESSAGES:
            raise ValueError("%s should be in %s"% (command, SERVICES_MESSAGES))
        self.command = command
        self.ip = None
        self.port = None
        self.data = None
        # creation_time is used as reference when cleaning
        self.creation_time = datetime.datetime.now()

    def __str__(self):
        return " ".join([self.command,
                         "%s:%d"% (self.ip or "?",
                                   self.port or -1),
                         self.data or ''])

    def create_message(message):
        """extract command, address and data from message.
        
        Expected format: MESSAGE host:port data
        returns Message instance"""
        # 2 maximum splits: data may contain spaces
        items = message.split(' ', 2)
        if not len(items) >= 2:
            raise ValueError("%s should define command & host's address"\
                             % message)
        message = Message(items[0])
        message.ip, port = parse_address(items[1])
        message.port = int(port)
        # check data
        if len(items) > 2:
            message.data = items[2]
        return message
    create_message = staticmethod(create_message)

class DownloadMessage(object):
    """wrapper to link connection, message sent and deferred to
    be called when download complete"""

    def __init__(self, transport, deferred, message):
        self.transport = transport
        self.deferred = deferred
        self.message = message
        self.file = None
        self.size = 0

    def send_message(self):
        self.transport.write(str(self.message)+"\r\n")

    # download management ############################################
    def setup_download(self):
        self.file = tempfile.NamedTemporaryFile()
        self.size = 0

    def write_data(self, data):
        self.size += len(data)
        self.file.write(data)

    def teardown_download(self):
        self.file.seek(0)
        self.deferred.callback(self)
        
    def close(self, reason=None):
        self.file.close()
