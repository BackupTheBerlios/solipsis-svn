import sys, random
import ConfigParser, logging, logging.config

class Parameters(object):
    """ This class manages the launch-time options for the Solipsis programs.

    The config file is located in the conf/ directory. """

    def __init__(self, option_parser, config_file="", defaults=None):
        """ Parameters(options, additional_defaults_values) """

        self.option_parser = option_parser
        self.configFileName = config_file
        self.params = {}
        self.logger = None
        self.defaults = defaults
        (self.options, self.args) = self.option_parser.parse_args()
        if len(self.args) > 1:
            option_parser.error("too many arguments")

        try:
            self.configFileName = self.options.config_file
        except:
            pass
        if self.configFileName:
            self.load()

    def __getattr__(self, name):
        """ Parameters are accessed as attributes for convenience. """

        try:
            return self.params[name]
        except:
            raise AttributeError("Missing parameter %s" % name)

    def load(self):
        """ Change config file and load parameters from it. """
        self.params = self.__getAllParameters()

    def __getAllParameters(self):
        """ Read and returns all parameters from the config file. """

        try:
            self.config = ConfigParser.ConfigParser(self.defaults)
            self.config.read(self.configFileName)
            params = {}

            #
            # Network options
            #

            # Solipsis-side network config
            if self.config.has_option("network", "host"):
                params['host'] = self.config.get("network", "host")
            else:
                params['host'] = ''

            if self.config.has_option("network", "port"):
                params['port'] = int(self.config.get("network", "port"))
            else:
                params['port'] = 5115

            # Navigator-side network config
            params['bot'] = False
            if self.config.has_option("control", "host"):
                params['control_host'] = self.config.get("control", "host")
            else:
                params['control_host'] = 'localhost'
            if self.config.has_option("control", "control_port"):
                params['control_port'] = int(self.config.get("control", "control_port"))
            else:
                params['control_port'] = 8550
            if self.config.has_option("control", "notification_port"):
                params['notif_port'] = int(self.config.get("control", "notification_port"))
            else:
                params['notif_port'] = 8551

            #
            # Geometry startup values
            #
            if self.config.has_option("general", "position_x"):
                params['pos_x'] = long(self.config.get("general", "position_x"))
            else:
                params['pos_x'] = long(random.random() * self.world_size)

            if self.config.has_option("general", "position_y"):
                params['pos_y'] = long(self.config.get("general", "position_y"))
            else:
                params['pos_y'] = long(random.random() * self.world_size)

            params['calibre'] = int(self.config.get("general", "calibre"))
            params['orientation'] = int(self.config.get("general", "orientation"))
            params['expected_neighbours'] = int(self.config.get("general", "expected_neighbours"))

            #
            # User interface options
            #
            if self.config.has_option("ui", "translation_dir"):
                params['translation_dir'] = self.config.get("ui", "translation_dir")

            #
            # Default user settings: identity, etc.
            #
            params['stat_infos'] = self.config.getboolean("general", "stat_infos")
            # navigator options
            if self.config.has_option("navigator", "pseudo"):
                params['pseudo'] = self.config.get("navigator", "pseudo")
            else:
                params['pseudo'] = "anonymous_"+ str(params['port'])
            params['display_pseudos'] = self.config.getboolean("navigator",
                                                         "display_pseudos")
            params['display_avatars'] = self.config.getboolean("navigator",
                                                         "display_avatars")
            params['entities_file'] = self.config.get("general", "entities_file")

        except Exception, e:
            sys.stderr.write("\nError while reading configuration file %s:\n" % self.configFileName)
            sys.stderr.write(str(e))
            sys.exit(1)

        #
        # Overload configuration values with values specified on the command line
        #
        params_override = dict([(k, v) for (k, v) in self.options.__dict__.items() if v is not None])
        params.update(params_override)

        #
        # Logging configuration
        # (note: only the root logger is used at the moment)
        #
        logging.config.fileConfig(self.configFileName, defaults={'logid': params['port']})
        self.logger = logging.getLogger('root')

        self.logger.info("Parameters initialized with: %s" % str(params))
        return params


    def setOption(self, section, option, value):
        """ Set the given option"""

        self.config.set(section, option, value)
        self.configFile = file(self.configFileName, 'w+')
        self.config.write(self.configFile)
        self.configFile.close()
        # reload configuration
        self.load()
