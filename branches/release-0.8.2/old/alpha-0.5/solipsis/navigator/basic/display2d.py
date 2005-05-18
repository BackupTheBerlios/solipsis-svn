import wx
from solipsis.navigator.basic.image import ImageManager
from solipsis.navigator.navigatorinfo import NavigatorInfo
from solipsis.navigator.service import Service

class Display2D:

    # to ensure that elements are corectly displayed inside the window
    # we specify an offset
    OFFSET = 30

    def __init__(self, window, navigatorInfo):
        """ Constructor.
        window : the wx.Window object where the entities are displayed
        navigatorInfo: navigator information : node, peers, options, etc..."""
        self.two_d_window = window
        self.navigatorInfo = navigatorInfo
        
    def OnPaint(self, event):
        dc = wx.ClientDC(self.two_d_window)

        # opions for the device context
        dc.SetBackground( wx.Brush("White",wx.SOLID) )
        dc.SetBackgroundMode(wx.TRANSPARENT)
        dc.SetFont( wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD, False) )
        dc.SetPen( wx.Pen("White",1) )
        dc.SetTextForeground("White")
        dc.SetBrush( wx.Brush("White",wx.TRANSPARENT) )


        # draw background picture
        two_d_bitmap = ImageManager.get2DBackgrounddWxBitmap()
        dc.DrawBitmap(two_d_bitmap, wx.Point(0,0), True)

        width  = self.two_d_window.GetClientSize().GetWidth()
        height = self.two_d_window.GetClientSize().GetHeight()
        # we are not connected, just display a 'not connected' message 
        if not self.navigatorInfo.isConnected():
            dc.DrawText('Not connected', wx.Point(width/2, height/2))
        else:            
            # display awarness radius
            dc.DrawCircle(wx.Point(width/2, height/2), width/2)
            
            self.displayEntity(dc, self.navigatorInfo.getNode())
            print '---'
            for peer in self.navigatorInfo.enumeratePeers():
                print peer.getId()
                self.displayEntity(dc, peer)

    def displayEntity(self, dc, entity):
        
        # display pseudo
        if self.navigatorInfo.arePseudosDisplayed() :
            pseudoCoordinate = self.getPseudoWindowCoordinate(entity)
            dc.DrawText(entity.getPseudo(), pseudoCoordinate)

        # display avatar
        if self.navigatorInfo.areAvatarsDisplayed() :
            avatarBitmap = ImageManager.getGreyAvatar()
            self.posAvatar = self.getWindowCoordinate(entity)
            dc.DrawBitmap(avatarBitmap, self.posAvatar, True)

            
        # display services picto bitmap
        for service in entity.enumerateServices():
            if service.id == Service.ID_CHAT:                
                chatBitmap = ImageManager.getChatPicto()
                chatCoordinate = self.getServiceWindowCoordinate(entity,
                                                                 Service.ID_CHAT)
                dc.DrawBitmap(chatBitmap, chatCoordinate, True)
            elif service.id == Service.ID_AVATAR:
                avatarPicto = ImageManager.getAvatarPicto()
                avatarCoordinate = self.getServiceWindowCoordinate(entity,
                                                             Service.ID_AVATAR)
                dc.DrawBitmap(avatarPicto, avatarCoordinate, True)
            elif service.id == Service.ID_FILE_TRANSFER:
                filePicto = ImageManager.getFilePicto()
                fileCoordinate = self.getServiceWindowCoordinate(entity,
                                                           Service.ID_FILE_TRANSFER)
                dc.DrawBitmap(filePicto, fileCoordinate, True)
            # unknown service type : display a question mark pictogram
            else:
                unknownPicto = ImageManager.getUnknownPicto()                
                unknownCoord = self.getServiceWindowCoordinate(entity,
                                                               Service.ID_UNKNOWN)
                dc.DrawBitmap(unknownPicto, unknownCoord, True)
        

    def getWindowCoordinate(self, entity):
        """ Return the coordinate of an entity based on its position 
        Entity : the Entity object we want to display
        Return : a wx.Point object"""
        
        # width and height of the window
        width  = self.two_d_window.GetClientSize().GetWidth() - Display2D.OFFSET
        height = self.two_d_window.GetClientSize().GetHeight()- Display2D.OFFSET

        # position of the entity (solipsis coordinate)
        # this position is relative to the position of the node
        # i.e. node has position (0,0)
        pos = entity.getRelativePosition()
        posX = pos.getPosX()
        posY = pos.getPosY()

        # To determine the scale we need to know what is the farthest peer
        # that we have to display
        maxX = self.navigatorInfo.getMaxPosX()
        maxY = self.navigatorInfo.getMaxPosY()
        
        # we have no peers, set a default using the size of the window
        if maxX == 0:
            maxX = width
        if maxY == 0:
            maxY = height
            
        # In the wx coordinate system:
        # wx.Point(0,0) is located in the top left
        # wx.Point(width,0) is located in the top right
        # wx.Point(width,height) is located in the bottom right
        # we are now converting the solipsis position into a coordinate in the
        # wx coordinate system

        # now posX is in the [0..2*maxX] range and posY is in the [0..2*maxY] range
        posX = posX + maxX
        posY = posY + maxY

        # compute the scale factor between this 2 coordinate systems
        scaleX = width/(2*maxX)
        scaleY = height/(2*maxY)

        # position of the entity in the wx coordinate system
        wxPosX = posX*scaleX
        wxPosY = height - (posY*scaleY) 

        return wx.Point(wxPosX, wxPosY)

    def getPseudoWindowCoordinate(self, entity):
        coordinate = self.getWindowCoordinate(entity)
        pseudoCoord = coordinate + wx.Point(0,Display2D.OFFSET)
        return pseudoCoord

    def getServiceWindowCoordinate(self, entity, serviceId):
        coordinate = self.getWindowCoordinate(entity)
        offset = None
        if serviceId == Service.ID_CHAT:
            offset = wx.Point(Display2D.OFFSET, 10)
        elif serviceId == Service.ID_AVATAR:
            offset = wx.Point(Display2D.OFFSET, 20)               
        elif serviceId == Service.ID_FILE_TRANSFER:
            offset = wx.Point(Display2D.OFFSET, 30)
        else:
            offset = wx.point(Display2D.OFFSET,40)

        return coordinate + offset
        
