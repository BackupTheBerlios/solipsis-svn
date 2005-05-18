from wxPython.wx import *

class Chat:
    
    def OnPaintChatWindow(self, event):
        dc = wxPaintDC(self.appli_window)
        # draw background picture
        two_d_bitmap = ImageManager.getChatFrameWxBitmap()
        dc.DrawBitmap(two_d_bitmap, 0, 0, TRUE)

    def displayChatterList(self, event):
        self.navigator.displayChatterList()
    
    def deleteChatServiceNeighbor(self, event):
        """ delete the chat service picto of the corresponding neighbor """
        
        id=event.id
        if self.neighbor_item.has_key(id):
            self.neighbor_item[id][3] = FALSE
            # refresh the drawing
            self.toRefresh = TRUE
        
    def newChatMessage(self, event):
        sender=event.sender
        message=event.message
        self.navigator.newChatMessage(sender, message)
        
    def addChatServiceNeighbor(self, id):
        """ add the chat service picto of the corresponding neighbor """
    
        if self.neighbor_item.has_key(id):     
            self.neighbor_item[id][3] = TRUE
            # refresh the drawing
            #self.toRefresh = TRUE

    def clearChatterList(self):
        """ clear the chatters list """
        self.chattersListBox.Clear()
            
    def insertChatter(self, pseudo):    
        """ insert a new chatter in the chatters list """        
        self.chattersListBox.Append(pseudo)

    
    def deleteNeighborInChatterList(self, pseudo):
        """ delete a neighbor in the chatters list """
        pos=self.chattersListBox.FindString(pseudo)
        self.chattersListBox.Delete(pos)
        
    def addMessageInChatText(self, text_to_display):
        self.chatTextCtrl.AppendText(text_to_display)

    def OnSendMessageButton(self,event):
        """ Send a message """
        
        # check the event
        if ((event.GetId() == wxID_WXMAINFRAMESENDMESSAGEBUTTON) or (event.GetKeyCode() == WXK_RETURN)):
            # get the message in the entry
            msg = self.messageTextCtrl.GetValue()
            # send the message to the navigator
            self.navigator.sendMessage(msg)
        else:
            event.Skip()    

    def delete_entry(self):
        """ refresh entry after sending message"""

        self.messageTextCtrl.Clear()
            
