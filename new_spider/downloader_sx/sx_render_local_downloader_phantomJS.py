# -*- coding: utf8 -*-
import sys
import traceback
import urllib2

from downloader.downloader import Downloader
from downloader_sx.list_pulldown_picture.sx_picture_phantomjs import FindPicture

reload(sys)
sys.setdefaultencoding('utf8')
# from downloader.picture_phantomjs


class HtmlLocalDownloader(Downloader):
    """
    html下载器
    """

    def __init__(self, set_mode='db', get_mode='db'):
        super(HtmlLocalDownloader, self).__init__(set_mode, get_mode)

    def set(self, request):
        try:
            results = dict()
            # param = request.downloader_get_param('http')
            param = request.downloader_set_param('http')
            for url in param['urls']:
                # print url
                results[url["url"]] = 1
            return results
        except Exception:
            print(traceback.format_exc())
            return 0

    @staticmethod
    def encoding(data):
        types = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']
        for t in types:
            try:
                return data.decode(t)
            except Exception, e:
                pass
        return None

    def get(self, request):
        param = request.downloader_set_param('http')
        if param is None:
            return 0
        urls = param['urls']
        if len(urls) > 0:
            try:
                results = dict()
                for url in urls:
                    task = {"url": url["url"], "type": 4, "store_type": 1, "status": "3", "result": ""}
                    result = {"url": url["url"], "status": "3", "result": "", "header": ""}
                    for i in range(0, 2):
                        try:
                            import datetime
                            starttime = datetime.datetime.now()
                            print "开始截图"
                            # render = WebRender(task)
                            # sx_result = render.result
                            # sx_result = ""
                            sx = FindPicture()
                            sx_result = sx.picture_screenshot_html(url["url"])

                            endtime = datetime.datetime.now()
                            print (endtime - starttime).seconds

                            if sx_result:
                                result['status'] = 2
                                result['result'] = sx_result
                                break

                        except Exception as e:
                            print e
                            print('抓取失败：第%d次' % (i + 1))
                    results[url['md5']] = result
                return results
            except Exception, e:
                print sx_result
                print e
                print 'get:'+(traceback.format_exc())
        return 0

    def get_result(self, opener, request, result):
        for i in range(0, 2):
            try:
                response = opener.open(request, timeout=10)
                # 什么情况下 是 元祖
                if isinstance(response, tuple):
                    result["redirect_url"] = response[0]
                    result["code"] = response[1]
                    headers = {}
                    if "User-agent" in request.headers.keys():
                        headers = {"User-agent": request.headers.get("User-agent")}
                    request = urllib2.Request(result["redirect_url"], headers=headers)
                    self.get_result(opener, request, result)
                else:
                    header = response.info()
                    body = response.read()
                    if ('Content-Encoding' in header and header['Content-Encoding']) or \
                            ('content-encoding' in header and header['content-encoding']):
                        import gzip
                        import StringIO
                        d = StringIO.StringIO(body)
                        gz = gzip.GzipFile(fileobj=d)
                        body = gz.read()
                        gz.close()
                    body = self.encoding(body)
                    if body is not None:
                        # result["result"] = body
                        # base64.b64encode()
                        result["result"] = body
                        result["status"] = "2"
                        if str(result["type"]) == "2":
                            result["header"] = str(header)
                        break
            except urllib2.HTTPError, e:
                print e.code
                result["code"] = e.code
                break
            except Exception, e:
                # 404 页面有可能断网 也返回这边
                # print e
                pass

class UnRedirectHandler(urllib2.HTTPRedirectHandler):

    def __init__(self):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        # if 'location' in headers:
        #     newurl = headers.getheaders('location')[0]
        #     print 'header location:'+newurl
        #     return newurl
        print headers
        if 'location' in headers:
            newurl = headers.getheaders('location')[0]
            return newurl, code
        pass


if __name__ == "__main__":
    sx = FindPicture()
    sx_result = sx.picture_screenshot_html("https://www.baidu.com/s?wd=%E6%B7%AE%E5%AE%89%E4%BA%BA%E6%89%8D%E7%BD%91%E6%9C%80%E6%96%B0%E6%8B%9B%E8%81%98%E4%BF%A1%E6%81%AF&rsv_spt=1&rsv_iqid=0x9d684d0e0000cecd&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=78040160_5_pg&rsv_enter=0&oq=%E6%8B%9B%E8%81%98&rsv_t=7e39msJWAhkatRpmx%2F691Ir2BU1904ljWxb%2B3gy7cl5pNJsIfLHDNBbY7prEA2Kv9ez9OQ&rsv_pq=dd1bb49d0003954a&inputT=135689006&rsv_n=2&rsv_sug3=1298&bs=%E6%8B%9B%E8%81%98")
    print sx_result