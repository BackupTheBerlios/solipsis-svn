#!/usr/local/bin/env python
######################################

## SOLIPSIS Copyright (C) France Telecom

## This file is part of SOLIPSIS.

##    SOLIPSIS is free software; you can redistribute it and/or modify
##    it under the terms of the GNU Lesser General Public License as published by
##    the Free Software Foundation; either version 2.1 of the License, or
##    (at your option) any later version.

##    SOLIPSIS is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU Lesser General Public License for more details.

##    You should have received a copy of the GNU Lesser General Public License
##    along with SOLIPSIS; if not, write to the Free Software
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

## ------------------------------------------------------------------------------
## -----                           module_Solipsis.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the main module of SOLIPSIS navigator.
##   It starts the main frame of the application.
##
## ******************************************************************************

from wxPython.wx import wxApp, wxInitAllImageHandlers
from solipsis.navigator.wx.wxMainFrame import wxMainFrame
from solipsis.util.parameter import Parameters
#modules ={'wxMainFrame': [1, 'Main frame of Application', 'wxMainFrame.py']}

class BoaApp(wxApp):
    def OnInit(self):
        try:
            configFileName = "conf/solipsis.conf"
            params = Parameters(configFileName)
        except:
            raise
        
        wxInitAllImageHandlers()
        #warnings.filterwarnings('always')        
        self.main = wxMainFrame(params)
        # needed when running from Boa under Windows 9X
        self.SetTopWindow(self.main)
        self.main.Show();self.main.Hide();self.main.Show()
        return True

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
