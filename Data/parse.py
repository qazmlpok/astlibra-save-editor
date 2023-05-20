#175c seems like the end.
#or 17b4

#234C for unlocks.
#220C
#which suggests 0x140 items.

max_id = 0x140
items_start = 0x12CC

filename = 'items_txt.txt'
lookup = {}
with open(filename, 'r') as f:
    data = f.readlines()
    for l in data:
        line = l.strip()
        #These are fixed length, so...
        addr = line[0:6]
        name = line[8:]
        addr = int(addr, 16)
        if (addr - items_start)%4 != 0:
            raise Exception("Something went wrong.")
        id = (addr - items_start) // 4
        lookup[id] = name

print("Id,Name")
for id in range(max_id):
    if id in lookup:
        name = lookup[id]
    else:
        name = f'unk_{id}'
    print(f"0x{id:02X},{name}")