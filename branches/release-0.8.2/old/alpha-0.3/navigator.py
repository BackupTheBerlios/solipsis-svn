import xmlrpclib
import curses.wrapper
from parameter import Parameters
from controller import Controller
import sys

configFileName = "solipsis.conf"

param = Parameters(configFileName)
[host, port, logger] = param.getControlParams()

controller = Controller([host, port, logger])

def window(stdscr2):
    #begin_x = 20 ; begin_y = 7
    #height = 5 ; width = 40
    #stdscr = curses.newwin(height, width, begin_y, begin_x)

    stdscr = curses.newwin(4,80,0,0)
    responsewin = curses.newwin(5,15)

    #stdscr.addstr( "Pretty text", curses.color_pair(1) )
    stdscr.addstr( "Solipsis navigator")
    stdscr.addstr( 1, 0, "Press q to quit, s to start a new node, " +
                   "i for node info, k to kill node")
    stdscr.refresh()

    while 1:
        c = stdscr.getch()
        try:
            if c == ord('q'): break
            elif c == ord('s'):
                controller.createNode()
                controller.connect()
                responsewin.addstr("node created")
                responsewin.refresh()
            elif c == ord('d'): controller.disconnect()
            elif c == ord('k'):
                controller.kill()
                responsewin.addstr("node killed")
                responsewin.refresh()
            elif c== ord('i'): controller.getNodeInfo()                
        except:
            stdscr.addstr(2,0,"exception " + str(sys.exc_type) + str(sys.exc_value))
            stdscr.refresh()

def menu():
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
                    main.addstr("node started")
                elif c == ord('d'): main.addstr("node disconnected")
                elif c == ord('k'):
                    main.erase()
                    main.addstr("node killed")
                    main.refresh()
                elif c== ord('i'):
                    main.addstr("node info x=" + str(x) + " y="+str(y))
                    main.refresh()
                    help.refresh()
            except:
                main.addstr(2,0,"exception " + str(sys.exc_type) + str(sys.exc_value))
                main.refresh()
        

        
        # and never forget to deinitialize curses
    finally:
        curses.endwin()    



    
if __name__ == '__main__':
    #curses.wrapper(window)
    menu()

#os.system("python startup.py")
#server = xmlrpclib.ServerProxy("http://"+ host + ":" + str(port))



