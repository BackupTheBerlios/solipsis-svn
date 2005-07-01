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
"""Plugin profile: allow users to define a set of personal information
and exchange it with other peers"""

import os, os.path
import gettext 
_ = gettext.gettext

ENCODING = "iso-8859-1"
VERSION = "0.2.1"
DISCLAIMER = "All data in profiles are shared within Solipsis communauty"

PROFILE_DIR = os.sep.join([os.path.expanduser("~"), u".solipsis", u"profiles"])
DOWNLOAD_REPO = os.sep.join([os.path.expanduser("~"), u".solipsis", u"download"])

global solipsis_dir

def set_solipsis_dir(new_dir):
    """directory must be set at launch time since it's read in file
    conf (and passed to the application through params"""
    global solipsis_dir
    solipsis_dir = new_dir

set_solipsis_dir(os.path.dirname(__file__))

images_dir = lambda : os.path.join(solipsis_dir, u"images")
PREVIEW_PT = lambda : os.path.join(solipsis_dir, u"preview.html")
QUESTION_MARK = lambda : os.path.join(images_dir(), u"question_mark.gif")
ADD_CUSTOM = lambda : os.path.join(images_dir(), u"add_file.jpeg")
DEL_CUSTOM = lambda : os.path.join(images_dir(), u"del_file.jpeg")
ADD_BLOG = lambda : os.path.join(images_dir(), u"edit_file.gif")
DEL_BLOG = lambda : os.path.join(images_dir(), u"delete_file.gif")
ADD_COMMENT = lambda : os.path.join(images_dir(), u"comment.gif")
UPLOAD_BLOG = lambda : os.path.join(images_dir(), u"add_file.gif")
ADD_REPO = lambda : os.path.join(images_dir(), u"browse.jpeg")
DEL_REPO = lambda : os.path.join(images_dir(), u"del_file.jpeg")
SHARE = lambda : os.path.join(images_dir(), u"add_file.gif")
UNSHARE = lambda : os.path.join(images_dir(), u"delete_file.gif")
EDIT = lambda : os.path.join(images_dir(), u"edit_file.gif")
PREVIEW = lambda : os.path.join(images_dir(), u"loupe.gif")
DOWNLOAD = lambda : os.path.join(images_dir(), u"down_file.gif")
DOWNLOAD_DIR = lambda : os.path.join(images_dir(), u"browse.jpeg")
BULB_ON_IMG = lambda : os.path.join(images_dir(), u"bulb.gif")
BULB_OFF_IMG = lambda : os.path.join(images_dir(), "ubulb_off.gif")
TORE_IMG = lambda : os.path.join(images_dir(), u"tore.gif")

PROFILE_FILE = ".default"
PROFILE_EXT = ".prf"
BLOG_EXT = ".blog"
DISCLAIMER_FILE = ".no_disclaim"
DISPLAY_FILE = ".no_display"

DEFAULT_INTERESTS = [_("City"), _("Country"),
                     _("Sport"), _("Studies"),
                     _("Favourite Book"), _("Favourite Movie"),
                     ]

KNOWN_PORT = 1160
FREE_PORTS = range(23000, 23999)

if not os.path.isdir(PROFILE_DIR):
    print "creating conf directory %s"% PROFILE_DIR
    os.makedirs(PROFILE_DIR)

if not os.path.exists(DOWNLOAD_REPO):
    os.mkdir(DOWNLOAD_REPO)

def skip_disclaimer():
    """returns true if About Dialog must be displayed at launch of
    profile"""
    return os.path.exists(os.path.join(PROFILE_DIR, DISCLAIMER_FILE))

def set_display_at_startup(display):
    """enable/disable display of About Dialog at launch of profile"""
    if display:
        if skip_disclaimer():
            os.remove(os.path.join(PROFILE_DIR, DISCLAIMER_FILE))
        # else: already configure not to skip
    else:
        if skip_disclaimer():
            # already configure to skip
            pass
        else:
            disclaimer = open(os.path.join(PROFILE_DIR, DISCLAIMER_FILE), "w")
            disclaimer.close()

def always_display():
    """returns true if About Dialog must be displayed at launch of
    profile"""
    return not os.path.exists(os.path.join(PROFILE_DIR, DISPLAY_FILE))

def set_always_display(display):
    """enable/disable display of About Dialog at launch of profile"""
    if display:
        if always_display():
            # already configure to skip
            pass
        else:
            os.remove(os.path.join(PROFILE_DIR, DISPLAY_FILE))
    else:
        if always_display():
            displayer = open(os.path.join(PROFILE_DIR, DISPLAY_FILE), "w")
            displayer.close()
        # else: already configure not to skip
