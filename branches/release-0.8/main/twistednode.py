#!/usr/bin/python -Qnew

import os
import os.path
import sys

if __name__ == '__main__':
    sys.path.insert(0, os.path.normcase(os.path.dirname(os.path.abspath(sys.argv[0]))))
    #print sys.path
    from solipsis.node import main
    main.main()
