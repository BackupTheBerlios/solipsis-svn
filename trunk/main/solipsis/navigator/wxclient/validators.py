
import re

from wxutils import Validator, _


class _RegexpValidator(Validator):
    """ Intermediate class for regexp-based validators. """

    def __init__(self, *args, **kargs):
        Validator.__init__(self, *args, **kargs)

    def _ReprToData(self, _repr):
        return str(_repr).strip()

    def _DataToRepr(self, _data):
        return str(_data)

    def _Validate(self, value):
        value = value.strip()
        return len(value) > 0 and self.regexp.match(value)


class PortValidator(Validator):
    """ Validator for port numbers (1 .. 65535). """

    def __init__(self, *args, **kargs):
        Validator.__init__(self, *args, **kargs)
        self.message = _("Port number must be between 1 and 65535")

    def _ReprToData(self, _repr):
        return int(_repr)

    def _DataToRepr(self, _data):
        return str(_data)

    def _Validate(self, value):
        try:
            port = int(value)
            return port > 0 and port < 65336
        except:
            return False


class HostnameValidator(_RegexpValidator):
    """ Validator for hostnames. """

    regexp = re.compile(r'^[-_\w\.\:]+$')

    def __init__(self, *args, **kargs):
        super(HostnameValidator, self).__init__(*args, **kargs)
        self.message = _("Please enter a valid hostname or address")


class NicknameValidator(_RegexpValidator):
    """ Validator for nicknames. """

    regexp = re.compile(r'^.+$')

    def __init__(self, *args, **kargs):
        super(NicknameValidator, self).__init__(*args, **kargs)
        self.message = _("Please enter a valid nickname")

