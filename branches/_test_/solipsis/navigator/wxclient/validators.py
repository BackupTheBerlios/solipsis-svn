# <copyright>
# Solipsis, a peer-to-peer serverless virtual world.
# Copyright (C) 2002-2005 France Telecom R&D
# 
# This software is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# </copyright>

import re

from solipsis.util.wxutils import Validator, _


class _RegexpValidator(Validator):
    """
    Intermediate class for regexp-based validators.
    """
    value_type = str

    def __init__(self, *args, **kargs):
        Validator.__init__(self, *args, **kargs)

    def _ReprToData(self, _repr):
        return self.value_type(_repr).strip()

    def _DataToRepr(self, _data):
        return unicode(_data)

    def _Validate(self, value):
        value = value.strip()
        return len(value) > 0 and self.regexp.match(value)


class PortValidator(Validator):
    """
    Validator for port numbers (1 .. 65535).
    """
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
    """
    Validator for hostnames.
    """
    regexp = re.compile(r'^[-_\w\.\:]+$')

    def __init__(self, *args, **kargs):
        super(HostnameValidator, self).__init__(*args, **kargs)
        self.message = _("Please enter a valid hostname or address")


class NicknameValidator(_RegexpValidator):
    """
    Validator for nicknames.
    """
    regexp = re.compile(r'^.+$')
    value_type = unicode

    def __init__(self, *args, **kargs):
        super(NicknameValidator, self).__init__(*args, **kargs)
        self.message = _("Please enter a valid nickname")


class BooleanValidator(Validator):
    """
    Validator for booleans (radio buttons, etc.).
    """
    def __init__(self, *args, **kargs):
        Validator.__init__(self, *args, **kargs)

    def _ReprToData(self, _repr):
        return _repr

    def _DataToRepr(self, _data):
        return _data

    def _Validate(self, value):
        assert isinstance(value, bool)
        return True
