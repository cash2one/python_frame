# -*- coding: utf8 -*-

import json
import base64
import os
import sys
import time
from datetime import datetime
reload(sys)
sys.setdefaultencoding('utf8')

# import GetHtmlBaidu
# import remove_file

class EquipmentManagement(object):

    def __init__(self):
        pass

    def closeWarningFirefox(self):
        command = "taskkill /f /im firefox.exe /t"  # 在command = "这里填写要输入的命令"
        os.system(command)
        command = "taskkill /f /im WerFault.exe /t"  # 在command = "这里填写要输入的命令"
        os.system(command)

    def executeWindows(self, command):
        os.system(command)

    def changeIpAndCheckEquipment(self):
        for i in xrange(0, 5):
            self.changeBroadBand()
            network = self.baiduGetHtml.getHtml()
            if network:
                break
            else:
                if i == 4:
                    # 重启
                    self.executeWindows("shutdown -r -t 0")

    def checkProcessAll(self):
        task = os.popen("tasklist")
        taskcontent = task.read()
        if taskcontent.find("adsl"):
            return True
        else:
            return False

    def changeBroadBand(self):
        broadFile = open(self.broadFile, "r+")
        content = broadFile.readlines()
        broadWord = str(content[0])
        strCommandDisconnect = "rasdial 宽带连接 /disconnect ".encode("gbk")
        strCommand = "rasdial 宽带连接 %s" % broadWord
        sx = strCommand.encode("gbk")
        # print sx
        self.executeWindows(strCommandDisconnect)
        self.executeWindows(sx)

def main():
    downloader = EquipmentManagement()
    downloader.executeWindows("shutdown -r -t 0")

    # downloader.run()

if __name__ == '__main__':
    main()
