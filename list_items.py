from Common import *
from Items import *

#Saves are stored in %APPDATA%\..\Local\ASTLIBRA\SAVE
#But also in \Steam\userdata\<userid>\1718570\remote

# I am too lazy to make any kind of GUI or even a console menu.
# This is part one of a two part script for editing items.
# This script will output all of the current item counts to a CSV file
# This can be edited and the companion script, edit_items.py, will then alter the values.

# Note for GAIDEN (the DLC): Most items are the same. A few DLC-specific items exist,
# and many storyline-based items are removed since they don't need to be in the DLC.
# If the save filename contains "Gaiden" it will use that item table.

if len(sys.argv) == 1:
    print(f"USAGE: list_items.py <full path to save file>")
    exit()

#Read in the save file...
fname = sys.argv[1]
with open(fname, 'rb') as f:
    fdata = bytearray(f.read())
Globals.set_is_dlc(fname)
outfilename = 'item_data.csv'

items = Items(fdata)

headers = [
    'Id',           #Id of the item. In hex just to be consistent with the spreadsheet.
    'Name',         #Name of the item. Not read by the script, only for convenience.
    'Count',        #Current count, or "Locked" if the item is still unknown (which implies 0 count)
    'New Count',    #Always left blank; fill this in for edit_items to consume.
]
rows = []

for id in items.item_data:
    item = items.item_data[id]
    name = item.name
    count = item.count
    #Skip items I'm pretty sure do not exist.
    if '_lock' in name and item.count == 0:
        continue
    unlock = item.unlock
    if unlock == 0 and count == 0:
        count = 'Locked'
    rows.append({
        'Id'       : id,
        'Name'     : name,
        'Count'    : count,
        'New Count': '',
    })

with open(outfilename, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
    
