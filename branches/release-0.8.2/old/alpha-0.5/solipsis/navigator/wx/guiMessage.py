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
## -----                           commun.py                                  -----
## ------------------------------------------------------------------------------


from wxPython.wx import *

    
def displayMessage(parent, message):
    """ Display an information message in the user interface """

    messageDialog = wxMessageDialog(parent, message, "Info", wxOK|wxCENTRE|wxICON_INFORMATION)
    messageDialog.Center(wxBOTH)
    messageDialog.ShowModal()

def displayError(parent, message):
    """ Display an error message in the user interface """

    messageDialog = wxMessageDialog(parent, message, "Error", wxOK|wxCENTRE|wxICON_ERROR)
    messageDialog.Center(wxBOTH)
    messageDialog.ShowModal()


