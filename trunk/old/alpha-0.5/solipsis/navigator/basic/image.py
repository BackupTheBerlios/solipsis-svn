#from wxPython.wx import wxBitmap, wxBITMAP_TYPE_PNG, wxIcon, wxImage
import wx, os

class ImageManager:
    # directory where images are stored
    imgDir = "img" + os.sep
    avatarDir = "avatar"


    def getSendWxBitmap():
        return wx.Bitmap(ImageManager.imgDir + 'send_n.png',wx.BITMAP_TYPE_PNG)

    def getSolipsisIconWxIcon():
        return wx.Icon(ImageManager.imgDir + 'icon_solipsis.png', wx.BITMAP_TYPE_PNG)

    def getSolipsisIconWxBitmap():
        return wx.Bitmap(ImageManager.imgDir + 'icon_solipsis.png',wx.BITMAP_TYPE_PNG)

    def getSolipsisLogoWxBitmap():
        return wx.Bitmap(ImageManager.imgDir + 'im_solipsis.png',wx.BITMAP_TYPE_PNG)

    def getTopBannerWxBitmap():
        return wx.Bitmap(ImageManager.imgDir + 'top_banner.png', wx.BITMAP_TYPE_PNG)

    def getBlueTransferWxBitmap():
        return wx.Bitmap(ImageManager.imgDir + 'transfer_blue.png',wx.BITMAP_TYPE_PNG)

    def getRedChatWxBitmap():
        return wx.Bitmap(ImageManager.imgDir + 'chat_red.png', wx.BITMAP_TYPE_PNG)

    def getRedSendWxBitmap():
        return wx.Bitmap(ImageManager.imgDir + 'send_red.png', wx.BITMAP_TYPE_PNG)

    def getBlueSendWxBitmap():
        return wx.Bitmap(ImageManager.imgDir + 'send_blue.png', wx.BITMAP_TYPE_PNG)

    def getChatFrameWxBitmap():
        return wx.Image(ImageManager.imgDir + 'im_chat.png',
                       wx.BITMAP_TYPE_PNG).ConvertToBitmap()

    def get2DBackgrounddWxBitmap():
        return wx.Image(ImageManager.imgDir + 'im_2D.png',
                       wx.BITMAP_TYPE_PNG).ConvertToBitmap()

    def getGreyAvatar():
        return wx.Image(ImageManager.imgDir + 'avat_grey.png',
                        wx.BITMAP_TYPE_PNG).ConvertToBitmap()

    def getChatPicto():
        return wxImage(ImageManager.imgDir + 'picto_chat.png',
                wxBITMAP_TYPE_PNG).ConvertToBitmap()

    def getAvatarPicto():
        return wxImage(ImageManager.imgDir + 'picto_avat.png',
                wxBITMAP_TYPE_PNG).ConvertToBitmap()

    def getFilePicto():
        return wxImage(ImageManager.imgDir + 'picto_file.png',
                wxBITMAP_TYPE_PNG).ConvertToBitmap()
    
    getSendWxBitmap = staticmethod(getSendWxBitmap)
    getSolipsisIconWxIcon = staticmethod(getSolipsisIconWxIcon)
    getSolipsisLogoWxBitmap = staticmethod(getSolipsisLogoWxBitmap)
    getSolipsisIconWxBitmap = staticmethod(getSolipsisIconWxBitmap)
    getTopBannerWxBitmap = staticmethod(getTopBannerWxBitmap)
    getBlueTransferWxBitmap = staticmethod(getBlueTransferWxBitmap)
    getRedChatWxBitmap = staticmethod(getRedChatWxBitmap)
    getRedSendWxBitmap = staticmethod(getRedSendWxBitmap)
    getBlueSendWxBitmap = staticmethod(getBlueSendWxBitmap)
    getChatFrameWxBitmap = staticmethod(getChatFrameWxBitmap)
    get2DBackgrounddWxBitmap = staticmethod(get2DBackgrounddWxBitmap)
    getGreyAvatar = staticmethod(getGreyAvatar)
    getChatPicto = staticmethod(getChatPicto)
    getAvatarPicto = staticmethod(getAvatarPicto)
    getFilePicto = staticmethod(getFilePicto)
