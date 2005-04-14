import os
import sys
import distutils.core
import glob
"""
How to build win32 Solipsis binaries :
Download Python2.4
wxPython
Twisted (source)
py2exe
build win32 twisted
    it requires MSVC 7.1 and .NET framework 1.1
    issue the command $python winsetup.py install in the twisted source directory
Edit this script to insert desired services (see data_files)
(services can be added in the solipsis/services distribution directory later)  
Then  issue the command $python setup.py py2exe
"""
name="Solipsis"
version="0.7"
description="Solipsis, A peer-to-peer system for a massively multi-participant virtual world"
author="France Telecom R&D"
author_email="solipsis-tech@lists.berlios.de"
url="http://solipsis.rd.francetelecom.fr"

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = version
        self.company_name = "France Telecom R&D"
        self.copyright = "France Telecom R&D"
        self.url = url

sys.path.append("solipsis/node")
sys.path.append("solipsis/navigator")

data_files=[
    ("",["entities.met", "LICENSE", "README.txt"]),
    ("",["msvcr71.dll"]),
    ("img", glob.glob("img/*.*")),
    ("conf", ["conf/solipsis.conf"]),
# Insert services files here
    ("solipsis/services", glob.glob("solipsis/services/*.*")),
    ("solipsis/services/chat", glob.glob("solipsis/services/chat/*.*")),
    ("solipsis/services/chat/po", glob.glob("solipsis/services/chat/po/*.*")),
    ("solipsis/services/chat/po/fr/LC_MESSAGES", 
        glob.glob("solipsis/services/chat/po/fr/LC_MESSAGES/*.*")),
# End services files
    ("log", []),
    ("resources", ["resources/navigator.xrc"]),
    ("po", ["po/messages.pot"]),
    ("po/fr/LC_MESSAGES", 
        ["po/fr/LC_MESSAGES/solipsis.mo",
        "po/fr/LC_MESSAGES/solipsis.po"])]

import py2exe

twistednode = Target(
    name = "node",
    description = "Solipsis Node",
    modules = "twistednode",
    script = "twistednode.py",
    icon_resources=[(1, "img/solipsis.ico")]
    )
   
navigator = Target(
    name = "navigator",
    description = "Solipsis Navigator",
    modules = "navigator",
    script = "navigator.py",
    icon_resources=[(1, "img/solipsis.ico")]
    )

distutils.core.setup(
    name=name,
    version=version,
    description=description,
    author=author,
    author_email=author_email,
    url=url,
    options={"py2exe":{"optimize":2,
                "packages": ["twisted", "wx", "encodings","solipsis"],
                "excludes": ["Tkconstants","Tkinter","tcl"],
                "dll_excludes": ["tcl84.dll", "tk84.dll"]}},
    console = [twistednode],
    windows = [navigator], 
    data_files=data_files)