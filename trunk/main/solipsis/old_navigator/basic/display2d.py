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
import wx
from solipsis.navigator.basic.image import ImageManager
from solipsis.navigator.navigatorinfo import NavigatorInfo
from solipsis.navigator.service import Service


class Display2D(object):

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
        two_d_bitmap = ImageManager.getBitmap(ImageManager.IMG_2D_BACKGROUND)
        dc.DrawBitmap(two_d_bitmap, 0, 0, True)

        width  = self.two_d_window.GetClientSize().GetWidth()
        height = self.two_d_window.GetClientSize().GetHeight()
        # we are not connected, just display a 'not connected' message
        if not self.navigatorInfo.isConnected():
            dc.DrawText('Not connected', width // 2, height // 2)
        else:
            # display awareness radius
            dc.DrawCircle(width / 2, height / 2, width / 2)

            self.displayEntity(dc, self.navigatorInfo.getNode())
            print '---'
            for peer in self.navigatorInfo.enumeratePeers():
                print peer.getId()
                self.displayEntity(dc, peer)

    def displayEntity(self, dc, entity):

        # display pseudo
        if self.navigatorInfo.arePseudosDisplayed() :
            pseudoCoordinate = self.getPseudoWindowCoordinate(entity)
            dc.DrawTextPoint(entity.getPseudo(), pseudoCoordinate)

        # display avatar
        if self.navigatorInfo.areAvatarsDisplayed() :
            avatarBitmap = ImageManager.getBitmap(ImageManager.IMG_AVATAR_GREY)
            self.posAvatar = self.getWindowCoordinate(entity)
            dc.DrawBitmapPoint(avatarBitmap, self.posAvatar, True)


        # display services picto bitmap
        for service in entity.enumerateServices():
            if service.id == Service.ID_CHAT:
                chatBitmap = ImageManager.getBitmap(ImageManager.IMG_CHAT_PICTO)
                chatCoordinate = self.getServiceWindowCoordinate(entity,
                                                                 Service.ID_CHAT)
                dc.DrawBitmapPoint(chatBitmap, chatCoordinate, True)
            elif service.id == Service.ID_AVATAR:
                avatarPicto = ImageManager.getBitmap(ImageManager.IMG_AVATAR_PICTO)
                avatarCoordinate = self.getServiceWindowCoordinate(entity,
                                                             Service.ID_AVATAR)
                dc.DrawBitmapPoint(avatarPicto, avatarCoordinate, True)
            elif service.id == Service.ID_FILE_TRANSFER:
                filePicto = ImageManager.getBitmap(ImageManager.IMG_TRANSFER_PICTO)
                fileCoordinate = self.getServiceWindowCoordinate(entity,
                                                           Service.ID_FILE_TRANSFER)
                dc.DrawBitmapPoint(filePicto, fileCoordinate, True)
            # unknown service type : display a question mark pictogram
            else:
                unknownPicto = ImageManager.getBitmap(ImageManager.IMG_UNKNOWN_PICTO)
                unknownCoord = self.getServiceWindowCoordinate(entity,
                                                               Service.ID_UNKNOWN)
                dc.DrawBitmapPoint(unknownPicto, unknownCoord, True)


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

