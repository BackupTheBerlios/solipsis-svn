from wxPython.wx import wxBitmap, wxBITMAP_TYPE_PNG, wxIcon, wxImage
import os

class ImageManager:
    # directory where images are stored
    imgDir = "img" + os.sep
    avatarDir = "avatar"


    def getSendWxBitmap():
        return wxBitmap(ImageManager.imgDir + 'send_n.png',wxBITMAP_TYPE_PNG)

    def getSolipsisIconWxIcon():
        return wxIcon(ImageManager.imgDir + 'icon_solipsis.png', wxBITMAP_TYPE_PNG)

    def getSolipsisIconWxBitmap():
        return wxBitmap(ImageManager.imgDir + 'icon_solipsis.png',wxBITMAP_TYPE_PNG)

    def getSolipsisLogoWxBitmap():
        return wxBitmap(ImageManager.imgDir + 'im_solipsis.png',wxBITMAP_TYPE_PNG)

    def getTopBannerWxBitmap():
        return wxBitmap(ImageManager.imgDir + 'top_banner.png', wxBITMAP_TYPE_PNG)

    def getBlueTransferWxBitmap():
        return wxBitmap(ImageManager.imgDir + 'transfer_blue.png',wxBITMAP_TYPE_PNG)

    def getRedChatWxBitmap():
        return wxBitmap(ImageManager.imgDir + 'chat_red.png', wxBITMAP_TYPE_PNG)

    def getRedSendWxBitmap():
        return wxBitmap(ImageManager.imgDir + 'send_red.png', wxBITMAP_TYPE_PNG)

    def getBlueSendWxBitmap():
        return wxBitmap(ImageManager.imgDir + 'send_blue.png', wxBITMAP_TYPE_PNG)

    def getChatFrameWxBitmap():
        return wxImage(ImageManager.imgDir + 'im_chat.png',
                       wxBITMAP_TYPE_PNG).ConvertToBitmap()

    def get2DBackgrounddWxBitmap():
        return wxImage(ImageManager.imgDir + 'im_2D.png',
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
