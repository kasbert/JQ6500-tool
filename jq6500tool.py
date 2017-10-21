#!/usr/bin/env python
# coding: utf-8

import sys
from pyscsi.pyscsi.scsi import SCSI
from pyscsi.pyscsi.scsi_device import SCSIDevice
from scsi_cdb_jq6500_read import JQ6500Read
from scsi_cdb_jq6500_write import JQ6500Write
from scsi_cdb_jq6500_erase import JQ6500Erase
import argparse
import glob
import os
from struct import *

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
        print "Read flash", (offset + i), len(r.datain), "\r",
        sys.stdout.flush()
        if debug:
            print "CMD", repr(r.cdb)
    print
    return data


def write_flash(sd, blocksize, offset, size, data, debug = False):
    if offset + size > 8192:
       raise BaseException("Out of range (max "+str((8192-offset)*256)+" bytes)")
    # Erase
    for i in range(0, size, 16):
        s = SCSI(sd, 0x0)
        r = erase_jq6500(s, (offset + i) * 0x100,)
        print "Erase flash", offset + i, 0x1000, "\r",
        sys.stdout.flush()
        if debug:
            print "CMD", repr(r.cdb)
    print
    # Write
    for i in range(0, size, 1):
        s = SCSI(sd, 0x100)
        d = data[(i*0x100):((i+1)*0x100)]
        try:
            r = write_jq6500(s, (offset + i) * 0x100, 0x100, d)
        except Exception as e:
	    print "Exception",repr(e)
            print (e.message)
            print "Retry"
            r = write_jq6500(s, (offset + i) * 0x100, 0x100, d)
        print "Write flash", offset + i, len(d), "\r",
        sys.stdout.flush()
        if debug:
            print "CMD", repr(r.cdb)
    print
    # Verify
    for i in range(0, size, 16):
        s = SCSI(sd, 0x4096)
        r = read_jq6500(s, (offset + i) * 0x100, 16 * 0x100,)
        d1 = r.datain
        d2 = data[(i*0x100):((i+16)*0x100)]
        print "Verify flash", offset + i, 0x100, len(d1), len(d2), "\r",
        sys.stdout.flush()
        if debug:
            print "CMD", repr(r.cdb)
        for j in range(len(d2)):
            assert ord(d2[j]) == d1[j], ("Verify failed",offset+i,j,ord(d2[j]),d1[j])
    print

def erase_flash(sd, offset, size, debug = False):
    if offset + size > 8192:
       raise BaseException("Out of range")
    for i in range(0, size, 16):
        s = SCSI(sd, 0x0)
        r = erase_jq6500(s, (offset + i) * 0x100,)
        print "Erase flash", offset + i, 0x1000, "\r",
        sys.stdout.flush()
        if debug:
            print "CMD", repr(r.cdb)
    print

def find_device(device, debug):
    if device is None:
        devices = glob.glob('/dev/sg[0-9]*')
    else:
        devices = [device]
    for device in devices:
        try:
            if debug:
                print "Trying", device
            sd = SCSIDevice(device)
            s = SCSI(sd)
            i = s.inquiry().result
            if debug:
                print str(i['t10_vendor_identification']).strip(), str(i['product_identification']).strip()
            if str(i['t10_vendor_identification']).strip() == 'YULIN' and str(i['product_identification']).strip() == 'PROGRAMMER':
                print "Device",device
                return sd
        except Exception as e:
	    print "Exception",repr(e), e.message
            pass
    raise BaseException("Cannot find JQ6500 (YULIN PROGRAMMER) device")    

def pack_files(files, debug):
    header = '\x05\x00\x00\x00\x18\x00\x04\x00'
    header += '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    count = len(files)
    header += pack('<L', count)
    assert len(header) == 28, len(header)
    addr = 0x40000 + 28 + count * 8
    for i in range(count):
        file = files[i]
        length = os.stat(file).st_size
        header += pack('<LL', addr, length)
        if debug:
            print file, "%x" % addr, length, i
        addr += length

    if debug:
        for b in header:
            print "%02x" % (ord(b)),
        print
    data = header
    for filename in files:
        print " Adding",filename
        f=open(filename, "rb")
        try:
            data = data + f.read()
        finally:
            f.close()
    return data
            
def main(argv):
    parser = argparse.ArgumentParser(description='JQ6500 MP3 module flash reader/programmer.')
    parser.add_argument('-w', dest='writefile')
    parser.add_argument('-r', dest='readfile')
    parser.add_argument('-b', dest='blocksize', type=int, default=256)
    parser.add_argument('-s', dest='size', type=int, default=8192-1024)
    parser.add_argument('-o', dest='offset', type=int, default=1024)
    parser.add_argument('-e', dest='erase', action='store_true', default=False)
    parser.add_argument('-d', dest='debug', action='store_true', default=False)
    parser.add_argument('-D', dest="device", help="Linux SG device name, e.g. /dev/sg5")
    parser.add_argument('files', nargs="*", help="MP3 files to flash")
    args = parser.parse_args()
    try:
        sd = find_device(args.device, args.debug)
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

        if args.readfile is None and args.writefile is None and not args.erase and len(args.files) > 0:
            print "Writing MP3 files to flash"
            data = pack_files(args.files, args.debug)
            size = (len(data) + 255) / 256
            write_flash(sd, args.blocksize, args.offset, size, data, args.debug)

    except Exception as e:
	print "Exception",repr(e), 
        print (e.message)


if __name__ == "__main__":
    main(sys.argv)
