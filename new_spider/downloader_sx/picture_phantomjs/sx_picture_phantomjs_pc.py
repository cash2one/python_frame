# -*- coding: utf8 -*-
from selenium import webdriver
import time
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#
# dcap = dict(DesiredCapabilities.PHANTOMJS)  # 设置userAgent
# dcap["phantomjs.page.settings.userAgent"] = (
# "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 ")
'''
    接下拉
'''

class FindPicturePc(object):

    def __init__(self):
        pass

    def picture_screenshot_html(self, url):
        try:
            path = u"E:\python\phantomjs-1.9.7-windows\phantomjs.exe"
            browser = webdriver.PhantomJS(executable_path=path)
            browser.set_page_load_timeout(20)
            browser.set_script_timeout(20)

            browser.get(url)

            # browser.get("https://www.baidu.com/")    # Load page
            #
            # browser.find_element_by_id('kw').clear()  # 用于清除输入框的内容
            # browser.find_element_by_id('kw').send_keys(u''+url)  # 在输入框内输入
            # browser.find_element_by_id('su').click()  # 用于点击按钮
            # browser.find_element_by_id('su').submit()  # 用于提交表单内容

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
            # time.sleep(1)
            # elem = browser.find_element_by_name("wd")
            # elem.send_keys(u"招聘")
            # browser.find_element_by_name("wd").click()

            base_64 = browser.get_screenshot_as_base64()    #图片
            html_source = browser.page_source           #页面

            cookiejs = "sessionStorage.clear(); " \
                       "localStorage.clear();"
            browser.execute_script(cookiejs)

            browser.close()
            browser.quit()
            # endtime = datetime.datetime.now()
            # print ((endtime - starttime).seconds)
            return base_64+"||||"+html_source
        except Exception, e:
            print e
            browser.close()
            browser.quit()

if __name__ == "__main__":
    pass
    # http: // codingpy.com
    # sx = FindPicture()
    # data = sx.picture_screenshot_html("https://www.baidu.com/s?wd=%E6%B7%AE%E5%AE%89%E4%BA%BA%E6%89%8D%E7%BD%91%E6%9C%80%E6%96%B0%E6%8B%9B%E8%81%98%E4%BF%A1%E6%81%AF&rsv_spt=1&rsv_iqid=0x9d684d0e0000cecd&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=78040160_5_pg&rsv_enter=0&oq=%E6%8B%9B%E8%81%98&rsv_t=7e39msJWAhkatRpmx%2F691Ir2BU1904ljWxb%2B3gy7cl5pNJsIfLHDNBbY7prEA2Kv9ez9OQ&rsv_pq=dd1bb49d0003954a&inputT=135689006&rsv_n=2&rsv_sug3=1298&bs=%E6%8B%9B%E8%81%98")
    # print data