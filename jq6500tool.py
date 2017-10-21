#!/usr/bin/env python
# coding: utf-8

import sys
from pyscsi.pyscsi.scsi import SCSI
from pyscsi.pyscsi.scsi_device import SCSIDevice
from scsi_cdb_jq6500_read import JQ6500Read
from scsi_cdb_jq6500_write import JQ6500Write
from scsi_cdb_jq6500_erase import JQ6500Erase
import argparse


def read_jq6500(self,
               address,
               length,
               **kwargs):
    cmd = JQ6500Read(address,
                 length,
                 **kwargs)
    self.execute(cmd)
    return cmd

def write_jq6500(self,
                address,
                length,
                data,
                **kwargs):
    cmd = JQ6500Write(address,
                     length,
                     data,
                     **kwargs)
    self.execute(cmd)
    return cmd

def erase_jq6500(self,
                address,
                **kwargs):
    cmd = JQ6500Erase(address,
                 **kwargs)
    self.execute(cmd)
    return cmd

def read_flash(sd, blocksize, offset, size, debug = False):
    data = ""
    if offset + size > 8192:
       raise BaseException("Out of range")
    for i in range(0, size, 16):
        s = SCSI(sd, 0x4096)
        r = read_jq6500(s, (offset + i) * 0x100, 16 * 0x100,)
        data = data + r.datain
        print "Read flash", (offset + i), len(r.datain)
        if debug:
            print "CMD", repr(r.cdb)
    return data


def write_flash(sd, blocksize, offset, size, data, debug = False):
    if offset + size > 8192:
       raise BaseException("Out of range")
    # Erase
    for i in range(0, size, 16):
        s = SCSI(sd, 0x0)
        r = erase_jq6500(s, (offset + i) * 0x100,)
        print "Erase flash", offset + i, 0x1000
        if debug:
            print "CMD", repr(r.cdb)
    # Write
    for i in range(0, size, 1):
        s = SCSI(sd, 0x100)
        d = data[(i*0x100):((i+1)*0x100)]
        r = write_jq6500(s, (offset + i) * 0x100, 0x100, d)
        print "Write flash", offset + i, len(d)
        if debug:
            print "CMD", repr(r.cdb)
    # Verify
    for i in range(0, size, 16):
        s = SCSI(sd, 0x4096)
        r = read_jq6500(s, (offset + i) * 0x100, 16 * 0x100,)
        d1 = r.datain
        d2 = data[(i*0x100):((i+16)*0x100)]
        print "Verify flash", offset + i, 0x100, len(d1), len(d2)
        if debug:
            print "CMD", repr(r.cdb)
        for j in range(len(d2)):
            assert ord(d2[j]) == d1[j], ("Verify failed",offset+i,j,ord(d2[j]),d1[j])

def erase_flash(sd, offset, size, debug = False):
    if offset + size > 8192:
       raise BaseException("Out of range")
    for i in range(0, size, 16):
        s = SCSI(sd, 0x0)
        r = erase_jq6500(s, (offset + i) * 0x100,)
        print "Erase flash", offset + i, 0x1000
        if debug:
            print "CMD", repr(r.cdb)

def main(argv):
    parser = argparse.ArgumentParser(description='Eeprom reader/programmer.')
    parser.add_argument('-w', dest='writefile')
    parser.add_argument('-r', dest='readfile')
    parser.add_argument('-b', dest='blocksize', type=int, default=256)
    parser.add_argument('-s', dest='size', type=int, default=8192-1024)
    parser.add_argument('-o', dest='offset', type=int, default=1024)
    parser.add_argument('-e', dest='erase', action='store_true', default=False)
    parser.add_argument('-d', dest='debug', action='store_true', default=False)
    parser.add_argument("device", help="Linux SG device name, e.g. /dev/sg5")
    args = parser.parse_args()
    try:
        sd = SCSIDevice(args.device)
        if args.readfile is not None:
            data = read_flash(sd, args.blocksize, args.offset, args.size, args.debug)
            f=open(args.readfile, "wb")
            f.write(data)
            f.close()
        
        if args.erase:
            data = erase_flash(sd, args.offset, args.size, args.debug)

        if args.writefile is not None:
            f=open(args.writefile, "rb")
            data = f.read()
            f.close()
            size = (len(data) + 255) / 256
            write_flash(sd, args.blocksize, args.offset, size, data, args.debug)

    except Exception as e:
	print "Exception",repr(e)
        print (e.message)


if __name__ == "__main__":
    main(sys.argv)
