import sys, random
import ConfigParser, logging, logging.config

class Parameters:
    def __init__(self, configFileName):
        self.configFileName = configFileName
        # create a file object in write mode
        #self.configFile = file(configFileName, 'r+')
        self.getAllParameters()
        
    def getAllParameters(self):        
        try:
            self.config = ConfigParser.ConfigParser()
            self.config.read(self.configFileName)            

            self.tcp_port_min = int(eval(self.config.get("general", "tcp_port_min")))
            self.tcp_port_max = int(eval(self.config.get("general", "tcp_port_max")))
            self.tcp_port = random.randint(self.tcp_port_min, self.tcp_port_max)
            self.buffer_size = int(eval(self.config.get("network", "buffer_size")))
            self.connection_timeout = int(eval(self.config.get("network",
                                                          "connection_timeout")))

            if self.config.has_option("network","host"):
                self.host = self.config.get("network","host")
            else:
                self.host = "localhost"

            if self.config.has_option("network","port"):
                self.port = int(self.config.get("network","port"))
            else:
                self.port = None
                
            logging.config.fileConfig(self.configFileName)
            self.netLogger = logging.getLogger("solipsis.engine.network")
            self.rootLogger = logging.getLogger("root")
            self.controlLogger = logging.getLogger("solipsis.engine.control")

            self.world_size = long(eval(self.config.get("general", "world_size")))
            if self.config.has_option("general", "position_x"):
                self.posX = long(self.config.get("general", "position_x"))
            else:
                self.posX = long(random.random() * self.world_size )
                
            if self.config.has_option("general", "position_y"):
                self.posY = long(self.config.get("general", "position_y"))
            else:
                self.posY = long(random.random() * self.world_size )
                
            self.ar = int(self.config.get("general", "awarness_radius"))
            self.caliber = int(self.config.get("general", "caliber"))
            self.caliber_max = int(self.config.get("general", "caliber_max"))
            self.ori = int(self.config.get("general", "orientation"))
            self.exp = int(self.config.get("general", "expected_neighbours"))
            
            self.statInfos = self.config.getboolean("general", "stat_infos")
            # navigator options
            if self.config.has_option("navigator","pseudo"):
                self.pseudo = self.config.get("navigator","pseudo")
            else:
                self.pseudo = "anonymous_"+str(self.tcp_port)
            self.scale = self.config.get("navigator","scale")
            self.zoom = self.config.get("navigator","zoom")
            self.arePseudosDisplayed = self.config.getboolean("navigator",
                                                         "display_pseudos")
            self.areAvatarsDisplayed = self.config.getboolean("navigator",
                                                         "display_avatars")
            self.entities_file = self.config.get("general", "entities_file")
            
            if self.config.has_option("control", "host"):
                self.controlHost = self.config.get("control", "host")
            if self.config.has_option("control", "control_port"):
                self.controlPort = int(self.config.get("control", "control_port"))
            if self.config.has_option("control", "notification_port"):
                self.notifPort = int(self.config.get("control", "notification_port"))
            
        except:
            sys.stderr.write("\nError while reading configuration file solipsis.conf :\n")
            raise

        i = 1
        length = len(sys.argv) - 1
        
        try:
            
            if length == 1:
                raise error
            
            while i < length and length > 0:

                # retrieve argument
                option = sys.argv[i]

                # check if this argument is an option
                if option[0] == "-":
                    # retrieve the option
                    changed_option = option[1]
                    
                    # option has interest only if there is an argument behind
                    if i+1 <= length:
        
                        # option is tcp_port
                        if changed_option == "t":
                            self.tcp_port = int(sys.argv[i+1])
                            if not (0 < self.tcp_port < self.tcp_port_max):
                                raise error
                        # option is udp_port (used for communications with peers)
                        if changed_option == "p":
                            self.port = int(sys.argv[i+1])    
                        
                        # option is pos x
                        if changed_option == "x":
                            self.posX = long(sys.argv[i+1]) % self.world_size

                        # option is pos y
                        if changed_option == "y":
                            self.posY = long(sys.argv[i+1]) % self.world_size

                        # option is caliber
                        if changed_option == "c":
                            self.caliber = int(sys.argv[i+1])
                            if not (0 < self.caliber <= self.caliber_max):
                                raise error

                        # option is the expected number of adjacents
                        if changed_option == "e":
                            self.exp = int(sys.argv[i+1])
                            if not (0 < self.exp):
                                raise error

                        # option is pseudo
                        if changed_option == "n":
                            self.pseudo = sys.argv[i+1]

                        # no notification to server
                        if changed_option == "z":
                            self.statInfos = False
                            i -= 1

                    i += 2
      
                else:
      
                    i += 1
                      
        except:
            sys.stderr.write("\nOptions :\n")
            sys.stderr.write("    -t : change tcp port for interface module <-> node\n")
            sys.stderr.write("    -x : change position x\n")
            sys.stderr.write("    -y : change position y\n")
            sys.stderr.write("    -c : change caliber\n")
            sys.stderr.write("    -e : change expected number of neighbors\n")
            sys.stderr.write("    -n : change pseudo\n")
            sys.exit(0)

        return [self.tcp_port_min, self.tcp_port_max, self.tcp_port,
                self.world_size, self.posX, self.posY, self.ar, self.caliber,
                self.caliber_max , self.ori, self.exp, self.statInfos, self.pseudo,
                self.entities_file]

    def getNetParams(self):
        """ Return network specific parameters
        buffer_size : max number of bytes read from socket
        netLogger   : logger object used by the network object
        host: optionnal - hostname or IP address of this node
        port : optionnal - port number used for UDP connections with peers
        """
        return [self.buffer_size, self.netLogger, self.host, self.port]

    def getPeersParams(self):
        """ Return peers specific parameters
        entities_file : name of the bootstrap file containing a list of entities
        potentially connected to solipsis
        rootLogger    : logger object used by the peer Manager
        """
        return [self.entities_file, self.exp, self.rootLogger]

    def getInternalParams(self):
        return [self.rootLogger]

    def getControlParams(self):
        return [self.controlHost, self.controlPort, self.notifPort,
                self.controlLogger]

    def getNavigatorParams(self):
        return [self.world_size, self.scale, self.zoom, self.pseudo,
                self.arePseudosDisplayed, self.areAvatarsDisplayed]

    def setOption(self, section, option, value):
        """ set the given option"""
        self.config.set(section, option, value)
        self.configFile = file(self.configFileName, 'w+')
        self.config.write(self.configFile)
        self.configFile.close()
        
