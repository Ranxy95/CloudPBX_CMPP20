#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@保活心跳回应处理
"""

from cmpp_header import *


class cmppActiveTestResp(cmppHeader):
    def __init__(self, respMessage):
        cmppHeader.__init__(self)
        self.Reserved = 0x00

        if len(respMessage) == 12:
            self.setTotalLength(struct.unpack('!I', respMessage[0:4])[0])
            self.setCommandId(struct.unpack('!I', respMessage[4:8])[0])
            self.setSequenceId(struct.unpack('!I', respMessage[8:12])[0])

    def getReserved(self):
        return self.Reserved

    def setReserved(self, Reserved):
        self.Reserved = Reserved

    # 字节流的形式写入buffer
    def writeToByteBuffer(self):
        return struct.pack('!III B', self.getTotalLength(), self.getCommandId(), self.getSequenceId(),
                           int(self.getReserved()))
