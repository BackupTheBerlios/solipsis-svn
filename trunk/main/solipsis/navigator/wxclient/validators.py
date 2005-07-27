# pylint: disable-msg=W0142
# Used * or **
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

import solipsis.navigator.validators as validator

from solipsis.util.wxutils import Validator

class _RegexpValidator(validator._RegexpValidator, Validator):

    def __init__(self, *args, **kargs):
        Validator.__init__(self, *args, **kargs)
        validator._RegexpValidator.__init__(self)

class PortValidator(validator.PortValidator, Validator):
    """
    Validator for port numbers (1 .. 65535).
    """
    def __init__(self, *args, **kargs):
        Validator.__init__(self, *args, **kargs)
        validator.PortValidator.__init__(self)

class HostnameValidator(validator.HostnameValidator, _RegexpValidator):
    """
    Validator for hostnames.
    """
    def __init__(self, *args, **kargs):
        Validator.__init__(self, *args, **kargs)
        validator.HostnameValidator.__init__(self)

class NicknameValidator(validator.NicknameValidator, _RegexpValidator):
    """
    Validator for nicknames.
    """
    def __init__(self, *args, **kargs):
        Validator.__init__(self, *args, **kargs)
        validator.NicknameValidator.__init__(self)

class BooleanValidator(validator.BooleanValidator, Validator):
    """
    Validator for booleans (radio buttons, etc.).
    """
    def __init__(self, *args, **kargs):
        Validator.__init__(self, *args, **kargs)
        validator.BooleanValidator.__init__(self)

class CoordValidator(validator.CoordValidator, Validator):
    """
    Validator for Solipsis coordinates (0.0 ... 1.0).
    """
    def __init__(self, *args, **kargs):
        Validator.__init__(self, *args, **kargs)
        validator.CoordValidator.__init__(self)
