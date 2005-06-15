#!/usr/bin/env python
import os, sys

import os
import os.path
import sys

if __name__ == '__main__':
    # following line needed at Logilab cause of weird behaviours...
#     print "WATCH OUT, stdout == stderr (logilab env)"
#     sys.stderr =  sys.stdout
    current_file = sys.argv[0]
    current_path = os.path.normcase(os.path.dirname(os.path.abspath(current_file)))
    os.chdir(current_path)
    sys.path.insert(0, current_path)
    #print sys.path
    from solipsis.navigator.wxclient import main
    main.main()
