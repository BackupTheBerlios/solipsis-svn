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


# TODO: can we force the charset to UTF-8 ?

import wx
import wx.xrc

locale = None

def InitLocale():
    """
    Locale initialization.
    """
    global locale, charset
    print "Getting locale:",
    locale = wx.GetLocale()
    if locale is None:
        print "Failed to get locale!"
    else:
        print locale.GetName()

def _(orig_string):
    """
    Translation function for wxWidgets.
    """
    if locale is None:
        InitLocale()
    if locale is None:
        return orig_string
    return wx.GetTranslation(orig_string)

def GetCharset():
    """
    Get the name of the current charset.
    """
    return str(wx.Locale.GetSystemEncodingName())


class IdPool(object):
    """
    Autogrowing pool of wxWidgets IDs.
    (why do we need them ? Grr)
    """
    def __init__(self):
        self.ids = []
        self.Begin()
    
    def Begin(self):
        self.cursor = 0
    
    def GetId(self):
        if self.cursor == len(self.ids):
            new_id = wx.NewId()
            self.ids.append(new_id)
        else:
            new_id = self.ids[self.cursor]
        self.cursor += 1
        return new_id


class XRCLoader(object):
    """
    This class is a mix-in that allows loading resources from an XRC file.
    """
    _resource = None

    def LoadResource(self, file_name):
        """
        Load resource tree from the specified resource file.
        """
        self._resource = wx.xrc.XmlResource.Get()
        self._resource.InitAllHandlers()
        self._resource.Load(file_name)

    def Resource(self, name):
        """
        Get a specific object from its resource ID.
        """
        if self._resource is None:
            raise RuntimeError("XRC resource not initialized")
        print "loading XRC object: %s" % name
        attr = self._resource.LoadObject(None, name, "")
        if attr is None:
            raise NameError("resource object '%s' does not exist" % name)
        return attr


class ManagedData(object):
    """
    Derive this class to create Managed data for use with validators.
    """
    def __init__(self):
        object.__setattr__(self, '_dict', {})

    def __setattr__(self, name, value):
        try:
            self._dict[name][0] = value
        except KeyError:
            self._dict[name] = [value]

    def __getattr__(self, name):
        assert name != "_dict"
        return self._dict[name][0]

    def GetDict(self):
        """
        Returns a dict contain managed datas in an unmanaged way.
        Changes to this dict will not be propagated to the object attributes.
        """
        d = {}
        for k, v in self._dict.iteritems():
            d[k] = v[0]
        return d

    def UpdateDict(self, d):
        """
        Update the attributes with a dictionnary containing values.
        """
        for k, v in d.iteritems():
            try:
                self._dict[k][0] = v
            except KeyError:
                self._dict[k] = [v]

    def Ref(self, name):
        """
        Returns a reference to an attribute, i.e. the list that contains
        the attribute as sole element.
        """
        return self._dict[name]


class Validator(wx.PyValidator):
    """
    This class holds the basic primitives for writing validators,
    with optional handling of a data reference where to copy the value from/to.
    """

    def __init__(self, list_ref=None):
        wx.PyValidator.__init__(self)
        self.list_ref = list_ref
        self.SetBellOnError(True)
        self.message = _("Please fill this form correctly")

    def Clone(self):
        if self.list_ref:
            assert isinstance(self.list_ref, list) and len(self.list_ref) == 1
        return self.__class__(self.list_ref)

    def TransferFromWindow(self):
        if self.list_ref:
            self.list_ref[0] = self._ReprToData(self.GetWindow().GetValue())
            #~ print "->", self.list_ref[0]
        return True

    def TransferToWindow(self):
        if self.list_ref:
            self.GetWindow().SetValue(self._DataToRepr(self.list_ref[0]))
            #~ print "<-", self.list_ref[0]
        return True

    def Validate(self, window):
        control = self.GetWindow()
        # Do not check the input if the widget is actually disabled
        if not control.IsEnabled():
            return True
        value = control.GetValue()
        if self._Validate(value):
            self.TransferFromWindow()
            return True
        else:
            wx.MessageBox(self.message, caption=_("Error"), style=wx.OK | wx.ICON_ERROR)
            return False
