class SolipsisException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return repr(self.message)
    
class SolipsisConnectionError(SolipsisException):
    def __init__(self):
        self.message = "cannot connect to solipsis"

class SolipsisEventParsingError(SolipsisException):
    """ An error occured while parsing a solipsis message"""
    pass

class SolipsisAbstractMethodError(SolipsisException):
    """ An abstarct method as been used. """
    def __init__(self):
        self.message = 'Error, trying to use an abstract method'

class SolipsisInternalError(SolipsisException):
    """ Generic solipsis exception. Program internal error, we shouldn't raise
    this exception in a production environement."""
    pass
