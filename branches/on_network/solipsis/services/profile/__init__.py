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

__revision__ = "$Id$"

import os, os.path
import locale
import gettext
_ = gettext.gettext

from solipsis.services.profile.message import display_error, display_status

VERSION = "0.4.0"
DISCLAIMER = "All data in profiles are shared within Solipsis communauty"

DOWNLOAD_REPO = os.sep.join([os.path.expanduser("~"), ".solipsis", "download"])
PROFILE_DIR = os.sep.join([os.path.expanduser("~"), ".solipsis", "profiles"])
PREFS_FILE = os.path.join(PROFILE_DIR, ".preferences")

ENCODING = locale.getpreferredencoding()
KNOWN_ENCODINGS = [ENCODING, "utf-8", "utf-16",
                   "ISO-8859-1", "ISO-8859-15"
                   "cp1252", "cp437", "cp850"]

global solipsis_dir

def set_solipsis_dir(new_dir):
    """directory must be set at launch time since it's read in file
    conf (and passed to the application through params"""
    global solipsis_dir
    solipsis_dir = new_dir

def force_unicode(chars):
    """return unicode string trying different encodings if locale one
    failed"""
    if isinstance(chars, unicode):
        return chars
    for encoding in KNOWN_ENCODINGS:
        try:
            return unicode(chars, encoding)
        except UnicodeDecodeError:
            print encoding, "does not apply on", chars
                
    
# Encoding not saved in preferences because it must be attached within
# the profile file (to be sent through network)
def save_encoding(file_obj, encoding):
    """write into profile document its encoding"""
    file_obj.write("# profile-encoding::%s\n"% encoding)

def load_encoding(file_obj):
    """load from profile document its encoding"""
    encoding_tag = file_obj.readline()
    if not encoding_tag.startswith("# profile-encoding::"):
        # wrong format
        # first line has been wastes: rewind
        file_obj.seek(0)
        # return default
        display_status(_("could not read encoding from profile file. "
                         "Using %s"% ENCODING))
        return ENCODING
    else:
        encoding = encoding_tag.split("::")[-1].strip()
        display_status(_("Profile read with encoding %s"% encoding))
        return encoding

set_solipsis_dir(os.path.dirname(__file__))

images_dir = lambda : os.path.join(solipsis_dir, u"images")
PREVIEW_PT = lambda : os.path.join(solipsis_dir, u"preview.html")
REGEX_HTML = lambda : os.path.join(solipsis_dir, u"regex.html")
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
DISPLAY_IMG = lambda : os.path.join(images_dir(), u"download_complete.gif")
DOWNLOAD = lambda : os.path.join(images_dir(), u"down_file.gif")
DOWNLOAD_DIR = lambda : os.path.join(images_dir(), u"browse.jpeg")
BULB_ON_IMG = lambda : os.path.join(images_dir(), u"bulb.gif")
BULB_OFF_IMG = lambda : os.path.join(images_dir(), "ubulb_off.gif")
TORE_IMG = lambda : os.path.join(images_dir(), u"tore.gif")

PROFILE_FILE = ".default"
PROFILE_EXT = ".prf"
BLOG_EXT = ".blog"
FILTER_EXT = ".filt"
UNIVERSAL_SEP = r"\\"

DEFAULT_INTERESTS = [_("City"), _("Country"),
                     _("Sport"), _("Studies"),
                     _("Favourite Book"), _("Favourite Movie"),
                     ]
# GUI
NB_SHARED_COL = 1
FULL_PATH_COL = 2
NAME_COL = 0
SIZE_COL = 1
SHARED_COL = 2
TAG_COL = 3

# NETWORK
KNOWN_PORT = 1160

if not os.path.isdir(PROFILE_DIR):
    print "creating conf directory %s"% PROFILE_DIR
    os.makedirs(PROFILE_DIR)

if not os.path.exists(DOWNLOAD_REPO):
    os.mkdir(DOWNLOAD_REPO)
