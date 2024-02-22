import sys, os

from Common import *
from Items import *

#Saves are stored in %APPDATA%\..\Local\ASTLIBRA\SAVE
#But also in \Steam\userdata\<userid>\1718570\remote

class Equipment(DataBase):
    """ Abstract base class for the 4 types of equipment, since they share most logic.
    """
class Weapon(Equipment):
    """
    """
    def __init__(self, filedata):
        self.fields = []
        super().__init__(filedata)
    #Equipment EXP:
    #Final weapon appears to be 2a04
    #Presumably all weapons are adjacent.
    #Maxed items are showing as FFFFFFB3
    #Just setting it to xxxxFF00 is enough to master it on the next kill
    #I'm pretty sure every item has a different exp requirement.
    purchased = 0x96C
class Shield(Equipment):
    """
    """
    def __init__(self, filedata):
        self.fields = []
        super().__init__(filedata)
    purchased = 0xAFC
class Armor(Equipment):
    """
    """
    def __init__(self, filedata):
        self.fields = []
        super().__init__(filedata)
    purchased = 0xBC4
class Accessory(Equipment):
    """
    """
    def __init__(self, filedata):
        self.fields = []
        super().__init__(filedata)
    
    #There's multiple slots. And the number is a variable.
    equipped = 0x737C
    purchased = 0xCA0 #Incorrect, but I don't have acc ids.

class Character(DataBase):
    """ Character data
    """
    def __init__(self, filedata):
        #self.exp = 
        self.fields = [
            Field('weapon',         0x7364, 4),
            Field('shield',         0x7368, 4),
            Field('armor',          0x736C, 4),
            Field('level',          0x7370, 4),
            Field('exp',            0x7390, 4), #only for current level
            Field('gold',           0x7394, 4),
        ]
        if (Globals.is_dlc):
            #These were set to "1" for a non-DLC save I tried. I have no idea if they're used for anything.
            self.fields.extend([
                Field('style',          0x20d6, 1),
                Field('substyle',       0x20d7, 1),
            ])
        #Currently available force
        self.fields.extend(Globals.array_to_field(Globals.force, 0x73b4, 4, 'force'))
        #Level-up stat allocations
        #DLC: These are all 0. The level-up change might mean they're stored separately now...
        self.fields.extend(Globals.array_to_field(Globals.stats, 0x1168, 4, 'stat'))
        
        #The force grid is around 0x374f. I'm not going to try to decode that.
        
        super().__init__(filedata)

class Partners(DataBase):
    """ Your current partner. Presumably it's possible to do weird stuff like use Kai in chapter 1
    I haven't tried.
    """
    def __init__(self, filedata):
        names = [
            'None',
            'Polin',
            'Gau'
            'Shiro',
            'Kuro',
            'Kai',
            'Sheero'
        ]
        self.partners = {i : names[i] for i in range(len(names))}
        self.ids = {names[i] : i for i in range(len(names))}
        
        self.fields = [
            Field('partner',      0x2728, 4),
            Field('partner_save', 0x2728, 4),   #I _think_ this is duplicated for the save preview.
            #The order here is odd - Kuro appears before Shiro, but not in IDs.
            Field('polin_exp',    0x30FC, 4),
            Field('gau_exp',      0x3100, 4),
            Field('kuro_exp',     0x3104, 4),    #Guess - I already maxed her. But only this addr makes sense.
            Field('shiro_exp',    0x3108, 4),
            Field('kai_exp',      0x310C, 4),
            Field('polin_collect',0x21F8, 1),
            Field('gau_collect',  0x21F9, 1),
            Field('kuro_collect', 0x21FA, 1),    #Guess - I already maxed her. But only this addr makes sense.
            Field('shiro_collect',0x21FB, 1),
            Field('kai_collect',  0x21FC, 1),
        ]
        
        #Shiro and Sheero definitely share xp.
        #Polin: 21f8
        #Gau collect: 21f9
        #Kuro: 21FA (guess)
        #Shiro Collected: 0x21FB?
        #Kai: 21fc
        
        super().__init__(filedata)
    def SetXp(self, partner=None, val=None):
        if partner is None:
            for i in self.partners:
                p = self.partners[i]
                self.SetXp(p, val)
            return
        if partner == 'None':
            return
        if partner == 'Sheero':
            partner = 'Shiro'
        #TODO: Block if collected 2 Love already
        col = getattr(self, f'{partner.lower()}_collect')
        if col >= 2:
            return
        if val is None or val > 0x70:
            #I'm not positive this is the maximum, but it is enough to grant love.
            val = 0x70
        setattr(self, f'{partner.lower()}_exp', val)
    def SetPartner(self, partner=None):
        if partner is None:
            partner = 'None'
        id = self.ids[partner]
        self.partner = id

class Libra(DataBase):
    """ Current LIBRA items.
    Pans are left to right, i.e. left_0 is the leftmost item in the left side of the scale
    right_0 is the leftmost item in the right side
    """
    def __init__(self, filedata, items):
        self.items = items
        #Main libra
        left_start = 0x91c
        #Set 1 is at 0x7dc; set 5 at 0x87c
        set_start = 0x7dc
        self.max_pans = 5
        right_start = left_start + self.max_pans*4
        self.fields = []
        for i in range(self.max_pans):
            self.fields.append(Field(f'left_{i}', left_start + i*4, 4))
            self.fields.append(Field(f'right_{i}', right_start + i*4, 4))
        
        for j in range(5):
            prefix = f'set_{j+1}'
            left_start = set_start + j * self.max_pans * 2 * 4
            right_start = left_start + self.max_pans*4
            for i in range(self.max_pans):
                self.fields.append(Field(f'{prefix}_left_{i}', left_start + i*4, 4))
                self.fields.append(Field(f'{prefix}_right_{i}', right_start + i*4, 4))
        #Looks a bit nicer this way.
        self.fields.sort(key=lambda x: x.position)
        super().__init__(filedata)
    def Balance(self):
        """ Attempt to balance the current Libra configuration. Reads in the current items,
        tries to find an arrangement where the scales are balanced.
        This may not exist. It's also not intelligent, and just brute-forces the solution.
        If there is exactly 1 empty slot, it will search for an available item with the exact missing weight
        and use that.
        """
        #All of this requires karma data, of course. 
        #Since it doesn't work, I haven't actually tested this code.
        scales = self.items.search('Scale Pan')[0]
        if scales.count < 2:
            return
        items = []
        for i in range((scales.count + 1)//2):
            item = getattr(self, f'left_{i}')
            items.append(self.items.ById(item))
        for i in range((scales.count + 0)//2):
            item = getattr(self, f'right_{i}')
            items.append(self.items.ById(item))
        real_items = list(filter(lambda x: x is not None, items))
        if len(real_items) == len(items) - 1:
            #Insert logic to find good configurations, using a chosen counterweight
            pass
        elif len(real_items) == len(items):
            #Try to balance the scales. There may not be a way to do this.
            total = sum(map(lambda x: x.weight, items))
            target = total // 2
            combs = itertools.combinations(items, scales.count//2)
            for c in combs:
                s = sum(map(lambda x: x.weight, c))
                #This will always produce multiple identical results which should be filtered.
                #I also haven't tested this with fewer than 10 scales.
                #The general approach should be fine, however.
                if s == target:
                    print(c)
        else:
            #The problem with trying to balance multiple empty slots is that you need to figure out
            #what abilities the user values
            raise Exception("Current LIBRA configuration should have at most 1 empty slot.")
    def Print(self):
        for f in self.fields:
            #TODO: Nicer names.
            name = f.field_name
            val = getattr(self, name)
            itemname = self.items.GetNameFromId(val)
            print(f"{name}: {itemname} ({val:02X})")

class QuickInventory(DataBase):
    """ This mostly just exists to make it easier to grab items.
    And for completeness
    """
    #Other inventory stuff: 0x2d2c and around there appears to be an array of the last-selected
    #item tabs. I haven't bothered to decode exactly how it works.
    def __init__(self, filedata, items):
        self.items = items
        inv_count = 6
        top_start = 0x8A8   #Consumables
        bottom_start = 0x8C0   #Weapons/tools
        self.fields = []
        for i in range(inv_count):
            self.fields.append(Field(f'a_{i}', top_start + i*4, 4))
            self.fields.append(Field(f'b_{i}', bottom_start + i*4, 4))
        self.fields.sort(key=lambda x: x.position)
        super().__init__(filedata)
    def Print(self):
        for f in self.fields:
            #TODO: Nicer names.
            name = f.field_name
            val = getattr(self, name)
            itemname = self.items.GetNameFromId(val)
            print(f"{name}: {itemname} ({val:02X})")
    def Write(self):
        #do nothing
        pass

class Karon(DataBase):
    """ Data class for current KARON skills. Except I haven't done much with these, so I only know a few.
    """
    #0x608 (Magical Vision)
    #0x634 (The Third Eye)
    #0x610 (Dash)
    #0x6c0 (Aegis)
    pass
    
class Arena(DataBase):
    """ Arena unlock flags
    """
    pass
    def __init__(self, filedata):
        self.fields = [Field(f'Chapter {i+1}', 0x203f + i, 1) for i in range(9)]
        super().__init__(filedata)
    def Write(self, srcdata):
        #Do nothing
        pass
    def Print(self):
        for f in self.GetFields():
            name = f.field_name
            val = getattr(self, name)
            sep = ['0' if val & (1<<i) == 0 else '1' for i in range(5)]
            #I have no idea what a good display for this would be.
            #I'm also not positive which bit is which (I'm guessing 0x01 is the first entry)
            #but I also don't care enough to find out.
            print(f"{name}: {' - '.join(sep)}")

class Record(DataBase):
    """ Stuff from the battle record. Miscellaneous details.
    Mostly useless since it's in-game, but works as a POC.
    """
    
    def __init__(self, filedata):
        self.fields = [
            Field('exp',            0x2728, 4),
            Field('coins',          0x272C, 4),
            Field('steps',          0x2730, 4),
            Field('hits',           0x2734, 4),
            Field('dashes',         0x2738, 4),
            Field('jumps',          0x273C, 4),
            Field('backstep',       0x2740, 4),
            Field('shield_charge',  0x2744, 4),
            Field('counter_bash',   0x2748, 4),
            Field('possessions',    0x274C, 4),
            #After this might be the individual possession uses, but the numbers don't quite match up.
            Field('sale',           0x27BC, 4),
            Field('purchase',       0x27C0, 4),
            Field('item_use',       0x27C4, 4),
            Field('max_damage',     0x27C8, 4),
            Field('throw_items',    0x27CC, 4),
            Field('stat_items',     0x27D0, 4),
            Field('enemy_defeats',  0x27D4, 4),
            Field('saves',          0x27D8, 4),
            Field('equipment_short',0x27DC, 4),
            Field('equipment_standard', 0x27E0, 4),
            Field('equipment_long', 0x27E4, 4),
            Field('partner_damage', 0x27E8, 4),
            Field('total_force',    0x27EC, 4),
            #0x27F0-0x2804: individual total force
            #These do not match the order in the book.
            Field('max_combo',      0x2808, 4),
            Field('guard_breaks',   0x280C, 4), #Maybe. I have a low number.
            Field('abnormal',       0x2810, 4),
            Field('poison',         0x2814, 4),
            Field('bleed',          0x2818, 4),
            Field('blind',          0x281C, 4),
            Field('paralysis',      0x2820, 4),
            Field('petrification',  0x2824, 4),
            Field('damage_taken',   0x2828, 4),
            Field('weakness_hits',  0x282C, 4),
            Field('resisted_hits',  0x2830, 4),
            Field('crit_hits',      0x2834, 4),
        ]
        
        self.fields.extend(Globals.array_to_field(Globals.force, 0x27F0, 4, 'total'))
        super().__init__(filedata)

#DLC only.
class Style(DataBase):
    pass
    #Current style is at 0x20d6; substyle 0x20d7 (Character)
    #Unlock flag _might_ be around 0x1930. That was Dancer.
    #Each style can have up to 3 boards, which have their own selections...
    #and an XP bar per style.
    #But these would be a pain to deal with.

def add_force(val, color = None):
    assert val > 0
    if color is None:
        for f in Globals.force:
            add_force(val, f)
        return
    if color.lower() in Globals.force_colors:
        color = Globals.force_colors[color.lower()]
    color = color.lower()
    curr = getattr(chara, f'force_{color}')
    setattr(chara, f'force_{color}', curr + val)
    #Record tracking; combined and individual.
    curr = getattr(stats, f'total_force')
    setattr(stats, f'total_force', curr + val)
    curr = getattr(stats, f'total_{color}')
    setattr(stats, f'total_{color}', curr + val)
    

if len(sys.argv) == 1:
    print(f"USAGE: editor.py <full path to save file>")
    exit()

#Read in the save file...
fname = sys.argv[1]
Globals.set_is_dlc(fname)
with open(fname, 'rb') as f:
    fdata = bytearray(f.read())
outfilename = os.path.splitext(fname)[0] + '_edit.DAT'

stats = Record(fdata)
chara = Character(fdata)
#arena = Arena(fdata)
#stats.Print()
#chara.Print()
#arena.Print()
items = Items(fdata)
lib = Libra(fdata, items)
#lib.Print()
#items.Print()
qinv = QuickInventory(fdata, items)
#qinv.Print()
partners = Partners(fdata)
#partners.SetXp('Gau')
#partners.SetXp('Polin')
#partners.SetXp('Kai')

#add_force(50000)
chara.Print()

#misc achievements
#stats.hits = 200000
#stats.steps = 50000
#650000 total force
#stats.enemy_defeats = 15000
#stats.coins = 600000
#stats.max_combo = 1000
#stats.possessions = 3000

#Apply modifications. 
#stats.Write(fdata)
#chara.Write(fdata)
#partners.Write(fdata)



#WriteToDisk(fdata, outfilename)
