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
## -----                           globalvars.py                            -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   Here are the global variables of SOLIPSIS, especially "me" which is
##   self entity.
##
## ******************************************************************************

from threading import Lock

# World Size
SIZE = long(2**128)

# boolean true if node is alive
ALIVE = 0

# for mutual exclusion
mutex = Lock()

# my self
me = 0
