import xmlrpclib
import curses.wrapper
import sys

from solipsis.util.parameter import Parameters
from solipsis.navigator.controller import Controller

def init():
    configFileName = "conf/solipsis.conf"
    
    param = Parameters(configFileName)
    [host, port, logger] = param.getControlParams()
    
    controller = Controller([host, port, logger])
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



