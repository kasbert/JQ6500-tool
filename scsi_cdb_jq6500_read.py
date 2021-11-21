# coding: utf-8

from pyscsi.pyscsi.scsi_command import SCSICommand
from pyscsi.pyscsi.scsi_opcode import OpCode

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
        opcode = OpCode('READ_JQ6500', 0xfd, {})
        #SCSICommand.__init__(self, opcode, 0, length)
        SCSICommand._cdb_bits = self._cdb_bits
        SCSICommand._cdb =  bytearray(16)
        dataout_alloclen = 0
        datain_alloclen = length
        self.dataout = bytearray(dataout_alloclen)
        self.datain = bytearray(datain_alloclen)
        self.result = {}
        self.page_code = None
        self.opcode = opcode
        self.cdb = self.build_cdb(opcode= self.opcode.value,
               opcode2= 0x03,
               address= address,
               length= length,
               code2= 0)