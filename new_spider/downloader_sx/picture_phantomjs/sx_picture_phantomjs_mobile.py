# -*- coding: utf8 -*-
from selenium import webdriver
import time
import datetime
import sys
from selenium.common.exceptions import TimeoutException
reload(sys)
sys.setdefaultencoding('utf-8')

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#
# dcap = dict(DesiredCapabilities.PHANTOMJS)  # 设置userAgent
# dcap["phantomjs.page.settings.userAgent"] = (
# "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:25.0) Gecko/20100101 Firefox/25.0 ")
'''
phantomjs 截图  直接截 url

'''
class FindPictureMobile(object):

    def __init__(self):
        pass

    def picture_screenshot_html(self, url):

        path = u"E:\python\phantomjs-1.9.7-windows\phantomjs.exe"
        try:
            starttime = datetime.datetime.now()

            dcap = dict(DesiredCapabilities.PHANTOMJS)  # 设置userAgent
            dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1")
            # , desired_capabilities = dcap

            browser = webdriver.PhantomJS(executable_path=path)
            browser.set_page_load_timeout(20)
            browser.set_script_timeout(20)

            browser.viewportSize = {'width': 414, 'height': 736}  # 重要这句！

            browser.get(url)    # Load page

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

            js = "var products = document.querySelectorAll('#page-hd');" \
                " products[0].setAttribute('style','background: #fff;');" \
                 "var products = document.querySelectorAll('#page-ft');" \
                 " products[0].setAttribute('style','background: #fff;');" \
                 "var products = document.querySelectorAll('#page-copyright');" \
                 " products[0].setAttribute('style','background: #fff;');" \

            browser.execute_script(js)

            base_64 = browser.get_screenshot_as_base64()    #图片
            html_source = browser.page_source           #页面

            cookiejs = "sessionStorage.clear(); " \
                       "localStorage.clear();"
            browser.execute_script(cookiejs)

            browser.close()
            browser.quit()

            return base_64+"||||"+html_source
            # return base_64
        except Exception, e:
            browser.close()
            browser.quit()
            print e

if __name__ == "__main__":
    pass
    # sx = FindPicture()
    #
    # data = sx.picture_screenshot_html("https://m.baidu.com/s?pn=10&word=%E6%8B%9B%E8%81%98")
    # import base64
    # imgdata = base64.b64decode(data)
    # file = open('9.jpg', 'wb')
    # file.write(imgdata)
    # file.close()