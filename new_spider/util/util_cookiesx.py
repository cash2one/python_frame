# -*- coding: utf8 -*-
# from downloader import Downloader
import sys
import traceback
import urllib2

reload(sys)
sys.setdefaultencoding('utf8')


class UtilCookie():
    """
    cookie下载器
    """

    def __init__(self):
        self.cookie = '';

    # def getCookie(self):
    #     headers = dict()
    #     headers["cookie"] = ""
    #     headers[
    #         "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36"
    #     request_param = {"url": 'https://www.baidu.com/', "headers": headers, "data": ""}
    #     hd = HtmlLocalDownloader()
    #     get()

    def getPc(self):
            try:
                opener = urllib2.build_opener()
                headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari / 537.36'}
                request = urllib2.Request('https://www.baidu.com/', headers=headers)
                for i in range(0, 2):
                    try:
                        response = opener.open(request, timeout=10)
                        header = response.info()
                        if 'Set-Cookie' in header:
                            cookiesx = header.getheaders('Set-Cookie')[0]
                            self.cookie = cookiesx
                            return cookiesx
                        break
                    except Exception, e:
                        traceback.print_exc()

            except Exception, e:
                traceback.print_exc()
                return ''
                # traceback.print_exc()


    def getMobile(self):
            try:
                opener = urllib2.build_opener()
                headers = {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',}
                request = urllib2.Request('https://www.baidu.com/', headers=headers)
                for i in range(0, 2):
                    try:
                        response = opener.open(request, timeout=10)
                        header = response.info()
                        if 'Set-Cookie' in header:
                            cookiesx = header.getheaders('Set-Cookie')[0]
                            self.cookie=cookiesx
                            return cookiesx
                        break
                    except Exception, e:
                        traceback.print_exc()

            except Exception, e:
                traceback.print_exc()
                return ''
                # traceback.print_exc()

    @staticmethod
    def encoding(data):
        types = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']
        for t in types:
            try:
                return data.decode(t)
            except Exception, e:
                pass
        return None


    class UnRedirectHandler(urllib2.HTTPRedirectHandler):
        def __init__(self):
            pass

        def http_error_302(self, req, fp, code, msg, headers):
            if 'location' in headers:
                newurl = headers.getheaders('location')[0]
                print  'header location:'+newurl
                return newurl
            pass


def Main():
    spider = UtilCookie()
    cookie =  spider.getPc()
    print spider.cookie

if __name__ == '__main__':
    Main()
