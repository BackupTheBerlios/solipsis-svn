class SolipsisConnectionError(Exception):
    def __init__(self):
        self.message = "cannot connect to solipsis"

    def __str__(self):
        return repr(self.message)

class SolipsisMessageParsingError(Exception):
    """ An error occured while parsing a solipsis message"""
    pass


class SolipsisInternalError(Exception):
    """ Generic solipsis exception. Program internal error, we shouldn't raise
    this exception in a production environement."""
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return repr(self.message)
