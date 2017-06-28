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
import traceback
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

    def picture_screenshot_html(self, keyword, ckurl, searchDevice, spidertype, searchPage, returnType):
        # self.removeDir(sxconfig.phantomJsLog)
        starttime = datetime.datetime.now()
        picturedata = None
        try:
            if int(searchDevice) == 1:
                browser = webdriver.Firefox(executable_path=sxconfig.geckodriverPath)
                # browser = webdriver.PhantomJS(executable_path=sxconfig.phantomJs)
                browser.set_page_load_timeout(sxconfig.page_load_timeout)
                browser.set_script_timeout(sxconfig.script_timeout)

                browser.maximize_window()
                browser.get(sxconfig.baiduPcUrl)  # Load page
                browser.find_element_by_id('kw').clear()  # 用于清除输入框的内容
                browser.find_element_by_id('kw').send_keys(u''+keyword)  # 在输入框内输入
                browser.find_element_by_id('su').click()  # 用于点击按钮
                browser.find_element_by_id('su').submit()  # 用于提交表单内容
                time.sleep(1)
                self.util.fullloaded(browser)
                for currentpage in xrange(1, searchPage+1):
                    jsScrollHeight = '''return  document.body.parentNode.scrollHeight'''
                    tatalHeight = browser.execute_script(jsScrollHeight)

                    html_source = browser.page_source  # 页面
                    if int(returnType) > 0:
                        # 根据页面返回排名 数组
                        rankitem = self.baiduPc.getRankListByHtmlPc(html_source, ckurl, spidertype)
                        # print rankitem
                        ranklist = rankitem['rankList']
                        nextPageUrl = rankitem['nextPageUrl']
                        rank_result_list = rankitem['rank_result_list']

                        if len(ranklist) > 0:
                            picturedata = self.baiduPc.getPictureAndScreenPc(browser, ranklist, sxconfig.baiduPcWidth,
                                                                             tatalHeight, returnType, currentpage)
                            break
                        else:
                            if currentpage == 5:
                                break
                            if nextPageUrl is None:
                                break
                            browser.get(sxconfig.baiduPcUrl+nextPageUrl)
                            time.sleep(1)
                            self.util.fullloaded(browser)
                    else:
                        break
            else:
                # browser = webdriver.PhantomJS(executable_path=sxconfig.phantomJs)
                browser = webdriver.Firefox(executable_path=sxconfig.geckodriverPath)
                # mobile
                # firefoxProfile = webdriver.FirefoxProfile()
                # 设置 useragent
                # firefoxProfile.set_preference("general.useragent.override",
                #                               sxconfig.mobileUserAgent)
                # browser = webdriver.Firefox(firefox_profile=firefoxProfile, executable_path=sxconfig.geckodriverPath)

                browser.set_page_load_timeout(sxconfig.page_load_timeout)
                browser.set_script_timeout(sxconfig.script_timeout)

                browser.set_window_size(sxconfig.baiduMobileWidth, sxconfig.baiduMobileHeight)
                browser.get(sxconfig.baiduMobileUrl)  # Load page
                browser.find_element_by_id('index-kw').clear()  # 用于清除输入框的内容
                browser.find_element_by_id('index-kw').send_keys(u'' + keyword)  # 在输入框内输入
                browser.find_element_by_id('index-bn').click()  # 用于点击按钮
                time.sleep(2)
                self.util.fullloaded(browser)
                # time.sleep(3)
                for currentpage in xrange(1, searchPage + 1):
                    html_source = browser.page_source  # 页面
                    if int(returnType) > 0:
                        # 根据页面返回排名 数组
                        rankitem = self.baiduMobile.getRankListByHtmlMobile(html_source, ckurl, spidertype)
                        ranklist = rankitem['rankList']
                        nextPageUrl = rankitem['nextPageUrl']
                        rank_result_list = rankitem['rank_result_list']
                        if len(ranklist) > 0:
                            picturedata = self.baiduMobile.getPictureAndScreenMobile(browser, ranklist,
                                               sxconfig.baiduMobileWidth, sxconfig.baiduMobileHeight, returnType)
                            break
                        else:
                            if currentpage == 5:
                                break
                            if nextPageUrl is None:
                                break
                            browser.get(nextPageUrl)
                            time.sleep(1)
                            self.util.fullloaded(browser)
                    else:
                        break
            js = "localStorage.clear(); " \
                 "sessionStorage.clear();"
            browser.execute_script(js)
            browser.delete_all_cookies()
            browser.close()
            # browser.quit()
            endtime = datetime.datetime.now()
            print ((endtime - starttime).seconds)
            if picturedata:
                # picturedata["html"] = html_source
                # picturedata["page"] = currentpage
                if int(searchDevice) == 2:
                    if currentpage > 1:
                        picturedata["rank"] = (currentpage - 2) * 10 + 11 + int(rank_result_list[0]["rank"])
                    else:
                        picturedata["rank"] = rank_result_list[0]["rank"]
                else:
                    picturedata["rank"] = rank_result_list[0]["rank"]
                picturedata["show_url"] = rank_result_list[0]["show_url"]
                picturedata["real_address"] = rank_result_list[0]["real_address"]
                return json.dumps(picturedata)
            else:
                return -2
        except Exception:
            print traceback.format_exc()
            browser.close()
            return -1

if __name__ == "__main__":
    sx = FindPicture()
    # data = sx.picture_screenshot_html("倩碧", "https://clinique.tmall.com/", 2, 2, 5, "0011")
    # data = sx.picture_screenshot_html("固特异安乘好吗", "www.goodyear.com.cn", 2, 1, 5, "1111")
    data = sx.picture_screenshot_html("LAC美容保养保健品", "www.lac.com.sg", 1, 1, 5, "1010")

    if data is not None:
        sx_dataDict = json.loads(data)
        # print sx_dataDict["show_url"]
        print "rank:%s" % str(sx_dataDict["rank"])
        # print sx_dataDict["real_address"]

        i = 1
        if "capture" in sx_dataDict:
            with open("temp.txt", "wb") as f:
                f.write(sx_dataDict["capture"])
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
    # 调用 windows 命令行
    import os
    command = "taskkill /f /im firefox.exe /t"  # 在command = "这里填写要输入的命令"
    os.system(command)
    # command = "taskkill /f /im WerFault.exe /t"  # 在command = "这里填写要输入的命令"
    # os.system(command)
