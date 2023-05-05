#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
cmppSend:发送处理对象，以及接受消息
"""
import struct
import sys
from cmpp_connectResp import cmppConnectResp
from cmpp_net import cmppNet
from cmpp_util import *
from cmpp_submitResp import cmppSubmitResp
from cmpp_activeTestResp import cmppActiveTestResp


class cmppSend(object):

    def __init__(self, socketfd, message, output):
        self.socketFd = socketfd
        self.message = message
        self.head_msg = ""
        self.body_msg = ""
        self.logout = output

    def sendService(self):
        self.logout.info("cmpp_send-Line[%s] -sendService IN" % (str(sys._getframe().f_lineno),))

        cmpp_net = cmppNet(self.logout)
        if self.socketFd != 0 and self.message != "":
            cmpp_net.sendMsg(self.socketFd, self.message)
        else:
            self.logout.error("cmpp_send-Line[%s] - socket or message error" % (str(sys._getframe().f_lineno),))
            return -1

        # 接收消息头
        self.head_msg = cmpp_net.recvMsg(self.socketFd, CMPP_HEADER_LEN)
        head_len = len(self.head_msg)
        if head_len == CMPP_HEADER_LEN:
            body_len = int(struct.unpack('!I', self.head_msg[0:4])[0]) - head_len
        else:
            self.logout.error("cmpp_send-Line[%s] - recv head msg error: head_len:%d" %
                              (str(sys._getframe().f_lineno), head_len,))
            return -1

        self.body_msg = cmpp_net.recvMsg(self.socketFd, body_len)

        if len(self.body_msg) >= 0:
            RecvMessage = self.head_msg + self.body_msg
            if len(RecvMessage) >= CMPP_HEADER_LEN:
                commandId = struct.unpack('!I', self.head_msg[4:8])[0]
                self.logout.info("cmpp_send-Line[%s] -recvmsg commandID:%s" %
                                 (str(sys._getframe().f_lineno), str(COMMAND_STATE[commandId])))

                if commandId == CMPP_CONNECT_RESP:
                    connectResp = cmppConnectResp(RecvMessage, self.logout)
                    return connectResp.getStatus()
                elif commandId == CMPP_SUBMIT_RESP:
                    submitResp = cmppSubmitResp(RecvMessage, self.logout)
                    return submitResp.getResult()
                elif commandId == CMPP_ACTIVE_TEST:
                    activeResp = cmppActiveTestResp(RecvMessage)
                    activeResp.setTotalLength(12 + 1)
                    activeResp.setCommandId(CMPP_ACTIVE_TEST_RESP)
                    sendMsg = activeResp.writeToByteBuffer()
                    self.socketFd.sendall(sendMsg)
                    return 0
                else:
                    self.logout.error("cmpp_send-Line[%s] - unknow the msg command:%s" %
                                      (str(sys._getframe().f_lineno), str(COMMAND_STATE[commandId])))
                    return -1
        else:
            self.logout.error("cmpp_send-Line[%s] - recv the message error" % (str(sys._getframe().f_lineno),))
            return -1
