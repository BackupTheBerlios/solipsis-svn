#!/usr/bin/python
import os,sys
from solipsis.navigator.netclient.main import run

# add current directory to the python search path
# it is needed in case solipsis is not installed in the standard python
# directory (e.g: /usr/lib/python2.3 in linux)

currentDir = os.path.dirname(os.path.abspath(sys.path[0]))
if os.environ.has_key('PYTHONPATH'):
    os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ':' + currentDir
else:
    os.environ['PYTHONPATH'] = currentDir

if __name__ == '__main__':
    run()
