#

import sys
import argparse
import os
from struct import *

parser = argparse.ArgumentParser(description='Pack yq6500 image.')
parser.add_argument('file', nargs='+')
parser.add_argument('-d', dest='debug', action='store_true', default=False)
parser.add_argument('-w', dest='binfile')
args = parser.parse_args()

BASE=0x40000

dircount = 1

header = bytearray()
header.extend(pack('<I', dircount))
diroffset = BASE + 4 + 4 * dircount
header.extend(pack('<I', diroffset))

count = len(args.file)
header.extend(pack('<I', count))
addr = diroffset + 4 + count * 8
for i in range(count):
    file = args.file[i]
    length = os.stat(file).st_size
    header.extend(pack('<II', addr, length))
    print(file, "%x" % addr, length, i)
    addr += length
    if (addr > 8192 * 0x100):
        print ("Warning: MP3 area size exceeded")
    if (addr > (8192 + 1024)* 0x100):
        print ("Error: Total size exceeded")
        sys.exit(1)

if args.debug:
    for b in header:
        print("%02x" % (b), end=' ')
    print()

if args.binfile is not None:
    print("Writing ",args.binfile)
    outf=open(args.binfile, "wb")
    try:
        outf.write(header)
        for filename in args.file:
            print(" Adding",filename)

            f=open(filename, "rb")
            try:
                data = f.read()
                outf.write(data)
            finally:
                f.close()
    finally:
        outf.close()

