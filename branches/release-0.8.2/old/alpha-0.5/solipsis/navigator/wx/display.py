from wxPython.wx import *
from solipsis.navigator.wx.image import ImageManager

class Display:
    def __init__(self, twoDwindow):
        self.two_d_window = twoDwindow
        
    def addDisplay2dServiceNeighbor(self, event):
        id=event.id
        if self.neighbor_item.has_key(id):
            self.neighbor_item[id][4] = TRUE
            # refresh the drawing
            self.toRefresh = TRUE
    
    def deleteDisplay2dServiceNeighbor(self, event):
        id=event.id
        
        if self.neighbor_item.has_key(id):
            self.neighbor_item[id][4] = FALSE
            # refresh the drawing
            self.toRefresh = TRUE
    
    def deleteImage(self, event):
        id=event.id
        self.navigator.deleteImage(id)
        
    def receiveImage(self, event):
        sender=event.sender
        image_name=event.image_name
        self.navigator.receiveImage(sender, image_name)

    def OnPaint2DView(self, event):
        dc = wxPaintDC(self.two_d_window)
        self.DoDrawing(dc)

    def ClearDrawing(self, dc=None):
        #print "ihm.ClearDrawing()"
        if dc is None:
            dc = wxClientDC(self.two_d_window)

        # draw background picture
        two_d_bitmap = ImageManager.get2DBackgrounddWxBitmap()
        dc.DrawBitmap(two_d_bitmap, 0, 0, TRUE)

    def DoDrawing(self, dc=None):
        if dc is None:
            dc = wxClientDC(self.two_d_window)

        # opions for the device context
        dc.SetBackground( wxBrush("White",wxSOLID) )

        dc.SetBackgroundMode(wxTRANSPARENT)
        dc.SetFont( wxFont(10, wxSWISS, wxNORMAL, wxBOLD, FALSE) )
        dc.SetPen( wxPen("White",1) )
        dc.SetTextForeground("White")
        dc.SetBrush( wxBrush("White",wxTRANSPARENT) )


        # draw background picture
        two_d_bitmap = ImageManager.get2DBackgrounddWxBitmap()
        dc.DrawBitmap(two_d_bitmap, 0, 0, TRUE)

        # display the image and the pseudo of my node
        if self.myNode_pseudo :
            avatar_bitmap = wxImage(self.myNode_avatar, wxBITMAP_TYPE_PNG).ConvertToBitmap()

            self.pos_avatar_x = long(((self.two_d_window.GetClientSize().GetWidth()-
                                       avatar_bitmap.GetWidth()) /2) + self.delta_x)
            self.pos_avatar_y = long(((self.two_d_window.GetClientSize().GetHeight()-
                                       avatar_bitmap.GetHeight()) /2) + self.delta_y)
            dc.DrawBitmap(avatar_bitmap, self.pos_avatar_x,self.pos_avatar_y, TRUE)

            # display pseudo of my node
            if self.isDisplayPseudos == 1:
                self.pos_pseudo_x = self.pos_avatar_x
                self.pos_pseudo_y = long(self.pos_avatar_y + avatar_bitmap.GetHeight())
                dc.DrawText(self.myNode_pseudo, self.pos_pseudo_x, self.pos_pseudo_y)

            # we display the awarness radius
            if self.myNode_ar :
                # Coordinates of the square enclosing the circle
                #arInDisplay2d = long(self.newCoordinates(long(self.myNode_ar)))
                #dc.DrawCircle(self.pos_avatar_x, self.pos_avatar_y, arInDisplay2d)
                dc.DrawCircle(  self.two_d_window.GetClientSize().GetWidth()/2,
                                self.two_d_window.GetClientSize().GetHeight()/2,
                                self.two_d_window.GetClientSize().GetWidth()/2)

            # display neighbor items
            for neighbor_object in self.neighbor_item.values():

                # recompute position in the screen
                posX = long(self.newCoordinates(neighbor_object[0])+(self.two_d_window.GetClientSize().GetWidth() /2))
                posY = long(self.newCoordinates(neighbor_object[1])+(self.two_d_window.GetClientSize().GetHeight() /2))
                pseudo = neighbor_object[2]
                #print "display Neighbor : [%s]" %pseudo

                # display neighbor image if it belongs to the screen
                if 0 < posY < self.two_d_window.GetClientSize().GetHeight() and 0 < posX < self.two_d_window.GetClientSize().GetWidth():
                    #print "display Neighbor image : [%s]" %pseudo
                    # resize the image in accordance with the ar
                    #self.display2d.chgSize(id)

                    # get the photo image object
                    if self.isDisplayAvatars == 1:
                        if (neighbor_object[6]):
                            avatar_bitmap = wxImage(neighbor_object[6], wxBITMAP_TYPE_PNG).ConvertToBitmap()
                        else:
                            # if the neighbor has no image, display the default image
                            avatar_bitmap = wxImage(self.neighbor_avatar, wxBITMAP_TYPE_PNG).ConvertToBitmap()
                    else:
                        avatar_bitmap = wxImage("img//avat_blanc.png", wxBITMAP_TYPE_PNG).ConvertToBitmap()

                    # display the image of neighbor
                    pos_avatar_x = long(posX-(avatar_bitmap.GetWidth())/2)
                    pos_avatar_y = long(posY-(avatar_bitmap.GetHeight())/2)
                    dc.DrawBitmap(avatar_bitmap, pos_avatar_x, pos_avatar_y, TRUE)

                    # display pseudo of the neighbor
                    if self.isDisplayPseudos == 1:
                        pos_pseudo_x = pos_avatar_x
                        pos_pseudo_y = long(pos_avatar_y + avatar_bitmap.GetHeight())
                        dc.DrawText(pseudo, pos_pseudo_x, pos_pseudo_y)

                    # display services picto bitmap
                    chat_bitmap = wxImage('img//picto_chat.png', wxBITMAP_TYPE_PNG).ConvertToBitmap()
                    pos_chat_x = long(pos_avatar_x + avatar_bitmap.GetWidth())
                    pos_chat_y = pos_avatar_y

                    avat_bitmap = wxImage('img//picto_avat.png', wxBITMAP_TYPE_PNG).ConvertToBitmap()
                    pos_avat_x = long(pos_avatar_x + avatar_bitmap.GetWidth())
                    pos_avat_y = long(pos_chat_y + chat_bitmap.GetHeight())

                    file_bitmap = wxImage('img//picto_fichier.png', wxBITMAP_TYPE_PNG).ConvertToBitmap()
                    pos_file_x = long(pos_avatar_x + avatar_bitmap.GetWidth())
                    pos_file_y = long(pos_avat_y + avat_bitmap.GetHeight())


                    # display the image of neighbor chat service
                    if neighbor_object[3]:
                        dc.DrawBitmap(chat_bitmap, pos_chat_x, pos_chat_y, TRUE)

                    # display the image of neighbor display2d service
                    if neighbor_object[4]:
                        dc.DrawBitmap(avat_bitmap, pos_avat_x, pos_avat_y, TRUE)

                    # display the image of neighbor chat service
                    if neighbor_object[5]:
                        dc.DrawBitmap(file_bitmap, pos_file_x, pos_file_y, TRUE)


    def setScale(self, ar):
        """ scale between the real distances and size of the display2d """
        
        debug.debug_info("ihm.setScale(%s)" %ar)
        
        # update max distance of Solipsis world displayed        
        if ar != 0:
            self.dist_max = ar

            # update scale for the screen
            sizeScreen = self.two_d_window.GetClientSize().GetWidth()
            self.scale = float( (sizeScreen / (2.0*ar) ))
        else:
            # if ar = 0 scale reinitialisation
            self.scale = 1

    def drawMyNode(self, pseudo, ar):
        self.myNode_pseudo = pseudo
        self.myNode_ar = ar

        # default avatar
        avatarFile = commun.AVATAR_DIR_NAME + os.sep + pseudo + "_default.png"
        shutil.copyfile("img//avat_gh.png", avatarFile)
        # resize the avatar file
        self.myNode_avatar = commun.chgSize(avatarFile)

        # refresh the drawing
        self.toRefresh = TRUE

    def drawMyAvatar(self, image_name):
        """ draw the avatar selected in the 2D View """
        self.myNode_avatar = image_name

        # refresh the drawing
        self.toRefresh = TRUE

    def insertNeighbor(self, id, posX, posY, pseudo):
        # store the new neighbor item with no service and no image
        self.neighbor_item[id] = [posX, posY, pseudo, FALSE, FALSE, FALSE, ""]

        # refresh the drawing
        #self.DoDrawing()
        self.toRefresh = TRUE

    def updateNeighbor(self, id, delta_x, delta_y):
        """ move the neighbor in the 2D view """
        
        # change the neighbor position
        if self.neighbor_item.has_key(id):
            # update the new coordinates of the neighbor
            posX = long(self.neighbor_item[id][0] + delta_x)
            if posX < -2**127L:
                posX = long(posX + 2**128L)
            elif posX > 2**127L:
                posX = long(posX - 2**128L)

            posY = long(self.neighbor_item[id][1] + delta_y)
            if posY < -2**127L:
                posY = long(posY + 2**128L)
            elif posY > 2**127L:
                posY = long(posY - 2**128L)

            self.neighbor_item[id][0] = posX
            self.neighbor_item[id][1] = posY

            # refresh the drawing
            self.toRefresh = TRUE

    def deleteNeighbor(self, id):
        debug.debug_info("ihm.deleteNeighbor(%s)" %id)
        # delete the neighbor item from the dictionnary
        del self.neighbor_item[id]

        # refresh the drawing
        #self.DoDrawing()
        self.toRefresh = TRUE
        # refresh the chatter list
        #self.navigator.displayChatterList()
        debug.debug_info("ihm.deleteNeighbor() OK")

    def displayNeighborImage(self, id, image_name):
        """ display the image of the neighbor in the display2d """
        
        # store the neighbor image
        if self.neighbor_item.has_key(id):
            self.neighbor_item[id][6] = image_name

            # refresh the drawing
            #self.DoDrawing()
            self.toRefresh = TRUE

    def deleteNeighborImage(self, id):
        """ delete the image of the neighbor in the display2d """
        debug.debug_info("ihm.deleteNeighborImage()")
        # delete the neighbor image
        if self.neighbor_item.has_key(id):
            self.neighbor_item[id][6] = ""

            # refresh the drawing
            self.toRefresh = TRUE
        debug.debug_info("ihm.deleteNeighborImage() OK")
        
    def newCoordinates(self, pos):
        """ return coordinates of a node in the display2d in accordance with its coordinates in the virtual world"""

        result = long(pos) * self.scale * self.coeff_zoom
        return result

    def clear2dView(self):
        """ clear all items displayed in 2D View """

        # my node variables
        self.myNode_pseudo = ""
        self.myNode_ar = ""
        #self.myNode_avatar = 'img//avat_gh.png'

        # dictionary associating widget item with a neighbor
        # {[neighbor_id]:[neighbor_posX, neighbor_posY, neighbor_pseudo, neighbor_display2d, neighbor_chat]}
        self.neighbor_item = {}

        # refresh the drawing
        #self.DoDrawing()
        self.toRefresh = TRUE

    def OnLeftDown(self, event):
        """ click on the display2d to move """
        #print "ihm.OnLeftDown()"

        # check if the navigator is connected to a node
        if (self.navigator.getIsConnected() == 1):

            # calculate the new node coordinates
            delta_x = event.m_x - self.pos_avatar_x
            delta_y = event.m_y - self.pos_avatar_y
            offset_x =  long( delta_x /(self.coeff_zoom * self.scale))
            offset_y =  long( delta_y/(self.coeff_zoom * self.scale))

            # display the node moving
            self.moveMyNode(delta_x, delta_y)

            # Inform the navigator
            mvt = str(offset_x) + ',' + str(offset_y)
            self.navigator.moveMyNode("POS",mvt)

    def moveMyNode(self, delta_x, delta_y):
        #print "ihm.moveMyNode(%d,%d)" %(delta_x, delta_y)
        for i in [1, 2, 3, 4]:
            self.delta_x = long(delta_x*i/4)
            self.delta_y = long(delta_y*i/4)
            # refresh the drawing
            self.DoDrawing()
            time.sleep(0.5)

        self.delta_x = 0
        self.delta_y = 0

