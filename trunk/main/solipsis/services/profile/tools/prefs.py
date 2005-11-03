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
"""Contains preferences for profile"""

__revision__ = "$Id$"

import os.path

import ConfigParser


DOWNLOAD_REPO = os.sep.join([os.path.expanduser("~"), ".solipsis", "download"])
PROFILE_DIR = os.sep.join([os.path.expanduser("~"), ".solipsis", "profiles"])
ENCODING = "iso-8859-1"

PREFS_FILE = os.path.join(PROFILE_DIR, ".preferences")
MAIN_SECTION = "General"
DIALOG_SECTION = "Dialogs"

def get_prefs(option):
    """load config from file PREFS_FILE creating it if necessary"""
    if not Preferences.conf:
        Preferences.conf = Preferences(PREFS_FILE)
        Preferences.conf.load()
    return Preferences.conf.get(option)

def set_prefs(option, value=None):
    """load config from file PREFS_FILE creating it if necessary"""
    if not Preferences.conf:
        Preferences.conf = Preferences(PREFS_FILE)
        Preferences.conf.load()
    Preferences.conf.set(option, value)

class Param:
    """simple structure to define a parameter"""

    def __init__(self, name, section, default, var_type, convertor):
        self.name = name
        self.section = section
        self.default = default
        self.var_type = var_type
        self.convertor = convertor

    def __str__(self):
        return "%s: %s"% (self.name, self.default)

    def __repr__(self):
        return self.name

class BoolParam(Param):
    """simple structure to define a boolean parameter"""

    def __init__(self, name, section, default):
        convertor = lambda value_str: not value_str in ["False", "0", "no"]
        Param.__init__(self, name, section, default, bool, convertor)

class IntParam(Param):
    """simple structure to define a boolean parameter"""

    def __init__(self, name, section, default):
        Param.__init__(self, name, section, default, int, int)

class StringParam(Param):
    """simple structure to define a boolean parameter"""

    def __init__(self, name, section, default):
        Param.__init__(self, name, section, default, str, str)

class Preferences:
    """manage all options providing setters and getters for every params"""

    conf = None
    # {param_name : [section, 
    params = {"disclaimer": BoolParam("Disclaimer", MAIN_SECTION, True),
              "display_dl": BoolParam("Download Dialog", MAIN_SECTION, True),
              "download_repo": StringParam("Download directory",
                                           MAIN_SECTION, DOWNLOAD_REPO),
              "profile_dir": StringParam("Profile directory",
                                           MAIN_SECTION, PROFILE_DIR),
              "profile_width": IntParam("Profile width", DIALOG_SECTION, 460),
              "profile_height": IntParam("Profile height", DIALOG_SECTION, 600),
              "match_width": IntParam("Match width", DIALOG_SECTION, 460),
              "match_height": IntParam("Match height", DIALOG_SECTION, 600),
              "filter_width": IntParam("Filter width", DIALOG_SECTION, 460),
              "filter_height": IntParam("Filter height", DIALOG_SECTION, 600),
              "simple_mode": BoolParam("Simple mode", DIALOG_SECTION, True),
              "encoding": StringParam("Encoding", MAIN_SECTION, ENCODING),
              "log": BoolParam("Enable logging", MAIN_SECTION, False),
              }

    def __init__(self, file_name):
        self.file_name = file_name
        self.config = None

    def __str__(self):
        if not self.config:
            return "not initialized"
        else:
            return ", ".join(self.params.keys())

    def load(self):
        """load params from file"""
        self.config = ConfigParser.ConfigParser()
        if not os.path.exists(self.file_name):
            for option in Preferences.params:
                self.set(option)
        else:
            pref_file = open(self.file_name)
            self.config.readfp(pref_file)
            pref_file.close()

    def _save(self):
        """save params to file"""
        pref_file = open(self.file_name, 'w')
        self.config.write(pref_file)
        pref_file.close()

    def set(self, option, value=None):
        """generic setter. Will save options each time called. Wrapped
        for every params under appropriate name"""
        assert self.config, "Preferences not loaded"
        assert option in Preferences.params, "no option %s. Available: %s"\
               % (option, Preferences.params)
        param = Preferences.params[option]
        # set value
        if value is None:
            value = param.default
        assert isinstance(value, param.var_type)
        if not self.config.has_section(param.section):
            self.config.add_section(param.section)
        self.config.set(param.section, param.name, str(value))
        self._save()

    def get(self, option):
        """generic getter. Wrapped for every params under appropriate name"""
        assert self.config, "Preferences not loaded"
        assert option in Preferences.params, "no option %s. Available: %s"\
               % (option, Preferences.params)
        param = Preferences.params[option]
        try:
            return param.convertor(self.config.get(param.section, param.name))
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.set(option)
            return param.default
        
        
        
