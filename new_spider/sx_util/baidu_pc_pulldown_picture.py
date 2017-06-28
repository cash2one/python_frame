# -*- coding: utf8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import datetime
import sys
from spider.baidusx import config
reload(sys)
sys.setdefaultencoding('utf-8')

'''
    关闭预测 截下拉
'''
class Baidu_pc_pulldown_picture(object):

    def __init__(self):
        pass

    def find_pulldown_picture(self, keyword):
        print "pulldown get picture"
        starttime = datetime.datetime.now()
        path = config.phantomjs_location
        browser = webdriver.PhantomJS(executable_path=path)
        try:
            browser.set_page_load_timeout(20)
            browser.maximize_window()  # 设置全屏

            browser.get("https://www.baidu.com/")    # Load page
            # browser.find_elements_by_class_name("bdnuarrow").
            # print browser.find_element_by_id("cp").text  # 获取元素的文本信息
            # browser.find_element_by_id('kw').clear()  # 用于清除输入框的内容

            browser.find_element_by_id('kw').send_keys(u''+keyword)  # 在输入框内输入
            # browser.find_element_by_id('kw').send_keys(Keys.ENTER)  # 用于点击按钮

            time.sleep(1)
            js = "var products = document.querySelectorAll('.bdsugbg');" \
                 "products[0].style.display = 'block' "

            browser.execute_script(js)

            picture_base = browser.get_screenshot_as_base64()

            # html_source = browser.page_source
            # print(html_source)
            # browser.save_screenshot(save_fn)
            browser.close()
            browser.quit()

            endtime = datetime.datetime.now()
            print "pulldown picture time:"+str((endtime - starttime).seconds)
            return picture_base
        except Exception as e:
            print e
            browser.quit()
            return ""

if __name__ == "__main__":
    sx = Baidu_pc_pulldown_picture()
    picture_base = sx.find_pulldown_picture("招聘")
    import base64
    imgdata = base64.b64decode(picture_base)
    # print imgdata
    file = open('svx_4.png', 'wb')
    file.write(imgdata)
    file.close()

