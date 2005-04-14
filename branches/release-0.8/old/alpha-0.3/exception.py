class SolipsisConnectionError(Exception):
    def __init__(self):
        self.message = "cannot connect to solipsis"

    def __str__(self):
        return repr(self.message)

class SolipsisInternalError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return repr(self.message)
