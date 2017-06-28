# -*- coding: utf8 -*-
from downloader.downloader import Downloader
import urllib2
import traceback
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class HtmlLocalDownloader(Downloader):
    """
    html下载器
    """

    def __init__(self, set_mode='db', get_mode='db'):
        super(HtmlLocalDownloader, self).__init__(set_mode, get_mode)

    def set(self, request):
        try:
            results = dict()
            param = request.downloader_get_param('http')
            for url in param['urls']:
                results[url] = 1
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
                url_type = param['url_type']
                headers = param['header']
                data = None
                if 'post_data' in param:
                    data = param['data']
                opener = urllib2.build_opener()
                if 'redirect' in param and str(param['redirect']) == '0':
                    redirect_handler = UnRedirectHandler()
                    opener = urllib2.build_opener(redirect_handler)
                for url in urls:
                    request = urllib2.Request(url['url'], data=data, headers=headers)
                    result = {"status": "3", "result": "", "header": ""}
                    for i in range(0, 2):
                        try:
                            response = opener.open(request, timeout=10)
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
                                # import base64
                                # result["result"] = base64.b64encode(body)
                                result["result"] = body
                                result["status"] = "2"
                                if url_type == 2:
                                    result["header"] = str(header)
                                break
                        except Exception, e:
                            traceback.print_exc()
                    results[url['url']] = result
                # print results
                return results
            except Exception:
                print 'get:'+(traceback.format_exc())
        return 0


class UnRedirectHandler(urllib2.HTTPRedirectHandler):

    def __init__(self):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        if 'location' in headers:
            newurl = headers.getheaders('location')[0]
            print 'header location:'+newurl
            return newurl
        pass
