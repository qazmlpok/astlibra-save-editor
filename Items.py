import sys, os
import zlib

from Common import *

class Items(DataBase):
    """ Container class for item data
    This is all consumables, key items, etc. Not equipment.
    """
    base_addr = 0x12CC
    unlock_addr = 0x220C
    def __init__(self, filedata):
        #Load from spreadsheet - so this doesn't actually require save data. Should it be completely separate?
        #All of the "_lock" items are locked on my endgame save, with the Egghead achievement. So they almost certainly do not exist.
        item_data = open_spreadsheet('Data/items.csv')
        self.item_data = {}
        
        #Turn each item into 2 fields, which get loaded in init.
        for id in item_data:
            item = Item(filedata, item_data[id])
            self.item_data[id] = item
        super().__init__(filedata)
    def GetFields(self):
        for id in self.item_data:
            item = self.item_data[id]
            yield from item.GetFields()
    def Print(self):
        for id in self.item_data:
            item = self.item_data[id]
            count = item.count
            unlock = item.unlock
            unlock = '' if unlock == 1 else ' (locked)'
            print(f"{item.name}: {count}{unlock}")
    #TODO: Ideally, all of these can be combined, e.g. "Get all items with this karma ability"
    # "that have a quantity of at least 1". Since you can't use them if you don't have them.
    # I don't know if these should be done as set operations or lambda functions.
    #Since the data isn't available, there's no point in figuring it out now.
    def search(self, text):
        """ Return a collection of matching items
        TODO: Make sure there aren't any duplicates. e.g. Battery.
        """
        pass
    def ById(self, id):
        if id == 0:
            return None
        return self.item_data[id]
    def GetByKarma(self, target):
        """ Return all items with a specific Karma value. Useful for LIBRA balancing
        ...Which requires Karma info, which isn't available.
        """
        pass
    def GetByAbility(self, target):
        """ Return all items with a specific Karma ability. Useful for LIBRA planning.
        ...Which requires Karma info, which isn't available.
        """
        pass
    def GetNameFromId(self, id):
        """ Use this when getting the name for an item, since it accounts for 0s.
        """
        if id == 0:
            return 'None'
        return self.item_data[id].name
    def GetAvailable(self):
        """ Items with a quantity of at least 1.
        """
        pass

class Item(DataBase):
    """ A single item. Represents a record in the spreadsheet, plus a counter from the save file.
    TODO: The spreadsheet should include a lot more fields, such as:
    jpn name
    karma
    karma abilities
    Type (e.g. consumable, force item, key item)
    Chapter available
    """
    def __init__(self, filedata, row):
        self.id = row['Id']
        self.name = row['Name']
        #Will need to add the other fields. Or just the entire row.
        self.fields = [
            Field('count', Items.base_addr + self.id * 4, 4),
            Field('unlock', Items.unlock_addr + self.id, 1)
        ]
        self.weight = 0
        self.chapter = 0
        self.karma = []
        self.type = ''
        super().__init__(filedata)
    def SetCount(self, val):
        self.count = val
        if val > 0:
            self.unlock = 1
        #No real point locking an item
    def SetCountIfBelow(self, val):
        if val > self.count:
            self.SetCount(val)
    
class ItemCollection():
    """ A collection of items that can be acted on at once.
    Intent is to allow searching for related items, e.g. all mats from chapter 1,
    and giving yourself 9 of them at once.
    """
    def __init__(self):
        self.selection = set()
    #TODO: Add the Add/Subtract set methods.
    def SetCount(self, val):
        """ Modify the count of every item in this collection.
        """
        for item in self.Contents():
            item.SetCount(val)
    def SetCountIfBelow(self, val):
        """ Modify the count of every item in this collection, but only if it is already below the
        given value. (i.e. only add items, never remove them)
        """
        for item in self.Contents():
            item.SetCountIfBelow(val)
    def Contents(self):
        #Can't iterate a set. Bleh.
        l = list(self.selection)
        return l
    