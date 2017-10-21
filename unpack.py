#
# Header addresses:
# 24 count of tracks
# 28 + n*8 address
# 32 + n*8 length
# 36 + count*8 track1
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

f=open(args.file, "rb")
try:
    data = f.read()
finally:
    f.close()

header = data[0:28]
if args.debug:
    for b in header:
        print "%02x" % (ord(b)),
    print
count = ord(data[24])
if args.debug:
    print "Count", count
for i in range (count):
    j = 28 + i*8
    addr,length = unpack("<LL", data[j:j+8])
    if args.debug:
        print "Address %x, length %x " % (addr,length)
    track = data[addr - 0x40000 : addr - 0x40000 + length]
    filename = "track%02d.mp3" % (i+1)
    print "Writing %s, %d bytes" %(filename, len(track))
    if args.debug:
        print repr(track)
    f = open(filename, "wb")
    try:
        f.write(track)
    finally:
        f.close()

