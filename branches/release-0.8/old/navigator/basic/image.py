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
#from wxPython.wx import wxBitmap, wxBITMAP_TYPE_PNG, wxIcon, wxImage
import wx, os

class ImageManager(object):
    # directory where images are stored
    imgDir = "img" + os.sep
    buttonDir = imgDir + "buttons" + os.sep
    avatarDir = "avatar"


    IMG_SOLIPSIS_ICON = 'icon_solipsis.png'
    IMG_SOLIPSIS_LOGO = 'im_solipsis.png'
    IMG_TOP_BANNER = 'top_banner.png'
    IMG_2D_BACKGROUND = 'im_2D.png'

    IMG_TRANSFER_BLUE = 'transfer_blue.png'
    IMG_TRANSFER_SMALL_BLUE = 'small_transfer_blue.png'
    IMG_TRANSFER_SMALL_RED= 'small_transfer_red.png'
    IMG_TRANSFER_PICTO = 'picto_file.png'

    IMG_CHAT = 'im_chat.png'
    IMG_CHAT_RED = 'chat_red.png'
    IMG_CHAT_SMALL_BLUE = 'small_chat_blue.png'
    IMG_CHAT_PICTO = 'picto_chat.png'

    IMG_SEND = 'send_n.png'
    IMG_SEND_RED = 'send_red.png'
    IMG_SEND_BLUE = 'send_blue.png'

    IMG_AVATAR_GREY = 'avat_grey.png'
    IMG_AVATAR_PICTO = 'picto_avat.png'

    IMG_UNKNOWN_PICTO = 'picto_file.png'

    BUT_CREATE = 'bu_createEntity_n.png'
    BUT_REMOVE = 'bu_removeEntity_n.png'
    BUT_CONNECT = 'bu_connect_n.png'
    BUT_CLOSE_ENTITY = 'bu_closeEntity_n.png'
    BUT_OK = 'bu_ok_n.png'
    BUT_CANCEL = 'bu_cancel_n.png'

    def getBitmap(imgId):
        return  wx.Bitmap(ImageManager.imgDir + imgId, wx.BITMAP_TYPE_PNG)

    def getIcon(imgId):
        return  wx.Icon(ImageManager.imgDir + imgId, wx.BITMAP_TYPE_PNG)


    def getButton(imgId):
        return wx.Bitmap(ImageManager.buttonDir +imgId, wx.BITMAP_TYPE_PNG)

    getBitmap = staticmethod(getBitmap)
    getIcon = staticmethod(getIcon)
    getButton = staticmethod(getButton)
