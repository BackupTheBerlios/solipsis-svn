
import wx, os

# IMG_SOLIPSIS_ICON = 'icon_solipsis.png'
# IMG_SOLIPSIS_LOGO = 'im_solipsis.png'
# IMG_TOP_BANNER = 'top_banner.png'
#
# IMG_TRANSFER_BLUE = 'transfer_blue.png'
# IMG_TRANSFER_SMALL_BLUE = 'small_transfer_blue.png'
# IMG_TRANSFER_SMALL_RED= 'small_transfer_red.png'
# IMG_TRANSFER_PICTO = 'picto_file.png'
#
# IMG_CHAT = 'im_chat.png'
# IMG_CHAT_RED = 'chat_red.png'
# IMG_CHAT_SMALL_BLUE = 'small_chat_blue.png'
# IMG_CHAT_PICTO = 'picto_chat.png'
#
# IMG_SEND = 'send_n.png'
# IMG_SEND_RED = 'send_red.png'
# IMG_SEND_BLUE = 'send_blue.png'

# IMG_UNKNOWN_PICTO = 'picto_file.png'

IMG_AVATAR_GREY = 'avat_grey.png'
IMG_AVATAR_PICTO = 'picto_avat.png'

IMG_AVATAR = IMG_AVATAR_GREY

IMG_2D_BACKGROUND = 'im_2D.png'


class ImageRepository(object):
    # Directory where images are stored
    img_dir = "img" + os.sep

    def __init__(self):
        self.bitmaps = {}
        self.icons = {}
        self.images = {}

    def GetBitmap(self, image_id):
        if image_id not in self.bitmaps:
            self.bitmaps[image_id] = wx.Bitmap(self.img_dir + image_id)
        return self.bitmaps[image_id]

    def GetIcon(self, image_id):
        if image_id not in self.icons:
            self.icons[image_id] = wx.Icon(self.img_dir + image_id)
        return self.icons[image_id]

    def GetImage(self, image_id):
        if image_id not in self.images:
            self.images[image_id] = wx.Image(self.img_dir + image_id)
        return self.images[image_id]


