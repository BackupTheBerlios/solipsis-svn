#!/usr/bin/python -Qnew
import os, time
from solipsis.navigator.printerNavigator import PrinterNavigator

# add current directory to the python search path
# it is needed in case solipsis is not installed in the standard python
# directory (e.g: /usr/lib/python2.3 in linux)
if os.environ.has_key('PYTHONPATH'):
    os.environ['PYTHONPATH'] = os.environ['PYTHONPATH'] + ':.'
else:
    os.environ['PYTHONPATH'] = '.'

if __name__ == '__main__':
    navigator = PrinterNavigator()
    navigator.controller.createNode()
    time.sleep(2)
    navigator.controller.getNodeInfo()
    navigator.controller.jump(1,7,0)

    time.sleep(8)
    #navigator.controller.kill()

