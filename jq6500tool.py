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
import traceback
from struct import *

MAX_BLOCKS = 8192
BASE_BLOCK = 1024 # 0x40000

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
    data = bytearray()
    if size > MAX_BLOCKS:
       raise BaseException("Out of range")
    for i in range(0, size, 16):
        s = SCSI(sd, 0x4096)
        r = read_jq6500(s, (offset + i) * 0x100, 16 * 0x100,)
        data.extend(r.datain)
        print("Read flash", (offset + i), len(r.datain), "\r", end=' ')
        sys.stdout.flush()
        if debug:
            print("CMD", repr(r.cdb))
    print()
    return data


def write_flash(sd, blocksize, offset, size, indata, debug = False):
    if size > MAX_BLOCKS:
       raise BaseException("Out of range (max "+str((MAX_BLOCKS)*256)+" bytes)")
    data = bytearray()
    data.extend(indata)
    while len(data) < size * 0x100:
        data.append(0)
    # Erase
    for i in range(0, size, 16):
        s = SCSI(sd, 0x0)
        r = erase_jq6500(s, (offset + i) * 0x100,)
        print("Erase flash", offset + i, '/', offset + size, "\r", end=' ')
        sys.stdout.flush()
        if debug:
            print("CMD", repr(r.cdb))
    print()
    # Write
    for i in range(0, size, 1):
        s = SCSI(sd, 0x100)
        d = data[(i*0x100):((i+1)*0x100)]
        try:
            r = write_jq6500(s, (offset + i) * 0x100, 0x100, d)
        except Exception as e:
            print()
            print("Exception",repr(e))
            print((e.message))
            print("Retry")
            r = write_jq6500(s, (offset + i) * 0x100, 0x100, d)
        print("Write flash", offset + i, '/', offset + size, "\r", end=' ')
        sys.stdout.flush()
        if debug:
            print("CMD", repr(r.cdb))
    print()
    # Verify
    for i in range(0, size, 16):
        s = SCSI(sd, 0x4096)
        r = read_jq6500(s, (offset + i) * 0x100, 16 * 0x100,)
        d1 = r.datain
        d2 = data[(i*0x100):((i+16)*0x100)]
        print("Verify flash", offset + i, '/', offset + size, "\r", end=' ')
        sys.stdout.flush()
        if debug:
            print("CMD", repr(r.cdb))
        for j in range(len(d2)):
            if i+j/256 >= size:
                continue
            assert d2[j] == d1[j], ("Verify failed, block %d, [%d] %x != %x" % (offset+i+j/256,j&0xff,d2[j],d1[j]))
    print()

def erase_flash(sd, offset, size, debug = False):
    if size > MAX_BLOCKS:
       raise BaseException("Out of range")
    for i in range(0, size, 16):
        s = SCSI(sd, 0x0)
        r = erase_jq6500(s, (offset + i) * 0x100,)
        print("Erase flash", offset + i, 0x1000, "\r", end=' ')
        sys.stdout.flush()
        if debug:
            print("CMD", repr(r.cdb))
    print()

def find_device(device, debug):
    if device is None:
        devices = glob.glob('/dev/sg[0-9]*')
    else:
        devices = [device]
    for device in devices:
        try:
            if debug:
                print("Trying", device, ' ',  end = '')
            sd = SCSIDevice(device)
            s = SCSI(sd)
            i = s.inquiry().result
            vendor = i['t10_vendor_identification'].decode("latin1", "backslashreplace").strip()
            product = i['product_identification'].decode("latin1", "backslashreplace").strip()
            if debug:
                print(vendor, product)
            if vendor == 'YULIN' and product == 'PROGRAMMER':
                print("Device",device)
                return sd
        except Exception as e:
            print("Exception",traceback.format_exc())
            pass
    raise BaseException("Cannot find JQ6500 (YULIN PROGRAMMER) device")

def pack_files(files, debug):
    BASE = 0x40000
    dircount = 1
    header = bytearray()
    header.extend(pack('<I', dircount))
    diroffset = BASE + 4 + 4 * dircount
    header.extend(pack('<I', diroffset))
    count = len(files)
    header.extend(pack('<I', count))
    addr = diroffset + 4 + count * 8
    for i in range(count):
        file = files[i]
        length = os.stat(file).st_size
        header.extend(pack('<II', addr, length))
        if debug:
            print(file, "%x" % addr, length, i)
        addr += length

    if debug:
        for b in header:
            print("%02x" % (ord(b)), end=' ')
        print()
    data = header
    for filename in files:
        print(" Adding",filename)
        f=open(filename, "rb")
        try:
            data = data + f.read()
        finally:
            f.close()
    return data

def main(argv):
    parser = argparse.ArgumentParser(description='JQ6500 MP3 module flash reader/programmer.')
    parser.add_argument('-w', dest='writefile', help='Write from file to module')
    parser.add_argument('-r', dest='readfile', help='Read from module to file')
    parser.add_argument('-b', dest='blocksize', type=int, default=256)
    parser.add_argument('-s', dest='size', type=int, default=MAX_BLOCKS-BASE_BLOCK, help="Size in blocks, 1-8192, default " + str(MAX_BLOCKS-BASE_BLOCK))
    parser.add_argument('-o', dest='offset', type=int, default=BASE_BLOCK, help="Offset in blocks, 0-8191, default " + str(BASE_BLOCK))
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
            size = int(len(data) / 256)
            write_flash(sd, args.blocksize, args.offset, size, data, args.debug)

        if args.readfile is None and args.writefile is None and not args.erase and len(args.files) > 0:
            print("Writing MP3 files to flash")
            data = pack_files(args.files, args.debug)
            size = int((len(data) + 255) / 256)
            write_flash(sd, args.blocksize, args.offset, size, data, args.debug)

    except Exception as e:
        print("Exception", traceback.format_exc())

if __name__ == "__main__":
    main(sys.argv)
