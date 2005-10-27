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

__revision__ = "$Id$"

import wx
import sys
import os, os.path
import pickle
from StringIO import StringIO

from solipsis. services.profile import PREVIEW_PT, ENCODING

# Search first in system directory, fall back to bundled version if necessary
try:
    from simpletal import simpleTAL, simpleTALES
except ImportError:
    import solipsis
    _simpletal_path = os.path.join(os.path.dirname(solipsis.__file__), "lib")
    sys.path.append(_simpletal_path)
    from simpletal import simpleTAL, simpleTALES
    sys.path.remove(_simpletal_path)
from solipsis.services.profile import force_unicode
from solipsis.util.uiproxy import UIProxy


class AbstractView:
    """Base class for all views"""

    def __init__(self, desc, do_import=True, name="abstract"):
        _desc = desc
        self.name = name
        if do_import:
            self.import_desc(desc)  

    def get_name(self):
        """used as key in index"""
        return self.name

    def import_desc(self, desc):
        """update view with document"""
        self._desc = desc
        # personal tab
        self.update_title()
        self.update_firstname()
        self.update_lastname()
        self.update_photo()
        self.update_email()
        # custom tab
        self.update_custom_attributes()
        # FILE TAB
        self.update_files()
        # OTHERS TAB
        self.update_peers()
        
    # PERSONAL TAB
    def update_pseudo(self):
        """display title in view"""
        raise NotImplementedError
    
    def update_title(self):
        """display title in view"""
        raise NotImplementedError

    def update_firstname(self):
        """display firstname in view"""
        raise NotImplementedError

    def update_lastname(self):
        """lastname"""
        raise NotImplementedError

    def update_photo(self):
        """photo"""
        raise NotImplementedError

    def update_email(self):
        """email"""
        raise NotImplementedError

    # CUSTOM TAB
    def update_custom_attributes(self):
        """custom_attributes"""
        raise NotImplementedError

    # BLOG TAB
    def update_blogs(self):
        """blog"""
        raise NotImplementedError

    # FILE TAB  
    def build_files(self):
        """structure changes (repository)"""
        raise NotImplementedError
        
    def update_files(self):
        """properties of files changes (tag...)"""
        raise NotImplementedError

    # OTHERS TAB
    def update_peers(self):
        """peer"""
        raise NotImplementedError


class PrintView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, desc, stream=None,
                 do_import=False, name="print"):
        if stream != None:
            self.output = stream
        else:
            stream = open("view.out", "w")
        AbstractView.__init__(self, desc, do_import, name)

    def println(self, string):
        """convert unicode if necessary and writes in correct place"""
        if isinstance(string, unicode):
            string = string.encode(ENCODING)
        else:
            string = str(string)
        self.output.write(string+"\n")
        self.output.flush()

    # PERSONAL TAB
    def update_pseudo(self):
        """display title in view"""
        self.println(self._desc.document.get_pseudo())
    
    def update_title(self):
        """title"""
        self.println(self._desc.document.get_title())

    def update_firstname(self):
        """firstname"""
        self.println(self._desc.document.get_firstname())
        
    def update_lastname(self):
        """lastname"""
        self.println(self._desc.document.get_lastname())

    def update_photo(self):
        """photo"""
        self.println(self._desc.document.get_photo())    

    def update_email(self):
        """email"""
        self.println(self._desc.document.get_email())   

    # CUSTOM TAB
    def update_custom_attributes(self):
        """dict custom_attributes"""
        self.println(self._desc.document.get_custom_attributes())

    # BLOG TAB
    def update_blogs(self):
        """blog"""
        self.println(pickle.dumps(self._desc.blog))
        
    # FILE TAB
    def build_files(self):
        """structure changes (repository)"""
        self.println(self._desc.document.get_files())
        
    def update_files(self):
        """properties of files changes (tag...)"""
        self.build_files()
        
    # OTHERS TAB        
    def update_peers(self):
        """peer"""
        self.println(self._desc.document.get_peers())

class HtmlView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, desc, html_window=None, auto_refresh=False,
                 do_import=True, name="html"):
        # init HTML string, wxWidget
        self.view = None
        self.auto_refresh = auto_refresh
        self.html_window = html_window and UIProxy(html_window) or None
        # Create the context that is used by the template
        self.context = simpleTALES.Context(allowPythonPath=1)
        template_file = open (PREVIEW_PT(), 'r')
        self.template = simpleTAL.compileHTMLTemplate(template_file,
                                                      inputEncoding=ENCODING)
        template_file.close()
        self.context.addGlobal("pseudo", desc.document.get_pseudo())
        # init view
        AbstractView.__init__(self, desc, do_import, name)
        self._update_view()

    def _update_view(self):
        """rebuild HTML View"""
        self.view and self.view.close()
        self.view = StringIO()
        self.template.expand(self.context, self.view, outputEncoding=ENCODING)
        self.html_window and self.html_window.SetPage(self.get_view())

    def get_view(self, update=False):
        """returns HTML String"""
        if update:
            self._update_view()
        return force_unicode(self.view.getvalue())

    def set_auto_refresh(self, enable):
        """change mode of refresh"""
        self.auto_refresh = enable

    # PERSONAL TAB: frame.personal_tab
    def update_pseudo(self):
        """display title in view"""
        self.context.addGlobal("pseudo", self._desc.document.get_pseudo())
        if self.auto_refresh:
            self._update_view()
    
    def update_title(self):
        """title"""
        self.context.addGlobal("title", self._desc.document.get_title())
        if self.auto_refresh:
            self._update_view()

    def update_firstname(self):
        """firstname"""
        self.context.addGlobal("firstname", self._desc.document.get_firstname())
        if self.auto_refresh:
            self._update_view()
        
    def update_lastname(self):
        """lastname"""
        self.context.addGlobal("lastname", self._desc.document.get_lastname())
        if self.auto_refresh:
            self._update_view()

    def update_photo(self):
        """photo"""
        self.context.addGlobal("photo", self._desc.document.get_photo())
        if self.auto_refresh:
            self._update_view()

    def update_email(self):
        """email"""
        self.context.addGlobal("email", self._desc.document.get_email())
        if self.auto_refresh:
            self._update_view() 

    def update_custom_attributes(self):
        """dict custom_attributes"""
        self.context.addGlobal("attributes",
                               self._desc.document.get_custom_attributes())
        if self.auto_refresh:
            self._update_view()

    # BLOG TAB
    def update_blogs(self):
        """blog"""
        self.context.addGlobal("blog", self._desc.blog)
        if self.auto_refresh:
            self._update_view()
        
    # FILE TAB : frame.file_tab
    def build_files(self):
        """structure changes (repository)"""
        self.context.addGlobal("files", self._desc.document.get_shared_files())
        if self.auto_refresh:
            self._update_view()
        
    def update_files(self):
        """properties of files changes (tag...)"""
        self.build_files()
        
    # OTHERS TAB
    def update_peers(self):
        """peer"""
        self.context.addGlobal("ordered_peers",
                               self._desc.document.get_ordered_peers())
        if self.auto_refresh:
            self._update_view()


class EditorView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, desc, frame,
                 do_import=True, name="editor"):
        # link to the frame used by view
        self.frame = frame
        # init view
        AbstractView.__init__(self, desc, do_import, name)

    # PERSONAL TAB: frame.personal_tab
    def update_pseudo(self):
        """title"""
        self.frame.personal_tab.nickname_value.SetValue(
            self._desc.document.get_pseudo())
        
    def update_title(self):
        """title"""
        self.frame.personal_tab.title_value.SetValue(
            self._desc.document.get_title())

    def update_firstname(self):
        """firstname"""
        self.frame.personal_tab.firstname_value.SetValue(
            self._desc.document.get_firstname())
        
    def update_lastname(self):
        """lastname"""
        self.frame.personal_tab.lastname_value.SetValue(
            self._desc.document.get_lastname())

    def update_photo(self):
        """photo"""
        self.frame.personal_tab.photo_button.SetBitmapLabel(
            wx.Bitmap(self._desc.document.get_photo(), wx.BITMAP_TYPE_ANY))

    def update_email(self):
        """email"""
        self.frame.personal_tab.email_value.SetValue(
            self._desc.document.get_email())     

    def update_custom_attributes(self):
        """dict custom_attributes"""
        self.frame.personal_tab.custom_list.DeleteAllItems()
        for key, value in self._desc.document.get_custom_attributes().items():
            index = self.frame.personal_tab.custom_list.InsertStringItem(
                sys.maxint, key)
            self.frame.personal_tab.custom_list.SetStringItem(index, 1, value)

    # BLOG TAB
    def update_blogs(self):
        """blog"""
        self.frame.blog_tab.on_update()
        
    # FILE TAB : frame.file_tab
    def build_files(self):
        self.frame.file_tab.cb_build_tree(self._desc.document.get_files())
        
    def update_files(self):
        self.frame.file_tab.cb_update_tree(self._desc.document.get_files())
        
    # OTHERS TAB
    def update_peers(self):
        """peer"""
        # was used in "Contacts" tab
        pass

class ViewerView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, desc, frame,
                 do_import=False, name="viewer"):
        # link to the frame used by view
        self.frame = frame
        # init view
        AbstractView.__init__(self, desc, do_import, name)
        
    # PERSONAL TAB
    def update_pseudo(self):
        """display title in view"""
        pass
    
    def update_title(self):
        """display title in view"""
        pass

    def update_firstname(self):
        """display firstname in view"""
        pass

    def update_lastname(self):
        """lastname"""
        pass

    def update_photo(self):
        """photo"""
        pass

    def update_email(self):
        """email"""
        pass

    # CUSTOM TAB
    def update_custom_attributes(self):
        """custom_attributes"""
        pass

    # BLOG TAB
    def update_blogs(self):
        """display blog"""
        peer_desc = self._desc.document.last_downloaded_desc
        if peer_desc != None:
            self.frame.display_blog(peer_desc)
        
    # FILE TAB : frame.file_tab
    def build_files(self):
        """structure changes (repository)"""
        peer_desc = self._desc.document.last_downloaded_desc
        if peer_desc != None:
            self.frame.display_files(peer_desc)
        
    def update_files(self):
        """properties of files changes (tag...)"""
        self.build_files()
        
    # OTHERS TAB
    def update_peers(self):
        """peer"""
        peer_desc = self._desc.document.last_downloaded_desc
        if peer_desc != None:
            self.frame.display_profile(peer_desc)

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
        self.frame.cb_update(filter_name)

    def delete_filter(self, filter_name):
        self.frame.cb_delete(filter_name)
    

