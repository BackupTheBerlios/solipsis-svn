#!/bin/sh
export PYTHONPATH=..

pydoc -w solipsis
pydoc -w solipsis.core
pydoc -w solipsis.core.entity
pydoc -w solipsis.core.peer
pydoc -w solipsis.core.connector
pydoc -w solipsis.core.main
pydoc -w solipsis.core.node
pydoc -w solipsis.core.state
pydoc -w solipsis.core.event
pydoc -w solipsis.core.controlevent
pydoc -w solipsis.core.peerevent

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


