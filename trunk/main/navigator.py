#!/usr/bin/python -Qnew
import os,sys
from solipsis.navigator.wxclient.main import main

# add current directory to the python search path
# it is needed in case solipsis is not installed in the standard python
# directory (e.g: /usr/lib/python2.3 in linux)
currentDir = sys.path[0]
if os.environ.has_key('PYTHONPATH'):
    os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ':' + currentDir
else:
    os.environ['PYTHONPATH'] = currentDir

if __name__ == '__main__':
    main()
