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
## -----                           configuration.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the configuration class of the Solipsis navigator.
##   This class is used to read or write information on the configuration file
##   of the application
##
## ******************************************************************************

import os, string
import commun

# debug module
from debug import *

# define configuration file name
confFile = "navigator.conf"

def readConfParameterValue(parameter):
    """ read the value of a parameter in the conf file """

    # open the conf file
    global confFile
    try:
        f = file(confFile, 'r')
    except:
        return

    # read file and close
    list = f.readlines()
    f.close()

    for line in list:
        param, value = line[:len(line) -1].split('=')
        if param == parameter:
            return value
    return

def writeConfParameterValue(parameter, value):
    """ write the value of a parameter in the conf file """

    # variables initialization
    global confFile
    list = []
    indice = 0

    # open the conf file in read mode
    try:
        f = file(confFile, 'r')

        # read and close file
        list = f.readlines()
        f.close()

    except:
        pass

    for line in list:
        param, val = line[:len(line) -1].split('=')
        if param == parameter:
            # change the line in the list
            line = string.join((parameter, str(value)), '=')
            line += '\n'
            list[indice] = line
            break
        indice +=1

    # creation mode
    if indice >= len(list):
        # write the new line in the list
        line = string.join((parameter, str(value)), '=')
        line += '\n'
        list.append(line)

    # save the new lines in file
    try:
        f = file(confFile, 'w')
        f.writelines(list)
        # close file
        f.close()
    except:
        message="Can't open the file " + confFile
        commun.displayError(self, message)
