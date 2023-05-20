#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
import re

from itertools import cycle
from operator import xor

#%APPDATA%\..\Local\ASTLIBRA\SAVE
#G:\Steam\userdata\95928894\1718570\remote

#Open two files of the same length. Read in all contents of both.
#Loop over the full file and output any differences.
#This is a very simple diff and will only work with minor differences,
#and if the files are exactly the same length.
#There's no attempt to actually match blocks - is byte x equal to byte x in the other files?

#List of tuples: start pos and end pos.
#This is going to be game-specific, obviously.
#The list will be sorted by start pos; when iterating over the files, if pos matches start pos, jump ahead to
#end pos. 
#Best stuff to put in here is things that will change frequently and have no importance, e.g. clock.
skip_blocks = [
    (0x7360, -4),   #Time
    (0x73b4, 0x73c8),   #Force
    (0x1168, 0x1180),   #Stat allocations
    (0x2720, 0x289f),   #Various statistics.
    #(0x608, 0x780),     #Karon skills (partially a guess)
    (0x7394, -4),       #Gold
    #Specific items that are going to change a lot.
    #(0x12f4, -4),       #Berries
    #(0x14d4, -4),       #Cactus Fruit
    #(0x12fc, -4),       #chest key
    (0x12fc, 0x17C8),   #All items
    (0x7390, -4),       #exp
    #(0x7394, -4),       #Gold
    #(0x7394, -4),       #Gold
]


new_skip_blocks = []
for x in skip_blocks:
    end = x[1]
    if end < 0:
        end = x[0] - end
    new_skip_blocks.append((x[0], end))
skip_blocks = sorted(new_skip_blocks, key = lambda x: x[1])
#
from timeit import default_timer as timer

start = timer()

if len(sys.argv) != 3:
    print("USAGE: bindiff.py infile infile2")
    exit()
#

infilename = sys.argv[1]
infilename2 = sys.argv[2]



with open(infilename, 'rb') as f:
    with open(infilename2, 'rb') as f2:
        data = bytearray(f.read())
        data2 = bytearray(f2.read())
        
        #xored = bytes(map(xor, data2, cycle(data)))
#

if (len(data) != len(data2)):
    raise Exception(f'Files must be of the same length. Left: {len(data)}, Right: {len(data2)}')

is_diff = False
start = 0
left_diff = ''
right_diff = ''
same = 0

def shex(inp):
    s = hex(inp).replace('0x', '')
    return ('0' + s)[-2:]

#for i in range(len(data)):
i=0
while (i < len(data)):
    if len(skip_blocks) > 0 and i == skip_blocks[0][0]:
        target = skip_blocks[0][1]
        del skip_blocks[0]
        i = target
    b1 = data[i]
    b2 = data2[i]
    if (b1 != b2):
        if (not is_diff):
            left_diff = ''
            right_diff = ''
            is_diff = True
            start = i
        same = 0
        left_diff += shex(b1)
        right_diff += shex(b2)
    else:
        same += 1
        if (is_diff):
            if (same > 4):
                #First, remove the identical stuff, which is fixed length.  
                left_diff = left_diff[0:-8]
                right_diff = right_diff[0:-8]
                print(f'From: {hex(start)}:\n\t{left_diff}\n\t{right_diff}')
                #State change.
                is_diff = False
            #Still add it, in case there are gaps.
            left_diff += shex(b1)
            right_diff += shex(b2)
        #
    #Do not use continue - why the fuck doesn't Python have a for loop?
    i += 1
