
from exceptions import *

#
# BUG:
# apparently, multiple inheritance new-style classes (derived from 'object') and exceptions do not mix well
#
# OTOH, 'super' does not seem available with classic classes (not derived from 'object')...
#

class SolipsisException:
     def __init__(self, msg = ""):
         self.message = msg
         #super(SolipsisException, self).__init__(msg)

     def __str__(self):
          return repr(self.message)


class ConnectionError(SolipsisException, IOError):
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Cannot connect to Solipsis'
        SolipsisException.__init__(self, msg)
        IOError.__init__(self, msg)

class EventParsingError(SolipsisException, Exception):
    """ An error occured while parsing a solipsis message"""
    def __init__(self, msg = ""):
        SolipsisException.__init__(self, msg)
        Exception.__init__(self, msg)

class AbstractMethodError(SolipsisException, NotImplementedError):
    """ An abstract method has been used. """
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Error, trying to use an abstract method'
        SolipsisException.__init__(self, msg)
        NotImplementedError.__init__(self, msg)

class InternalError(SolipsisException, RuntimeError):
    """ Generic solipsis exception. Program internal error, we shouldn't raise
    this exception in a production environement."""
    def __init__(self, msg = ""):
        SolipsisException.__init__(self, msg)
        RuntimeError.__init__(self, msg)

class ConnectorError(SolipsisException, IOError):
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Connection aborted, please check port in not already in use'
        SolipsisException.__init__(self, msg)
        IOError.__init__(self, msg)

class DuplicateIdError(SolipsisException, Exception):
    def __init__(self, id_):
        msg = "Error : duplicate ID '" + str(id_) + "'"
        SolipsisException.__init__(self, msg)
        Exception.__init__(self, msg)

class UnknownIdError(SolipsisException, Exception):
    def __init__(self, id_):
        msg = "Error : unknown ID" + str(id_)
        SolipsisException.__init__(self, msg)
        Exception.__init__(self, msg)

class EmptyIdError(SolipsisException, Exception):
    def __init__(self):
        msg = "Error : ID is empty"
        SolipsisException.__init__(self, msg)
        Exception.__init__(self, msg)


