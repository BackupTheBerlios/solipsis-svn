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

import wx
import sys
import os, os.path
import pickle
from StringIO import StringIO

from solipsis. services.profile import PREVIEW_PT

# Search first in system directory, fall back to bundled version if necessary
try:
    from simpletal import simpleTAL, simpleTALES
except ImportError:
    import solipsis
    _simpletal_path = os.path.join(os.path.dirname(solipsis.__file__), "lib")
    sys.path.append(_simpletal_path)
    from simpletal import simpleTAL, simpleTALES
    sys.path.remove(_simpletal_path)
from solipsis.services.profile import ENCODING
from solipsis.util.uiproxy import UIProxy


class AbstractView:
    """Base class for all views"""

    def __init__(self, document, do_import=True, name="abstract"):
        self.document = document
        self.name = name
        if do_import:
            self.import_document(document)  

    def get_name(self):
        """used as key in index"""
        return self.name

    def import_document(self, document):
        """update view with document"""
        self.document = document
        # personal tab
        self.update_title()
        self.update_firstname()
        self.update_lastname()
        self.update_pseudo()
        self.update_photo()
        self.update_email()
        self.update_birthday()
        self.update_language()
        self.update_address()
        self.update_postcode()
        self.update_city()
        self.update_country()
        self.update_description()
        self.update_download_repo()
        # custom tab
        self.update_hobbies()
        self.update_custom_attributes()
        # FILE TAB
        self.update_files()
        # OTHERS TAB
        self.update_peers()
        
    # PERSONAL TAB
    def update_title(self):
        """display title in view"""
        raise NotImplementedError

    def update_firstname(self):
        """display firstname in view"""
        raise NotImplementedError

    def update_lastname(self):
        """lastname"""
        raise NotImplementedError

    def update_pseudo(self):
        """pseudo"""
        raise NotImplementedError

    def update_photo(self):
        """photo"""
        raise NotImplementedError

    def update_email(self):
        """email"""
        raise NotImplementedError

    def update_birthday(self):
        """birthday"""
        raise NotImplementedError

    def update_language(self):
        """language"""
        raise NotImplementedError

    def update_address(self):
        """address"""
        raise NotImplementedError

    def update_postcode(self):
        """postcode"""
        raise NotImplementedError

    def update_city(self):
        """city"""
        raise NotImplementedError

    def update_country(self):
        """country"""
        raise NotImplementedError

    def update_description(self):
        """description"""
        raise NotImplementedError

    def update_download_repo(self):
        """download_repo"""
        raise NotImplementedError

    # CUSTOM TAB
    def update_hobbies(self):
        """hobbies"""
        raise NotImplementedError

    def update_custom_attributes(self):
        """custom_attributes"""
        raise NotImplementedError

    # BLOG TAB
    def update_blogs(self, blogs):
        """blog"""
        raise NotImplementedError

    def display_blog(self, peer_id, blog):
        """display blog"""
        raise NotImplementedError

    # FILE TAB  
    def reset_files(self):
        """file"""
        pass
    
    def update_files(self):
        """file"""
        raise NotImplementedError

    def display_files(self, peer_id, files):
        """display shared files"""
        raise NotImplementedError

    # OTHERS TAB
    def update_peers(self):
        """peer"""
        raise NotImplementedError


class PrintView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, document, stream=open("view.out", "w"),
                 do_import=False, name="print"):
        self.output = stream
        AbstractView.__init__(self, document, do_import, name)

    def println(self, string):
        """convert unicode if necessary and writes in correct place"""
        if isinstance(string, unicode):
            string = string.encode(ENCODING)
        else:
            string = str(string)
        self.output.write(string+"\n")
        self.output.flush()

    # PERSONAL TAB
    def update_title(self):
        """title"""
        self.println(self.document.get_title())

    def update_firstname(self):
        """firstname"""
        self.println(self.document.get_firstname())
        
    def update_lastname(self):
        """lastname"""
        self.println(self.document.get_lastname())

    def update_pseudo(self):
        """pseudo"""
        self.println(self.document.get_pseudo())

    def update_photo(self):
        """photo"""
        self.println(self.document.get_photo())    

    def update_email(self):
        """email"""
        self.println(self.document.get_email())   

    def update_birthday(self):
        """birthday"""
        self.println(self.document.get_birthday()) 

    def update_language(self):
        """language"""
        self.println(self.document.get_language())

    def update_address(self):
        """address"""
        self.println(self.document.get_address())

    def update_postcode(self):
        """int postcode"""
        self.println(self.document.get_postcode())

    def update_city(self):
        """city"""
        self.println(self.document.get_city())

    def update_country(self):
        """country"""
        self.println(self.document.get_country())

    def update_description(self):
        """description"""
        self.println(self.document.get_description())

    def update_download_repo(self):
        """download_repo"""
        self.println(self.document.get_download_repo())

    # CUSTOM TAB
    def update_hobbies(self):
        """list hobbies"""
        self.println(self.document.get_hobbies())
        
    def update_custom_attributes(self):
        """dict custom_attributes"""
        self.println(self.document.get_custom_attributes())

    # BLOG TAB
    def update_blogs(self, blogs):
        """blog"""
        self.println(pickle.dumps(blogs))
        
    def display_blog(self, peer_id, blog):
        """display blog"""
        self.println("%s: %s"% (peer_id, blog))

    def display_files(self, peer_id, files):
        """display shared files"""
        self.println("%s: %s"% (peer_id, files))
        
    # FILE TAB
    def update_files(self):
        """file"""
        self.println(self.document.get_files())
        
    # OTHERS TAB        
    def update_peers(self):
        """peer"""
        self.println(self.document.get_peers())
        

class GuiView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, document, frame, do_import=True, name="gui"):
        # link to the frame used by view
        self.frame = frame
        # init view
        AbstractView.__init__(self, document, do_import, name)

    # PERSONAL TAB: frame.personal_tab
    def update_title(self):
        """title"""
        self.frame.personal_tab.title_value.SetValue(self.document.get_title())

    def update_firstname(self):
        """firstname"""
        self.frame.personal_tab.firstname_value.SetValue(
            self.document.get_firstname())
        
    def update_lastname(self):
        """lastname"""
        self.frame.personal_tab.lastname_value.SetValue(
            self.document.get_lastname())

    def update_pseudo(self):
        """pseudo"""
        self.frame.personal_tab.nickname_value.SetValue(
            self.document.get_pseudo())

    def update_photo(self):
        """photo"""
        self.frame.personal_tab.photo_button.SetBitmapLabel(
            wx.Bitmap(self.document.get_photo(), wx.BITMAP_TYPE_ANY))
    def update_email(self):
        """email"""
        self.frame.personal_tab.email_value.SetValue(
            self.document.get_email())     

    def update_birthday(self):
        """birthday"""
        self.frame.personal_tab.birthday_value.SetValue(
            self.document.get_birthday()) 

    def update_language(self):
        """language"""
        self.frame.personal_tab.language_value.SetValue(
            self.document.get_language())

    def update_address(self):
        """address"""
        self.frame.personal_tab.road_value.SetValue(
            self.document.get_address())

    def update_postcode(self):
        """int postcode"""
        self.frame.personal_tab.postcode_value.SetValue(
            self.document.get_postcode())

    def update_city(self):
        """city"""
        self.frame.personal_tab.city_value.SetValue(
            self.document.get_city())

    def update_country(self):
        """country"""
        self.frame.personal_tab.country_value.SetValue(
            self.document.get_country())

    def update_description(self):
        """description"""
        self.frame.personal_tab.description_value.SetValue(
            self.document.get_description())

    def update_download_repo(self):
        """download_repo"""
        self.frame.file_dlg.set_download_repo(
            self.document.get_download_repo())

    # CUSTOM TAB : frame.custom_tab
    def update_hobbies(self):
        """list hobbies"""
        self.frame.custom_tab.hobbies_value.SetValue(
            '\n'.join(self.document.get_hobbies()))
        
    def update_custom_attributes(self):
        """dict custom_attributes"""
        self.frame.custom_tab.custom_list.DeleteAllItems()
        for key, value in self.document.get_custom_attributes().iteritems():
            index = self.frame.custom_tab.custom_list.InsertStringItem(
                sys.maxint, key)
            self.frame.custom_tab.custom_list.SetStringItem(index, 1, value)

    # BLOG TAB
    def update_blogs(self, blogs):
        """blog"""
        self.frame.blog_tab.on_update()
        
    def display_blog(self, peer_id, blog):
        """display blog"""
        self.frame.display_blog(peer_id, blog)
        
    # FILE TAB : frame.file_tab        
    def reset_files(self):
        """file"""
        self.frame.file_tab.reset_files()
        
    def update_files(self):
        """file"""
        for sharing_container in self.document.get_files().values():
            self.frame.file_tab.cb_update_tree(sharing_container)

    def display_files(self, peer_id, files):
        """display shared files"""
        self.frame.display_files(peer_id, files)
        
    # OTHERS TAB : frame.other_tab  
    def update_peers(self):
        """peer"""
        self.frame.other_tab.cb_update_peers(self.document.get_peers())

class HtmlView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, document, html_window=None,
                 auto_refresh=False, do_import=True, name="html"):
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
        # init view
        AbstractView.__init__(self, document, do_import, name)

    def update_view(self):
        """rebuild HTML View"""
        self.view and self.view.close()
        self.view = StringIO()
        self.template.expand(self.context, self.view, outputEncoding=ENCODING)
        self.html_window and self.html_window.SetPage(self.get_view())

    def get_view(self, update=False):
        """returns HTML String"""
        if update:
            self.update_view()
        return unicode(self.view.getvalue(), ENCODING)

    def set_auto_refresh(self, enable):
        """change mode of refresh"""
        self.auto_refresh = enable

    # PERSONAL TAB: frame.personal_tab
    def update_title(self):
        """title"""
        self.context.addGlobal("title", self.document.get_title())
        if self.auto_refresh:
            self.update_view()

    def update_firstname(self):
        """firstname"""
        self.context.addGlobal("firstname", self.document.get_firstname())
        if self.auto_refresh:
            self.update_view()
        
    def update_lastname(self):
        """lastname"""
        self.context.addGlobal("lastname", self.document.get_lastname())
        if self.auto_refresh:
            self.update_view()

    def update_pseudo(self):
        """pseudo"""
        self.context.addGlobal("pseudo", self.document.get_pseudo())
        if self.auto_refresh:
            self.update_view()

    def update_photo(self):
        """photo"""
        self.context.addGlobal("photo", self.document.get_photo())
        if self.auto_refresh:
            self.update_view()

    def update_email(self):
        """email"""
        self.context.addGlobal("email", self.document.get_email())
        if self.auto_refresh:
            self.update_view() 

    def update_birthday(self):
        """birthday"""
        self.context.addGlobal("birthday", self.document.get_birthday())
        if self.auto_refresh:
            self.update_view()

    def update_language(self):
        """language"""
        self.context.addGlobal("language", self.document.get_language())
        if self.auto_refresh:
            self.update_view()

    def update_address(self):
        """address"""
        self.context.addGlobal("address", self.document.get_address())
        if self.auto_refresh:
            self.update_view()

    def update_postcode(self):
        """int postcode"""
        self.context.addGlobal("postcode", self.document.get_postcode())
        if self.auto_refresh:
            self.update_view()

    def update_city(self):
        """city"""
        self.context.addGlobal("city", self.document.get_city())
        if self.auto_refresh:
            self.update_view()

    def update_country(self):
        """country"""
        self.context.addGlobal("country", self.document.get_country())
        if self.auto_refresh:
            self.update_view()

    def update_description(self):
        """description"""
        self.context.addGlobal("description", self.document.get_description())
        if self.auto_refresh:
            self.update_view()

    def update_download_repo(self):
        """download_repo"""
        self.context.addGlobal("download_repo", self.document.get_description())
        if self.auto_refresh:
            self.update_view()

    # CUSTOM TAB : frame.custom_tab
    def update_hobbies(self):
        """list hobbies"""
        self.context.addGlobal("hobbies", self.document.get_hobbies())
        if self.auto_refresh:
            self.update_view()
        
    def update_custom_attributes(self):
        """dict custom_attributes"""
        self.context.addGlobal("attributes",
                               self.document.get_custom_attributes())
        if self.auto_refresh:
            self.update_view()

    # BLOG TAB
    def update_blogs(self, blogs):
        """blog"""
        self.context.addGlobal("blogs", blogs)
        if self.auto_refresh:
            self.update_view()
        
    def display_blog(self, peer_id, blog):
        """display blog"""
        pass
        
    # FILE TAB : frame.file_tab
    def update_files(self):
        """file"""
        html_format = {}
        for repo in self.document.get_repositories():
            content = {}
            html_format[repo] = content
            for container in self.document.get_shared(repo):
                content[container.path[len(repo):]] = container._tag
        self.context.addGlobal("files", html_format)
        if self.auto_refresh:
            self.update_view()
            
    def display_files(self, peer_id, files):
        """display shared files"""
        self.context.addGlobal("shared_files", (peer_id, files))
        
    # OTHERS TAB : frame.other_tab  
    def update_peers(self):
        """peer"""
        self.context.addGlobal("ordered_peers",
                               self.document.get_ordered_peers())
        if self.auto_refresh:
            self.update_view()
