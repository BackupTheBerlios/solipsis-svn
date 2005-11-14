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
"""Represents views used in model. It reads its data from a Document
(document.py) even if its independant from the structure and the inner
workings of documents"""

__revision__ = "$Id: view.py 929 2005-11-01 23:56:12Z emb $"

from solipsis.services.profile.editor.view import AbstractView

class FilterView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, desc, frame,
                 do_import=True, name="filter"):
        # link to the frame used by view
        self.frame = frame
        # init view
        AbstractView.__init__(self, desc, do_import, name)

    def import_desc(self, desc):
        """update view with document"""
        self._desc = desc
        for filter_name in self._desc.document.filters:
            self.update_filter(filter_name)

    def update_filter(self, filter_name):
        """refresh gui when changing filter"""
        self.frame.cb_update(filter_name)

    def delete_filter(self, filter_name):
        """refresh gui when deleting filter"""
        self.frame.cb_delete(filter_name)
    

