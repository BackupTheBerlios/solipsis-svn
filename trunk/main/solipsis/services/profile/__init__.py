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

ENCODING = "ISO-8859-1"
VERSION = "0.1.0"
DISCLAIMER = "All data in profiles are shared within Solipsis communauty"

PROFILE_DIR = os.sep.join([os.path.expanduser("~"), ".solipsis", "profiles"])
DOWNLOAD_REPO = os.sep.join([os.path.expanduser("~"), ".solipsis", "download"])
PROFILE_FILE = ".default"
PROFILE_EXT = ".prf"
BLOG_EXT = ".blog"
DISCLAIMER_FILE = ".no_disclaim"

#IMAGES
images_dir = os.path.join(os.path.dirname(__file__), "images")
QUESTION_MARK = os.path.join(images_dir, "question_mark.gif")
ADD_CUSTOM = os.path.join(images_dir, "add_file.jpeg")
DEL_CUSTOM = os.path.join(images_dir, "del_file.jpeg")
ADD_BLOG = os.path.join(images_dir, "edit_file.gif")
DEL_BLOG = os.path.join(images_dir, "delete_file.gif")
ADD_COMMENT = os.path.join(images_dir, "comment.gif")
UPLOAD_BLOG = os.path.join(images_dir, "add_file.gif")
ADD_REPO = os.path.join(images_dir, "browse.jpeg")
DEL_REPO = os.path.join(images_dir, "del_file.jpeg")
SHARE = os.path.join(images_dir, "add_file.gif")
UNSHARE = os.path.join(images_dir, "delete_file.gif")
EDIT = os.path.join(images_dir, "edit_file.gif")
PREVIEW = os.path.join(images_dir, "loupe.gif")
DOWNLOAD = os.path.join(images_dir, "down_file.gif")
DOWNLOAD_DIR = os.path.join(images_dir, "browse.jpeg")
BULB_ON_IMG = os.path.join(images_dir, "bulb.gif")
BULB_OFF_IMG = os.path.join(images_dir, "bulb_off.gif")
TORE_IMG = os.path.join(images_dir, "tore.gif")

KNOWN_PORT = 1160
FREE_PORTS = range(23000, 23999)

if not os.path.exists(DOWNLOAD_REPO):
    os.mkdir(DOWNLOAD_REPO)

if not os.path.isdir(PROFILE_DIR):
    print "creating conf directory %s"% PROFILE_DIR
    os.makedirs(PROFILE_DIR)

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
