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

import os
import gc
import bisect
import gettext
_ = gettext.gettext
from pprint import pprint
from cStringIO import StringIO
from threading import Timer

from solipsis.util.entity import ServiceData
from solipsis.util.address import Address
from solipsis.util.position import Position
from solipsis.util.uiproxy import TwistedProxy, UIProxyReceiver
from solipsis.util.memdebug import MemSizer
from solipsis.services.collector import ServiceCollector

from validators import *
from viewport import Viewport
from world import World
from statusbar import StatusBar
from network import NetworkLoop, SolipsisUiFactory
from config import ConfigData
from launch import Launcher

USE_SERVICE = ['profile']

class NavigatorApp(UIProxyReceiver):
    version = "0.1.1"
    config_file = os.sep.join(["state", "config.bin"])

    def __init__(self, params, *args, **kargs):
        self.params = params
        self.alive = True
        self.config_data = ConfigData()
        self.node_proxy = None
        if self.params.memdebug:
            self.memsizer = MemSizer()
        else:
            self.memsizer = None
        UIProxyReceiver.__init__(self)
        self.OnInit()

    def InitTwisted(self):
        """
        Import and initialize the Twisted event loop.
        Note: Twisted will run in a separate thread from the GUI.
        """
        from twisted.internet import reactor
        from twisted.python import threadable
        threadable.init(1)
        self.reactor = reactor

    def InitWx(self):
        raise NotImplementedError

    def InitResources(self):
        self.viewport = Viewport()
        self.statusbar = StatusBar(_("Not connected"))

    def InitValidators(self):
        raise NotImplementedError

    def InitNetwork(self):
        """
        Launch network event loop.
        """
        loop = NetworkLoop(self.reactor, self)
        loop.setDaemon(True)
        loop.start()
        self.network_loop = loop
        self.network = TwistedProxy(loop, self.reactor)

    def InitServices(self):
        """
        Initialize all services.
        """
        self.services = ServiceCollector(self.params, self.reactor)
        for service in USE_SERVICE:
            service_path = self.services._ServiceDirectory(service)
            service_id, plugin =self.services.LoadService(service_path, service)
            self.services.InitService(service_id, plugin)
        self.services.SetNode(self.config_data.GetNode())
        self.services.EnableServices()
        self.config_data.SetServices(self.services.GetServices())

    def OnInit(self):
        """
        Main initialization handler.
        """
        # Load last saved config
        try:
            f = file(self.config_file, "rb")
            self.config_data.Load(f)
        except (IOError, EOFError):
            if os.path.exists(self.config_file):
                print "Config file '%s' broken, erasing"
                os.remove(self.config_file)
        # creating components
        if self.memsizer:
            self._MemDebug()
        print "setting resources"
        self.InitResources()
        print "creating world"
        self.world = World(self.viewport)
        print "setting network and services"
        # Other tasks 
        self.InitTwisted()
        self.InitNetwork()
        self.InitServices()
        print "UI launched"
        self.reactor.listenTCP(1079, SolipsisUiFactory(self))
        self.reactor.run()

    def Redraw(self):
        raise NotImplementedError

    def AskRedraw(self):
        raise NotImplementedError

    def OnIdle(self, event):
        raise NotImplementedError
    
    def OnPaint(self, event):
        raise NotImplementedError

    def OnResize(self, event):
        raise NotImplementedError

    #
    # Helpers
    #
    def _NotImplemented(self, evt=None):
        """
        Displays a dialog warning that a function is not implemented.
        """
        print _("This function is not yet implemented.\nSorry! Please come back later...")

    def _CheckNodeProxy(self, display_error=True):
        """
        Checks if we are connected to a node, if not, displays a message box.
        Returns True if we are connected, False otherwise.
        """
        if self.node_proxy is not None:
            return True
        else:
            if display_error:
                print _("This action cannot be performed, because you are not connected to a node.")
            return False
    
    def _MemDebug(self):
        if self.memsizer:
            stream = StringIO()
            gc.collect()
            self.memsizer.sizeall()
            print >> stream, "\n... memdump ...\n"
            items = self.memsizer.get_deltas()
            print >> stream, "\n".join(items)
            t = Timer(10, self._MemDebug)
            t.start()
            print >> stream, "\n\n"
            return stream.getvalue()
        else:
            return "navigator not launched in debug mode"
    
    def _TryConnect(self):
        """
        Tries to connect to the configured node.
        """
        if self._CheckNodeProxy(False):
            self.network.DisconnectFromNode()
        self._SetWaiting(True)
        self.viewport.Reset()
        self.network.ConnectToNode(self.config_data)
        self.statusbar.SetText(_("Connecting"))
        self.services.RemoveAllPeers()
        self.services.SetNode(self.config_data.GetNode())
        return "connecting to %s:%d"% (self.config_data.host, self.config_data.port)
    
    def _DestroyProgress(self):
        raise NotImplementedError
    
    def _SetWaiting(self, waiting):
        if waiting:
            print "Waiting ..."
        else:
            print "Wait ended."


    #===-----------------------------------------------------------------===#
    # Event handlers for the main window
    # (in alphabetical order)
    #
    def _About(self, evt):
        """
        Called on "about" event (menu -> Help -> About).
        """
        return _("Solipsis Navigator") + " " + self.version + "\n\n" + _("Licensed under the GNU LGPL") + "\n(c) France Telecom R&D"

    def _OpenBookmarksDialog(self, evt):
        """Not necessary in cmdClient"""
        raise NotImplementedError

    def _CreateNode(self, evt):
        """
        Called on "create node" event (menu -> File -> New node).
        """
        stream = StringIO()
        print >> stream, "creating node for", self.config_data.pseudo
        l = Launcher(port=self.config_data.solipsis_port)
        # First try to spawn the node
        if not l.Launch():
            self.viewport.Disable()
            print >> stream, _("Node creation failed. \nPlease check you have sufficient rights.")
            return stream.getvalue()
        # Then connect using its XMLRPC daemon
        self.config_data.host = 'localhost'
        self.config_data.port = 8550
        self.config_data.proxymode_auto = False
        self.config_data.proxymode_manual = False
        self.config_data.proxymode_none = True
        self.config_data.Compute()
        # Hack so that the node has the time to launch
        self.connection_trials = 5
        print >> stream, self._TryConnect()
        return stream.getvalue()

    def _OpenConnect(self, evt):
        self.config_data.Compute()
        self.connection_trials = 0
        return self._TryConnect()
        
    def _Disconnect(self, evt):
        """
        Called on "disconnect" event (menu -> File -> Disconnect).
        """
        self._SetWaiting(False)
        if self._CheckNodeProxy():
            self.network.DisconnectFromNode()
            self.node_proxy = None
            self.viewport.Disable()
            self.statusbar.SetText(_("Not connected"))
            self.services.RemoveAllPeers()
            return _("Not connected")
        else:
            return "not connected"

    def _DisplayNodeAddress(self, evt):
        """
        Called on "node address" event (menu -> Actions -> Jump Near).
        """
        if self._CheckNodeProxy():
            return self.world.GetNode().address.ToString()
        else:
            return "not connected"

    def _JumpNear(self, evt):
        """
        Called on "jump near" event (menu -> Actions -> Node address).
        """
        if self._CheckNodeProxy():
            try:
                address = Address.FromString(evt)
            except ValueError, e:
                return str(e)
            else:
                self.node_proxy.JumpNear(address.ToStruct())
        else:
            return "not connected"

    def _Kill(self, evt):
        """
        Called on "kill" event (menu -> File -> Kill).
        """
        if self._CheckNodeProxy():
            self.network.KillNode()
            self.services.RemoveAllPeers()
        else:
            return "not connected"

    def _Preferences(self, evt):
        """
        Called on "preferences" event (menu -> File -> Preferences).
        """
        stream = StringIO()
        self.config_data.Compute()
        pprint(self.config_data.__dict__["_dict"], stream)
        return stream.getvalue()

    def _Quit(self, evt):
        """
        Called on quit event (menu -> File -> Quit, window close box).
        """
        self.alive = False
        # Save current configuration
        try:
            f = file(self.config_file, "wb")
            self.config_data.Save(f)
            f.close()
        except IOError, e:
            print str(e)
        # Kill the node if necessary
        if self.config_data.node_autokill and self._CheckNodeProxy(False):
            self.network.KillNode()
            self._SetWaiting(True)
            # Timeout in case the Kill request takes too much time to finish
            t = Timer(1, self._Quit2)
            t.start()
        else:
            self._Quit2()
    
    def _Quit2(self):
        """
        The end of the quit procedure ;-)
        """
        # Disable event proxying: as of now, all UI -> network
        # and network -> UI events will be discarded
        self.DisableProxy()
        self.network.DisableProxy()
        # Finish running services
        self.services.Finish()
        # Now we are sure that no more events are pending, kill everything
        self.reactor.stop()

    def _ToggleAutoRotate(self, evt):
        raise NotImplementedError


    #===-----------------------------------------------------------------===#
    # Event handlers for the about dialog
    #
    def _CloseAbout(self, evt):
        raise NotImplementedError


    #===-----------------------------------------------------------------===#
    # Event handlers for the connect dialog
    #
    def _CloseConnect(self, evt):
        raise NotImplementedError

    def _ConnectOk(self, evt):
        raise NotImplementedError


    #===-----------------------------------------------------------------===#
    # Event handlers for the world viewport
    #
    def _KeyPressViewport(self, evt):
        raise NotImplementedError

    def _LeftClickViewport(self, evt):
        """
        Called on left click event.
        """
        if self._CheckNodeProxy(False):
            x, y = evt
            self.world.UpdateNodePosition(Position((x, y, 0)))
            self.node_proxy.Move(str(long(x)), str(long(y)), str(0))
        else:
            return "not connected"

    def _RightClickViewport(self, evt):
        """
        Called on right click event.
        """
        stream = StringIO()
        if self._CheckNodeProxy(False):
            l = self.services.GetPointToPointActions(id_)
            if len(l) > 0:
                for item in l:
                    print >> stream, item
                print  >> stream,'---'
            print >> stream, _("Disconnect")
        else:
            print >> stream, _("Connect to node")
        return stream.getvalue()

    def _HoverViewport(self, evt):
        """
        Called on mouse movement in the viewport.
        """
        if self._CheckNodeProxy(False):
            x, y = evt.GetPositionTuple()
            changed, id_ = self.viewport.Hover((x, y))
            if changed and id_:
                self.statusbar.SetTemp(self.world.GetPeer(id_).pseudo)
            elif changed and not id_:
                self.statusbar.Reset()
        else:
            return "not connected"


    #===-----------------------------------------------------------------===#
    # Actions from the network thread(s)
    #
    def AddPeer(self, *args, **kargs):
        """
        Add an object to the viewport.
        """
        self.world.AddPeer(*args, **kargs)
        self.services.AddPeer(*args, **kargs)

    def RemovePeer(self, *args, **kargs):
        """
        Remove an object from the viewport.
        """
        self.world.RemovePeer(*args, **kargs)
        self.services.RemovePeer(*args, **kargs)

    def UpdatePeer(self, *args, **kargs):
        """
        Update an object.
        """
        self.world.UpdatePeer(*args, **kargs)
        self.services.UpdatePeer(*args, **kargs)

    def UpdateNode(self, *args, **kargs):
        """
        Update node information.
        """
        self.services.SetNode(*args, **kargs)
        self.world.UpdateNode(*args, **kargs)
    
    def UpdateNodePosition(self, *args, **kargs):
        """
        Update node position.
        """
        self.world.UpdateNodePosition(*args, **kargs)
    
    def ProcessServiceData(self, *args, **kargs):
        """
        Process service-specific data.
        """
        self.services.ProcessServiceData(*args, **kargs)

    def ResetWorld(self, *args, **kargs):
        """
        Reset the world and the viewport.
        """
        self.world.Reset(*args, **kargs)

    def SetStatus(self, status):
        """
        Change connection status.
        """
        if status == 'READY':
            self._SetWaiting(False)
            self.viewport.Enable()
            self.statusbar.SetText(_("Connected"))
        elif status == 'BUSY':
            self._SetWaiting(True)
            self.viewport.Enable()
            self.statusbar.SetText(_("Searching peers"))
        elif status == 'UNAVAILABLE':
            self._SetWaiting(False)
            self.viewport.Disable()
            self.statusbar.SetText(_("Not connected"))

    def NodeConnectionSucceeded(self, node_proxy):
        """
        We managed to connect to the node.
        """
        # We must call the node proxy from the Twisted thread!
        self._SetWaiting(False)
        self.node_proxy = TwistedProxy(node_proxy, self.reactor)
        self.statusbar.SetText(_("Connected"))
        print "NodeConnectionSucceeded", node_proxy

    def NodeConnectionFailed(self, error):
        """
        Failed connecting to the node.
        """
        self._SetWaiting(False)
        self.node_proxy = None
        self.statusbar.SetText(_("Not connected"))
        print _("Connection to the node has failed. \nPlease the check the node is running, then retry.")

    def NodeKillSucceeded(self):
        """
        We managed to kill the (remote/local) node.
        """
        if self.alive:
            self.node_proxy = None
            self._SetWaiting(False)
            self.viewport.Disable()
            self.statusbar.SetText(_("Not connected"))
        else:
            # If not alive, then we are in the quit phase
            self._Quit2()
        print "NodeKillSucceeded"

    def NodeKillFailed(self):
        """
        The node refused to kill itself.
        """
        if self.alive:
            self.node_proxy = None
            self._SetWaiting(False)
            self.viewport.Disable()
            print _("You cannot kill this node.")
        else:
            # If not alive, then we are in the quit phase
            self._Quit2()
        print "NodeKillFailed"

    #===-----------------------------------------------------------------===#
    # Actions from the services
    #
    def SetServiceMenu(self, service_id, title, menu):
        print "SetServiceMenu:", title, service_id

    def SendServiceData(self, peer_id, service_id, data):
        if self._CheckNodeProxy(False):
            d = ServiceData(peer_id, service_id, data)
            self.node_proxy.SendServiceData(d.ToStruct())
