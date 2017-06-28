# -*- coding: utf8 -*-

from tld import get_tld

from PIL import ImageGrab
from bs4 import BeautifulSoup
import sxconfig
import json
import urllib2
import time
import base64
import os
import random

class UtilsFunction(object):

    def __init__(self):
        self.ua = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
                   "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b8pre) Gecko/20101114 Firefox/4.0b8pre",
                   "Mozilla/5.0 (X11; U; Linux i686; it-IT; rv:1.9.0.2) Gecko/2008092313 Ubuntu/9.25 (jaunty) Firefox/3.8",
                   "Mozilla/5.0 (Windows; U; Windows NT 6.1; cs; rv:1.9.2.4) Gecko/20100513 Firefox/3.6.4 (.NET CLR 3.5.30729)",
                   "Mozilla/5.0 (Windows; U; Windows NT 6.0; fr; rv:1.9.2.28) Gecko/20120306 Firefox/3.6.28"]
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

    def findReal_Address_improve(self, url, domain=""):
        headers = {"User-Agent": random.choice(self.ua)}
        request = urllib2.Request(url, headers=headers)
        redirect_handler = UnRedirectHandler()
        opener = urllib2.build_opener(redirect_handler)
        result = dict()
        result["url"] = ""
        self.get_result(opener, request, 1, True, domain, result, temp_url=url)
        opener.close()
        return result["url"]

    def findReal_result(self, url, domain=""):
        request = urllib2.Request(url)
        redirect_handler = UnRedirectHandler()
        opener = urllib2.build_opener(redirect_handler)
        result = dict()
        result["url"] = ""
        self.get_result(opener, request, 1, True, domain, result, temp_url=url)
        opener.close()
        return result

    # def get_result(self, opener, request, redirect, flag, domain, result, temp_url=""):
    #     if not flag:
    #         return flag
    #     else:
    #         try:
    #             response = opener.open(request, timeout=5)
    #             # 什么情况下 是 元祖
    #             if isinstance(response, tuple):
    #                 url = response[0]
    #                 result["url"] = url
    #                 if "User-agent" in request.headers.keys():
    #                     headers = {"User-agent": request.headers.get("User-agent")}
    #                 request = urllib2.Request(url)
    #                 flag = self.get_result(opener, request, redirect, flag, url, result, temp_url=temp_url)
    #             else:
    #                 # result["body"] = response.read()
    #                 result["url"] = domain
    #                 return False
    #         except urllib2.HTTPError, e:
    #             result["url"] = domain
    #             return False
    #         except Exception:
    #             result["url"] = domain
    #             return False

    def get_result(self, opener, request, redirect, flag, domain, result, temp_url=""):
        if not flag:
            return flag
        else:
            try:
                response = opener.open(request, timeout=5)
                if isinstance(response, tuple):
                    url = response[0]
                    result["url"] = url
                    # code = response[1]
                    request = urllib2.Request(url)
                    flag = self.get_result(opener, request, redirect, flag, url, result, temp_url=temp_url)
                else:
                    body = response.read()
                    if body.find("window.location.replace") > -1:
                        direct_url = self.cut_word(body)
                        result["url"] = direct_url
                        request = urllib2.Request(direct_url)
                        flag = self.get_result(opener, request, redirect, flag, direct_url, result, temp_url=temp_url)
                    return False
            except urllib2.HTTPError:
                result["url"] = domain
                return False
            except Exception:
                result["url"] = domain
                return False

    def cut_word(self, content):
        start_index = content.find("window.location.replace")
        temp_content = content[start_index + 25:]
        end_index = temp_content.find("\"")
        return temp_content[0: end_index]

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
                    url = self.findReal_Address(redirect_url)
            except urllib2.HTTPError, e:
                print e.code
                break
            except Exception, e:
                print e
            finally:
                opener.close()
                return url

    def getScreenshot(self, fileNamePicture):
        try:
            time.sleep(sxconfig.sleeptimeSecond)
            if os.path.exists(fileNamePicture):
                os.remove(fileNamePicture)
            image = ImageGrab.grab()
            image.save(fileNamePicture)
            icon = open(fileNamePicture, 'rb')
            iconData = icon.read()
            screenshot = base64.b64encode(iconData)
            return screenshot
        except Exception, e:
            return None

    def fullloaded(self, browser):
        browser.execute_script("""
                               (function () {
                                   var y = 0;
                                   var step = 300;
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
                                   setTimeout(f, 100);
                               })();
                           """)
        # time.sleep(1)

    def removeCharacters(self, previouUrl):
        if previouUrl.startswith("https://"):
            previouUrl = previouUrl.replace("https://", "")
        if previouUrl.startswith("http://"):
            previouUrl = previouUrl.replace("http://", "")
        if previouUrl.endswith("/"):
            previouUrl = previouUrl[0:len(previouUrl)-1]
        if previouUrl.find("?") > -1:
            middle_index = previouUrl.find("?")
            previouUrl = previouUrl[0:middle_index]
        return previouUrl

class UnRedirectHandler(urllib2.HTTPRedirectHandler):

    def __init__(self):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        if 'location' in headers:
            newurl = headers.getheaders('location')[0]
            return newurl, code

    http_error_301 = http_error_303 = http_error_307 = http_error_302

if __name__ == "__main__":
    sxutil = UtilsFunction()
    # "http://www.baidu.com/link?url=SdqmrNTAZl8KPMrusYP1Q_SHtLwqL37ICwZBTsBV0s_"
    # http: // www.hxb.com.cn /
    # print sxutil.findReal_Address("https://clinique.tmall.com/")
    print sxutil.removeCharacters("https://mp.weixin.qq.com/s?src=3&timestamp=1496802275&ver=1&signature=H9ckzJqmpehe1pnZSMmO7CPYCQmj7GE401V4zXg4cIKUyOd17YMEQ6g0VQRrigvTsg99O9nChaFAgl7OyrL0aqkh7AtrmZwo22O1*LzDMPb-6fnzGYqLLptahTFJIXSZcScjYvLpuGTUZ6GTdGUoPI7V7jtOgu2mWHOrI6NFcoc=")

    # print sxutil.findReal_Address_improve(
    #     "http://www.zhuoyanlw.com/",
    #     "www.baidu.com")