#!/usr/bin/python -Qnew

import os, sys

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/solipsis/twistednode')
    #print sys.path
    import main
    main.main()
