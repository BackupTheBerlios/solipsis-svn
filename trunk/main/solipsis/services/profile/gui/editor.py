#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.4cvs on Tue Jun 21 10:17:16 2005
"""Application defined for testing purpose"""

import wx

from solipsis.util.wxutils import _
from solipsis.services.profile.facade import create_facade
from solipsis.services.profile.view import EditorView
from solipsis.services.profile.gui.EditorFrame import EditorFrame

class EditorApp(wx.App):
    """Top-level class of GUI: application"""
    def __init__(self, options, *args):
        self.options = options
        self.options['App'] = self
        wx.App.__init__(self, *args)
        
    def OnInit(self):
        """overrides"""
        facade = create_facade("manu")
        facade.load()
        # set up GUI
        wx.InitAllImageHandlers()
        editor_frame = EditorFrame(self.options, None, -1, _("Profile Editor"))
        self.SetTopWindow(editor_frame)
        editor_frame.Show()
        # set up facade
        facade.add_view(EditorView(facade._desc, editor_frame))
        editor_frame.on_change_facade()
        return 1

# end of class EditorApp

def run():
    """launch editor of profile"""
    import gettext
    gettext.install("editor") # replace with the appropriate catalog name
    # set options
    options = {}
    options["standalone"] = True
    # launch gui
    editor = EditorApp(options, 0)
    try:
        editor.MainLoop()
    except:
        print "UNCAUGHT EXCEPTION"

    
if __name__ == "__main__":
    run()
