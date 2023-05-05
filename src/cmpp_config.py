#!/usr/bin/python
# -*- coding: UTF-8 -*-
import struct
import xml.dom.minidom
import sys
import datetime
import os


class cmppConfig:
    def __init__(self):
        self.CustomData = {}  # 包含一些数值参数
        self.SP_Id = "923252"
        self.MsgId = 0  # 信息标识，由SP接入的短信网关本身产生，本处填空
        self.Pktotal = 1
        self.Pknumber = 1
        self.RegisteredDelivery = 1
        self.Msglevel = 1

        self.ServiceId = ""  # 10位业务标识，用于查询
        self.FeeUserType = 0
        self.FeeTerminalId = ""
        self.TPpId = 0  # GSM协议类型,一般文本的时候设0,铃声图片设1
        self.TPudhi = 0  # 0不包含头部信息,1包含头部信息
        self.MsgFmt = 24  # 消息格式,0或8为普通短信,闪信为24
        self.MsgSrc = "923252"  # SP_Id,消息内容来源,6位的企业代码

        self.FeeType = "01"  # 资费类别按条计信息费, 与FeeUserType有关
        self.FeeCode = "5"  # 资费代码(以分为单位)
        self.ValIdTime = ""  # 存活有效期
        self.AtTime = ""  # 定时发送时间
        self.SrcId = ""  # 主叫号码，设置为caller
        self.DestUsrtl = 1  # 接收信息的用户数量(小于100个用户)

        self.DestTerminalId = ""  # 接收短信的MSISDN号码,对应为callee
        self.MsgLength = 0
        self.MsgContent = ""
        self.Reserve = ""
        self.Version = "0x00"

        self.ShareSecret = "Sc_923252"
        self.mas_url = "127.0.0.1"
        self.mas_port = "7890"
        self.LogFilePath = "/var/svc9000/log/softswitch/cmpp.log"  # 日志打印

        # TODO 超时重连机制待完善
        self.timeout = 60
        self.timeout_number = 3
        self.timeout_deliver = 48   # 等待状态报告时间缺省48小时

        self.parseXml()

    def parseXml(self):
        try:
            conf_path = "/svc9000/monitor/cmpp.conf.xml"
            # conf_path = os.getcwd() + "/cmpp.conf.xml"
            dom = xml.dom.minidom.parse(conf_path)
        except BaseException as e:
            try:
                rfind = self.LogFilePath.rfind("/")
                if rfind != -1 and not os.path.exists(self.LogFilePath[0:rfind + 1]):
                    os.makedirs(self.LogFilePath[0:rfind + 1])

                fo = open(self.LogFilePath, "a", 0)
                logdata = str("%s <critical> CMPPConfig-line:%s ERROR:%s\n" %
                              (str(datetime.datetime.now()),
                               str(sys._getframe().f_lineno),
                               str(e)
                               ))
                print(logdata)
                fo.write(logdata)
                fo.close()
            except BaseException:
                pass
            return

        root = dom.documentElement
        settings = root.getElementsByTagName("settings")
        setting = settings[0]
        params = setting.getElementsByTagName("param")

        for param in params:
            ParamName = param.getAttribute("name")
            ParamValue = param.getAttribute("value").encode("utf-8")

            # debug
            # print("name:{0}, value:{1}".format(ParamName, ParamValue))

            if ParamName == "SP_Id":
                self.SP_Id = ParamValue
            elif ParamName == "Msg_Id":
                self.MsgId = ParamValue
            elif ParamName == "Pk_total":
                self.Pktotal = ParamValue
            elif ParamName == "Pk_number":
                self.Pknumber = ParamValue
            elif ParamName == "Registered_Delivery":
                self.RegisteredDelivery = ParamValue
            elif ParamName == "Msg_level":
                self.Msglevel = ParamValue
            if ParamName == "Service_Id":
                self.ServiceId = ParamValue
            elif ParamName == "Fee_UserType":
                self.FeeUserType = ParamValue
            elif ParamName == "Fee_terminal_Id":
                self.FeeTerminalId = ParamValue
            elif ParamName == "TP_pId":
                self.TPpId = ParamValue
            elif ParamName == "TP_udhi":
                self.TPudhi = ParamValue
            elif ParamName == "Msg_Fmt":
                self.MsgFmt = ParamValue
            elif ParamName == "Msg_src":
                self.MsgSrc = ParamValue
            elif ParamName == "FeeType":
                self.FeeType = ParamValue
            elif ParamName == "FeeCode":
                self.FeeCode = ParamValue
            elif ParamName == "ValId_Time":
                self.ValIdTime = ParamValue
            elif ParamName == "At_Time":
                self.AtTime = ParamValue
            elif ParamName == "Src_Id":
                self.SrcId = ParamValue
            elif ParamName == "DestUsr_tl":
                self.DestUsrtl = ParamValue
            elif ParamName == "Dest_terminal_Id":
                self.DestTerminalId = ParamValue
            elif ParamName == "Msg_Length":
                self.MsgLength = ParamValue
            elif ParamName == "Msg_Content":
                self.MsgContent = ParamValue
            elif ParamName == "Reserve":
                self.Reserve = ParamValue
            elif ParamName == "Version":
                self.Version = ParamValue
            elif ParamName == "Share_secret":
                self.ShareSecret = ParamValue
            elif ParamName == "mas_url":
                self.mas_url = ParamValue
            elif ParamName == "mas_port":
                self.mas_port = ParamValue
            elif ParamName == "log_file_path":
                self.LogFilePath = ParamValue
            elif ParamName == "timeout":
                self.timeout = ParamValue
            elif ParamName == "timeout_number":
                self.timeout_number = ParamValue
            elif ParamName == "timeout_deliver":
                self.timeout_deliver = ParamValue
            self.CustomData[ParamName.encode("utf-8")] = ParamValue

    # get
    def getSpId(self):
        return self.SP_Id

    def getMsgId(self):
        return self.MsgId

    def getPktotal(self):
        return self.Pktotal

    def getPknumber(self):
        return self.Pknumber

    def getRegisteredDelivery(self):
        return self.RegisteredDelivery

    def getMsglevel(self):
        return self.Msglevel

    def getServiceId(self):
        return self.ServiceId

    def getFeeUserType(self):
        return self.FeeUserType

    def getFeeTerminalId(self):
        return self.FeeTerminalId

    def getTPpId(self):
        return self.TPpId

    def getTPudhi(self):
        return self.TPudhi

    def getMsgFmt(self):
        return self.MsgFmt

    def getMsgSrc(self):
        return self.MsgSrc

    def getFeeType(self):
        return self.FeeType

    def getFeeCode(self):
        return self.FeeCode

    def getValIdTime(self):
        return self.ValIdTime

    def getAtTime(self):
        return self.AtTime

    def getSrcId(self):
        return self.SrcId

    def getDestUsrtl(self):
        return self.DestUsrtl

    def getDestTerminalId(self):
        return self.DestTerminalId

    def getMsgLength(self):
        return self.MsgLength

    def getMsgContent(self):
        return self.MsgContent

    def getReserve(self):
        return self.Reserve

    def getVersion(self):
        return self.Version

    def getLogFilePath(self):
        return self.LogFilePath

    def getShareSecret(self):
        return self.ShareSecret

    def getMasUrl(self):
        return self.mas_url

    def getMasPort(self):
        return self.mas_port

    def getTimeout(self):
        return self.timeout

    def getTimeoutNumber(self):
        return self.timeout_number

    def getTimeoutDeliver(self):
        return self.timeout_deliver

    # set
    def setSpId(self, SpId):
        self.SP_Id = SpId

    def setMsgId(self, MsgId):
        self.MsgId = MsgId

    def setPktotal(self, Pktotal):
        self.Pktotal = Pktotal

    def setPknumber(self, Pknumber):
        self.Pknumber = Pknumber

    def setRegisteredDelivery(self, RegisteredDelivery):
        self.RegisteredDelivery = RegisteredDelivery

    def setMsglevel(self, Msglevel):
        self.Msglevel = Msglevel

    def setServiceId(self, ServiceId):
        self.ServiceId = ServiceId

    def setFeeUserType(self, FeeUserType):
        self.FeeUserType = FeeUserType

    def setFeeTerminalId(self, FeeTerminalId):
        self.FeeTerminalId = FeeTerminalId

    def setTPpId(self, TPpId):
        self.TPpId = TPpId

    def setTPudhi(self, TPudhi):
        self.TPudhi = TPudhi

    def setMsgFmt(self, MsgFmt):
        self.MsgFmt = MsgFmt

    def setMsgSrc(self, MsgSrc):
        self.MsgSrc = MsgSrc

    def setFeeType(self, FeeType):
        self.FeeType = FeeType

    def setFeeCode(self, FeeCode):
        self.FeeCode = FeeCode

    def setValIdTime(self, ValIdTime):
        self.ValIdTime = ValIdTime

    def setAtTime(self, AtTime):
        self.AtTime = AtTime

    def setSrcId(self, SrcId):
        self.SrcId = SrcId

    def setDestUsrtl(self, DestUsrtl):
        self.DestUsrtl = DestUsrtl

    def setDestTerminalId(self, DestTerminalId):
        self.DestTerminalId = DestTerminalId

    def setMsgLength(self, MsgLength):
        self.MsgLength = MsgLength

    def setMsgContent(self, MsgContent):
        self.MsgContent = MsgContent

    def setReserve(self, Reserve):
        self.Reserve = Reserve

    def setVersion(self, Version):
        self.Version = Version

    def setLogFilePath(self, LogFilePath):
        self.LogFilePath = LogFilePath

    def setShareSecret(self, ShareSecret):
        self.ShareSecret = ShareSecret

    def setMasUrl(self, mas_url):
        self.mas_url = mas_url

    def setMasPort(self, mas_port):
        self.mas_port = mas_port

    def setTimeout(self, timeout):
        self.timeout = timeout

    def setTimeoutNumber(self, timeout_number):
        self.timeout_number = timeout_number

    def setTimeoutDeliver(self, timeout_deliver):
        self.timeout_deliver = timeout_deliver


dealXmlConfig = cmppConfig
