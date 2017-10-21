#

import sys
import argparse
import os
from array import array
from struct import *

parser = argparse.ArgumentParser(description='Pack yq6500 image.')
parser.add_argument('file', nargs='+')
parser.add_argument('-d', dest='debug', action='store_true', default=False)
parser.add_argument('-w', dest='binfile')
args = parser.parse_args()

header = '\x05\x00\x00\x00\x18\x00\x04\x00XXXXXXXXXXXXXXXX'
count = len(args.file)
header += pack('<L', count)
addr = 0x40000 + 28 + count * 8
for i in range(count):
    file = args.file[i]
    length = os.stat(file).st_size
    header += pack('<LL', addr, length)
    print file, "%x" % addr, length, i
    addr += length

if args.debug:
    for b in header:
        print "%02x" % (ord(b)),
    print

if args.binfile is not None:
    print "Writing ",args.binfile
    outf=open(args.binfile, "wb")
    try:
        outf.write(header)
        for filename in args.file:
            print " Adding",filename
            
            f=open(filename, "rb")
            try:
                data = f.read()
                outf.write(data)
            finally:
                f.close()
    finally:
        outf.close()

