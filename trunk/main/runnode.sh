#!/usr/bin/python -Qnew
import os
import solipsis.node.main

# add current directory to the python search path
# it is needed in case solipsis is not installed in the standard python
# directory (e.g: /usr/lib/python2.3 in linux)
if os.environ.has_key('PYTHONPATH'):
    os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ':.'
else:
    os.environ['PYTHONPATH'] = '.'

if __name__ == '__main__':
    solipsis.node.main.main()
