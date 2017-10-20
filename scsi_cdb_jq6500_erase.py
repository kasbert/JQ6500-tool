# coding: utf-8

from pyscsi.pyscsi.scsi_command import SCSICommand
from pyscsi.utils.converter import encode_dict, decode_bits

class JQ6500Erase(SCSICommand):
    """
    A class to send a Erase command to a scsi device
    """
    _cdb_bits = {'opcode': [0xff, 0],
                 'opcode2': [0xff, 1],
                 'address': [0xffffffff, 2],
                 'code2': [0xffff, 14],
    }

    def __init__(self,
                 address,
                 **kwargs):
        if (address & 0xfff) != 0:
            raise SCSICommand.MissingBlocksizeException
        SCSICommand.__init__(self, 0xfb, 0, 0)
        cdb = {'opcode': self.opcode,
               'opcode2': 0xd8,
               'address': address,
               'code2': 0x00
        }
        self.cdb = self.marshall_cdb(cdb)

    @staticmethod
    def unmarshall_cdb(cdb):
        result = {}
        decode_bits(cdb,
                    JQ6500Erase._cdb_bits,
                    result)
        return result

    @staticmethod
    def marshall_cdb(cdb):
        result = bytearray(16)
        encode_dict(cdb,
                    JQ6500Erase._cdb_bits,
                    result)
        return result
