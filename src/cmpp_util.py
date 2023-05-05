#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
 cmpp 相关定义
"""

import hashlib
import socket
import time
import threading


CMPP_HEADER_LEN       = 12

CMPP_VERSION          = 0x02  # CMPP2.0
CMPP_VERSION_MT       = 0x00  # CMPP2.0,发送信息给用户
CMPP_VERSION_MO       = 0x01  # CMPP2.0,接收状态报告

CMPP_CONNECT          = 0x00000001  # 请求连接
CMPP_CONNECT_RESP     = 0x80000001  # 请求连接应答    2147483649
CMPP_TERMINATE        = 0x00000002  # 终止连接
CMPP_TERMINATE_RESP   = 0x80000002  # 终止连接应答
CMPP_SUBMIT           = 0x00000004  # 提交短信
CMPP_SUBMIT_RESP      = 0x80000004  # 提交短信应答    2147483652
CMPP_DELIVER          = 0x00000005  # 短信下发
CMPP_DELIVER_RESP     = 0x80000005  # 下发短信应答    2147483653
CMPP_QUERY            = 0x00000006  # 发送短信状态查询
CMPP_QUERY_RESP       = 0x80000006  # 发送短信状态查询应答    2147483654
CMPP_CANCEL           = 0x00000007  # 删除短信
CMPP_CANCEL_RESP      = 0x80000007  # 删除短信应答    2147483655
CMPP_ACTIVE_TEST      = 0x00000008  # 激活测试
CMPP_ACTIVE_TEST_RESP = 0x80000008  # 激活测试应答    2147483656

COMMAND_STATE = {
    0x00000001: 'CMPP_CONNECT',
    0x80000001: 'CMPP_CONNECT_RESP',
    0x00000002: 'CMPP_TERMINATE',
    0x80000002: 'CMPP_TERMINATE_RESP',
    0x00000004: 'CMPP_SUBMIT',
    0x80000004: 'CMPP_SUBMIT_RESP',
    0x00000005: 'CMPP_DELIVER',
    0x80000005: 'CMPP_DELIVER_RESP',
    0x00000006: 'CMPP_QUERY',
    0x80000006: 'CMPP_QUERY_RESP',
    0x00000007: 'CMPP_CANCEL',
    0x80000007: 'CMPP_CANCEL_RESP',
    0x00000008: 'CMPP_ACTIVE_TEST',
    0x80000008: 'CMPP_ACTIVE_TEST_RESP',
}


# CMPP_DELIVER-Msg_content-Message Stat
MESSAGE_DELIVERED        = "DELIVRD"   # Message is delivered to destination
MESSAGE_EXPIRED          = "EXPIRED"   # Message validity period has expired
MESSAGE_DELETED          = "DELETED"   # Message has been deleted.
MESSAGE_UNDELIVERABLE    = "UNDELIV"   # Message is undeliverable
MESSAGE_ACCEPTED         = "ACCEPTD"   # Message is in accepted state
MESSAGE_UNKNOWN          = "UNKNOWN"   # Message is in invalid state
MESSAGE_REJECTED         = "REJECTD"   # Message is in a rejected state

# socket连接类型
CMPP_CONNECT_MO          = "MO"
CMPP_CONNECT_MT          = "MT"

# socket连接状态，-1：创建socket失败，0：创建socket成功，1：找到已连接的socket
NET_STATUS = {
    'false': -1,
    'ok': 0,
    'find': 1,
}

# 两种socket连接：MT：PBX发送消息， MO：PBX接收状态报告
connectedISMG = {CMPP_CONNECT_MT:False, CMPP_CONNECT_MO:False, "keepAlive":False, "run":False}

keepAliveSockets = []

# 需要发送的消息
msgSendQueue = []

# 消息流水号的最大值
MAX_SEQUENCE_ID          = 4294967296   # 2^32
MAX_SOCKET_BUFFER_LEN    = 2048


# 给状态处理报告的资源创建一把锁
DELIVER_LOCK = threading.Lock()



class cmppUtil:
    static_sequenceId = 0
    sequenceID_list = []

    # 获取序列号
    @staticmethod
    def getSequenceId():
        while True:
            cmppUtil.static_sequenceId += 1
            if cmppUtil.static_sequenceId <= MAX_SEQUENCE_ID:
                if cmppUtil.static_sequenceId not in cmppUtil.sequenceID_list:
                    cmppUtil.sequenceID_list.append(cmppUtil.static_sequenceId)
                    break
                else:
                    continue
            elif len(cmppUtil.sequenceID_list) >= MAX_SEQUENCE_ID:
                # 规定范围内的序列号已全部使用完，返回-1
                cmppUtil.static_sequenceId = 0
                return -1
            else:
                cmppUtil.static_sequenceId = 0
        return cmppUtil.static_sequenceId

    @staticmethod
    def delSequenceId(seq_id):
        if int(seq_id) in cmppUtil.sequenceID_list:
            cmppUtil.sequenceID_list.remove(int(seq_id))

    # 生成时间戳明文格式:"MMDDHHMMSS"
    @staticmethod
    def getTimestamp():
        return time.strftime("%m%d%H%M%S", time.localtime(time.time()))

    # 生成MD5 source_addr + 9字节0 + secret + timestamp
    @staticmethod
    def getAuthenticatorSource(sp_id, secret):
        return hashlib.md5(sp_id + 9*b'\x00' + secret + cmppUtil.getTimestamp()).digest()

    # 写入指定长度的字符串，不足补0
    @staticmethod
    def writeString(fd, msgbuffer, msglen):
        pass

    @staticmethod
    def generateSequenceId():
        pass

    @staticmethod
    def socketClose(socketFd):
        socketFd.shutdown(socket.SHUT_RDWR)
        socketFd.close()


