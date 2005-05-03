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

import threading
from pprint import pprint
from cStringIO import StringIO

from solipsis.util.uiproxy import UIProxy
from solipsis.util.remote import RemoteConnector

from twisted.internet import protocol, reactor, defer
from twisted.protocols import basic

from validators import AddressValidator

COMMANDS = {"check": ["chech status of connection", ""],
            "mem": ["dump a snapshot of memory (debugging tool)", ""],
            "about": ["display general information", ""],
            "create": ["create Node", "Guest"],
            "connect": ["connect to specified node", "bots.netofpeers.net:8551"],
            "disconnect": ["discoonnect from current node", ""],
            "kill": ["kill node", ""],
            "jump": ["jump to node", "192.33.178.29:5010"],
            "pref": ["change preferences", ""],
            "quit": ["close navigator", ""],
            "display": ["display current address", '192.33.178.29:5010'""],
            "go": ["go to position", "0,0"],
            "menu": ["display peer menu", ""],
            "hover": ["emumate hover on peer", "0,0"],
            "help": ["display help [on cmd]", "all"]}

class NetworkLoop(threading.Thread):
    """
    NetworkLoop is an event loop running in its own thread.
    It manages socket-based communication with the Solipsis node
    and event-based communication with the User Interface (UI).
    """
    def __init__(self, reactor, ui_service):
        """
        Builds a network loop from a Twisted reactor and a Wx event handler.
        """
        super(NetworkLoop, self).__init__()
        self.repeat_hello = True
        self.repeat_count = 0
        self.ui = UIProxy(ui_service)
        self.reactor = reactor

        self.angle = 0.0
        self.remote_connector = RemoteConnector(self.reactor, self.ui)

    def run(self):
        """
        Run the reactor loop.
        """
        self.reactor.run(installSignalHandlers=0)

    #
    # Actions from the UI thread
    #
    def ConnectToNode(self, *args, **kargs):
        self.remote_connector.Connect(*args, **kargs)

    def DisconnectFromNode(self, *args, **kargs):
        self.remote_connector.Disconnect(*args, **kargs)

    def KillNode(self, *args, **kargs):
        self.remote_connector.Kill(*args, **kargs)

class SolipsisUiProtocol(basic.LineReceiver):

    def __init__(self):
        self.cmd = None

    def connectionMade(self):
        self.transport.write("type help to get available commands\r\n")
        
    def lineReceived(self, line):
        cmd_passed = line.strip().lower()
        if cmd_passed in ["q", "exit"]:
            self.transport.loseConnection()
            return
        if not self.cmd:
            # define function to be called
            try:
                cmd = "do_" + cmd_passed
                self.cmd = getattr(self.factory, cmd)
                if COMMANDS[cmd_passed][1]:
                    # display default param 
                    self.transport.write("[%s]"% COMMANDS[cmd_passed][1])
                else:
                    # call function if none needed
                    out_msg = self.cmd("")
                    if out_msg:
                        self.transport.write(out_msg+"\r\n")
                    self.cmd = None
            except AttributeError:
                self.transport.write("%s not a valid command\n"% line)
        else:
            # call function with param
            out_msg = self.cmd(line)
            if out_msg:
                self.transport.write(out_msg+"\r\n")
            self.cmd = None

class SolipsisUiFactory(protocol.ServerFactory):

    protocol = SolipsisUiProtocol

    def __init__(self, application):
        self.app = application
        self.address_val = AddressValidator()

    # UI events
    def do_check(self, arg):
        return str(self.app._CheckNodeProxy())
    
    def do_mem(self, arg):
        return self.app._MemDebug()

    # UI events in menu
    def do_about(self, arg):
        return self.app._About(arg)

    def do_create(self, arg):
        return self.app._CreateNode(arg)

    def do_connect(self, arg):
        stream = StringIO()
        args = self.address_val._Validate(arg)
        if not args:
            args = self.address_val._Validate(COMMANDS['connect'][1])
            print >> stream,  "no valid address. Default used..."
        host, port = args.groups()
        self.app.config_data.host = host
        self.app.config_data.port = int(port)
        print >> stream,  self.app._OpenConnect(arg)
        return stream.getvalue()
        
    def do_disconnect(self, arg):
        return self.app._Disconnect(arg)

    def do_kill(self, arg):
        print "calling _Kill" 
        self.app._Kill(arg)

    def do_jump(self, arg):
        args = self.address_val._Validate(arg)
        if not args:
            args = self.address_val._Validate(COMMANDS['jump'][1])
        return self.app._JumpNear(arg)

    def do_pref(self, arg):
        return self.app._Preferences(arg)

    def do_quit(self, arg):
        print "calling _Quit" 
        self.app._Quit(arg)

    def do_display(self, arg):
        return self.app._DisplayNodeAddress(arg)

    # UI events in viewport
    def do_go(self, arg):
        # arg must be like 'x,y'
        try:
            position = [int(coord) for coord in arg.split(',')]
            if len(position) == 2:
                self.app._LeftClickViewport(position)
            else:
                return "enter position as 'x,y'"
        except ValueError:
            return "enter position as 'x,y'"

    def do_menu(self, arg):
        return self.app._RightClickViewport(arg)

    def do_hover(self, arg):
        print "calling _HoverViewport" 
        self.app._HoverViewport(arg)

    def do_help(self, arg):
        str_stream = StringIO()
        if arg in ["", "all"]:
            pprint(COMMANDS, str_stream)
        elif arg in COMMANDS:
            print >> str_stream, COMMANDS[arg][0]
        else:
            print >> str_stream, "available commands are:"
            pprint(COMMANDS, str_stream)
        return str_stream.getvalue()
