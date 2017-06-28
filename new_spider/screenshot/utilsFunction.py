# -*- coding: utf8 -*-

from tld import get_tld

from PIL import ImageGrab


from bs4 import BeautifulSoup
import config
import json
import urllib2
import time
import base64
import os

class UtilsFunction(object):

    def __init__(self):
        pass

    def get_domain(self, url):
        if url.startswith("."):
            url = "www." + url
        if url.startswith("http"):
            pass
        else:
            url = "http://" + url
        try:
            domain = get_tld(url)
            domain_list = domain.split(".")
            return domain_list[0]
        except Exception as e:
            return ""

    def findReal_Address(self, url):
        headers = {}
        request = urllib2.Request(url, headers=headers)
        redirect_handler = UnRedirectHandler()
        opener = urllib2.build_opener(redirect_handler)
        for i in range(0, 2):
            try:
                response = opener.open(request, timeout=10)
                # 什么情况下 是 元祖
                if isinstance(response, tuple):
                    redirect_url = response[0]
                    code = response[1]
                    url = redirect_url
            except urllib2.HTTPError, e:
                print e.code
                break
            except Exception, e:
                print e
            finally:
                opener.close()
                return url


    def getScreenshot(self, fileNamePicture):
        time.sleep(config.sleeptimeSecond)
        if os.path.exists(fileNamePicture):
            os.remove(fileNamePicture)
        image = ImageGrab.grab()
        image.save(fileNamePicture)
        icon = open(fileNamePicture, 'rb')
        iconData = icon.read()
        screenshot = base64.b64encode(iconData)
        return screenshot

    def fullloaded(self, browser):
        # browser.execute_script("""
        #                        (function () {
        #                            var y = 0;
        #                            var step = 300;
        #                            window.scroll(0, 0);
        #
        #                            function f() {
        #                                if (y < document.body.scrollHeight) {
        #                                    y += step;
        #                                    window.scroll(0, y);
        #                                    setTimeout(f, 100);
        #                                } else {
        #                                     window.scroll(0, 0);
        #                                     document.title += "scroll-done";
        #                                 }
        #                            }
        #                            setTimeout(f, 100);
        #                        })();
        #                    """)
        time.sleep(config.sleeptimeSecond)
        # time.sleep(5)

class UnRedirectHandler(urllib2.HTTPRedirectHandler):

    def __init__(self):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        if 'location' in headers:
            newurl = headers.getheaders('location')[0]
            return newurl, code
        pass