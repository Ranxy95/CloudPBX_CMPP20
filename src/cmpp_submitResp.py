#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@ 发送短信后回应处理
"""
import sys
import time

from cmpp_header import *
from cmpp_util import *


class cmppSubmitResp(cmppHeader):
    msg_id = []

    def __init__(self, respMessage, output):
        cmppHeader.__init__(self)
        self.logout = output

        if len(respMessage) == (12 + 8 + 1):
            self.setTotalLength(struct.unpack('!I', respMessage[0:4])[0])
            self.setCommandId(struct.unpack('!I', respMessage[4:8])[0])
            self.setSequenceId(struct.unpack('!I', respMessage[8:12])[0])

            cmppUtil.delSequenceId(int(self.getSequenceId()))

            self.logout.info("cmpp_submitResp-Line[%s] - pop sequence id: %s" %
                             (str(sys._getframe().f_lineno), self.getSequenceId()))

            # body
            self.msgId = struct.unpack('!Q', respMessage[12:20])[0]
            self.result = struct.unpack('!B', respMessage[20:21])[0]

            self.logout.debug("cmpp_submitResp-Line[%s] - total length: %s, commandID:%s, sequenceID:%s, msgid:%s, result:%s" %
                             (str(sys._getframe().f_lineno),
                              self.getTotalLength(), COMMAND_STATE[self.getCommandId()],self.getSequenceId(),
                              self.getMsgId(),self.getResult()))

            # 将submit resp的msg_id 保存下来，用于处理后续的deliver
            tup = (self.msgId, time.time())
            cmppSubmitResp.msg_id.append(tup)

        else:
            self.logout.info("cmpp_submitResp-Line[%s] - respMesage len error: %s" %
                             (str(sys._getframe().f_lineno), str(len(respMessage))))

    def getMsgId(self):
        return self.msgId

    def getResult(self):
        return self.result

