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

import sys
import os
import socket

from solipsis.navigator.main import USAGE, OPTIONS, build_params
from solipsis.navigator.wxclient.app import NavigatorApp

def main():
    params = build_params()
    # If an URL has been specified, try to connect to a running navigator
    if params.url_jump:
        filename = os.path.join('state', 'url_jump.port')
        try:
            f = file(filename, 'rb')
            url_port = int(f.read())
            f.close()
        except (IOError, EOFError, ValueError):
            pass
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect(('127.0.0.1', url_port))
            except socket.error:
                pass
            else:
                s.send(params.url_jump + '\r\n')
                s.close()
                sys.exit(0)

    application = NavigatorApp(redirect=False, 
                               params=params)
    application.MainLoop()
    sys.exit(0)

if __name__ == "__main__":
    main()
