Q: How do I run solipsis?
A: You just need to run navigator.py or navigator.exe and to create a new node (File - New Node (Ctrl+N)). The navigator will automatically connects on it.

Q: What is a node?
A: A node is an entity of the solipsis virtual world. Thanks to the Solipsis protocol, it ensures that the entity is directly connected with its virtual neighbors.

Q: What is a navigator?
A: A navigator allows you to take control of your node and offers to you a graphic representation of the virtual world. It also acts as enabler for the communication between entities with the help of pluggable services.

Q: How do I create a new node?
A: You can either create a new node in the file menu of a running navigator (File - New Node (Ctrl+N)), either start a node by running twistednode.py or twistednode.exe.

Q: How can I connect a navigator on an existing node?
A: The navigator allows the connection on any node running on any computer connected to Internet. You just have to provide the IP address and port.

Q: Does solipsis send statistics to a central server when running?
A: In its pre-release version, a solipsis node sends a simple http request at startup. This functionnality allows us to try to estimate the number of visitors in the solipsis virtual world. Of course, it can be disabled by setting the parameter send_statistic to 0 (zero) in the configuration file (conf/solipsis.conf).

Q: What language is Solipsis written in?
A: Current implementations of node and navigator uses Python (>=2.3). It also uses wxWindows (>=2.5) for its GUI and Twisted for networking.

Q: I am behind a NAT/firewall, can i use Solipsis?
A: Yes, but just make sure that UDP port 6000 is open on the computer that runs the node. If you want to take control of your node from a remote location, TCP port 8550 must also be opened.
NOTE: 6000 and 8550 are default values. Both of them are specified in the configuration file (<solipsis installation dir>/conf/solipsis.conf). If you use alternate ports, make sure that you opened the correct ones.