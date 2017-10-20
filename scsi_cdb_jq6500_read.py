# coding: utf-8

from pyscsi.pyscsi.scsi_command import SCSICommand
from pyscsi.utils.converter import encode_dict, decode_bits

class JQ6500Read(SCSICommand):
    """
    A class to send a Read command to a scsi device
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
                 **kwargs):
        if (address & 0xff) != 0 or (length & 0xff) != 0 :
            raise SCSICommand.MissingBlocksizeException
        SCSICommand.__init__(self, 0xfd, 0, length)
        cdb = {'opcode': self.opcode,
               'opcode2': 0x03,
               'address': address,
               'length': length,
               'code2': 0
        }
        self.cdb = self.marshall_cdb(cdb)

    @staticmethod
    def unmarshall_cdb(cdb):
        result = {}
        decode_bits(cdb,
                    JQ6500Read._cdb_bits,
                    result)
        return result

    @staticmethod
    def marshall_cdb(cdb):
        result = bytearray(16)
        encode_dict(cdb,
                    JQ6500Read._cdb_bits,
                    result)
        return result
