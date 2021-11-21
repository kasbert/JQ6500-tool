#
#Header:
#Directory structure is described in little endian 32 bit unsigned integers.
#```
#Header:
# 4 Number of subdirectories (N)
# N*4 Offset of subdir
#Subdir:
# 4 Number of tracks in this dir (M)
# M*8 Directory entry
#   4 Offset of track
#   4 Size of track
#
# Example headers
# 05 00 00 00 18 00 04 00 ec 42 06 00 f0 42 06 00 f4 42 06 00 f8 42 06 00 01 00 00 00
# 05 00 00 00 18 00 04 00 62 00 04 00 66 00 04 00 6a 00 04 00 6e 00 04 00 03 00 00 00
# 05 00 00 00 18 00 04 00 57 8c 04 00 5b 8c 04 00 5f 8c 04 00 63 8c 04 00 02 00 00 00
#


import sys
import argparse
from struct import *

parser = argparse.ArgumentParser(description='Unpack spokeled image.')
parser.add_argument('file')
parser.add_argument('-d', dest='debug', action='store_true', default=False)
args = parser.parse_args()

BASE=0x40000

f=open(args.file, "rb")
try:
    data = f.read()
finally:
    f.close()

if args.debug:
    for a in range(4):
        for b in data[a*16:a*16+15]:
            print("%02x" % (b), end=' ')
        print()
idx = 0
dircount, = unpack("<I", data[idx:idx+4])
idx += 4
subdiroffsets = []
if args.debug:
    print ("Subdircount ", dircount)
for i in range (dircount):
    offset, = unpack("<I", data[idx:idx+4])
    subdiroffsets.append(offset)
    idx += 4
if args.debug:
    print(idx, subdiroffsets)

for offset in subdiroffsets:
    if args.debug:
        print ("Subdir offset %x" % (offset))
    if offset < BASE:
        continue
    idx = offset - BASE
    count, = unpack("<I", data[idx:idx+4])
    idx += 4
    if args.debug:
        print("Count", count)
    if count > 1000:
        continue
    for i in range (count):
        addr,length = unpack("<II", data[idx:idx+8])
        idx += 8
        if args.debug:
            print("Address %x, length %x " % (addr,length))
        track = data[addr - BASE : addr - BASE + length]
        if len(track) == 0:
            continue
        filename = "track%02d.mp3" % (i+1)
        print("Writing %s, %d bytes" %(filename, len(track)))
        #if args.debug:
        #    print(repr(track))
        f = open(filename, "wb")
        try:
            f.write(track)
        finally:
            f.close()

