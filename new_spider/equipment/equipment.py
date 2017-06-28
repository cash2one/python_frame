# -*- coding: utf8 -*-

import json
import base64
import os
import sys
import time
from datetime import datetime
reload(sys)
sys.setdefaultencoding('utf8')

import GetHtmlBaidu
import remove_file

class EquipmentManagement(object):

    def __init__(self):
        self.baiduGetHtml = GetHtmlBaidu.GetHtmlBaidu()
        # self.fileName = """D:/pyCharm/alter/new_spider/equipment/"""
        self.fileName = "C://python//equipment//"
        self.programfile = "%sadslprogram.txt" % self.fileName
        self.broadFile = "%sbroad.txt" % self.fileName
        self.changeIpSeconds = 600
        self.removeFile = remove_file.RemoveTemp()

    def run(self):
        startTime = time.time()
        while True:
            programfile = open(self.programfile, "r+")
            content = programfile.readlines()
            programfile.close()
            for i in xrange(0, 5):
                for adslprogram in content:
                    self.executeWindows(adslprogram)
            if startTime + self.changeIpSeconds < time.time():
                startTime = time.time()
                print "time_now:"+str(datetime.today())+";check"
                self.changeIpAndCheckEquipment()
                self.removeFile.removeTemp()

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
    downloader.run()

if __name__ == '__main__':
    main()
    # start_time = time.time()
    # while True:
    #     print datetime.today()
    #     main()
    #     time.sleep(1)
    #     # 切换ip
    #     if start_time + 300 < time.time():
    #         print "change ip"
    #         start_time = time.time()
    #         # "057114180549----875949"
    #         os.system("rasdial 宽带连接 /disconnect ")
    #         os.system("rasdial 宽带连接 057114180549 875949")
    #         time.sleep(10)
