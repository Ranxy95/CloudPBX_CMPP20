#!/usr/bin/python
# -*- coding: utf-8 -*-
import struct
import sys
import threading
import time

from cmpp_manager import cmppManager
from cmpp_config import cmppConfig
import LogDeal
import MonitorConfig
from cmpp_util import *


class cmppRun(threading.Thread):
    def __init__(self, cmppData, output):
        threading.Thread.__init__(self)
        self.logjob = output

        # 添加一个空格，可避免闪信显示内容尾部的一个乱码
        self.msgContent = str(cmppData['card_content'])
        self.callee = str(cmppData['callee'])

    def run(self):
        cmppManager.sendMessage(self.msgContent, self.callee, self.logjob)


# if __name__ == "__main__":
# DealXmlConfig = MonitorConfig.dealXmlConfig
# LogQueue = LogDeal.LogQueue(0)
#
# LogRedirectThread = LogDeal.LogRedirectThread(LogQueue,DealXmlConfig.LogFilePath)
# LogRedirectThread.start()
# LogQueue.info("[%s] main-line:%s Thread start:%s" % (str(threading.current_thread().name), \
#                                                          str(sys._getframe().f_lineno), \
#                                                          str(LogRedirectThread)))
# LogQueue.stdoutfile = LogRedirectThread.stdoutfile
#
#
# conf = cmppConfig()
# cmppdata = {"callee": "10086", "card_content": "靓仔，请勿挂机！"}
# for i in range(2):
#     cmppdata["message"] = "靓仔，请勿挂机！" + str(i)
#     cmppRun(cmppdata, LogQueue).start()
#     # time.sleep(1)

tes = "123456"
tmp = tes.decode('utf-8').encode('utf-16be')
print len(tes)
print str(len(tmp))


tes = "呼叫测试123"
tmp = tes.decode('utf-8').encode('utf-16be')
msg_len = len(tmp)
print len(tes)
print str(len(tmp))
print tmp

con = struct.pack('!{length}s'.format(length=msg_len), tmp)
print con



