#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@所有请求的消息头
@totalLength 消息长度
@command_id 消息ID
@sequence_id  流水号，顺序累加，一对请求回应，流水号相同
"""
import struct


class cmppHeader:

    def __init__(self):
        self.total_length = 0
        self.command_id = 0
        self.sequence_id = 0

        # self.setTotalLength(struct.unpack('!I', recvMessage[0:4]))
        # self.setCommandId(struct.unpack('!I', recvMessage[4:8]))
        # self.setSequenceId(struct.unpack('!I', recvMessage[8:12]))

    def getTotalLength(self):
        return self.total_length

    def setTotalLength(self, total_length):
        self.total_length = total_length

    def getCommandId(self):
        return self.command_id

    def setCommandId(self, command_id):
        self.command_id = command_id

    def getSequenceId(self):
        return self.sequence_id

    def setSequenceId(self, sequence_id):
        self.sequence_id = sequence_id

    def toStringBuffer(self, msg):
        pass

    # 字节流的形式写入buffer
    def writeToByteBuffer(self):
        return struct.pack("!III", self.total_length, self.command_id, self.sequence_id)

    # 读取字节流中的int类型
    def readToByteBuffer(self, resp_msg):
        self.total_length, self.command_id, self.sequence_id = struct.unpack('!III', resp_msg)
