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

import os, os.path
import sys
import random
import locale
from ConfigParser import ConfigParser
import logging, logging.config

from solipsis.util.utils import safe_str, safe_unicode

# The parameters come from an external source (config file or
# command-line options), so we have to take into account the
# system-wide charset (not always utf-8).
CHARSET = locale.getpreferredencoding()

class Parameters(object):
    """
    This class manages the launch-time options for the Solipsis programs.
    It can fetch parameters from a configuration file and override these values
    with command-line options.
    """

    solipsis_section = {
        'host': ('host', str, ""),
        'port': ('port', int, 5999),
        'position_x': ('pos_x', long, 0),
        'position_y': ('pos_y', long, 0),
        'expected_neighbours': ('expected_neighbours', int, 10),
        'entities_file': ('entities_file', str, None),
        'address_discovery': ('discovery_methods', lambda s: [t.strip() for t in s.split(',')], []),
        'controllers': ('controllers', lambda s: [t.strip() for t in s.split(',')], []),
        'send_statistics': ('send_stats', int, 0),
    }

    navigator_section = {
        'translation_dir': ('translation_dir', os.path.normcase, None),
        'pseudo': ('pseudo', unicode, u""),
        'url_port_min': ('url_port_min', int, 0),
        'url_port_max': ('url_port_max', int, 0),
        'local_control_port_min': ('local_control_port_min', int, 0),
        'local_control_port_max': ('local_control_port_max', int, 0),
    }

    services_section = {
        'directory': ('services_dir', os.path.normcase, None),
    }

    def __init__(self, option_parser, config_file="", defaults=None):
        """
        Parameters(options, additional_defaults_values)
        """
        self._option_parser = option_parser
        self._config_file = config_file
        self._params = {}
        self._config_parser = None
        self._logger = None
        self._defaults = defaults
        (self._options, self._args) = self._option_parser.parse_args()
        if len(self._args) > 0:
            option_parser.error("too many arguments")
        try:
            self._config_file = self._options.config_file
        except AttributeError:
            pass
        if self._config_file:
            self.Load()

    def __getattr__(self, name):
        """
        Parameters are accessed as attributes for convenience.
        """
        raise AttributeError("Missing parameter %s" % name)


    def LoadSection(self, section_name, fields):
        """
        Load the given config options from the given section.
        """
        p = self._config_parser
        for k, (var, cons, default) in fields.items():
            # For each requested field, get the corresponding value
            # from the config file or use the default value
            if p.has_option(section_name, k):
                v = cons(safe_unicode(p.get(section_name, k), CHARSET))
            else:
                v = default
            setattr(self, var, v)
        for var, v in self._options.__dict__.items():
            # For each command-line option that is not None or empty,
            # override the config file value
            if v or not hasattr(self, var):
                if isinstance(v, str):
                    v = safe_unicode(v, CHARSET)
                setattr(self, var, v)

    def Load(self):
        """
        Load parameters from the config file.
        """
        try:
            self._config_parser = ConfigParser(self._defaults)
            self._config_parser.read(self._config_file)

        except Exception, e:
            sys.stderr.write("\nError while reading configuration file %s:\n" % self.configFileName)
            sys.stderr.write(str(e))
            sys.exit(1)

        self.LoadSection("solipsis", self.solipsis_section)
        self.LoadSection("navigator", self.navigator_section)
        self.LoadSection("services", self.services_section)

        #
        # Logging configuration
        # (note: only the root logger is used at the moment)
        #
        logging.config.fileConfig(self._config_file, defaults={'logid': self.port})
        self._logger = logging.getLogger()
        self._logger.info("Parameters initialized")
