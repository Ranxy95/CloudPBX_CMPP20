#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@ 认证成功后解析处理回应状态
"""
import sys

from cmpp_header import *
from cmpp_util import cmppUtil

dictStatus = {
    0: '正确',
    1: '消息结构错误',
    2: '非法源地址',
    3: '认证错误',
    4: '版本太高',
    5: '其他错误'
}


class cmppConnectResp(cmppHeader):

    def __init__(self, respMessage, output):
        cmppHeader.__init__(self)
        self.logout = output

        self.status = 0

        sureLen = 12 + 1 + 16 + 1
        if len(respMessage) == sureLen:
            self.setTotalLength(struct.unpack('!I', respMessage[0:4])[0])
            self.setCommandId(struct.unpack('!I', respMessage[4:8])[0])
            self.setSequenceId(struct.unpack('!I', respMessage[8:12])[0])

            cmppUtil.delSequenceId(int(self.getSequenceId()))

            self.logout.info("cmpp_connectResp-Line[%s] - pop sequence id: %s" %
                             (str(sys._getframe().f_lineno), self.getSequenceId()))

            # body
            self.status = struct.unpack('!B', respMessage[12:13])[0]
            self.authenticator_ISMG = struct.unpack('!16s', respMessage[13:29])[0]
            self.version = struct.unpack('!B', respMessage[29:30])[0]

            # self.logout.debug(
            #     "cmpp_connectResp-Line[%s] - total length: %s, commandID:%s, sequenceID:%s, status:%s, auth:%s, ver:%s" %
            #     (str(sys._getframe().f_lineno),
            #      self.getTotalLength(), self.getCommandId(),self.getSequenceId(),
            #      self.getStatus(), self.getAuthenticator_ISMG(), self.getVersion()))

        else:
            self.logout.info("cmpp_connectResp-Line[%s] - respMesage len error: %s" %
                             (str(sys._getframe().f_lineno), str(len(respMessage))))

    def getStatus(self):
        return self.status

    # TODO 可能需要返回的的是状态码
    def setStatus(self, status):
        if dictStatus.get(status, '') != '':
            self.status = dictStatus[status]
        else:
            self.status = '未知错误'

    def getAuthenticator_ISMG(self):
        return self.authenticator_ISMG

    def getVersion(self):
        return self.version
