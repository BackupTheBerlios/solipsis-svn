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
import os
from StringIO import StringIO
# Search first in system directory, fall back to bundled version if necessary
try:
    from simpletal import simpleTAL, simpleTALES
except ImportError:
    _simpletal_path = os.sep.join([os.path.curdir, "solipsis", "lib"])
    sys.path.append(_simpletal_path)
    from simpletal import simpleTAL, simpleTALES
    sys.path.remove(_simpletal_path)
from solipsis.services.profile import ENCODING


class AbstractView:
    """Base class for all views"""

    def __init__(self, document, name="abstract"):
        self.document = document
        self.name = name
        self.import_document()

    def get_name(self):
        """used as key in index"""
        return self.name

    def import_document(self):
        """update view with document"""
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
        # custom tab
        self.update_hobbies()
        self.update_custom_attributes()
        # FILE TAB
        self.update_repository()
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

    # CUSTOM TAB
    def update_hobbies(self):
        """hobbies"""
        raise NotImplementedError

    def update_custom_attributes(self):
        """custom_attributes"""
        raise NotImplementedError

    # FILE TAB
    def update_repository(self):
        """repository"""
        raise NotImplementedError

    def update_files(self):
        """file"""
        raise NotImplementedError

    def new_files(self, files):
        """file"""
        raise NotImplementedError

    # OTHERS TAB
    def update_peers(self):
        """peer"""
        raise NotImplementedError


class PrintView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, document, name="print"):
        AbstractView.__init__(self, document, name)

    # PERSONAL TAB
    def update_title(self):
        """title"""
        print  self.document.get_title()

    def update_firstname(self):
        """firstname"""
        print self.document.get_firstname()
        
    def update_lastname(self):
        """lastname"""
        print self.document.get_lastname()

    def update_pseudo(self):
        """pseudo"""
        print self.document.get_pseudo()  

    def update_photo(self):
        """photo"""
        print self.document.get_photo()      

    def update_email(self):
        """email"""
        print self.document.get_email()      

    def update_birthday(self):
        """DateTime birthday"""
        print self.document.get_birthday()  

    def update_language(self):
        """language"""
        print self.document.get_language()

    def update_address(self):
        """address"""
        print self.document.get_address()

    def update_postcode(self):
        """int postcode"""
        print self.document.get_postcode()

    def update_city(self):
        """city"""
        print self.document.get_city()

    def update_country(self):
        """country"""
        print self.document.get_country()

    def update_description(self):
        """description"""
        print self.document.get_description()

    # CUSTOM TAB
    def update_hobbies(self):
        """list hobbies"""
        print self.document.get_hobbies()
        
    def update_custom_attributes(self):
        """dict custom_attributes"""
        print self.document.get_custom_attributes()
        
    # FILE TAB
    def update_repository(self):
        """repository"""
        print self.document.get_repository()
        
    def update_files(self):
        """file"""
        print self.document.get_files()

    def new_files(self, files):
        """file"""
        print "new files: %s"% str(files)
        
    # OTHERS TAB        
    def update_peers(self):
        """peer"""
        print self.document.get_peers()
        

class GuiView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, document, frame, name="gui"):
        # link to the frame used by view
        self.frame = frame
        # init view
        AbstractView.__init__(self, document, name)

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
        """DateTime birthday"""
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
        
    # FILE TAB : frame.file_tab
    def update_repository(self):
        """repository"""
        self.frame.file_tab.build_tree(self.document.get_repository())
        
    def update_files(self):
        """file"""
        #TODO
        raise NotImplementedError

    def new_files(self, files):
        """file"""
        #TODO
        raise NotImplementedError
        
    # OTHERS TAB : frame.other_tab  
    def update_peers(self):
        """peer"""
        self.frame.other_tab.peers_list.Clear()
        peers = self.document.get_peers()
        for peer_and_doc in peers.values():
            self.frame.other_tab.peers_list.add_peer(*peer_and_doc)
        self.frame.other_tab.peers_list.RefreshAll()
        
    def update_peer_preview(self, pseudo, text=u""):
        """peer"""
        document = self.frame.other_tab.peers_list.get_peer_document(pseudo)
        if document:
            view = HtmlView(document)
            self.frame.other_tab.detail_preview.SetPage(text + view.get_view())
        else:
            self.frame.other_tab.detail_preview.SetPage(text or "<font color='red'>%s %s</font>"\
                                                        % (_("no data available for"), pseudo))
            
        

class HtmlView(AbstractView):
    """synthetises information and renders it in HTML"""

    def __init__(self, document, html_window=None, name="html"):
        # init HTML string, wxWidget
        self.view = None
        self.html_window = html_window
        # Create the context that is used by the template
        self.context = simpleTALES.Context(allowPythonPath=1)
        template_file = open ("../preview.html", 'r')
        self.template = simpleTAL.compileHTMLTemplate(template_file,
                                                      inputEncoding=ENCODING)
        template_file.close()
        # init view
        AbstractView.__init__(self, document, name)

    def update_view(self):
        """rebuild HTML View"""
        self.view and self.view.close()
        self.view = StringIO()
        self.template.expand(self.context, self.view, outputEncoding=ENCODING)
        self.html_window and self.html_window.SetPage(self.get_view())

    def get_view(self):
        """returns HTLM String"""
        return unicode(self.view.getvalue(), ENCODING)

    # PERSONAL TAB: frame.personal_tab
    def update_title(self):
        """title"""
        self.context.addGlobal("title", self.document.get_title())

    def update_firstname(self):
        """firstname"""
        self.context.addGlobal("firstname", self.document.get_firstname())
        
    def update_lastname(self):
        """lastname"""
        self.context.addGlobal("lastname", self.document.get_lastname())

    def update_pseudo(self):
        """pseudo"""
        self.context.addGlobal("pseudo", self.document.get_pseudo())

    def update_photo(self):
        """photo"""
        self.context.addGlobal("photo", self.document.get_photo())

    def update_email(self):
        """email"""
        self.context.addGlobal("email", self.document.get_email()) 

    def update_birthday(self):
        """DateTime birthday"""
        self.context.addGlobal("birthday", self.document.get_birthday())

    def update_language(self):
        """language"""
        self.context.addGlobal("language", self.document.get_language())

    def update_address(self):
        """address"""
        self.context.addGlobal("address", self.document.get_address())

    def update_postcode(self):
        """int postcode"""
        self.context.addGlobal("postcode", self.document.get_postcode())

    def update_city(self):
        """city"""
        self.context.addGlobal("city", self.document.get_city())

    def update_country(self):
        """country"""
        self.context.addGlobal("country", self.document.get_country())

    def update_description(self):
        """description"""
        self.context.addGlobal("description", self.document.get_description())

    # CUSTOM TAB : frame.custom_tab
    def update_hobbies(self):
        """list hobbies"""
        self.context.addGlobal("hobbies", self.document.get_hobbies())
        
    def update_custom_attributes(self):
        """dict custom_attributes"""
        self.context.addGlobal("attributes",
                               self.document.get_custom_attributes())
        
    # FILE TAB : frame.file_tab
    def update_repository(self):
        """repository"""
        self.context.addGlobal("repository", self.document.get_repository())
        
    def update_files(self):
        """file"""
        self.context.addGlobal("files", self.document.get_files())
        files = self.document.get_files()

    def new_files(self, files):
        """nothing to change in HTML view when files expanded since they are not shared by default"""
        pass
        
    # OTHERS TAB : frame.other_tab  
    def update_peers(self):
        """peer"""
        self.context.addGlobal("peers",  self.document.get_peers())
