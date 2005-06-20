"""this class is specific to GUI, kept in cmdClient for its API only"""

# ID allocation
_ids = None

class BookmarksDialog:
    def __init__(self, world, bookmarks, *args, **kwds):
        raise NotImplementedError
    
    def __set_properties(self):
        raise NotImplementedError

    def __do_layout(self):
        raise NotImplementedError
 
    # Event handlers
    def OnAddBookmark(self, event):
        raise NotImplementedError
 
    def OnDelBookmark(self, event):
        raise NotImplementedError
 
    def OnClose(self, event): 
        raise NotImplementedError
