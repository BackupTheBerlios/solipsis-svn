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
## -----                           debug.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the debug module.
##   If the debug_mode is set to 0, no trace will be generated.
##
## ******************************************************************************


import os

""" debug_mode = 1 to have trace info or 0 if no trace is necessary """
debug_mode=0

def debug_info(msg):
    """ print a debug message in a file """
    global debug_mode
    if debug_mode == 1:
        f = file("Debug.txt", 'a')
        f.write(msg)
        f.write("\n")
        f.close()
