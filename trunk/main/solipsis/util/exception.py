
from exceptions import *


class UnauthorizedRequest(Exception):
    def __init__(self, msg = ""):
        Exception.__init__(self, msg or "Unauthorized request to the node")
    pass



class ConnectionError(IOError):
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Cannot connect to Solipsis'
        IOError.__init__(self, msg)

class EventParsingError(Exception):
    """ An error occured while parsing a solipsis message"""
    def __init__(self, msg = ""):
        Exception.__init__(self, msg)

class AbstractMethodError(NotImplementedError):
    """ An abstract method has been used. """
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Error, trying to use an abstract method'
        NotImplementedError.__init__(self, msg)

class InternalError(RuntimeError):
    """ Generic solipsis exception. Program internal error, we shouldn't raise
    this exception in a production environement."""
    def __init__(self, msg = ""):
        RuntimeError.__init__(self, msg)

class ConnectorError(IOError):
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Connection aborted, please check port in not already in use'
        IOError.__init__(self, msg)

class DuplicateIdError(Exception):
    def __init__(self, id_):
        msg = "Error : duplicate ID '" + str(id_) + "'"
        Exception.__init__(self, msg)

class UnknownIdError(Exception):
    def __init__(self, id_):
        msg = "Error : unknown ID" + str(id_)
        Exception.__init__(self, msg)

class EmptyIdError(Exception):
    def __init__(self):
        msg = "Error : ID is empty"
        Exception.__init__(self, msg)

