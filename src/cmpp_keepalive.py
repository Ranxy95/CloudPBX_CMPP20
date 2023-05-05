#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
 cmpp 链路检测/保活
"""
import struct


from cmpp_net import *
from cmpp_activeTest import cmppActiveTest
from cmpp_activeTestResp import cmppActiveTestResp
from cmpp_config import cmppConfig


class cmppKeepAlive(threading.Thread):
    AliveInterval = 180

    def __init__(self, output):
        threading.Thread.__init__(self)
        self.logjob = output

    def run(self):
        cmpp_net = cmppNet(self.logjob)
        wait_T = int(cmppConfig().getTimeout())

        self.logjob.info("cmpp_keepAlive-Line[%s] - keep alive thread IN" % (str(sys._getframe().f_lineno)))

        while True:
            repeat_N = int(cmppConfig().getTimeoutNumber())

            for socketFd in keepAliveSockets:
                self.logjob.info("cmpp_keepAlive-Line[%s] - try to keep alive, get socketFd:%s" %
                                 (str(sys._getframe().f_lineno), socketFd))

                recv_msg = ''
                active = cmppActiveTest()
                active.setTotalLength(12)
                active.setCommandId(CMPP_ACTIVE_TEST)
                active.setSequenceId(cmppUtil().getSequenceId())
                sendMsg = active.writeToByteBuffer()
                # socketFd.sendall(sendMsg)

                # 60s内未收到回复，则重发消息; 总共循环3次
                while repeat_N:
                    repeat_N = repeat_N - 1
                    socketFd.sendall(sendMsg)
                    try:
                        socketFd.settimeout(wait_T)
                        recv_msg = cmpp_net.recvMsg(socketFd, CMPP_HEADER_LEN + 1)
                        if recv_msg:
                            break
                    except BaseException as e:
                        self.logjob.info("cmpp_keepAlive-Line[%s] - more than time:%s not recv msg, error:%s, retry" %
                                         (str(sys._getframe().f_lineno), str(wait_T), str(e)))
                        continue

                if len(recv_msg) >= CMPP_HEADER_LEN:
                    commandId = struct.unpack('!I', recv_msg[4:8])[0]
                    self.logjob.info("cmpp_keepAlive-Line[%s] -recvmsg commandID:%s" %
                                     (str(sys._getframe().f_lineno), str(COMMAND_STATE[commandId])))
                    if commandId == CMPP_ACTIVE_TEST_RESP:
                        pass
            time.sleep(cmppKeepAlive.AliveInterval)

def setKeepAliveInterval(interval):
    cmppKeepAlive.AliveInterval = interval
