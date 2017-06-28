# -*- coding: UTF-8 -*-

import urllib2
import sys
import time
import traceback
# from sx_util.baidu_id_build import Baidu_id_build
import random
reload(sys)
sys.setdefaultencoding('utf8')

class GetReal_Address(object):

    '''
        获取真实url
    '''
    def __int__(self):
        self.ua = [
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b8pre) Gecko/20101114 Firefox/4.0b8pre",
            "Mozilla/5.0 (X11; U; Linux i686; it-IT; rv:1.9.0.2) Gecko/2008092313 Ubuntu/9.25 (jaunty) Firefox/3.8",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; cs; rv:1.9.2.4) Gecko/20100513 Firefox/3.6.4 (.NET CLR 3.5.30729)",
            "Mozilla/5.0 (Windows; U; Windows NT 6.0; fr; rv:1.9.2.28) Gecko/20120306 Firefox/3.6.28"]
        pass

    def findReal_Address_improve(self, url, domain=""):
        request = urllib2.Request(url)
        redirect_handler = UnRedirectHandler()
        opener = urllib2.build_opener(redirect_handler)
        result = dict()
        result["url"] = ""
        self.get_result(opener, request, 1, True, domain, result, temp_url=url)
        opener.close()
        return result["url"]

    def findReal_result(self, url, domain=""):
        headers = {"User-Agent": random.choice(self.ua)}
        request = urllib2.Request(url, headers=headers)
        redirect_handler = UnRedirectHandler()
        opener = urllib2.build_opener(redirect_handler)
        result = dict()
        result["url"] = ""
        self.get_result(opener, request, 1, True, domain, result, temp_url=url)
        opener.close()
        return result

    def get_result(self, opener, request, redirect, flag, domain, result, temp_url=""):
        if not flag:
            return flag
        else:
            try:
                response = opener.open(request, timeout=5)
                # 什么情况下 是 元祖
                if isinstance(response, tuple):
                    url = response[0]
                    result["url"] = url
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
            except urllib2.HTTPError, e:
                print "findReal_Address HTTPError exception %s; domain:%s" % (temp_url, domain)
                result["url"] = domain
                return False
            except Exception:
                print "findReal_Address Exception exception %s; domain:%s" % (temp_url, domain)
                result["url"] = domain
                return False

    def cut_word(self, content):
        start_index = content.find("window.location.replace")
        temp_content = content[start_index + 25:]
        end_index = temp_content.find("\"")
        return temp_content[0: end_index]

    def findReal_Address(self, url, domain=""):
        headers = {}
        request = urllib2.Request(url, headers=headers)
        redirect_handler = UnRedirectHandler()
        opener = urllib2.build_opener(redirect_handler)
        # for i in range(0, 2):
        try:
            response = opener.open(request, timeout=10)
            # 什么情况下 是 元祖
            if isinstance(response, tuple):
                redirect_url = response[0]
                url = self.findReal_Address(redirect_url)
        except urllib2.HTTPError:
            if domain != "":
                url = domain
        except Exception:
            if domain != "":
                url = domain
        finally:
            opener.close()
            return url

class UnRedirectHandler(urllib2.HTTPRedirectHandler):

    def __init__(self):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        if 'location' in headers:
            newurl = headers.getheaders('location')[0]
            return newurl, code, headers
        pass

    http_error_301 = http_error_303 = http_error_307 = http_error_302

def Main():
    sx = GetReal_Address()

    # 百度文库 内部跳转
    # "http://www.baidu.com/link?url=mCIVN6nm4gys5J66NOgeQW67AfFj34EUhyL1RnU2cIQotpP_kx_aiJqRgpvgi9ouS13q1kGPqOvJbpyK9hBj66xBljoyi8oul6k-5lkud1W"
    # "http://www.baidu.com/link?url=hL-4vhy1PNAyW7ffmD5LZah018LgVN8LFuhVV6eZI43B4gEadU_lUmQ2yTH2FGF5"
    # "http://www.baidu.com/link?url=Fjxtvw1xc54CYcI0JZClotEMRT7qkXc0T2Y33IoomVrNJgkPVRF1F3qSWaTdV0r6iocOaS0by6XIzjWCr8yG4R5WWl2xYRGaapZ2F3F6iXB39UQ7Q4NrwBUBgRbMJdo2"
    xx = sx.findReal_Address_improve("http://m.baidu.com/from=844b/bd_page_type=1/ssid=0/uid=0/pu=sz%40320_1001%2Cta%40iphone_2_6.0_3_537%2Cusm%402/baiduid=A73CC65DB183F0C03E8B0592090E672B/w=0_10_/t=iphone/l=1/tc?ref=www_iphone&lid=12715393425672460698&order=1&fm=alwk&tj=wenkuala_1_0_10_l1&w_qd=IlPT2AEptyoA_yk663cbzweu_zJPc71oqk5Yc4DV9g7&sec=21199&di=f604030eb4b7e886&bdenc=1&nsrc=IlPT2AEptyoA_yixCFOxXnANedT62v3IER3PLjkK1De8mVjte4viZQRAVDbqRzrIBZyfxT0RqR92xn0uPGUm7sYOrv95qmsf8nTdxvb6tcKBSRB4rNU7PAaAUDYpzK", "www.baidu.com")
    # print sx.findReal_result("http://www.baidu.com/link?url=2_EDsjkLNt45CL8we3tHvv5mSv9SRx7MRexntfFFeA_99VM6jiA0yX8639ttieIJrle6tpJIRza0JKJbfkw7JCOFHMlxrX7F9r3khcIO1QLFoMmpoEa_ZW07eXtmEPNt")

    print xx

if __name__ == '__main__':
    Main()