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

from pprint import pprint
from cStringIO import StringIO

from twisted.internet import protocol, defer
from twisted.protocols import basic
from solipsis.navigator.validators import AddressValidator
from solipsis.navigator.network import BaseNetworkLoop
from solipsis.util.uiproxy import TwistedProxy

class NetworkLoop(BaseNetworkLoop):
    """
    NetworkLoop should be an event loop running in its own
    thread. However, in this version of the navigator, it shares the
    thread of the reactor.
    """
    def __init__(self, reactor, ui, testing=False):
        BaseNetworkLoop.__init__(self, reactor, TwistedProxy(ui, reactor), testing)

class Commands:

    def __init__(self, name, help, *args, **kwargs):
        """kwargs contains 'converter' which is the function used on conversion"""
        self.name = name
        self.help = help
        if 'converter' in kwargs:
            self.converter = kwargs['converter']
        else:
            self.converter = lambda s: (str(s),)
        self.args = args

    def convert(self, *args):
        """formats input thanks to converter"""
        return self.converter(*args)

    def call(self, factory, deferred, *args):
        """check given args and use default ones accordingly, or none
        at all. Call corresponding function inb factory and returns
        its result.

        *args are forwarded to function called on factory"""
        # get function
        function = getattr(factory, "do_" + self.name)
        # call function
        if len(args) > 0:
            return function(deferred, *args)
        else:
            if self.args is None:
                return function(deferred)
            else:
                return function(deferred, *self.args)

######
#
# WRAPPER for Navigator
#
######
def _get_separator(string):
    if ":" in string:
        separator = ":"
    elif " " in string:
        separator = " "
    elif "," in string:
        separator = ","
    else:
        raise ValueError("no separator found")
    return separator

def address_converter(string):
    separator = _get_separator(string)
    address, port = string.split(separator)
    return (address, int(port))

def position_converter(string):
    separator = _get_separator(string)
    x, y = string.split(separator)
    return (float(x), float(y))

COMMANDS = {"about":   Commands("about", "display general information"),
            "launch": Commands("launch", "connect to local node"),
            "connect": Commands("connect", "connect to specified node",
                                "bots.netofpeers.net", 8554,
                                converter=address_converter),
            "disconnect": Commands("disconnect", "disconnect from current node"),
            "display": Commands("display", "display current address"),
            "jump":    Commands("jump", "jump to node",
                                "192.33.178.29:5010"),
            "go":      Commands("go", "go to position",
                                0, 0,
                                converter=position_converter),
            "where":   Commands("where", "display current position"),
            "kill":    Commands("kill", "kill node"),
            "quit":    Commands("quit", "close navigator"),
            "menu":    Commands("menu", "display peer menu"),
            "help":    Commands("help", "display help [on cmd]",
                                converter=lambda s: s.split(" "))}

class SolipsisUiProtocol(basic.LineReceiver):

    def connectionMade(self):
        self.factory.transport = self.transport
        if self.factory.app.initialised:
            self.sendLine("Ready")
        else:
            self.factory.initialised.append(
                defer.Deferred().addCallback(lambda b: self.sendLine("Ready")))

    def lineReceived(self, line):
        cmd_passed = line.strip().lower()
        # quit command
        if cmd_passed in ["q", "exit"]:
            self.transport.loseConnection()
            return
        # split command & arguments
        try:
            cmd_passed, args = cmd_passed.split(" ", 1)
        except ValueError:
            args = None
        # call
        try:
            command = COMMANDS[cmd_passed]
            deferred = defer.Deferred()
            deferred.addCallback(self.sendLine)
            if args:
                args = command.convert(args)
                msg = command.call(self.factory, deferred, *args)
            else:
                msg = command.call(self.factory, deferred)
            if not msg is None:
                deferred.callback(msg)
        except (KeyError, AttributeError), err:
            import traceback
            traceback.print_exc()
            self.sendLine("%s (in %s): %s"% (err.__class__, line, err))

class SolipsisUiFactory(protocol.ServerFactory):

    protocol = SolipsisUiProtocol

    def __init__(self, application):
        self.app = application
        self.address_val = AddressValidator()
        self.initialised = []

    # UI events in menu
    def do_about(self, deferred):
        return self.app._OnAbout()

    def do_launch(self, deferred):
        self.app.config_data.solipsis_port = 6010
        self.app.config_data.connection_type = 'local'
        self.app._OnConnect(deferred=deferred)

    def do_connect(self, deferred, host, port):
        self.app.config_data.connection_type = 'remote'
        self.app.config_data.host = host
        self.app.config_data.port = port
        self.app._OnConnect(deferred=deferred)

    def do_disconnect(self, deferred):
        return self.app._OnDisconnect()

    def do_display(self, deferred):
        return self.app._OnDisplayAddress()

    def do_jump(self, deferred, adress):
        self.app._OnJumpNear(adress)

    def do_go(self, deferred, x, y):
        stream = StringIO()
        self.app._OnJumpPos((x, y))

    def do_where(self, deferred):
        return self.app.get_position()

    def do_kill(self, deferred):
        self.app._OnKill(deferred)

    def do_quit(self, deferred):
        self.app._OnQuit(deferred)

    def do_menu(self, deferred):
        return "Not implemented yet"

    def do_help(self, deferred, *args):
        str_stream = StringIO()
        if args:
            for item in args:
                if item in COMMANDS:
                    print >> str_stream, item, ":", COMMANDS[item].help
                else:
                    print >> str_stream, item, "not available"
        else:
            print >> str_stream, "available commands are:", COMMANDS.keys()
        return str_stream.getvalue()
