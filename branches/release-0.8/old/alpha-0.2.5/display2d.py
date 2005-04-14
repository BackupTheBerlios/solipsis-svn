#!/usr/local/bin/env python
######################################

## SOLIPSIS Copyright (C) France Telecom

## This file is part of SOLIPSIS.

##    SOLIPSIS is free software; you can redistribute it and/or modify
##    it under the terms of the GNU Lesser General Public License as published by
##    the Free Software Foundation; either version 2.1 of the License, or
##    (at your option) any later version.

##    SOLIPSIS is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU Lesser General Public License for more details.

##    You should have received a copy of the GNU Lesser General Public License
##    along with SOLIPSIS; if not, write to the Free Software
##    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

## ------------------------------------------------------------------------------
## -----                           display2d.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   This module is the display2d service.
##   It sends avatars to the neighbors and receive avatars from them.
##
## ******************************************************************************

import os, socket, time, string, re
import StringIO
from threading import Lock
from math import ceil
#import thread
from service import *

import commun

# debug module
import debug
import wxMainFrame
from wxPython.wx import *

class Display2d(Service):
    """ This service allows to transfer image and display it where the sender is in the world."""

    def __init__(self, id_service, desc_service,  host, port, my_node, navigator):
        """ initialization of display2d service."""
        Service.__init__(self, id_service, desc_service,  host, port)
        #print "Display2d initialisation (%s,%s)" %(host, port)
        # connected node
        self.my_node = my_node

        # navigator
        self.navigator = navigator

        # number of chunks and size of chunk
        self.numchunks = ''
        self.chunksize = 0

        self.lastImageSent = []

        self.chunkdict = {}
        # {[(me.id, chunkfilename)]: [data, time]}

        self.beatDict = {}
        # {[sender(id)]: [time, chunkfilename]}

        self.dictListSender = {}
        # {sender(id): list}

        # DEB SUP MCL
        #self.imageMemory = {}
        # {sender(id): image}
        # FIN SUP MCL

        self.dict_chunk_sent = {}
        # {chunkfilename: data}

        # default scale between size of image and AR
        self.sizeDefault = float(75)/float(155550461870895619133451574326843146240)

        self.dictLock = Lock()
        self.CHECKWAIT = 0.5
        
        
    def update(self,node,delta_x, delta_y):

        return 0


    def insert_service(self, node, host, port):
        """ if a node has display2d service, we insert him in our list of neighbors having this service,"""
        """ if others neighbors have yet sent images between themselves, this node has to receive them directly."""

        #print "insert display2d service (%s)" %node.id
        # insert the node in the display2d list
        self.list_neighbors[node.id] = node

        # add the display2d service associated to the node
        self.dictLock.acquire()
        #self.navigator.addDisplay2dServiceNeighbor(node.id)
        wxPostEvent(self.navigator.ihm, wxMainFrame.addDisplay2dServiceNeighborEvent(id=node.id))
        self.dictLock.release()

        # retrieve my last image sent (if I have) in order to send it again to the new neighbor who enters the display2d service
        if self.lastImageSent <> []:
            imageName = self.lastImageSent[0]
            #print "imageName=[%s]" %imageName
            try:
                f = open(imageName, 'rb')

            except (OSError, IOError),e:
                print e
                print "can't open the file"

            # Split the file in chunks
            # get the size file
            fileSize = os.path.getsize(imageName)

            # Get size of each chunk
            self.numchunks = ceil(float(fileSize)/900)
            self.numchunks = int(self.numchunks)
            self.chunksize = int(float(fileSize)/self.numchunks)

            for chunk in range(self.numchunks):
                chunkfilename = os.path.basename(imageName) +"-"+ str(chunk+1)
                #print "chunkfilename=[%s]" %chunkfilename
                try:
                    # read this chunk
                    data = f.read(900)

                    # keep a track of the chunk sent
                    self.dict_chunk_sent[chunkfilename] = data

                    if not data: break

                    # send the chunk
                    list = ["NEWCHUNK", self.my_node.id, str(chunkfilename), str(self.numchunks), data]
                    msg = self.encodeMsg(list)
                    host, port = node.dict_service[self]
                    self.udp_socket.sendto(msg, (host, int(port)))

                except (OSError, IOError),e:
                    print e
                    continue
                except EOFError,e:
                    print e
                    break

        return 1


    def delete_service(self, node):
        """ function in order to inform a node leaves display2d service"""
        #print "display2d.delete_service(%s)" %node.id
        if not self.list_neighbors.has_key(node.id):
            #print "ERROR, this neighbor %s is not in the list" %node.pseudo
            return 0

        else:

            # remove id's node from list of neighbors having this service
            del self.list_neighbors[node.id]
            # delete the neighbor's image in the 2D View screen
            self.dictLock.acquire()
            #self.navigator.deleteDisplay2dServiceNeighbor(node.id)
            #self.navigator.deleteImage(node.id)
            wxPostEvent(self.navigator.ihm, wxMainFrame.deleteDisplay2dServiceNeighborEvent(id=node.id))
            wxPostEvent(self.navigator.ihm, wxMainFrame.deleteImageEvent(id=node.id))
            self.dictLock.release()

        return 1



    def sendImage(self, filename):
        """ Send my image to all neighbors having this service """

        #print "sendImage(%s)" %filename
        try:
            f = open(filename, 'rb')
        except (OSError, IOError),e:
            print e
            print "can't open the file"
            return 0


        # Split the file in chunks
        # get the size file
        fileSize = os.path.getsize(filename)

        # Get size of each chunk
        self.numchunks = ceil(float(fileSize)/900)
        self.numchunks = int(self.numchunks)
        self.chunksize = int(float(fileSize)/self.numchunks)
        #print "numchunks=[%d]" %self.numchunks
        #print "chunksize=[%d]" %self.chunksize
        for chunk in range(self.numchunks):
            #chunkfilename = filename +"-"+ str(chunk+1)
            chunkfilename = os.path.basename(filename) +"-"+ str(chunk+1)
            #print "chunkfilename=[%s]" %chunkfilename

            try:
                # read this chunk
                data = f.read(900)

                # keep a track of the chunk sent
                self.dict_chunk_sent[chunkfilename] = data

                if not data: break

                # send the chunk
                list = ["NEWCHUNK", self.my_node.id, str(chunkfilename), str(self.numchunks), data]
                msg_to_send = self.encodeMsg(list)
                for neighbors in self.list_neighbors.values():
                    host, port = neighbors.dict_service[self]
                    self.udp_socket.sendto(msg_to_send,(host, int(port)))

            except (OSError, IOError),e:
                print e
                continue

            except EOFError,e:
                print e
                break

        self.lastImageSent = [filename]
        f.close()
        return 1

    def run(self):
        """ Receive images. A timeout is swithching between 'receive' mode and 'watch' mode so if no message arrives,"""
        """ timeout switch in 'watch' mode in order to see when the last chunk of image has been received """
        """ and if the last chunk has been received since a long time either all chunks af image have been received or one or more chunk have been lost"""
        """ in case all chunks have been received, we reconstitute the image"""
        """ in case some chunks have been lost, we send a request in order to pick up chunks missing from the sender of image"""

        self.alive = 1

        while self.alive:
            try:
                # we put in place the time out
                #self.udp_socket.settimeout(0.01)
                time.sleep(0.1)
                self.watch()
                self.udp_socket.setblocking(0)
                # if time < settimeout, a message is received
                data, addr = self.udp_socket.recvfrom(1024)
                #debug.debug_info("receive data:[%s]" %data)

                if not data: break

                else:

                    # we decode the message
                    msg = self.decodeMsg(data, 4)

                    # a new chunk is received
                    if msg[0] == "NEWCHUNK":

                        # get the id,
                        # the name of chunk (in order to know the number of chunk),
                        # number of all chunks(in order to check if all chunks have been received)
                        # data of image
                        sender = msg[1]
                        chunkfilename = msg[2]
                        number_of_chunk_to_send = msg[3]
                        data = msg[4]

                        # in order to know when the last chunk arrived
                        self.lastArrival(sender, chunkfilename)

                        # we sort this chunk in his list of chunks received
                        # so we retrieve the sender of this chunk, we check if this sender has ever sent a chunk, if yes, we retrieve the list of chunks received by this sender
                        self.dictLock.acquire()
                        if self.chunkdict <> {}:
                            # so, I have ever received chunks
                            chunkfile_present = []

                            # check up if I have ever received chunks from THIS sender
                            for key in self.chunkdict.keys():
                                chunkfile_present.append(key[0])

                                if sender in chunkfile_present:
                                    # yes I have ever received chunks from this sender, I have to retrieve his list.

                                    if chunkfilename not in self.dictListSender[sender]:
                                        # insert this chunk in chunk list of this sender
                                        self.dictListSender[sender].append(chunkfilename)
                                        # get in memory data of this chunk
                                        self.chunkdict[(sender, chunkfilename)] = data

                                else:
                                    # it's the first chunk of this sender, create a list for this sender
                                    self.dictListSender[sender] = []
                                    # and update it with firts, number of all chunk of image and then with this chunk
                                    self.dictListSender[sender].append(number_of_chunk_to_send)
                                    self.dictListSender[sender].append(chunkfilename)
                                    # get in memory data of this chunk
                                    self.chunkdict[(sender, chunkfilename)] = data

                        else:
                            # I have never received chunks...
                            self.chunkdict[(sender, chunkfilename)] = data
                            self.dictListSender[sender] = []
                            self.dictListSender[sender].append(number_of_chunk_to_send)
                            self.dictListSender[sender].append(chunkfilename)

                        self.dictLock.release()



                    # message in order to inform chunks missing
                    if msg[0] == "MISSINGCHUNK":

                        self.dictLock.acquire()

                        # get the list of all chunks missing (string data)
                        list_missing = msg[2]

                        # convert string data in list
                        data_chunk = self.combineList(list_missing)
                        asker_id = msg[1]
                        totalChunk = msg[3]

                        # retrieve chunks missing in dict_chunk_sent and send them again
                        for chunk_missing in data_chunk:
                            data = self.dict_chunk_sent[chunk_missing]
                            list = ["NEWCHUNK", self.my_node.id, str(chunk_missing), str(totalChunk), str(data)]
                            msg = self.encodeMsg(list)
                            sender_object = self.list_neighbors[asker_id]
                            host, port = sender_object.dict_service[self]
                            self.udp_socket.sendto(msg, (host, int(port)))

                        self.dictLock.release()


                    # message indicating all chunks of an image have been received
                    if msg[0] == "ACKNOWLEDGEMENT":

                        filename = msg[1]
                        self.dict_chunk_sent.clear()


                    # message from sender sending a request in order to delete his image from display2d
                    if msg[0] == "DELETE_IMAGE":

                        sender_id = msg[1]
                        sender_object = self.list_neighbors[sender_id]

            #except socket.timeout:
            #    self.watch()
            except:
                pass

        debug.debug_info("End of Display2d service ...")


    def watch(self):    
        """ watching if a chunk has been received since a long time, a way to check chunk lost"""
        #debug.debug_info("display2d.watch()")
        # get the list of chunks received since a long time
        silent = self.extractSilent(self.CHECKWAIT)

        # if a chunk has been received since a long time
        if silent:
            self.dictLock.acquire()
            for i in silent:
                # get information about this chunk(sender, number of this chunk, name of image)
                sender = i[0]
                chunkfilename = i[1]
                hyphen = chunkfilename.find("-")
                filename = chunkfilename[:hyphen]
                if self.list_neighbors.has_key(sender):
                    object_sender = self.list_neighbors[sender]

                    # get the list of chunks of this sender
                    chunklist = self.dictListSender[sender]

                    # create a list in order to sort chunks missing
                    list_number = []

                    # get the number of the chunkfile (because chunklist == [filename - number)]
                    for chunk in chunklist[1:]:
                        number_chunk = string.splitfields(chunk, "-", 1)[1]
                        chunklist.remove(chunk)
                        list_number.append(number_chunk)

                    # sort listnumber
                    list_number_sorted = self.sortStr(list_number)

                    # reconstitute the list of chunk_missing in the order (because list_number_sorted == 1, 2, 3........)
                    for number in list_number_sorted:
                        chunkfile = filename +"-"+ number
                        chunklist.append(chunkfile)

                    # get total number of chunks that should be received
                    totalChunk = int(chunklist[0])

                    if len(chunklist) == totalChunk +1:
                        # we have all chunks
                        data = ""
                        for chunk in chunklist[1:]:
                            data += self.chunkdict[(sender, chunk)]
                            del self.chunkdict[(sender,chunk)]

                        # create a file to save image
                        filename = str(commun.AVATAR_DIR_NAME) + os.sep + object_sender.pseudo + "_" + filename
                        imgfile = file(filename, "wb")
                        imgfile.write(data)
                        imgfile.close()

                        # resize the avatar image
                        resizeFile = commun.chgSize(filename)

                        # display image in the 2D View screen
                        #self.navigator.receiveImage(sender, resizeFile)
                        wxPostEvent(self.navigator.ihm, wxMainFrame.receiveImageEvent(sender=sender, image_name=resizeFile))

                        # we remove the sender from the list "silent"
                        silent.remove((sender, self.beatDict[sender][1]))

                        # we remove sender from all dictionaries
                        del self.dictListSender[sender]
                        del self.beatDict[sender]

                        # send acknowledgement in order to inform we have received all chunks
                        list = ["ACKNOWLEDGEMENT", str(filename)]
                        msg = self.encodeMsg(list)
                        host, port = object_sender.dict_service[self]
                        self.udp_socket.sendto(msg, (host, int(port)))

                    else:
                        # chunks miss
                        # retrieve the chunks missing (number...)
                        missing_list = []

                        for chunk_number in list_number_sorted:
                            if chunk_number in list_number_sorted[1:-1]:
                                chunk_index = list_number_sorted.index(chunk_number)
                                previous_value = int(list_number_sorted[chunk_index-1])
                                if int(chunk_number) <> previous_value+1:
                                    self.retrieveChunkMiss(missing_list, previous_value, int(chunk_number) - 1, filename)

                            if chunk_number == list_number_sorted[0]:
                                if int(chunk_number) <> 1:
                                    self.retrieveChunkMiss(missing_list, int(0), int(chunk_number) - 1, filename)


                            if chunk_number == list_number_sorted[-1]:
                                if int(chunk_number) <> totalChunk:
                                    self.retrieveChunkMiss(missing_list, int(chunk_number), int(totalChunk), filename)


                        # send the list of name of chunks missing
                        list = ["MISSINGCHUNK", self.my_node.id, str(missing_list), str(totalChunk)]
                        msg = self.encodeMsg(list)
                        host, port = object_sender.dict_service[self]
                        self.udp_socket.sendto(msg, (host, int(port)))

                        # delete the last chunk received since a long time in order to watch the new chunks received since the missingchunk request
                        del self.beatDict[sender]


            self.dictLock.release()


    def retrieveChunkMiss(self, missing_list, value_comp, last_value, filename):
        """ retrieve the chunks missing from the lsit of chunks received"""

        number_missing = int(value_comp + 1)
        chunk_missing = filename +"-"+ str(number_missing)
        missing_list.append(chunk_missing)
        while number_missing <> last_value:
            number_missing = number_missing + 1
            chunk_missing = filename +"-"+ str(number_missing)
            missing_list.append(chunk_missing)


    def sortStr(self, seq, func=(lambda x,y: int(x) <= int(y))):
        """ sort strings in from list in growing order"""

        res = seq[:0]
        for j in range(len(seq)):
            i = 0
            for y in res:
                if func(seq[j], y): break
                i = i+1
            res = res[:i] + seq[j:j+1] + res[i:]
        return res


    def combineList(self, string_list):
        """ convert string in item of a list"""

        list_missing = []
        string_list = string_list[:-1]
        string_chunk = string.splitfields(string_list, ",")
        for chunk_str in string_chunk:
            chunk_missing = chunk_str[2:-1]
            list_missing.append(chunk_missing)

        return list_missing


    def deleteMyImage(self):
        """ Send message in order to delete my image"""

        list = ["DELETE_IMAGE", self.my_node.id]
        msg_to_send = self.encodeMsg(list)
        for friend_object in self.list_neighbors.values():
            host, port = friend_object.dict_service[self]
            self.udp_socket.sendto(msg_to_send,(host, int(port)))

        return 1

    def lastArrival(self, entry, chunkfilename):
        """Create or update a dictionary entry"""
        self.dictLock.acquire()
        self.beatDict[entry] = [time.time(), chunkfilename]
        self.dictLock.release()


    def extractSilent(self, howPast):
        """Returns a list of entries older than howPast"""

        silent = []
        when = time.time() - howPast
        self.dictLock.acquire()
        if self.beatDict <> {}:
            for sender in self.beatDict.keys():
                if self.beatDict[sender][0] < when:
                    silent.append((sender, self.beatDict[sender][1]))

        self.dictLock.release()
        return silent


    def encodeMsg(self, list):
        """ encode list of string list and return a string"""
        return string.joinfields(list, ";")


    def decodeMsg(self, msg, maxlist):
        """ decode message msg and return a list of params"""
        return string.splitfields(msg, ";", maxlist)
