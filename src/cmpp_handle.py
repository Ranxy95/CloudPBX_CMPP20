#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
cmpp 认证和短信的主要处理接口实现
"""
import struct
import threading
import time

from cmpp_connect import cmppConnect
from cmpp_net import *
from cmpp_send import cmppSend
from cmpp_submit import cmppSubmit
from cmpp_util import *
from cmpp_config import cmppConfig
from cmpp_activeTest import cmppActiveTest
from cmpp_activeTestResp import cmppActiveTestResp
from cmpp_deliverResp import cmppDeliverResp
from cmpp_connectResp import cmppConnectResp
from cmpp_submitResp import cmppSubmitResp


class cmppHandle(object):
    def __init__(self, output):
        self.logjob = output

    # connect认证
    def connectISMG(self, dataPack):
        ip = dataPack["ip"]
        port = dataPack["port"]
        version = dataPack["version"]

        if version != CMPP_CONNECT_MT and version != CMPP_CONNECT_MO:
            self.logjob.error("cmpp_handle-Line[%s] - version[%s] error" %
                              (str(sys._getframe().f_lineno), version))
            return -1, 0

        cmpp_net = cmppNet(self.logjob)
        socketFd, reply = cmpp_net.startTcpClient(0, dataPack)
        res = 0
        if socketFd > 0:
            if reply == NET_STATUS['ok']:
                conf = cmppConfig()
                seq_id = cmppUtil().getSequenceId()
                if seq_id == -1:
                    return -1, -1

                connObj = cmppConnect()
                connObj.setTotalLength(12 + 6 + 16 + 1 + 4)
                connObj.setCommandId(CMPP_CONNECT)

                connObj.setSequenceId(seq_id)

                self.logjob.info("cmpp_handle-Line[%s] connect sequenceId:%d, version[%s]" %
                                 (str(sys._getframe().f_lineno), seq_id, version))

                connObj.setSourceAddr(conf.getSpId())
                connObj.setAuthenticatorSource(
                    cmppUtil.getAuthenticatorSource(sp_id=conf.getSpId(), secret=conf.getShareSecret()))
                if version == CMPP_CONNECT_MT:
                    connObj.setVersion(CMPP_VERSION_MT)
                elif version == CMPP_CONNECT_MO:
                    connObj.setVersion(CMPP_VERSION_MO)

                connObj.setTimestamp(time.strftime('%m%d%H%M%S', time.localtime(time.time())))

                sendMsg = connObj.writeToByteBuffer()
                sendObjc = cmppSend(socketFd, sendMsg, self.logjob)
                res = sendObjc.sendService()

                self.logjob.info("cmpp_handle-Line[%s] - request connect result:[%s]" %
                                 (str(sys._getframe().f_lineno), str(res),))
            elif reply == NET_STATUS['find']:
                self.logjob.info("cmpp_handle-Line[%s] - socket already connected" %
                                 (str(sys._getframe().f_lineno),))
                res = 0
        else:
            self.logjob.error("cmpp_handle-Line[%s] - connectISMG connect error:%s:%s" %
                              (str(sys._getframe().f_lineno), ip, port,))
            res = -1

        return res, socketFd

    # submit 发送短信
    def submitMessage(self, socketFd, message, number):
        if socketFd <= 0 or message == '' or number == '':
            # print('submitMessage param error')
            return -1

        seq_id = cmppUtil().getSequenceId()
        if seq_id == -1:
            return -1

        # init and set msg body
        msg_len = len(message.decode('utf-8').encode('utf-16be'))
        submitObj = cmppSubmit(message, number)

        # header
        submitObj.setTotalLength(
            12 + 8 + 1 + 1 + 1 + 1 + 10 + 1 + 21 + 1 + 1 + 1 + 6 + 2 + 6 + 17 + 17 + 21 + 1 + 21 + 1 + msg_len + 8)
        submitObj.setCommandId(CMPP_SUBMIT)
        submitObj.setSequenceId(seq_id)

        self.logjob.debug("cmpp_handle-Line[%s] - submit sequenceId:%d" %
                          (str(sys._getframe().f_lineno), seq_id))

        sendMsg = submitObj.writeToByteBuffer()
        # sendObjc = cmppSend(socketFd, sendMsg, self.logjob)
        # return sendObjc.sendService()

        msgSendQueue.append(sendMsg)

    # 发送心跳保活连接
    def sendActiveTest(self, sockFd):
        if sockFd > 0:
            activeObj = cmppActiveTest()
            activeObj.setTotalLength(12)  # 消息总长度，总字节数:4+4+4(消息头)
            activeObj.setCommandId(CMPP_ACTIVE_TEST)
            activeObj.setSequenceId(cmppUtil().getSequenceId())  # 序列，由我们指定

            activeMessage = activeObj.writeToByteBuffer()

            sendObj = cmppSend(sockFd, activeMessage, self.logjob)
            return sendObj.sendService()
        # else:
        # print('sendActiveTest error, sockFd:' + sockFd)

    # 回应心跳处理
    def sendAciveTestResp(self, sockFd, recvmessage):
        activeRespObj = cmppActiveTestResp(recvmessage)
        activeRespObj.setTotalLength(12 + 1)
        activeRespObj.setCommandId(CMPP_ACTIVE_TEST_RESP)
        sendMsg = activeRespObj.writeToByteBuffer()
        try:
            sockFd.sendall(sendMsg)
        except BaseException as e:
            self.logjob.error("cmpp_deliver-Line[%s] -sendAciveTestResp failed, ERROR:%s" %
                              (str(sys._getframe().f_lineno), str(e)))

    # 根据连接类型，返回对应的socketFd
    @staticmethod
    def getSocketByType(connect_type):
        if not connectedISMG[connect_type]:
            return 0

        for i in range(len(cmppNet.connectList)):
            tup = cmppNet.connectList[i]
            if tup[3] == connect_type:
                return tup[2]
        return 0

    # 处理状态报告以及保活
    def deliverRequest(self, socketFd):
        cmpp_net = cmppNet(self.logjob)

        self.logjob.info("cmpp_handle- Line[%s] handle deliver status report and keep alive" %
                         (str(sys._getframe().f_lineno),))

        old_time = time.time()
        wait_T = int(cmppConfig().getTimeout())
        while True:
            socketFd = self.getSocketByType(CMPP_CONNECT_MO)
            if socketFd == 0:
                continue

            # 保活
            repeat_N = int(cmppConfig().getTimeoutNumber())
            now_time = time.time()
            if now_time - old_time >= wait_T:
                old_time = now_time

                self.logjob.info("cmpp_handle-Line[%s] - send CMPP_ACTIVE_TEST packet begin......" % (
                    str(sys._getframe().f_lineno)))

                # send alive packet
                active = cmppActiveTest()
                active.setTotalLength(12)
                active.setCommandId(CMPP_ACTIVE_TEST)
                active.setSequenceId(cmppUtil().getSequenceId())
                sendMsg = active.writeToByteBuffer()

                try:
                    cmpp_net.sendMsg(socketFd, sendMsg)
                    head_msg = cmpp_net.recvMsg(socketFd, CMPP_HEADER_LEN)
                    total_len = int(struct.unpack('!I', head_msg[0:4])[0])

                    self.logjob.info("cmpp_handle-Line[%s] - head_msg len:%s, total_len:%s" %
                                     (str(sys._getframe().f_lineno), str(len(head_msg)), str(total_len)))

                    if total_len == CMPP_HEADER_LEN:
                        self.sendAciveTestResp(socketFd, head_msg)
                        continue

                    body_msg = cmpp_net.recvMsg(socketFd, total_len - CMPP_HEADER_LEN)
                    self.logjob.info("cmpp_handle-Line[%s] - body_msg len:%s" %
                                     (str(sys._getframe().f_lineno),str(len(body_msg))))

                    recv_msg = head_msg + body_msg
                    if len(recv_msg) >= CMPP_HEADER_LEN:
                        commandId = struct.unpack('!I', recv_msg[4:8])[0]
                        self.logjob.info("cmpp_handle-Line[%s] -recvmsg commandID:%s" %
                                         (str(sys._getframe().f_lineno), str(commandId)))
                        if commandId == CMPP_ACTIVE_TEST_RESP:
                            pass
                        # elif commandId == CMPP_SUBMIT_RESP:
                        #     submitResp = cmppSubmitResp(recv_msg, self.logjob)
                        #     ret = submitResp.getResult()
                        #     self.logjob.info("cmpp_handle-Line[%s] - submit message result:%s" %
                        #                      (str(sys._getframe().f_lineno), str(ret)))
                        elif commandId == CMPP_ACTIVE_TEST:
                            self.sendAciveTestResp(socketFd, recv_msg)
                except BaseException as e:
                    self.logjob.info("cmpp_handle- Line[%s] socket recv msg failed, ERROR:%s" % (
                        str(sys._getframe().f_lineno), str(e)))
                    cmpp_net.popSocketFd(socketFd)
                    continue

            # 接收处理deliver消息
            # TODO　主动接收消息的连接，接收消息长度为0是正常的，需要其他方法检测socket是否断开
            try:
                head_msg = cmpp_net.recvMsg(socketFd, CMPP_HEADER_LEN)
                head_len = len(head_msg)
                body_len = int(struct.unpack('!I', head_msg[0:4])[0]) - head_len

                # TODO 接收消息体，如果消息体长度过长，则说明socket消息异常, 是否需要关闭socket
                self.logjob.info("cmpp_handle-Line[%s] - head_msg len:%s, body_len:%s" %
                                 (str(sys._getframe().f_lineno), str(len(head_msg)), str(body_len)))

                if body_len == 0:
                    self.sendAciveTestResp(socketFd, head_msg)
                    continue

                body_msg = cmpp_net.recvMsg(socketFd, body_len)

                self.logjob.info("cmpp_handle-Line[%s] - body_msg len:%s" %
                                 (str(sys._getframe().f_lineno), str(len(body_msg))))

                if body_len != len(body_msg):
                    # self.logjob.info("cmpp_handle-Line[%s] -recvmsg msg failed, length:%s" %
                    #                  (str(sys._getframe().f_lineno), str(len(body_msg))))

                    # TODO 是否需要删除socket 待定
                    # cmpp_net.popSocketFd(socketFd)
                    continue
                elif body_len == len(body_msg):
                    RecvMessage = head_msg + body_msg
                    commandId = struct.unpack('!I', head_msg[4:8])[0]

                    self.logjob.info("cmpp_handle-Line[%s] -recvmsg commandID:%s" %
                                     (str(sys._getframe().f_lineno), str(commandId)))

                    if commandId == CMPP_DELIVER:
                        deliverResp = cmppDeliverResp(self.logjob, socketFd, RecvMessage)
                        deliverResp.start()
                    elif commandId == CMPP_ACTIVE_TEST:
                        self.sendAciveTestResp(socketFd, RecvMessage)
            except BaseException as e:
                self.logjob.error("cmpp_handle- Line[%s] socket recv msg failed, ERROR:%s" % (
                    str(sys._getframe().f_lineno), str(e)))
                cmpp_net.popSocketFd(socketFd)
                continue

    # 心跳服务
    @staticmethod
    def deliverService(socketFd, output):
        thread1 = threading.Thread(target=cmppHandle(output).deliverRequest, kwargs={"socketFd": socketFd})
        thread1.start()

    # submit消息以及保活
    def handleMessage(self, socketFd):
        cmpp_net = cmppNet(self.logjob)
        self.logjob.info(
            "cmpp_handle- Line[%s] handle message transform and keep alive" % (str(sys._getframe().f_lineno)))

        old_time = time.time()
        wait_T = int(cmppConfig().getTimeout())
        while True:
            socketFd = self.getSocketByType(CMPP_CONNECT_MT)
            if socketFd == 0:
                continue

            # 保活
            repeat_N = int(cmppConfig().getTimeoutNumber())
            now_time = time.time()
            if now_time - old_time >= wait_T:
                old_time = now_time

                self.logjob.info(
                    "cmpp_handle-Line[%s] - send CMPP_ACTIVE_TEST packet begin......" % (str(sys._getframe().f_lineno)))

                # send alive packet
                active = cmppActiveTest()
                active.setTotalLength(CMPP_HEADER_LEN)
                active.setCommandId(CMPP_ACTIVE_TEST)
                active.setSequenceId(cmppUtil().getSequenceId())
                sendMsg = active.writeToByteBuffer()

                try:
                    cmpp_net.sendMsg(socketFd, sendMsg)
                    while True:
                        head_msg = cmpp_net.recvMsg(socketFd, CMPP_HEADER_LEN)
                        total_len = int(struct.unpack('!I', head_msg[0:4])[0])

                        self.logjob.info("cmpp_handle-Line[%s] - head_msg len:%s, total_len:%s" %
                                         (str(sys._getframe().f_lineno), str(len(head_msg)), str(total_len)))

                        if total_len == CMPP_HEADER_LEN:
                            self.sendAciveTestResp(socketFd, head_msg)
                            continue
                        else:
                            break

                    body_msg = cmpp_net.recvMsg(socketFd, total_len - CMPP_HEADER_LEN)
                    self.logjob.info("cmpp_handle-Line[%s] - body_msg len:%s" %
                                     (str(sys._getframe().f_lineno),str(len(body_msg))))

                    recv_msg = head_msg + body_msg
                    if len(recv_msg) >= CMPP_HEADER_LEN:
                        commandId = struct.unpack('!I', recv_msg[4:8])[0]
                        self.logjob.info("cmpp_handle-Line[%s] -recvmsg commandID:%s" %
                                         (str(sys._getframe().f_lineno), str(commandId)))
                        if commandId == CMPP_ACTIVE_TEST_RESP:
                            pass
                        elif commandId == CMPP_SUBMIT_RESP:
                            submitResp = cmppSubmitResp(recv_msg, self.logjob)
                            ret = submitResp.getResult()
                            self.logjob.info("cmpp_handle-Line[%s] - submit message result:%s" %
                                             (str(sys._getframe().f_lineno), str(ret)))
                        elif commandId == CMPP_ACTIVE_TEST:
                            self.sendAciveTestResp(socketFd, recv_msg)
                except BaseException as e:
                    self.logjob.info("cmpp_handle- Line[%s] socket recv msg failed, ERROR:%s" % (
                        str(sys._getframe().f_lineno), str(e)))
                    cmpp_net.popSocketFd(socketFd)
                    continue

            # submit message
            # TODO msgSendQueue 当呼叫很多时，可能需要加锁
            for msg in msgSendQueue:
                self.logjob.info(
                    "cmpp_handle- Line[%s] submit message begin......" % (str(sys._getframe().f_lineno)))

                try:
                    cmpp_net.sendMsg(socketFd, msg)

                    while True:
                        # 接收消息头
                        head_msg = cmpp_net.recvMsg(socketFd, CMPP_HEADER_LEN)
                        head_len = len(head_msg)
                        body_len = int(struct.unpack('!I', head_msg[0:4])[0]) - head_len

                        # TODO 接收消息体，如果消息体长度过长，则说明socket消息异常, 是否需要关闭socket
                        self.logjob.info("cmpp_handle-Line[%s] - head_msg len:%s, body_len:%s" %
                                         (str(sys._getframe().f_lineno), str(len(head_msg)), str(body_len)))

                        if body_len == 0:
                            self.sendAciveTestResp(socketFd, head_msg)
                            continue

                        body_msg = cmpp_net.recvMsg(socketFd, body_len)

                        self.logjob.info("cmpp_handle-Line[%s] - body_msg len:%s" %
                                         (str(sys._getframe().f_lineno), str(len(body_msg))))

                        if len(body_msg) == body_len:
                            RecvMessage = head_msg + body_msg
                            commandId = struct.unpack('!I', head_msg[4:8])[0]

                            self.logjob.info("cmpp_handle-Line[%s] -recvmsg commandID:%s" %
                                             (str(sys._getframe().f_lineno), str(commandId)))

                            if commandId == CMPP_SUBMIT_RESP:
                                submitResp = cmppSubmitResp(RecvMessage, self.logjob)
                                ret = submitResp.getResult()
                                self.logjob.info("cmpp_handle-Line[%s] - submit message result:%s" %
                                                 (str(sys._getframe().f_lineno), str(ret)))
                                break
                            elif commandId == CMPP_ACTIVE_TEST:
                                self.sendAciveTestResp(socketFd, RecvMessage)
                        else:
                            self.logjob.error("cmpp_handle-Line[%s] -recv body_msg failed, length:%s" %
                                              (str(sys._getframe().f_lineno), str(head_len)))
                            # continue
                except BaseException as e:
                    self.logjob.info("cmpp_handle- Line[%s] socket recv msg failed, ERROR:%s" % (
                        str(sys._getframe().f_lineno), str(e)))
                    cmpp_net.popSocketFd(socketFd)
                    continue

            # 消息不需要重发，清空消息列表
            del msgSendQueue[:]

    @staticmethod
    def handleService(socketFd, output):
        thread1 = threading.Thread(target=cmppHandle(output).handleMessage, kwargs={"socketFd": socketFd})
        thread1.start()
