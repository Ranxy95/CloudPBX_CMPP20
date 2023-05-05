#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@cmpp需要的配置信息
"""

from cmpp_handle import *
from cmpp_config import cmppConfig
from cmpp_keepalive import cmppKeepAlive


# 全局的socket连接标识
socketFd_MT = 0
socketFd_MO = 0


class cmppManager(object):
    IP = ""
    PORT = "7890"
    SRCID = ""
    SPID = ""
    SERVICEID = ""
    PWD = ""

    @staticmethod
    def initConfig():
        conf = cmppConfig()
        cmppManager.setServerIP(conf.getMasUrl())
        cmppManager.setServerPort(conf.getMasPort())
        cmppManager.setSrcID(conf.getSrcId())   # 服务代码，最终显示为主叫号码
        cmppManager.setSPID(conf.getSpId())
        cmppManager.setServiceID(conf.getServiceId())
        cmppManager.setPassword(conf.getShareSecret())

    """
    @发送短信,也是短信模块的入口函数
    """
    @staticmethod
    def sendMessage(message, number, output):
        """
        :param message: 需要发送的内容
        :param number: 接收短信的被叫号码
        :param output:
        :return:
        """
        # 注：MT/MO连接的socketFd不同

        global socketFd_MT
        global socketFd_MO

        cmppManager.initConfig()
        cmpp_handle = cmppHandle(output)
        cmpp_net = cmppNet(output)

        # 创建发送信息的连接
        if not connectedISMG['MT']:
            dataPack = {"ip":cmppManager.IP, "port":cmppManager.PORT, "version":CMPP_CONNECT_MT}
            ret, socketFd_MT = cmpp_handle.connectISMG(dataPack)

            if ret >= 0 and socketFd_MT > 0:
                connectedISMG['MT'] = True
                keepAliveSockets.append(socketFd_MT)
                output.info("cmpp_manager-Line[%s] connected ISMG MT success, socket:%s" %
                            (str(sys._getframe().f_lineno),socketFd_MT))

                # TODO 开启新的线程，负责保活，以及发送消息
                # cmpp_handle.handleService(socketFd_MT, output)
            else:
                output.info("cmpp_manager-Line[%s] connected ISMG MT failed" % (str(sys._getframe().f_lineno)))
                cmpp_net.popSocketFd(socketFd_MT)
                return -1

        # 创建接收状态报告的连接
        if not connectedISMG['MO']:
            dataPack = {"ip": cmppManager.IP, "port": cmppManager.PORT, "version": CMPP_CONNECT_MO}
            ret, socketFd_MO = cmpp_handle.connectISMG(dataPack)
            if ret >= 0 and socketFd_MO > 0:
                connectedISMG['MO'] = True
                # keepAliveSockets.append(socketFd_MO)
                output.info("cmpp_manager-Line[%s] connected ISMG MO success, socket:%s" %
                            (str(sys._getframe().f_lineno),socketFd_MO))

                # 认证成功后，开启新的线程处理状态报告,以及保活
                # cmpp_handle.deliverService(socketFd_MO, output)
            else:
                output.info("cmpp_manager-Line[%s] connected ISMG MO failed" % (str(sys._getframe().f_lineno),))
                cmpp_net.popSocketFd(socketFd_MO)
                return -1

        if not connectedISMG["run"]:
            connectedISMG["run"] = True
            cmpp_handle.handleService(socketFd_MT, output)
            cmpp_handle.deliverService(socketFd_MO, output)

        # 已建立连接，可以提交信息
        ret = cmpp_handle.submitMessage(socketFd_MT, message, number)
        # if ret == 0:
        #     output.info("cmpp_manager-Line[%s] send message success" % (str(sys._getframe().f_lineno),))
        # else:
        #     output.info("cmpp_manager-Line[%s] send message failed" % (str(sys._getframe().f_lineno),))

        # 保活：发送CMPP_ACTIVE_TEST进行链路检测, 避免重复运行该线程
        # if not connectedISMG["keepAlive"]:
        #     connectedISMG["keepAlive"] = True
        #     time.sleep(5)
        #     keepAlive = cmppKeepAlive(output)
        #     keepAlive.start()

    # 网关IP
    @staticmethod
    def getServerIP():
        return cmppManager.IP

    @staticmethod
    def setServerIP(ip):
        cmppManager.IP = ip

    # 网关端口
    @staticmethod
    def getServerPort():
        return cmppManager.PORT

    @staticmethod
    def setServerPort(port):
        cmppManager.PORT = port

    # 服务代码
    @staticmethod
    def getSrcID():
        return cmppManager.SRCID

    @staticmethod
    def setSrcID(srcid):
        cmppManager.SRCID = srcid

    # 企业代码
    @staticmethod
    def getSPID():
        return cmppManager.SPID

    @staticmethod
    def setSPID(spid):
        cmppManager.SPID = spid

    # 业务代码
    @staticmethod
    def getServiceID():
        return cmppManager.SERVICEID

    @staticmethod
    def setServiceID(serviceid):
        cmppManager.SERVICEID = serviceid

    # 密码
    @staticmethod
    def getPassword():
        return cmppManager.PWD

    @staticmethod
    def setPassword(pwd):
        cmppManager.PWD = pwd


if __name__ == "__main__":
    cmppManager.sendMessage("Helloworld", "10086")
