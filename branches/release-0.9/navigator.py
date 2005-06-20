#!/usr/bin/env python
import os, sys

import os
import os.path
import sys

if __name__ == '__main__':
    # following line needed at Logilab cause of weird behaviours...
#     print "WATCH OUT, stdout == stderr (logilab env)"
#     sys.stderr =  sys.stdout
    # Adjust path
    current_file = sys.argv[0]
    current_path = os.path.normcase(os.path.dirname(os.path.abspath(current_file)))
    os.chdir(current_path)
    if not current_path in sys.path:
        sys.path.insert(0, current_path)
    # Launch
    from solipsis.navigator.wxclient import main
    main.main()
