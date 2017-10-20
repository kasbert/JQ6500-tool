# coding: utf-8

from pyscsi.pyscsi.scsi_command import SCSICommand
from pyscsi.utils.converter import encode_dict, decode_bits

class JQ6500Write(SCSICommand):
    """
    A class to send a Write command to a scsi device
    """
    _cdb_bits = {'opcode': [0xff, 0],
                 'opcode2': [0xff, 1],
                 'address': [0xffffffff, 2],
                 'length': [0xffff, 12],
                 'code2': [0xffff, 14],
    }

    def __init__(self,
                 address,
                 length,
                 data,
                 **kwargs):
        if (address & 0xff) != 0 or (length & 0xff) != 0 :
            raise SCSICommand.MissingBlocksizeException
        SCSICommand.__init__(self, 0xfb, length, 0)
        cdb = {'opcode': self.opcode,
               'opcode2': 0xd9,
               'address': address,
               'length': length,
               'code2': 0x00
        }
        self.cdb = self.marshall_cdb(cdb)
        self.dataout = data

    @staticmethod
    def unmarshall_cdb(cdb):
        result = {}
        decode_bits(cdb,
                    JQ6500Write._cdb_bits,
                    result)
        return result

    @staticmethod
    def marshall_cdb(cdb):
        result = bytearray(16)
        encode_dict(cdb,
                    JQ6500Write._cdb_bits,
                    result)
        return result
