#!/usr/bin/python -Qnew

import os
import os.path
import sys

#test
if __name__ == '__main__':
    sys.path.insert(0, os.path.normcase(os.path.dirname(os.path.abspath(__file__)) + '/solipsis/node'))
    #print sys.path
    import main
    main.main()
