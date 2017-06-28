# -*- coding: utf8 -*-
from selenium import webdriver

import os
import sys
# PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# sys.path.append(PROJECT_PATH)
# sys.path.append(os.path.join(PROJECT_PATH, 'screenshot'))

import datetime
import time
import config
import base64
from selenium.common.exceptions import TimeoutException
reload(sys)
sys.setdefaultencoding('utf-8')

from screenshot.baiduPcFunction import PcFunction
from screenshot.baiduMobileFunction import MobileFunction
from screenshot.utilsFunction import UtilsFunction
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class FindPicture(object):

    def __init__(self):
        self.baiduPc = PcFunction()
        self.baiduMobile = MobileFunction()
        self.util = UtilsFunction()
        pass

    def picture_screenshot_html(self, keyword, ckurl, searchDevice, spidertype, searchPage, returnType):
        starttime = datetime.datetime.now()
        picturedata = None
        try:
            # pc
            if int(searchDevice) == 1:

                browser = webdriver.Firefox(executable_path=config.geckodriverPath)
                browser.set_page_load_timeout(config.page_load_timeout)
                browser.set_script_timeout(config.script_timeout)

                browser.maximize_window()
                browser.get(config.baiduPcUrl)  # Load page
                browser.find_element_by_id('kw').clear()  # 用于清除输入框的内容
                browser.find_element_by_id('kw').send_keys(u''+keyword)  # 在输入框内输入
                browser.find_element_by_id('su').click()  # 用于点击按钮
                browser.find_element_by_id('su').submit()  # 用于提交表单内容

                # browser.get(url)    # Load page
                # print browser.current_url
                self.util.fullloaded(browser)

                jsClientWidth  = '''return document.body.clientWidth'''
                tatalWidth = browser.execute_script(jsClientWidth)
                # print tatalWidth
                jsScrollHeight = '''return  document.body.parentNode.scrollHeight'''
                tatalHeight = browser.execute_script(jsScrollHeight)
                # print tatalHeight

                for currentpage in xrange(1, searchPage+1):
                    print currentpage
                    html_source = browser.page_source  # 页面
                    # 根据页面返回排名 数组
                    rankitem = self.baiduPc.getRankListByHtmlPc(html_source, ckurl, spidertype)
                    ranklist = rankitem['rankList']
                    if len(ranklist) > 0:
                        picturedata = self.baiduPc.getPictureAndScreenPc(browser, ranklist, tatalWidth, tatalHeight, returnType)
                        break
                    else:
                        browser.find_element_by_class_name("n").click()
                        self.util.fullloaded(browser)
            else:
                # mobile
                firefoxProfile = webdriver.FirefoxProfile()
                # 设置 useragent
                firefoxProfile.set_preference("general.useragent.override",
                                              config.mobileUserAgent)
                browser = webdriver.Firefox(firefox_profile=firefoxProfile, executable_path=config.geckodriverPath)

                browser.set_page_load_timeout(config.page_load_timeout)
                browser.set_script_timeout(config.script_timeout)

                browser.set_window_size(config.baiduMobileWidth, config.baiduMobileHeight)
                browser.get(config.baiduMobileUrl)  # Load page

                # browser.add_cookie(cookie)
                browser.find_element_by_id('index-kw').clear()  # 用于清除输入框的内容
                browser.find_element_by_id('index-kw').send_keys(u'' + keyword)  # 在输入框内输入
                browser.find_element_by_id('index-bn').click()  # 用于点击按钮

                # ActionChains(browser).key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys("m").perform()
                # browser.find_element_by_tag_name("body").send_keys(Keys.CONTROL, Keys.SHIFT, 'm')  # ctrl + x 剪切输入框内容
                self.util.fullloaded(browser)

                for currentpage in xrange(1, searchPage + 1):
                    print currentpage
                    print browser.current_url
                    html_source = browser.page_source  # 页面
                    # 根据页面返回排名 数组
                    rankitem = self.baiduMobile.getRankListByHtmlMobile(html_source, ckurl, spidertype)
                    ranklist = rankitem['rankList']
                    nextPageUrl = rankitem['nextPageUrl']

                    if len(ranklist) > 0:
                        picturedata = self.baiduMobile.getPictureAndScreenMobile(browser, ranklist,
                                                config.baiduMobileWidth, config.baiduMobileHeight, returnType)
                        break
                    else:
                        # browser.find_element_by_class_name("new-nextpage-only").click()
                        browser.get(nextPageUrl)
                        self.util.fullloaded(browser)
            # cookiejs = "sessionStorage.clear(); " \
            #            "localStorage.clear();"
            # browser.execute_script(cookiejs)
            browser.delete_all_cookies()
            browser.close()
            browser.quit()

            endtime = datetime.datetime.now()
            print ((endtime - starttime).seconds)
            # print picturedata
            if picturedata:
                return picturedata
        except Exception, e:
            # 很有可能
            print e
            print "testScreenshot"
            browser.close()
            browser.quit()


if __name__ == "__main__":
    sx = FindPicture()
    # url = '''https://www.baidu.com'''
    # keyword, ckurl, searchDevice, spidertype, searchPage, returnType
    data = sx.picture_screenshot_html("租房", ".fang.com", 2, 1, 5 ,"1100")

    # data = sx.picture_screenshot_html("贝因美", ".qqbaobao.com", 2, 1, 5, "1100")

    # data = sx.picture_screenshot_html("招聘", ".zhaopin.com", 2, 1, 5, "1100")

    # data = sx.picture_screenshot_html("招聘", ".zhaopin.com", 1, 1, 5, "1111")
    print "result"
    if data is not None:
        sx_datalist = str(data).split("||||")
        lengthdata = len(sx_datalist)
        for i in xrange(0, lengthdata-1):
            picture = sx_datalist[i]
            if picture != "":
                imgdata = base64.b64decode(picture)
                file = open('PC'+str(i)+'.png', 'wb')
                file.write(imgdata)
                file.close()
    else:
        print "no rank "
    # 调用 windows 命令行
    import os
    command ="taskkill /f /im WerFault.exe /t"  #在command = "这里填写要输入的命令"
    os.system(command)
