#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@向ISMG发送保活心跳
"""

from cmpp_header import *


class cmppActiveTest(cmppHeader):
    def __init__(self):
        cmppHeader.__init__(self)

    # 字节流的形式写入buffer
    def writeToByteBuffer(self):
        return struct.pack('!III', self.getTotalLength(), self.getCommandId(), self.getSequenceId())
