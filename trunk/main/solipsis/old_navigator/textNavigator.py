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
import xmlrpclib
import curses.wrapper
import sys

from solipsis.util.parameter import Parameters
from solipsis.navigator.controller import Controller

def init():
    configFileName = "conf/solipsis.conf"
    
    param = Parameters(configFileName)
    host, ctlPort, notifPort, logger = param.getControlParams()
    
    controller = Controller([host, ctlPort, notifPort, logger])
    return controller

def main():
    controller = init()
    scr = curses.initscr()
    try:
        # don't echo user keys
        curses.noecho()
        
        # create new windows
        y, x = scr.getmaxyx()
        main = curses.newwin(y-3, x, 0, 0)
        help = curses.newwin(3, x,y-3,0)

        help.addstr("Press q to quit, s to start a new node, " +
                    "i for node info, k to kill node")
        help.refresh()
        while 1:
            c = main.getch()
            try:
                if c == ord('q'): break
                elif c == ord('s'):
                    controller.createNode()
                    controller.connect()
                    main.addstr("node started")
                elif c == ord('d'):
                    main.addstr("node disconnected")
                elif c == ord('k'):
                    main.clear()
                    controller.kill()
                    main.addstr("node killed")
                    main.refresh()
                elif c== ord('i'):
                    main.erase()
                    main.clear()
                    info = controller.getNodeInfo()   
                    main.addstr("node info: id=%s host=%s posX=%s posY=%s"
                                %(info[0], info[1], info[3], info[4]))
                    main.refresh()                    
            except:
                main.addstr(2,0,"exception " + str(sys.exc_type) +
                            " " + str(sys.exc_value))
                main.refresh()
        

        
        # and never forget to deinitialize curses
    finally:
        curses.endwin()    



    
if __name__ == '__main__':
    #curses.wrapper(window)
    main()

#os.system("python startup.py")
#server = xmlrpclib.ServerProxy("http://"+ host + ":" + str(port))



