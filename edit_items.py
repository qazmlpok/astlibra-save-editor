from Common import *
from Items import *

#Saves are stored in %APPDATA%\..\Local\ASTLIBRA\SAVE
#But also in \Steam\userdata\<userid>\1718570\remote

# I am too lazy to make any kind of GUI or even a console menu.
# This is part two of a two part script for editing items.
# This script will edit the items in the CSV file generated by the companion script,
# list_items.py. Enter the value in the "new" column and run it; it will set the item quantity to that value
# Locked items can be unlocked by putting in any integer, including 0. This will cause them to appear
# in the book.

# The output file name is always "item_data.csv". No checking is done to make sure it's safe to overwrite the file.

if len(sys.argv) == 1:
    print(f"USAGE: edit_items.py <full path to save file>")
    exit()

#Read in the save file...
fname = sys.argv[1]
Globals.set_is_dlc(fname)
with open(fname, 'rb') as f:
    fdata = bytearray(f.read())

srcfilename = 'item_data.csv'
outfilename = os.path.splitext(fname)[0] + '_edit.DAT'

items = Items(fdata)

headers = [
    'Id',           #Id of the item. In hex just to be consistent with the spreadsheet.
    'Name',         #Name of the item. Not read by the script, only for convenience.
    'Count',        #Current count, or "Locked" if the item is still unknown (which implies 0 count)
    'New Count',    #Always left blank; fill this in for edit_items to consume.
]

editdata = open_spreadsheet(srcfilename)
for i in editdata:
    row = editdata[i]
    item = items.ById(i)
    #print(item)
    if row['New Count'] is None or row['New Count'] == '':
        continue
    
    count = row['New Count']
    if count.casefold() == 'Locked'.casefold():
        #There is no reason to lock an item, but allow it.
        item.SetCount(0)
        item.unlock = 0
        print(f"Locking item {item.name}")
    else:
        count = int(count)
        print(f"Changing count for item {item.name} from '{item.count}' to '{count}'")
        item.SetCount(count)
items.Write(fdata)
WriteToDisk(fdata, outfilename)
    