
import wx
import wx.xrc

locale = None

def _(orig_string):
    """ Translation function for wxWidgets. Automatically manages locale initialization. """

    global locale
    if locale is None:
        print "Getting locale:",
        locale = wx.GetLocale()
        if locale is None:
            print "Failed to get locale!"
        else:
            print locale.GetName()
    if locale is None:
        return orig_string
    return wx.GetTranslation(orig_string)


class XRCLoader(object):
    """ This class is a mix-in that allows loading resources from an XRC file. """

    _resource = None

    def LoadResource(self, file_name):
        """ Load resource tree from the specified resource file. """

        self._resource = wx.xrc.XmlResource.Get()
        self._resource.InitAllHandlers()
        self._resource.Load(file_name)

    def Resource(self, name):
        """ Get a specific object from its resource ID. """

        if self._resource is None:
            raise RunTimeError("XRC resource not initialized")
        print "loading XRC object: %s" % name
        attr = self._resource.LoadObject(None, name, "")
        if attr is None:
            raise NameError("resource object '%s' does not exist" % name)
        return attr


class ManagedData(object):
    """ Derive this class to create Managed data for use with validators. """

    def __init__(self):
        object.__setattr__(self, '_dict', {})

    def __setattr__(self, name, value):
        try:
            self._dict[name][0] = value
        except:
            self._dict[name] = [value]

    def __getattr__(self, name):
        assert name != "_dict"
        return self._dict[name][0]

    def Ref(self, name):
        return self._dict[name]


class Validator(wx.PyValidator):
    """ This class holds the basic primitives for writing validators,
    with optional handling of a data reference where to copy the value from/to. """

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
            print "->", self.list_ref[0]
        return True

    def TransferToWindow(self):
        if self.list_ref:
            self.GetWindow().SetValue(self._DataToRepr(self.list_ref[0]))
            print "<-", self.list_ref[0]
        return True

    def Validate(self, window):
        value = self.GetWindow().GetValue()
        if self._Validate(value):
            self.TransferFromWindow()
            return True
        else:
            wx.MessageBox(self.message, caption=_("Error"), style=wx.OK | wx.ICON_ERROR)
            return False
