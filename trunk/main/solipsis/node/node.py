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

import random

from solipsis.util.position import Position
from solipsis.util.address import Address
from solipsis.util.exception import *
from solipsis.util.utils import CreateSecureId
from solipsis.util.entity import Entity, Service


class Node(Entity):
    count = 0

    # Translation of the word "home" in many languages
    # (see:
    # - http://www.majstro.com/
    # - http://free.translated.net/
    # - ...
    # )
    home_translations = [
        u'llar',                # Catalan
        u'hjem',                # Danish
        u'thuis',               # Dutch
        u'ham',                 # Old English
        u'hejmen',              # Esperanto
        u'heim',                # Faeroese
        u'koti',                # Finnish
        u'maison',              # French
        u'th\xfas',             # Frisian
        u'Heim',                # German
        u'\u03c3\u03c0\u03af\u03c4\u03b9', # Greek
        u'haza',                # Hungarian
        u'b\xfasta\xf0ur',      # Icelandic
        u'Rumah',               # Indonesian
        u'casa',                # Italian
        #~ u'uti',                 # Japanese
        u'\u5bb6',              # Japanese
        u'\uac00\uc815',        # Korean
        u'atrium',              # Latin
        u'bolig',               # Norwegian
        u'kas',                 # Papiamento
        u'dom',                 # Polish
        u'casa',                # Portuguese
        u'\u0434\u043e\u043c\u043e\u0439', # Russian
        u'dhachaidh',           # Scottish Gaelic
        u'\u5bb6\u5ead',        # Simplified Chinese
        u'casa',                # Spanish
        u'hem',                 # Swedish
        u'otoch',               # Yucatec
        u'ikhaya',              # Zulu
    ]

    random_pseudos = [
        u'aardvark',
        u'cat',
        u'dog',
        u'elephant',
        u'rabbit',
        u'tasmanian devil',
        
        u'armchair',
        u'bathroom',
        u'bedroom',
        u'dining-room',
        u'flowerpot',
        u'kitchen',
        u'shower',
        u'sofa',
        u'washing-machine',

        u'Izwal',
        u'Buggol',
        u'Croolis-Ulv',
        u'Croolis-Var',
        u'Torka',
        u'Trauma',
        u'Migrax',
        u'the Ark',
        
        u'another shrubbery',
        u'argument clinic',
        u'bakery',
        u'castle Anthrax',
        u'cheese shop',
        u'family homestead',
        u'garage',
        u'gorge of eternal peril',
        u'hell\'s grannies',
        u'junk food shop',
        u'little fluffy clouds',
        u'police station',
        u'shrubbery',
        u'wine shop',
    ]
    
    world_size = 2**128

    def __init__(self, reactor, params):
        self.reactor = reactor
        self.params = params

        id_ = self.CreateId()
        position = Position((params.pos_x, params.pos_y, 0))
        address = Address(params.host, params.port)

        # Call parent class constructor
        Entity.__init__(self, id_=id_, position=position, pseudo=params.pseudo, address=address)

        # Random pseudos for unnamed nodes
        if not self.pseudo:
            self.SetRandomPseudo()

        # Dummy test data
        self.languages = ['fr', 'en']
        #~ self.AddService(Service('chat', address='127.0.0.1:5555'))
        #~ self.AddService(Service('video', address='127.0.0.1:6543'))
        #~ self.AddService(Service('browse', 'in'))
        #~ self.AddService(Service('share', 'out'))

    def CreateId(self):
        # TODO: reasonable/persistent ID generation and attribution ?
        id_ = "%d_%d_%s" % (self.params.port, Node.count, CreateSecureId())
        Node.count += 1
        return id_

    def SetRandomPseudo(self):
        x, y = self.position.GetXY()
        #~ self.pseudo = unicode(random.choice(self.random_pseudos))
        #~ a = random.randrange(ord('A'), ord('Z') + 1)
        #~ b = random.randrange(0, 10)
        a = x * (10.0 / self.world_size)
        b = y * (10.0 / self.world_size)
        #~ print a, b
        #~ c = random.choice(['ga', 'bu', 'zo', 'meu'])
        c = random.choice(self.home_translations)
        self.pseudo = '%s%s-%s' % (chr(int(a) + ord('a')), str(int(b) + 1), c)
        #~ d = random.randrange(1, 100)
        #~ self.pseudo = '%s%s-%s' % (chr(a), str(b), c)
