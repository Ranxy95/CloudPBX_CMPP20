#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@ 处理接收到的状态报告
"""
import struct
import sys
import threading

from cmpp_config import cmppConfig
from cmpp_util import *
from cmpp_submitResp import cmppSubmitResp
from cmpp_header import cmppHeader

resp_result = {
    0:"正确",
    1:"消息结构错",
    2:"命令字错",
    3:"消息序号重复",
    4:"消息长度错",
    5:"资费代码错",
    6:"超过最大信息长",
    7:"业务代码错",
    8:"流量控制错",
    9:"其他错误",
}


class cmppDeliverResp(threading.Thread, cmppHeader):
    def __init__(self, output, socketFd, recvMessage):
        threading.Thread.__init__(self)
        conf = cmppConfig()
        self.timeout = int(conf.getTimeoutDeliver())*60*60
        self.socketFd = socketFd
        self.logjob = output
        self.lock = threading.Lock()

        # self.setTotalLength(struct.unpack('!I', recvMessage[0:4])[0])
        # self.setCommandId(struct.unpack('!I', recvMessage[4:8])[0])
        self.setSequenceId(struct.unpack('!I', recvMessage[8:12])[0])

        self.Msg_Id = struct.unpack('!Q', recvMessage[12:20])[0]
        self.Dest_Id = struct.unpack('!21s', recvMessage[20:41])[0]
        self.Service_Id = struct.unpack('!10s', recvMessage[41:51])[0]
        self.TP_pid = struct.unpack('!B', recvMessage[51])[0]
        self.TP_udhi = struct.unpack('!B', recvMessage[52])[0]
        self.Msg_Fmt = struct.unpack('!B', recvMessage[53])[0]
        self.Src_terminal_Id = struct.unpack('!21s', recvMessage[54:75])[0]
        self.Registered_Delivery = struct.unpack('!B', recvMessage[75])[0]
        self.Msg_Length = struct.unpack('!B', recvMessage[76])[0]
        self.Msg_Content = {
            "Msg_Id":struct.unpack('!Q', recvMessage[77:85])[0],
            "Stat":struct.unpack('!7s', recvMessage[85:92])[0],
            "Submit_time":struct.unpack('!10s', recvMessage[92:102])[0],
            "Done_time":struct.unpack('!10s', recvMessage[102:112])[0],
            "Dest_terminal_Id":struct.unpack('!21s', recvMessage[112:133])[0],
            "SMSC_sequence":struct.unpack('!I', recvMessage[133:137])[0],
        }
        self.Reserved = struct.unpack('!8s', recvMessage[137:145])[0],

        self.result = 0

    # 字节流的形式写入buffer
    def writeToByteBuffer(self):
        return struct.pack('!3I QB',
                           int(self.getTotalLength()), int(self.getCommandId()), int(self.getSequenceId()),
                           self.Msg_Id, self.result)

    def run(self):
        self.logjob.info("cmpp_deliverResp-Line[%s] - deliver content:%s" %
                         (str(sys._getframe().f_lineno), self.Msg_Content))

        self.logjob.info("cmpp_deliverResp-Line[%s] - msgid:%s, destid:%s, ser_id:%s, tpid:%s, tpudhi:%s, msgfmt:%s, ter id:%s," %
                         (str(sys._getframe().f_lineno),
                          self.Msg_Id, self.Dest_Id, self.Service_Id, self.TP_pid, self.TP_udhi,
                          self.Msg_Fmt, self.Src_terminal_Id))

        try:
            self.lock.acquire()
            for i in range(len(cmppSubmitResp.msg_id)):
                tup = cmppSubmitResp.msg_id[i]
                now = time.time()
                if tup[0] == self.Msg_Content["Msg_Id"]:
                    cmppSubmitResp.msg_id.pop(i)
                    self.logjob.info("cmpp_deliverResp-Line[%s] - handle deliver status report of msg_id[%s]" %
                                     (str(sys._getframe().f_lineno), self.Msg_Content["Msg_Id"]))

                # TODO 如果超过48小时没有收到状态报告，直接删除该条记录，处理方式待优化，可以使用线程实时监控
                if now - tup[1] > self.timeout:
                    cmppSubmitResp.msg_id.pop(i)
                    self.logjob.info(
                        "cmpp_deliverResp-Line[%s] - no deliver status report received of msg_id[%s] over 48 hours" %
                        (str(sys._getframe().f_lineno), tup[0]))
            self.lock.release()

            # init header and set msg body
            self.setTotalLength(12 + 8 + 1)
            self.setCommandId(CMPP_DELIVER_RESP)
            sendMsg = self.writeToByteBuffer()

            self.socketFd.sendall(sendMsg)
        except BaseException as e:
            self.logjob.info("cmpp_deliver-Line[%s] - response deliver failed, ERROR:%s" %
                             (str(sys._getframe().f_lineno), str(e)))
