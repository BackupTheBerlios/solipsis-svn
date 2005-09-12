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

import os
import sys

# Python < 2.4 compatibility
try:
    set = set
except NameError:
    from sets import Set as set

DEFAULT_CHARSET = 'utf-8'


# Transparent support for unicode filepaths
getcwd = os.path.supports_unicode_filenames and os.getcwdu or os.getcwd

# Taken and improved from Python stdlib
def abspath(path):
    """
    Return an absolute path (unicode-safe version).
    """
    if not os.path.isabs(path):
        path = os.path.join(getcwd(), path)
    return os.path.normpath(path)


def safe_unicode(s, charset=None):
    """
    Forced conversion of a string to unicode, does nothing
    if the argument is already an unicode object.
    This function is useful because the .decode method
    on an unicode object, instead of being a no-op, tries to
    do a double conversion back and forth (which often fails
    because 'ascii' is the default codec).
    """
    if isinstance(s, str):
        return s.decode(charset or DEFAULT_CHARSET)
    else:
        return s

def safe_str(s, charset=None):
    """
    Forced conversion of an unicode to string, does nothing
    if the argument is already a plain str object.
    This function is useful because the .encode method
    on an str object, instead of being a no-op, tries to
    do a double conversion back and forth (which often fails
    because 'ascii' is the default codec).
    """
    if isinstance(s, unicode):
        return s.encode(charset or DEFAULT_CHARSET)
    else:
        return s

