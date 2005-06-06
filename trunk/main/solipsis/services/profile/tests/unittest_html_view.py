"""Represents data used in model. It has been split from Views
gathared in views.py. Documents are to be seen as completely
independant from views"""

import unittest
import difflib
from os.path import abspath
from solipsis.services.profile.data import PeerDescriptor
from solipsis.services.profile.document import CacheDocument, FileDocument
from solipsis.services.profile.view import HtmlView

TEMPLATE = """<html>
<head>
  <title>user preview</title>
  <style>
#contact { 
         text-align: left;
 }

#email {
          color:blue;
}

#description {
          font-style:italic;
	  max-width:400px;
	  border:thin solid black;
}

.header { 
          font-weight: bold;
	  text-decoration:underline;
          margin-top: .5em;
 }</style>
</head>
<body>

  <div id="contact">
    <img src="%s">
    <div>%s</div>
  </div>

  <h2 class="header">Personal Information</h2>
  <div> 
    <span>%s</span>
    <span>%s</span>
    <span>%s</span>
  </div>
  <div id="email">%s</div>
  <div>
    <span>%s</span>
    <span>%s</span>
  </div>
  <div>       
    <span>%s</span>
    <span>%s</span>
    <span>%s</span>
    <span>%s</span>
  </div>
  <div id="description">%s</div>

  <h2 class="header">Special Interests</h2>
  <div>
    %s 
  </div>
  <div>
    %s
  </div>

  <h2 class="header">Personal Files</h2>
  <dl>
    %s
  </dl>

  <h2 class="header">Known Neighbors</h2>
  <table>
    %s
  </table>
</body>
</html>
"""
   
class HtmlTest(unittest.TestCase):
    """test that all fields are correctly validated"""

    def setUp(self):
        """override one in unittest.TestCase"""
        self.document = CacheDocument()
        self.view = HtmlView(self.document)

    def assert_template(self):
        """diff result from view with expeceted template"""
        self.view.import_document(self.document)
        result = difflib.ndiff([line.strip() for line in self.print_template().splitlines()],
                               [line.strip() for line in self.view.get_view(True).splitlines()],
                               charjunk=lambda x: x in [' ', '\t'])
        result = list(result)
        for index, line in enumerate(result):
            if not line.startswith("  "):
                print self.view.get_view()
                print "*************"
                print '\n'.join(result[index-2:index+10])
            self.assert_(line.startswith("  "))
 
    def print_template(self):
        """fill template with values"""
        return TEMPLATE % (self.document.get_photo(),
                           self.document.get_pseudo(),
                           self.document.get_title(),
                           self.document.get_firstname(),
                           self.document.get_lastname(),
                           self.document.get_email(),
                           self.document.get_birthday(),
                           self.document.get_language(),
                           self.document.get_address(),
                           self.document.get_postcode(),
                           self.document.get_city(),
                           self.document.get_country(),
                           self.document.get_description(),
                           self.print_hobbies(),
                           self.print_custom(),
                           self.print_files(),
                           self.print_peers())

    def print_hobbies(self):
        html = [" <span>%s</span> |"% item for item in self.document.get_hobbies()] or ""
        return ''.join(html)

    def print_custom(self):
        html = ["<div><b>%s</b>: <span>%s</span></div>"% (key, value)
                for key, value in self.document.get_custom_attributes().iteritems()]
        return ''.join(html)

    def print_files(self):
        html = []
        repos = self.document.get_repositories()
        repos.sort()
        for repo in repos:
            html.append("""
    <dt>%s</dt>
    <dd>%d shared files</dd>
"""% (repo, len(self.document.get_shared(repo).keys())))
        # concatenate all description of directories & return result
        return ''.join(html)

    def print_peers(self):
        html = []
        peers = self.document.get_peers()
        keys = peers.keys()
        keys.sort()
        for key in keys:
            peers_desc = peers[key]
            doc = peers_desc.document
            html.append("""<tr>
      <td>%s</td>
      <td>%s</td>
      <td>%s</td>
    </tr>"""% (peers_desc.state,
               doc and doc.get_pseudo() or "--",
               peers_desc.peer_id))
        return ''.join(html)
        
    
    # PERSONAL TAB
    def test_personal(self):
        """personal info"""
        self.document.set_title(u"Mr")
        self.document.set_firstname(u"Bruce")
        self.document.set_lastname(u"Willis")
        self.document.set_pseudo(u"john")
        self.document.set_photo("/home/emb/svn/solipsis/trunk/main/solipsis/services/profile/images/profile_male.gif")
        self.document.set_email(u"bruce.willis@stars.com")
        self.document.set_birthday(u"1/6/1947")
        self.document.set_language(u"English")
        self.document.set_address(u"Hill")
        self.document.set_postcode(u"920")
        self.document.set_city(u"Los Angeles")
        self.document.set_country(u"US")
        self.document.set_description(u"Lots of movies, quite famous, doesn't look much but very effective")
        self.assert_template()
       
    # CUSTOM TAB
    def test_hobbies(self):
        self.document.set_hobbies([u"cinema", u"theatre", u"cop", u"action"])
        self.assert_template()
        
    def test_custom(self):
        self.document.add_custom_attributes([u"zic", u"jazz"])
        self.document.add_custom_attributes([u"cinema", u"Die Hard"])
        self.assert_template()
        
    # FILE TAB       
    def test_files(self):
        self.document.add_repository(abspath(u"."))
        self.document.expand_dir(abspath(u"data"))
        self.document.share_files((abspath(u"data"), ["routage"], True))
        self.document.share_file((abspath(u"data/emptydir"), True))
        self.assert_template()
            
    # OTHERS TAB
    def test_ordered_peer(self):
        self.document.add_peer(u"nico")
        self.document.make_friend(u"emb")
        self.document.make_friend(u"star")
        self.document.make_friend(u"albert")
        self.assert_template()
        
    def test_adding_peer(self):
        self.document.add_peer(u"nico")
        self.assert_template()
        
    def test_filling_data(self):
        self.document.fill_data((u"emb", FileDocument()))
        self.assert_template()
    
    def test_peers_status(self):
        self.document.blacklist_peer(u"nico")
        self.assert_template()

    #TODO test fill data

if __name__ == '__main__':
    unittest.main()
