# pylint: disable-msg=C0103,C0101,W0142,W0613
# name not valid // oo short name // use * or ** // Unused argument
#<copyright>
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
"""Base class for application: common initialisation and management functions"""

import os
import gc
import gettext
import socket
_ = gettext.gettext

from solipsis.util.urls import SolipsisURL
from solipsis.util.address import Address
from solipsis.util.network import get_free_port
from solipsis.util.entity import ServiceData
from solipsis.util.position import Position
from solipsis.util.uiproxy import TwistedProxy, UIProxyReceiver
from solipsis.util.memdebug import MemSizer
from solipsis.util.launch import Launcher

class BaseNavigatorApp(UIProxyReceiver):
    """
    Main application class
    """
    version = "0.1.1"
    config_file = os.sep.join(["state", "config.bin"])
    world_size = 2**128

    def __init__(self, params, *args, **kargs):
        """available kargs: port"""
        self.params = params
        self.alive = True
        self.node_proxy = None
        self.url_jump = self.params.url_jump or None
        self.connection_trials = 0
        if self.params.memdebug:
            self.memsizer = MemSizer()
            #~ gc.set_debug(gc.DEBUG_LEAK)
        else:
            self.memsizer = None
        # members that should be definied in specific classes
        self.config_data = None	 #__init__
        self.network_loop = None #InitNetwork
        self.services = None	 #InitServices
        self.world = None	 #InitResources
        self.viewport = None	 #InitResources
        # default value will be overridden by stun result
        self.local_ip = socket.gethostbyname(socket.gethostname())
        self.local_port = get_free_port()
        UIProxyReceiver.__init__(self)

    def OnInit(self):
        """
        Main initialization handler.
        """
        self._LoadConfig()
        self.InitResources()
        # creating components
        if self.memsizer:
            self._MemDebug()

    def InitIpAddress(self):
        """
        Get local address from Stun
        """
        raise NotImplementedError

    def InitResources(self):
        """
        Load UI layout from XML file(s).
        """
        raise NotImplementedError

    def InitTwisted(self):
        """
        Import and initialize the Twisted event loop.
        Note: Twisted will run in a separate thread from the GUI.
        """
        from twisted.internet import reactor
        from twisted.python import threadable
        threadable.init(1)
        self.reactor = reactor

    def InitNetwork(self):
        """
        Launch network event loop.
        """
        assert self.network_loop, "network_loop must be initialised first"
        self.network_loop.setDaemon(True)
        self.network_loop.start()
        self.network = TwistedProxy(self.network_loop, self.reactor)
        # get local ip
        self.InitIpAddress()

    def InitServices(self):
        """
        Initialize all services.
        """
        assert self.config_data, "config must be initialised first"
        assert self.services, "services must be initialised first"
        self.services.ReadServices()
        self.services.SetNode(self.config_data.GetNode())
        self.services.EnableServices()
        self.config_data.SetServices(self.services.GetServices())

    def Redraw(self):
        """
        Redraw the world view.
        """
        assert self.viewport, "viewport must be initialised first"
        self.viewport.Draw(onPaint=False)

    #
    # Helpers
    #
    def future_call(self, delay, function):
        """call function after delay (milli sec)"""
        raise NotImplementedError

    def display_message(self, title, msg):
        """Display message to user, using for instance a dialog"""
        raise NotImplementedError

    def display_error(self, title, msg):
        """Report error to user"""
        raise NotImplementedError

    def display_status(self, msg):
        """report a status"""
        raise NotImplementedError

    def _DestroyProgress(self):
        """
        Destroy progress dialog if necessary.
        """
        raise NotImplementedError
    
    def _SetWaiting(self, waiting):
        """
        Set "waiting" state of the interface.
        """
        raise NotImplementedError

    def _NotImplemented(self, evt=None):
        """
        Displays a dialog warning that a function is not implemented.
        """
        self.display_message(_("Not implemented"),
                             _("""This function is not yet implemented.
Sorry! Please come back later..."""))

    def _UpdateURLPort(self, url_port):
        """change URL Listener port"""
        filename = os.path.join('state', 'url_jump.port')
        f = file(filename, 'wb')
        f.write(str(url_port))
        f.close()

    def _CheckNodeProxy(self, display_error=True):
        """
        Checks if we are connected to a node, if not, displays a message box.
        Returns True if we are connected, False otherwise.
        """
        if self.node_proxy is not None:
            return True
        else:
            if display_error:
                self.display_message(_("Not connected"),
                                     _("This action cannot be performed, "
                                       "because you are not connected."))
            return False

    def _MemDebug(self):
        """debug display of garbage collector"""
        gc.collect()
        self.memsizer.sizeall()
        print "\n... memdump ...\n"
        items = self.memsizer.get_deltas()
        print "\n".join(items)
        self.future_call(1000.0 * 10, self._MemDebug)

    def _JumpNearAddress(self, address):
        """move node near given address"""
        if self._CheckNodeProxy():
            self.node_proxy.JumpNear(address.ToStruct())

    def _JumpNearURL(self, url_string):
        """change node position according to given url"""
        print "Received:", url_string
        if self._CheckNodeProxy(False):
            try:
                url = SolipsisURL.FromString(url_string)
            except ValueError, e:
                print str(e)
            else:
                self._JumpNearAddress(url.GetAddress())
            self.url_jump = None
        else:
            self.url_jump = url_string

    def _TryConnect(self, deferred=None):
        """
        Tries to connect to the configured node.
        """
        assert self.config_data, "config must be initialised first"
        assert self.services, "services must be initialised first"
        assert self.world, "world must be initialised first"
        assert self.viewport, "viewport must be initialised first"
        if self._CheckNodeProxy(False):
            self.network.DisconnectFromNode()
        self._SetWaiting(True)
        self.world.Reset()
        self.viewport.Reset()
        self.network.ConnectToNode(self.config_data, deferred)
        self.display_status("connecting to %s:%d"\
                            % (self.config_data.host, self.config_data.port))
        self.services.RemoveAllPeers()
        self.services.SetNode(self.config_data.GetNode())

    def _LaunchNode(self, deferred=None):
        """Create new node and connect"""
        assert self.config_data, "config must be initialised first"
        assert self.viewport, "viewport must be initialised first"
        self.config_data.Compute()
        l = Launcher(node_id=self.config_data.node_id,
            port=self.config_data.solipsis_port,
            control_port=self.config_data.local_control_port)
        # First try to spawn the node
        if not l.Launch():
            self.viewport.Disable()
            msg = _("""Node creation failed.
Please check you have sufficient rights.""")
            self.display_message(_("Kill refused"), msg)
            return
        # Then connect using its XMLRPC daemon
        # Hack so that the node has the time to launch
        self.connection_trials = 5
        self._TryConnect(deferred)

    def _MoveNode(self, (x, y), jump=False, jump_near=False):
        """
        Move the node and update our world view.
        """
        assert self.world, "world must be initialised first"
        self.world.UpdateNodePosition(Position((x, y, 0)),
                                      jump=jump or jump_near)
        if jump_near:
            self.node_proxy.JumpNearPosition(str(long(x)), str(long(y)), str(0))
        else:
            self.node_proxy.Move(str(long(x)), str(long(y)), str(0))

    def _LoadConfig(self):
        """helper to load config from file"""
        assert self.config_data, "config must be initialised first"
        # Load last saved config
        try:
            f = file(self.config_file, "rb")
            self.config_data.Load(f)
            f.close()
        except (IOError, EOFError):
            if os.path.exists(self.config_file):
                print "Config file '%s' broken, erasing"
                os.remove(self.config_file)

    def _SaveConfig(self):
        """
        Save current configuration to the user's config file.
        """
        assert self.config_data, "config must be initialised first"
        try:
            f = file(self.config_file, "wb")
            self.config_data.Save(f)
            f.close()
        except IOError, e:
            print "Failed to saved config:", str(e)

    #===-----------------------------------------------------------------===#
    # Event handlers for the main window
    # (in alphabetical order)
    #

    def _OnAbout(self, evt):
        """
        Called on "about" event (menu -> Help -> About).
        """
        msg = _("Solipsis Navigator") + " " \
              + self.version + "\n\n" \
              + _("Licensed under the GNU LGPL") + "\n(c) France Telecom R&D"
        self.display_message(_("About..."), msg)

    def _OnConnect(self, evt=None):
        """
        Called on "connect" event (menu -> File -> Connect).
        """
        assert self.config_data, "config_data must be defined first"
        if self.config_data.connection_type == 'local':
            # Local connection mode: create a dedicated Solipsis node
            self._LaunchNode()
        else:
            # Remote connection mode: connect to an existing node
            self.connection_trials = 0
            self._TryConnect()

    def _OnDisconnect(self, evt):
        """
        Called on "disconnect" event (menu -> File -> Disconnect).
        """
        self._DestroyProgress()
        self._SetWaiting(False)
        if self._CheckNodeProxy():
            assert self.services, "services must be initialised first"
            assert self.viewport, "viewport must be initialised first"
            self.network.DisconnectFromNode()
            self.node_proxy = None
            self.viewport.Disable()
            self.Redraw()
            self.display_status(_("Not connected"))
            self.services.RemoveAllPeers()

    def _OnDisplayAddress(self, evt=None):
        """
        returns address of the node.
        """
        self.display_message("Address", self.world.GetNode().address.ToString())

    def _OnJumpNear(self, evt):
        """
        move node address to address evt (like slp://192.33.178.29:5010/).
        """
        assert isinstance(evt, str) or isinstance(evt, unicode), \
               "adress must be formatted as slp://192.33.178.29:5010/"
        try:
            address = Address.FromString(evt)
        except ValueError:
            self._JumpNearURL(evt)
        else:
            self._JumpNearAddress(address)

    def _OnJumpPos(self, evt):
        """
        change position according to evt, formated as (x,y).
        """
        assert len(evt) == 2, "_OnJumpPos must be called with tuple (x, y)"
        x, y = evt
        self._MoveNode((x * self.world_size, y * self.world_size),
                       jump_near=True)

    def _OnKill(self, evt):
        """
        Called on "kill" event (menu -> File -> Kill).
        """
        if self._CheckNodeProxy():
            assert self.services, "services must be initialised first"
            self.network.KillNode()
            self.services.RemoveAllPeers()

    def _OnQuit(self, evt):
        """
        Called on quit event (menu -> File -> Quit, window close box).
        """
        self.alive = False
        self._SaveConfig()
        # Kill the node if necessary
        if self.config_data.node_autokill and self._CheckNodeProxy(False):
            self.network.KillNode()
            self._SetWaiting(True)
            # Timeout in case the Kill request takes too much time to finish
            self.future_call(1000, self._Quit2)
        else:
            self._Quit2()

    def _Quit2(self):
        """
        The end of the quit procedure ;-)
        """
        assert self.services, "services must be initialised first"
        # Disable event proxying: as of now, all UI -> network
        # and network -> UI events will be discarded
        self.DisableProxy()
        self.network.DisableProxy()
        # Finish running services
        self.services.Finish()
        # Now we are sure that no more events are pending, kill everything
        self.reactor.stop()


    #===-----------------------------------------------------------------===#
    # Actions from the network thread(s)
    #
    def AddPeer(self, *args, **kargs):
        """
        Add an object to the viewport.
        """
        assert self.services, "services must be initialised first"
        assert self.world, "world must be initialised first"
        self.world.AddPeer(*args, **kargs)
        self.services.AddPeer(*args, **kargs)

    def RemovePeer(self, *args, **kargs):
        """
        Remove an object from the viewport.
        """
        assert self.services, "services must be initialised first"
        assert self.world, "world must be initialised first"
        self.world.RemovePeer(*args, **kargs)
        self.services.RemovePeer(*args, **kargs)

    def UpdatePeer(self, *args, **kargs):
        """
        Update an object.
        """
        assert self.services, "services must be initialised first"
        assert self.world, "world must be initialised first"
        self.world.UpdatePeer(*args, **kargs)
        self.services.UpdatePeer(*args, **kargs)

    def UpdateNode(self, *args, **kargs):
        """
        Update node information.
        """
        assert self.services, "services must be initialised first"
        assert self.world, "world must be initialised first"
        self.services.SetNode(*args, **kargs)
        self.world.UpdateNode(*args, **kargs)
    
    def UpdateNodePosition(self, *args, **kargs):
        """
        Update node position.
        """
        assert self.world, "world must be initialised first"
        self.world.UpdateNodePosition(*args, **kargs)
    
    def ProcessServiceData(self, *args, **kargs):
        """
        Process service-specific data.
        """
        assert self.services, "services must be initialised first"
        self.services.ProcessServiceData(*args, **kargs)

    def ResetWorld(self, *args, **kargs):
        """
        Reset the world and the viewport.
        """
        assert self.world, "world must be initialised first"
        self.world.Reset(*args, **kargs)

    def SetStatus(self, status):
        """
        Change connection status.
        """
        assert self.viewport, "viewport must be initialised first"
        if status == 'READY':
            self._SetWaiting(False)
            self.viewport.Enable()
            self.Redraw()
            self.display_status(_("Connected"))
        elif status == 'BUSY':
            self._SetWaiting(True)
            self.viewport.Enable()
            self.Redraw()
            self.display_status(_("Searching peers"))
        elif status == 'UNAVAILABLE':
            self._SetWaiting(False)
            self.viewport.Disable()
            self.Redraw()
            self.display_status(_("Not connected"))
        if self.url_jump:
            self._JumpNearURL(self.url_jump)

    def NodeConnectionSucceeded(self, node_proxy):
        """
        We managed to connect to the node.
        """
        assert self.config_data, "config must be initialised first"
        self._DestroyProgress()
        self._SetWaiting(False)
        # We must call the node proxy from the Twisted thread!
        self.node_proxy = TwistedProxy(node_proxy, self.reactor)
        self.node_proxy.SetNodeInfo(self.config_data.GetNode().ToStruct())
        self.display_status(_("Connected"))

    def NodeConnectionFailed(self, error):
        """
        Failed connecting to the node.
        """
        self._DestroyProgress()
        self._SetWaiting(False)
        self.node_proxy = None
        self.display_status(_("Not connected"))
        msg = _("""Connection to the node has failed.
Please the check the node is running, then retry.""")
        self.display_error(_("Connection error"), msg)

    def NodeKillSucceeded(self):
        """
        We managed to kill the (remote/local) node.
        """
        if self.alive:
            assert self.viewport, "viewport must be initialised first"
            self.node_proxy = None
            self._SetWaiting(False)
            self.viewport.Disable()
            self.Redraw()
            self.display_status(_("Not connected"))
        else:
            # If not alive, then we are in the quit phase
            self._Quit2()

    def NodeKillFailed(self):
        """
        The node refused to kill itself.
        """
        if self.alive:
            assert self.viewport, "viewport must be initialised first"
            self.node_proxy = None
            self._SetWaiting(False)
            self.viewport.Disable()
            msg = _("You cannot kill this node.")
            self.display_error(_("Kill refused"), msg)
        else:
            # If not alive, then we are in the quit phase
            self._Quit2()
 
    #===-----------------------------------------------------------------===#
    # Actions from the services
    #
    def SendServiceData(self, peer_id, service_id, data):
        """use UDP link between nodes to send data"""
        if self._CheckNodeProxy(False):
            d = ServiceData(peer_id, service_id, data)
            self.node_proxy.SendServiceData(d.ToStruct())
