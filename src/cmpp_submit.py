#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@向短信网关发送消息
"""

import struct

from cmpp_header import cmppHeader
from cmpp_config import cmppConfig


class cmppSubmit(cmppHeader):

    def __init__(self, message, number):
        cmppHeader.__init__(self)
        conf = cmppConfig()

        self.MsgId = conf.getMsgId()  # 信息标示
        self.Pk_total = conf.getPktotal()  # 相同的msgId总数，从1开始
        self.Pk_number = conf.getPknumber()  # 想用的msgId序号，从1开始
        self.Registered_Delivery = conf.getRegisteredDelivery()

        self.Msg_level = conf.getMsglevel()  # 信息级别
        self.Service_Id = conf.getServiceId()  # 业务标示，企业代码
        self.Fee_UserType = conf.getFeeUserType()  # 用户计费类型， 谁接收，计谁的费

        # Fee_terminal_Id 是21字节的unsigned int
        self.Fee_terminal_Id = conf.getFeeTerminalId()  # 被计费的号码

        self.TP_pId = conf.getTPpId()
        self.TP_udhi = conf.getTPudhi()
        self.Msg_Fmt = conf.getMsgFmt()  # 信息格式 不建议使用15
        self.Msg_src = conf.getMsgSrc()  # 信息内容来源

        self.FeeType = conf.getFeeType()  # 资费类型， 默认为按条计费
        self.FeeCode = conf.getFeeCode()
        self.ValId_Time = conf.getValIdTime()  # 存活有效期，暂不支持
        self.At_Time = conf.getAtTime()  # 定时发送时间，暂不支持

        # 主叫号码，从C程序的FIFO传递过来
        self.Src_Id = conf.getSrcId()
        self.DestUsr_tl = conf.getDestUsrtl()  # 不支持群发
        # 被叫号码，从C程序的FIFO传递过来
        self.Dest_Terminal_Id = number  # 接收短信的MSISDN号码
        # 信息内容,注意：需要使用UCS2(即utf-16be)编码,中文才能正常显示！
        self.Msg_Content = message.decode('utf-8').encode('utf-16be')
        self.Msg_Length = str(len(message.decode('utf-8').encode('utf-16be')))
        # self.Msg_Length = str(len(message))

        self.Reserve = conf.getReserve()  # 保留

    def getMsgId(self):
        return self.MsgId

    def setMsgId(self, id):
        self.MsgId = id

    def getPk_total(self):
        return self.Pk_total

    def setPk_total(self, total):
        self.Pk_total = total

    def getPk_number(self):
        return self.Pk_number

    def setPk_number(self, number):
        self.Pk_number = number

    def getRegistered_Delivery(self):
        return self.Registered_Delivery

    def setRegistered_Delivery(self, Registered_Delivery):
        self.Registered_Delivery = Registered_Delivery

    def getMsg_level(self):
        return self.Msg_level

    def setMsg_level(self, Msg_level):
        self.Msg_level = Msg_level

    def getService_Id(self):
        return self.Service_Id

    def setService_Id(self, Service_Id):
        self.Service_Id = Service_Id

    def getFee_UserType(self):
        return self.Fee_UserType

    def setFee_UserType(self, Fee_UserType):
        self.Fee_UserType = Fee_UserType

    def getFee_terminal_Id(self):
        return self.Fee_terminal_Id

    def setFee_terminal_Id(self, Fee_terminal_Id):
        self.Fee_terminal_Id = Fee_terminal_Id

    def getTP_pId(self):
        return self.TP_pId

    def setTP_pId(self, TP_pId):
        self.TP_pId = TP_pId

    def getTP_udhi(self):
        return self.TP_udhi

    def setTP_udhi(self, TP_udhi):
        self.TP_udhi = TP_udhi

    def getMsg_Fmt(self):
        return self.Msg_Fmt

    def setMsg_Fmt(self, Msg_Fmt):
        self.Msg_Fmt = Msg_Fmt

    def getMsg_src(self):
        return self.Msg_src

    def setMsg_src(self, Msg_src):
        self.Msg_src = Msg_src

    def getFeeType(self):
        return self.FeeType

    def setFeeType(self, FeeType):
        self.FeeType = FeeType

    def getFeeCode(self):
        return self.FeeCode

    def setFeeCode(self, FeeCode):
        self.FeeCode = FeeCode

    def getValId_Time(self):
        return self.ValId_Time

    def setValId_Time(self, ValId_Time):
        self.ValId_Time = ValId_Time

    def getAt_Time(self):
        return self.At_Time

    def setAt_Time(self, At_Time):
        self.At_Time = At_Time

    def getSrc_Id(self):
        return self.Src_Id

    def setSrc_Id(self, Src_Id):
        self.Src_Id = Src_Id

    def getDestUsr_tl(self):
        return self.DestUsr_tl

    def setDestUsr_tl(self, DestUsr_tl):
        self.DestUsr_tl = DestUsr_tl

    def getDest_Terminal_Id(self):
        return self.Dest_Terminal_Id

    def setDest_Terminal_Id(self, Dest_Terminal_Id):
        self.Dest_Terminal_Id = Dest_Terminal_Id

    def getMsg_Length(self):
        return self.Msg_Length

    def setMsg_Length(self, Msg_Length):
        self.Msg_Length = Msg_Length

    def getMsg_Content(self):
        return self.Msg_Content

    def setMsg_Content(self, Msg_Content):
        self.Msg_Content = Msg_Content

    def getReserve(self):
        return self.Reserve

    def setReserve(self, Reserve):
        self.Reserve = Reserve

    # 字节流的形式写入buffer
    def writeToByteBuffer(self):
        length = self.getMsg_Length()
        return struct.pack('!III QBBB B10sB21s BBB6s 2s6s17s17s 21sB21sB{length}s8s'.format(length=length),
                           int(self.getTotalLength()), int(self.getCommandId()), int(self.getSequenceId()),
                           int(self.getMsgId()), int(self.getPk_total()), int(self.getPk_number()), int(self.getRegistered_Delivery()),
                           int(self.getMsg_level()), self.getService_Id(), int(self.getFee_UserType()), self.getFee_terminal_Id(),
                           int(self.getTP_pId()), int(self.getTP_udhi()), int(self.getMsg_Fmt()), self.getMsg_src(),
                           self.getFeeType(), self.getFeeCode(), self.getValId_Time(), self.getAt_Time(),
                           self.getSrc_Id(), int(self.getDestUsr_tl()), self.getDest_Terminal_Id(), int(self.getMsg_Length()),
                           self.getMsg_Content(), self.getReserve())

