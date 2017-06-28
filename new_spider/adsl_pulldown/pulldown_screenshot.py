# -*- coding: utf8 -*-
from selenium import webdriver

import os
import sys
# PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# sys.path.append(PROJECT_PATH)
# sys.path.append(os.path.join(PROJECT_PATH, 'screenshot'))

import datetime
import time
import sxconfig
import base64
from selenium.common.exceptions import TimeoutException
reload(sys)
sys.setdefaultencoding('utf-8')

import baiduPcFunction
import baiduMobileFunction
import utilsFunction

import json
class FindPicture(object):

    def __init__(self):
        self.baiduPc = baiduPcFunction.PcFunction()
        self.baiduMobile = baiduMobileFunction.MobileFunction()
        self.util = utilsFunction.UtilsFunction()

    def removeDir(self, dirPath):
        '''
        删除文件夹下面的文件
        :param dirPath:
        :return:
        '''
        if not os.path.isdir(dirPath):
            return
        files = os.listdir(dirPath)
        try:
            for file in files:
                filePath = os.path.join(dirPath, file)
                if os.path.isfile(filePath):
                    os.remove(filePath)
                elif os.path.isdir(filePath):
                    os.removedirs(filePath)
            os.rmdir(dirPath)
        except Exception, e:
            print e

    def picture_screenshot_html(self, keyword, searchDevice, returnType, targetKeywords=""):
        # 删除phantomjs 的缓存文件
        self.removeDir(sxconfig.phantomJsLog)
        starttime = datetime.datetime.now()
        picturedata = None
        html_source = None
        try:
            browser = webdriver.PhantomJS(executable_path=sxconfig.phantomJs)
            browser.set_page_load_timeout(sxconfig.page_load_timeout)
            browser.set_script_timeout(sxconfig.script_timeout)
            browser.delete_all_cookies()

            if int(searchDevice) == 1:
                browser.maximize_window()
                # 关闭预测
                browser.get(sxconfig.baiduPcGaoJi)
                options = browser.find_elements_by_tag_name("option")
                # 1,2,3 一页 条数  4,5，6 输入法  7,8 预测
                options[7].click()
                browser.find_element_by_id("save").click()
                self.util.fullloaded(browser)
                # browser.switch_to_alert().accept()
                # browser.switch_to_default_content()

                # browser.get(sxconfig.baiduPcUrl)
                browser.find_element_by_id('kw').clear()  # 用于清除输入框的内容
                browser.find_element_by_id('kw').send_keys(u''+keyword)  # 在输入框内输入
                self.util.fullloaded(browser)

                picturedata = self.baiduPc.getDataPullDown(browser, returnType, targetKeywords, keyword)
                html_source = browser.page_source

            else:
                browser.set_window_size(sxconfig.baiduMobileWidth, sxconfig.baiduMobileHeight)
                browser.get(sxconfig.baiduMobileUrl)  # Load page

                self.clear_storage(browser)
                browser.find_element_by_id('index-kw').clear()  # 用于清除输入框的内容
                browser.find_element_by_id('index-kw').send_keys(u'' + keyword)  # 在输入框内输入
                self.util.fullloaded(browser)
                picturedata = self.baiduMobile.getDataPullDown(browser, returnType, targetKeywords, keyword)
                html_source = browser.page_source

            self.clear_storage(browser)
            browser.delete_all_cookies()
            browser.close()
            endtime = datetime.datetime.now()
            print ((endtime - starttime).seconds)
            if picturedata:
                picturedata["html"] = html_source
                return json.dumps(picturedata)
            # else:
            #     return -2
        except Exception, e:
            browser.close()
            return -1
            # browser.quit()

    def closeForeCast(self, browser):
        browser.get(sxconfig.baiduPcGaoJi)
        options = browser.find_elements_by_tag_name("option")
        # 1,2,3 一页 条数  4,5，6 输入法  7,8 预测
        options[7].click()
        browser.find_element_by_id("save").click()
        browser.switch_to_alert().accept()
        # browser.switch_to_default_content()

    @staticmethod
    def clear_storage(browser):
        js = "localStorage.clear(); " \
             "sessionStorage.clear();"
        browser.execute_script(js)
        time.sleep(1)

if __name__ == "__main__":
    sx = FindPicture()
    # url = '''https://www.baidu.com'''
    # keyword, ckurl, searchDevice, spidertype, searchPage, returnType
    # data = sx.picture_screenshot_html("租房", ".51job.com", 2, 1, 5 ,"1100")

    # data = sx.picture_screenshot_html("招聘", "http://www.suzhoubank.com/", 1, 1, 5, "1100", "招聘网站")
    # data = sx.picture_screenshot_html("招聘", "www.job5156.com", 2, 1, 5, "1111")
    # data = sx.picture_screenshot_html("招聘", "www.hrm.cn", 2, 1, 5, "1111")

    # data = sx.picture_screenshot_html("招聘", "m.yingjiesheng.com", 2, 1, 5, "0010")
    # data = sx.picture_screenshot_html("贝因美", ".qqbaobao.com", 2, 1, 5, "1010")

    # data = sx.picture_screenshot_html("招聘", ".zhaopin.com", 1, 1, 5, "1100", "招聘网站")
    # data = sx.picture_screenshot_html("招聘", ".qlrc.com", 1, 1, 5, "1111")
    # targetKeywords = "招聘网,招聘图片,招聘海报"
    # data = sx.picture_screenshot_html("js", 1, "0011", targetKeywords=",")

    # data = sx.picture_screenshot_html("奥迪", 1, "1111", targetKeywords="一汽,图片,海报")
    # "奥迪"

    # data = sx.picture_screenshot_html("招聘", 1, "1111", targetKeywords="网站,图片")

    data = sx.picture_screenshot_html("双摄像头手机", 2, "0011", targetKeywords="双摄像头手机vivo x9热卖")

    if data is not None:
        sx_dataDict = json.loads(data)
        # print "end"
        print sx_dataDict["rankIndex"]

        rankIndex = sx_dataDict["rankIndex"]
        # print rankIndex
        tempIndex = 15
        for index in rankIndex:
            if tempIndex > index["rank"]:
                tempIndex = index["rank"]
        print "tempIndex:"+str(tempIndex)

        i = 1
        if "capture" in sx_dataDict:
            sxcapture = base64.b64decode(sx_dataDict["capture"])
            file = open("%scapture.png" % i, "wb")
            file.write(sxcapture)
            file.close()
        if "capture_red" in sx_dataDict:
            sxcapture = base64.b64decode(sx_dataDict["capture_red"])
            file = open("%scapture_red.png" % i, "wb")
            file.write(sxcapture)
            file.close()
        if "screenshot" in sx_dataDict:
            sxcapture = base64.b64decode(sx_dataDict["screenshot"])
            file = open("%sscreenshot.png" % i, "wb")
            file.write(sxcapture)
            file.close()
        if "screenshot_red" in sx_dataDict:
            sxcapture = base64.b64decode(sx_dataDict["screenshot_red"])
            file = open("%sscreenshot_red.png" % i, "wb")
            file.write(sxcapture)
            file.close()

    else:
        print "no rank "
    import os
    # command = "taskkill /f /im firefox.exe /t"  # 在command = "这里填写要输入的命令"
    os.system("taskkill /f /im phantomjs.exe /t")
    # 调用 windows 命令行
    # import os
    # command = "taskkill /f /im firefox.exe /t"  # 在command = "这里填写要输入的命令"
    # os.system(command)
    # command = "taskkill /f /im WerFault.exe /t"  # 在command = "这里填写要输入的命令"
    # os.system(command)
