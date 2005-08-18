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
from solipsis.util.utils import CreateSecureId, safe_str, safe_unicode
from solipsis.util.entity import Entity, Service
import protocol


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
        u'\u30db\u30fc\u30e0',  # Japanese
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

    world_size = 2**128

    def __init__(self, reactor, params):
        Entity.__init__(self)

        self.reactor = reactor
        self.params = params

        # Initial property values
        self.address = Address(params.host, params.port)
        if params.node_id:
            self.id_= safe_str(params.node_id)
        else:
            self.id_ = self.CreateId(params)
        if params.pos_x or params.pos_y:
            self.position = Position((params.pos_x, params.pos_y, 0))
        else:
            self.position = self.RandomPosition()
        if params.pseudo:
            self.pseudo = safe_unicode(params.pseudo)
        else:
            self.pseudo = self.RandomPseudo()
        print "Creating node '%s'" % self.id_

        # Call parent class constructor

        # Dummy test data
        self.languages = ['fr', 'en']
        #~ self.AddService(Service('chat', address='127.0.0.1:5555'))
        #~ self.AddService(Service('video', address='127.0.0.1:6543'))
        #~ self.AddService(Service('browse', 'in'))
        #~ self.AddService(Service('share', 'out'))

    def CreateId(self, params):
        """
        Create a random ID based on parameters.
        """
        base_id = CreateSecureId(params.pseudo)
        id_ = "%d_%d_%s" % (params.port, Node.count, base_id)
        Node.count += 1
        return id_

    def FillMeta(self, message):
        """
        Fill meta-information in a Solipsis message.
        """
        a = message.args
        a.pseudo = self.pseudo
        a.accept_languages = self.GetLanguages()
        a.accept_services = self.GetServices()

    def RandomPseudo(self):
        """
        Returns a random pseudo according to other node properties
        (e.g. position).
        """
        x, y = self.position.GetXY()
        a = x * (10.0 / self.world_size)
        b = y * (10.0 / self.world_size)
        c = random.choice(self.home_translations)
        pseudo = '%s%s-%s' % (chr(int(a) + ord('a')), str(int(b) + 1), c)
        return safe_unicode(pseudo)

    def RandomPosition(self):
        """
        Returns a random position in the world.
        """
        return Position((random.random() * self.world_size, random.random() * self.world_size, 0))

