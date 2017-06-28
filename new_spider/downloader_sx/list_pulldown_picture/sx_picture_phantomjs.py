# -*- coding: utf8 -*-
from selenium import webdriver
import time
import datetime
from spider.baidusx import config
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#
# dcap = dict(DesiredCapabilities.PHANTOMJS)  # 设置userAgent
# dcap["phantomjs.page.settings.userAgent"] = (
# "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 ")
'''
    截下拉  和 百度列表页
'''

class FindPicture(object):

    def __init__(self):
        pass

    def picture_screenshot_html(self, keyword):
        try:
            # dcap = dict(DesiredCapabilities.PHANTOMJS)  # 设置userAgent
            # dcap["phantomjs.page.settings.cookie"] = ("BAIDUID=D433C649D164DEDCA91B1837BF41BBA8:FG=1; PSTM=1486553499; BIDUPSID=C858DA4168B1E3CDD01C477E81E5533E; sug=3; sugstore=0; ORIGIN=2; bdime=0; H_PS_645EC=94ed%2BsN%2FLRtGHrGi8wS877szecEq0GgslvywwVpHAWtf0k58rIo9aMX%2BTGuPR378cgaoGA; BDRCVFR[HHw4GR7hd6D]=mk3SLVN4HKm; BD_HOME=0; BD_UPN=12314353; BD_CK_SAM=1; PSINO=3; BDSVRTM=869; H_PS_PSSID=1444_19035_21087_22")
            # , desired_capabilities = dcap

            path = config.phantomjs_location
            browser = webdriver.PhantomJS(executable_path=path)

            # browser.delete_cookie()
            # browser.set
            # starttime = datetime.datetime.now()
            # browser = webdriver.Firefox(executable_path='C:\Program Files (x86)\Mozilla Firefox\geckodriver.exe')
            # browser.set_window_size(1200, 2600)

            browser.get("https://www.baidu.com/")    # Load page
            browser.find_element_by_id('kw').send_keys(u''+keyword)  # 在输入框内输入

            time.sleep(1)
            # 显示下拉
            js = "var products = document.querySelectorAll('.bdsugbg');" \
                 "if(products.length > 0){products[0].style.display = 'block';}"

            browser.execute_script(js)
            time.sleep(1)
            picture_base_pulldown = browser.get_screenshot_as_base64()
            html_pulldown = browser.page_source  # 页面

            browser.find_element_by_id('su').click()  # 用于点击按钮
            browser.find_element_by_id('su').submit()  # 用于提交表单内容

            browser.execute_script("""
                (function () {

                    var y = 0;
                    var step = 100;
                    window.scroll(0, 0);

                    function f() {
                        if (y < document.body.scrollHeight) {
                            y += step;
                            window.scroll(0, y);
                            setTimeout(f, 100);
                        } else {
                             window.scroll(0, 0);
                             document.title += "scroll-done";
                         }
                    }
                    setTimeout(f, 1000);
                })();
            """)
            time.sleep(1)

            sx_js = "localStorage.clear();"
            browser.execute_script(sx_js)

            base_64 = browser.get_screenshot_as_base64()    #图片
            html_source = browser.page_source           #页面

            browser.close()
            browser.quit()
            # endtime = datetime.datetime.now()
            # print ((endtime - starttime).seconds)
            return base_64+"||||"+html_source+"||||"+picture_base_pulldown+"||||"+html_pulldown
        except Exception, e:
            browser.quit()
            print e

if __name__ == "__main__":
    sx = FindPicture()
    data = str(sx.picture_screenshot_html("昂科威"))

    sx_result = data.split("||||")
    result_picture = sx_result[0]
    result_html = sx_result[1]
    result_picture_pulldown = sx_result[2]
    html_pulldown = sx_result[3]

    import base64
    imgdata = base64.b64decode(result_picture)
    # print imgdata
    file = open('17.png', 'wb')
    file.write(imgdata)
    file.close()

    imgdata2 = base64.b64decode(result_picture_pulldown)
    file2 = open('18.png', 'wb')
    file2.write(imgdata2)
    file2.close()