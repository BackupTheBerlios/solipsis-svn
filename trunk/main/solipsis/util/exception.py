
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
         super(SolipsisException, self).__init__(msg)

     def __str__(self):
          return repr(self.message)

class ConnectionError(SolipsisException, IOError):
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Cannot connect to Solipsis'
        #IOError.__init__(self, msg)
        super(ConnectionError, self).__init__(msg)
    pass

class EventParsingError(SolipsisException, Exception):
    """ An error occured while parsing a solipsis message"""
    #def __init__(self, msg = ""):
    #    super(EventParsingError, self).__init__(msg)
    def __init__(self, msg = ""):
         SolipsisException.__init__(self, msg)


class AbstractMethodError(SolipsisException, NotImplementedError):
    """ An abstract method has been used. """
    #def __init__(self):
    #    super(AbstractMethodError, self).__init__('Error, trying to use an abstract method')
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Error, trying to use an abstract method'
        NotImplementedError.__init__(self, msg)
    pass

class InternalError(SolipsisException, RuntimeError):
    """ Generic solipsis exception. Program internal error, we shouldn't raise
    this exception in a production environement."""
    #def __init__(self, msg = ""):
    #    super(InternalError, self).__init__(msg)
    def __init__(self, msg = ""):
        RuntimeError.__init__(self, msg)
    pass

class ConnectorError(SolipsisException, IOError):
    def __init__(self, msg = ""):
        if not msg:
            msg = 'Connection aborted, please check port in not already in use'
        NotImplementedError.__init__(self, msg)
    pass


class DuplicateIdError(SolipsisException, Exception):
    def __init__(self, id_):
        self.message = "Error : duplicate ID '" + str(id_) + "'"
        super(DuplicateIdError, self).__init__(self.message)

class UnknownIdError(SolipsisException, Exception):
    def __init__(self, id_):
        self.message = "Error : unknown ID" + str(id_)
        super(UnknownIdError, self).__init__(self.message)

class EmptyIdError(SolipsisException, Exception):
    def __init__(self):
        self.message = "Error : ID is empty"
        super(EmptyIdError, self).__init__(self.message)

