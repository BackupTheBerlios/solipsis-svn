
import sys, random
from ConfigParser import ConfigParser
import logging, logging.config


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
        'address_discovery': ('discovery_methods', str, None),
    }

    control_section = {
        'host': ('control_host', str, ""),
        'port': ('control_port', int, 8550),
    }

    navigator_section = {
        'translation_dir': ('translation_dir', str, None),
        'pseudo': ('pseudo', unicode, u"anonymous"),
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
        getters = {
            int: p.getint,
            float: p.getfloat,
            bool: p.getboolean,
        }
        for k, (var, cons, default) in fields.items():
            if p.has_option(section_name, k):
                getter = getters.get(k, p.get)
                v = cons(getter(section_name, k))
            else:
                v = default
            setattr(self, var, v)
        for var, v in self._options.__dict__.items():
            if v is not None or not hasattr(self, var):
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
        self.LoadSection("control", self.control_section)
        self.LoadSection("navigator", self.navigator_section)

        #
        # Logging configuration
        # (note: only the root logger is used at the moment)
        #
        logging.config.fileConfig(self._config_file, defaults={'logid': self.port})
        self._logger = logging.getLogger('root')
        self._logger.info("Parameters initialized")
        return
