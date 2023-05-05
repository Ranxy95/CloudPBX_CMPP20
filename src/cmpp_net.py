#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
创建相关网络socket，并进行一些消息的收发处理
和CMPP协议无关。独立模块
"""

import socket
import sys
from cmpp_util import *

class cmppNet(object):
    def __init__(self, output):
        self.logjob = output

    # 监听地址信息
    listenList = []

    # 连接地址信息
    connectList = []

    @staticmethod
    def startTcpService(flags, port, callbackFunc):
        """
        @remarks:创建socket服务端服务
        @flags  tcp/udp
        @port   监听端口
        @callbackFunc 收到消息的回调接口
        """
        for i in range(len(cmppNet.listenList)):
            tup = cmppNet.listenList[i]
            if tup[0] == port:
                if tup[1] > 0:
                    return tup[1]  # 返回socketFd
                else:
                    cmppNet.listenList.pop(i)

        sockFd = 0
        if flags == 0:
            sockFd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            sockFd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sockFd.bind(('127.0.0.1', port))
        except socket.error:
            # print('Failed to connect')
            sockFd = -1
        sockFd.listen(10)
        # create a thread to accept
        '''
            while True 
                connct, addr  = sockFd.accept()
        '''
        tup = (port, sockFd)
        cmppNet.listenList.append(tup)
        return sockFd

    def startTcpClient(self, flags, dataPack):
        ret = NET_STATUS['ok']
        ip = dataPack["ip"]
        port = int(dataPack["port"])
        version = dataPack["version"]

        for i in range(len(cmppNet.connectList)):
            tup = cmppNet.connectList[i]
            if tup[0] == ip and tup[1] == port and tup[3] == version:
                self.logjob.info("cmpp_net-Line[%s] - find alive socket and return" % (str(sys._getframe().f_lineno)))
                ret = NET_STATUS['find']
                return tup[2], ret

        if flags == 0:
            sockFd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            sockFd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 客户端开启心跳维护
        sockFd.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        try:
            sockFd.connect((ip, port))
        except socket.error:
            self.logjob.error("cmpp_net-Line[%s] - Failed to connect socket" % (str(sys._getframe().f_lineno)))
            sockFd = -1
            ret = NET_STATUS['false']

        if sockFd > 0:
            tup = (ip, port, sockFd, version)
            cmppNet.connectList.append(tup)
        return sockFd, ret

    '''
    发送消息
    '''
    @staticmethod
    def sendMsg(sockFd, msg):
        try:
            sockFd.sendall(msg)
        except BaseException as e:
            pass

    def recvMsg(self, sockFd, buf_len=0):
        msg_len = MAX_SOCKET_BUFFER_LEN
        recv_size = 0
        msg = ''
        try:
            if buf_len > 0:
                # TODO 是否会接收消息超时
                while recv_size < buf_len:
                    recv_data = sockFd.recv(buf_len-recv_size)
                    recv_size += len(recv_data)
                    msg += recv_data
            else:
                msg = sockFd.recv(MAX_SOCKET_BUFFER_LEN)

            # TODO 接收消息的长度如果等于0，不一定是socket断开，待解决
            # if len(msg) == 0:
            if msg == -1:
                self.logjob.warning("cmpp_net-Line[%s] - socket may disconnect......" % (str(sys._getframe().f_lineno)))
                self.popSocketFd(sockFd)
                return ''
            return msg
        except BaseException as e:
            self.logjob.info("cmpp_net-Line[%s] - socket recv msg failed, ERROR:%s" %
                             (str(sys._getframe().f_lineno), str(e)))
            self.popSocketFd(sockFd)
            return ''

    # 连接失败，接收消息失败时，删除已创建的socket fd
    def popSocketFd(self, socketFd):
        for i in range(len(cmppNet.connectList)):
            tup = cmppNet.connectList[i]
            if socketFd in tup:
                self.logjob.info("cmpp_net-Line[%s] - pop socketFD[%s] from connectList" %
                                 (str(sys._getframe().f_lineno), socketFd))

                cmppNet.connectList.pop(i)
                # 重置cmppManager.connectedISMG的socket连接标记为false，用于重连
                connectedISMG[tup[3]] = False
                break

            if socketFd in keepAliveSockets:
                keepAliveSockets.remove(socketFd)

        # cmppUtil().socketClose(socketFd)

