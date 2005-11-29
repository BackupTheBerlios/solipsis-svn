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
import wx
from wx.xrc import XRCCTRL, XRCID

from PIL import Image

from solipsis.util.compat import abspath, safe_unicode
from solipsis.util.uiproxy import UIProxyReceiver
from solipsis.util.wxutils import _
from solipsis.util.wxutils import *        # '*' doesn't import '_'

from repository import AcceptFilename


class ConfigDialog(wx.EvtHandler, XRCLoader, UIProxyReceiver):
    size = 64
    # We voluntarily limit the list of supported file formats
    # in order to make interoperability easier
    allowed_formats = ['PNG', 'GIF', 'JPEG']

    def __init__(self, plugin, plugin_dir):
        self.plugin = plugin
        self.plugin_dir = plugin_dir
        self.filename = 'avatars/mouette.jpg'
        self.avatar_dir = 'avatars'

        wx.EvtHandler.__init__(self)
        UIProxyReceiver.__init__(self)

    def ConfigureSingleFile(self, callback=None):
        """
        Launches the dialog to configure a single file.
        When done, returns the chosen file path, or None.
        (optionally invokes a callback if successful)
        """
        file_spec = "%s (PNG, JPEG, GIF)|*.gif;*.png;*.jpg;*.jpeg|%s (*.*)|*.*" \
            % (_("Images"), _("All files"))
        # Bug workaround for Windows, where os.path gives paths in the local
        # charset (e.g. "windows-1252") but wxWidgets tries to decode it using
        # the 'ascii' codec...
        charset = GetCharset()
        default_dir = safe_unicode(abspath(self.avatar_dir), charset)
        default_file = safe_unicode(os.path.basename(self.filename), charset)
        dialog = wx.FileDialog(None, _("Choose your avatar"),
            defaultDir=default_dir,
            defaultFile=default_file,
            wildcard=file_spec,
            style=wx.OPEN | wx.FILE_MUST_EXIST,
        )
        # Loop while the user tries to choose a file and the file is not acceptable
        while dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetPath()
            try:
                # Try to open the file ourselves to check it is readable
                f = file(filename, 'rb')
            except IOError, e:
                print str(e)
                msg = _("The file you chose could not be opened.")
            else:
                try:
                    im = Image.open(f)
                except IOError, e:
                    pass
                else:
                    # Ensure the file format is one of the supported formats
                    format = im.format
                    # Explicitely delete the Image object (freeing some resources)
                    del im
                    if format in self.allowed_formats:
                        dialog.Destroy()
                        if callback is not None:
                            callback(filename)
                        ok_dialog = wx.MessageDialog(None,
                            _("Your avatar has been updated."),
                            _("Avatar updated"),
                            style=wx.OK | wx.ICON_INFORMATION)
                        ok_dialog.ShowModal()
                        return filename
                msg = _("The file you chose does not belong to the \nsupported image types (%s).") \
                    % ", ".join(self.allowed_formats)
            # Display error dialog
            msg += "\n" + _("Please choose another file.")
            err_dialog = wx.MessageDialog(None, msg, _("Error"),
                style=wx.OK | wx.ICON_ERROR)
            err_dialog.ShowModal()

        # We come here if the user pressed Cancel in the file dialog
        dialog.Destroy()
        return None

    def ConfigureDirectory(self, callback=None):
        """
        Launches the dialog to configure a whole directory.
        When done, returns the chosen directory path, or None.
        (optionally invokes a callback if successful)
        """
        # Bug workaround for Windows, where os.path gives paths in the local
        # charset (e.g. "windows-1252") but wxWidgets tries to decode it using
        # the 'ascii' codec...
        charset = GetCharset()
        default_dir = safe_unicode(abspath(self.avatar_dir), charset)
        dialog = wx.DirDialog(None, _("Choose a directory to load avatars from"),
            defaultPath=default_dir,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        # Loop while the user tries to choose a file and the file is not acceptable
        while dialog.ShowModal() == wx.ID_OK:
            dirpath = dialog.GetPath()
            try:
                l = os.listdir(dirpath)
            except (IOError, OSError), e:
                print str(e)
                msg = _("The directory you chose could not be opened.")
            else:
                found_images = 0
                for filename in l:
                    if not AcceptFilename(filename):
                        continue
                    path = os.path.join(dirpath, filename)
                    if not os.path.isfile(path):
                        continue
                    try:
                        f = file(path, "rb")
                        im = Image.open(f)
                    except IOError, e:
                        print str(e)
                        continue
                    else:
                        # Ensure the file format is one of the supported formats
                        format = im.format
                        # Explicitely delete the Image object (freeing some resources)
                        del im
                        if format in self.allowed_formats:
                            found_images += 1
                if found_images:
                    dialog.Destroy()
                    if callback is not None:
                        callback(dirpath)
                    ok_dialog = wx.MessageDialog(None,
                        _("%d avatars have been loaded.") % found_images,
                        _("Avatars updated"),
                        style=wx.OK | wx.ICON_INFORMATION)
                    ok_dialog.ShowModal()
                    return dirpath
                msg = _("The directory you chose does not contain any of the \nsupported image types (%s).") \
                    % ", ".join(self.allowed_formats)
            # Display error dialog
            msg += "\n" + _("Please choose another directory.")
            err_dialog = wx.MessageDialog(None, msg, _("Error"),
                style=wx.OK | wx.ICON_ERROR)
            err_dialog.ShowModal()

        # We come here if the user pressed Cancel in the file dialog
        dialog.Destroy()
        return None

    def Destroy(self):
        pass
