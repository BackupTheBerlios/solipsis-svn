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
"""Plugin profile: allow users to define a set of personal information
and exchange it with other peers"""

import wx

def get_all_item_ids(list):
    items = []
    item_id = -1
    while True:
        item_id = list.GetNextItem(item_id)
        if item_id == -1:
            break
        else:
            items.append(item_id)
    return items

def get_item_id_by_label(list, label, column=0):
    item_id = list.GetNextItem(-1)
    while item_id != -1:
        if list.GetItem(item_id, column).GetText() == label:
            return item_id
        else:
            item_id = list.GetNextItem(item_id)
    raise KeyError(label + "not found in list")

def get_selected_item_ids(list):
    items = []
    item_id = -1
    while True:
        item_id = list.GetNextItem(item_id, state=wx.LIST_STATE_SELECTED)
        if item_id == -1:
            break
        else:
            items.append(item_id)
    return items

def get_all_items(list, column=0):
    items = get_all_item_ids(list)
    return [list.GetItem(item_id, column) for item_id in items]

def get_all_labels(list, column=0):
    items = get_all_item_ids(list)
    return [list.GetItem(item_id, column).GetText() for item_id in items]

def get_selected_labels(list, column=0):
    items = get_selected_item_ids(list)
    return [list.GetItem(item_id, column).GetText() for item_id in items]

def get_new_label(list, prefix="item_"):
    existing =  get_all_labels(list)
    item = 0
    while prefix + str(item) in existing:
        item += 1
    return prefix + str(item)
