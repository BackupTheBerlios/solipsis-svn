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
## -----                           List.py                                  -----
## ------------------------------------------------------------------------------

## ******************************************************************************
##
##   In this module, we define a generic class for List of entity
##   We provide all methods for inserting, removing and sorting quickly any entity
##   Then, we define two lists :
##   - the list of entities sorted by counterclockwise around self
##   - the list of entities sorted by distance to self.
##
## ******************************************************************************

import math

#################################################################################################
#                                                                                               #
#				------- Generic List ---------					#
#                                                                                               #
#################################################################################################
class GenericList:

    def ins(self, entity):
        """ insert entity in the list"""

        self.ll.insert(self.dichotomy(entity), entity)
        self.length += 1
    
    def dichotomy(self, entity):
        """ return the index at which the element entity may be inserted using dichotomic scheme """

        start = 0
        end = self.length
        while start < end :
            i = (start + end)>>1 # (start + end)/2
            pivot = self.ll[i]
            if self.cmpFunc(pivot, entity) > 0: # pivot > entity
                end = i
            else:
                start = i+1

        return start

    def delete(self, entity):
        """ delete entity from the list"""

        if self.ll.count(entity) <> 0:
            self.ll.remove(entity)
            self.length -= 1

    def update(self, p):
        """ update list when self.p moves"""

        self.ll.sort(self.cmpFunc)

##        # the list is almost ordered, so use Bubble sort algorithm
##        start = 0
##        end = self.length-1
##        if end > 0:
##            changed = 1
##            while changed and start < end:
##                for i in range(start, end):
##                    changed = 0
                
##                    if self.cmpFunc(self.ll[i], self.ll[i+1]): # i+1 is before i
##                        self.ll[i], self.ll[i+1] = self.ll[i+1], self.ll[i]
##                        changed = 1
##                    if self.cmpFunc(self.ll[end-i-1], self.ll[end-i]): # end-i is before end-i-1
##                        self.ll[end-i-1], self.ll[end-i] = self.ll[end-i], self.ll[end-i-1]
##                        changed = 1
          
##                start += 1
##                end -= 1

            
    def replace(self, entity):
        """ replace, if required, a moving entity in the list"""

        i = self.ll.index(entity)
        down, up = 0, 0 # boolean variables to indicate that the entity has moved, either up or down
        k = 1
        while i-k <> -1 and self.cmpFunc(self.ll[i-k], self.ll[i]) > 0: # i is before i-1, i-2, ...
            k += 1
            down = 1
           
        if not down:
            while i+k <> self.length and self.cmpFunc(self.ll[i], self.ll[i+k]) > 0: # i+1, i+2... is before i
                k += 1
                up = 1
                
        # replace the entity if its position was not well
        if down:
            if i-k == -1:
                self.ll.pop(i)
                self.ll.insert(0,entity)
            else:
                self.ll.pop(i)
                self.ll.insert(i-k+1, entity)
        elif up:
            if i+k == self.length:
                self.ll.append(entity)
                self.ll.pop(i)
            else:
                self.ll.insert(i+k, entity)
                self.ll.pop(i)


class CcwList(GenericList):
    """ entities sorted counterclockwise"""

    def __init__(self):

        # the list
        self.ll = []

        # length of the list
        self.length = 0

        # comparaison function
        self.cmpFunc = ccwOrder

    def filterList(self, sector):
        """ create a list from entities in ll and in sector"""

        i = self.dichotomy(sector.startEnt) 
        j = self.dichotomy(sector.endEnt)
        
        if i <= j :
            result = self.ll[i:j]
        else:
            result = self.ll[i:]+self.ll[:j]
            
        return result

    def checkGlobalConnectivity(self):
        """ check if global connectivity is ensured

        return a list of pair of entities not respecting property"""
        result = []

        # three or more entities,
        if self.length > 3:
	  for index in range(self.length-1) :
	    ent = self.ll[index]
	    next_ent = self.ll[ (index+1) % self.length ]
	    if not inHalfPlane(ent.local_position, [0,0], next_ent.local_position) :
	      result.append( [ ent, next_ent ] )
	
	return result      
	

#################################################
#		   DistList		        #
#################################################

class DistList(GenericList):
    """ entities sorted by distance criteria"""
    
    def __init__(self):

        # the list
        self.ll = []

        # length of the list
        self.length = 0

        # compraison function
        self.cmpFunc = distOrder

    def closer_to_d(self,d):
      """ return number of entities closer than distance d"""  
      result = 0
      while result < self.length and distance( self.ll[result].local_position, [0,0] ) < d :
	result += 1

      return result
    
#################################################
#		   distOrder		        #
#################################################
def distOrder(x, y):
  """ return positive if entity y is closer to position pos than entity x"""

  dist_y = distance(y.local_position, [0,0])
  dist_x = distance(x.local_position, [0,0])

  if dist_y < dist_x:
      return 1
  
  elif dist_y == dist_x:
      return 0
  
  else:
      return -1

#################################################
#		    ccwOrder		        #
#################################################
def ccwOrder(x, y):
  """ return positive if entity y is before entity x in ccw order relation to position pos"""

  # verify that they lie in the same half-plane (up or down to pos)
  upX = x.local_position[1] <= 0
  upY = y.local_position[1] <= 0

  if upX <> upY:
    # they do not lie to the same half-plane, y is before x if y is up
    result = upY
  else:
    # they lie in the same plane, compute the determinant and check the sign
    result = not inHalfPlane(x.local_position, [0,0], y.local_position)

  if result:
      return 1
  else:
      return -1

#################################################
#                  distance                     #
#################################################
def distance(p1, p2):
  """ compute euclidean distance for the minimal geodesic between two positions p1 and p2"""

  return long(math.hypot( p1[0]-p2[0], p1[1]-p2[1] ))

#################################################
#                  inHalfPlane                  #
#################################################
def inHalfPlane(p1, p2, pos):
  """ compute if pos belongs to half-plane delimited by (p1, p2)
  p2 is the central point for ccw
  return boolean TRUE if pos belongs to half-plane"""

  return (pos[0]-p1[0])*(p1[1]-p2[1]) + (pos[1]-p1[1])*(p2[0]-p1[0]) > 0
