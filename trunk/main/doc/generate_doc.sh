#!/bin/sh
export PYTHONPATH=..

pydoc -w solipsis
pydoc -w solipsis.node
pydoc -w solipsis.node.entity
pydoc -w solipsis.node.peer
pydoc -w solipsis.node.connector
pydoc -w solipsis.node.main
pydoc -w solipsis.node.node
pydoc -w solipsis.node.state
pydoc -w solipsis.node.event
pydoc -w solipsis.node.controlevent
pydoc -w solipsis.node.peerevent

pydoc -w solipsis.util
pydoc -w solipsis.util.util
pydoc -w solipsis.util.exception
pydoc -w solipsis.util.parameter

pydoc -w solipsis.navigator
pydoc -w solipsis.navigator.subscriber
pydoc -w solipsis.navigator.service
pydoc -w solipsis.navigator.navigatorinfo
pydoc -w solipsis.navigator.chat
pydoc -w solipsis.navigator.filetransfer

pydoc -w solipsis.navigator.basic
pydoc -w solipsis.navigator.basic.basicFrame



#pydoc -w ../solipsis/core/*.py
#pydoc -w ../solipsis/util/*.py
#pydoc -w ../solipsis/navigator/*.py


