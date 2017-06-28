# -*- coding: utf8 -*-
from downloader.downloader import Downloader
import urllib2
import urllib
import traceback
import sys
import json
import base64
import MySQLdb

from util.util_md5 import UtilMD5
reload(sys)
sys.setdefaultencoding('utf8')

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebKitWidgets import QWebPage
from PyQt5.QtCore import Qt, QUrl, QSize, QByteArray, QBuffer
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from PyQt5.QtGui import QImage, QPainter

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
                # url_type = param['url_type']
                # headers = param['header']
                # data = None
                # if 'post_data' in param:
                #     # data = urllib.urlencode(json.loads(param['data']))
                #     # print data
                #     data = param['data']
                # opener = urllib2.build_opener()
                # if 'redirect' in param and str(param['redirect']) == '0':
                #     redirect_handler = UnRedirectHandler()
                #     opener = urllib2.build_opener(redirect_handler)
                for url in urls:
                    task = {"url": url["url"], "type": 4, "store_type": 1, "status": "3", "result": ""}
                    result = {"url": url["url"], "status": "3", "result": "", "header": ""}
                    # self.get_result(opener, request, result)
                    for i in range(0, 2):
                        try:
                            import datetime
                            starttime = datetime.datetime.now()
                            print "开始截图"
                            render = WebRender(task)
                            sx_result = render.result

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

class WebRender(QWebPage):

    def __init__(self, task):
        self.app = QApplication(sys.argv)
        self.app.flush()
        super(WebRender, self).__init__()
        self.loadFinished.connect(self.save_result)
        self.type = int(task['type'])
        self.load_task(task)
        self.result = ""
        self.app.exec_()

    def load_task(self, task):
        req = QNetworkRequest(QUrl(task['url']))
        operation = QNetworkAccessManager.GetOperation
        data = QByteArray()
        headers = {}
        if 'header' in task:
            headers = json.loads(task['header'])
        if 'useragent' in task:
            headers['User-Agent'] = task['useragent']
        if 'cookie' in task:
            headers['Cookie'] = task['cookie']
        for key in headers:
            req.setRawHeader(QByteArray().append(key), QByteArray().append(headers[key]))
        if 'data' in task:
            operation = QNetworkAccessManager.PostOperation
            data.append(urllib.urlencode(json.loads(task['data'])).encode('ascii'))
        if self.type == 4:
            self.mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)
            self.mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
            capture_width = 1024
            capture_height = 768
            if 'param' in task:
                param = task['param']
                if 'capture_width' in param:
                    capture_width = int(param['capture_width'])
                if 'capture_height' in param:
                    capture_height = int(param['capture_height'])
            self.setViewportSize(QSize(capture_width, capture_height))
        self.mainFrame().load(req, operation, data)

    def save_result(self):
        try:
            frame = self.mainFrame()
            url = frame.url()
            if url.isEmpty():
                pass
            else:
                image = QImage(frame.contentsSize(), QImage.Format_ARGB32_Premultiplied)
                image.fill(Qt.transparent)
                painter = QPainter(image)
                painter.setRenderHint(QPainter.Antialiasing, True)
                painter.setRenderHint(QPainter.TextAntialiasing, True)
                painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
                frame.documentElement().render(painter)
                painter.end()
                img_data = QByteArray()
                img_buf = QBuffer(img_data)
                image.save(img_buf, 'PNG')

                self.result = img_data.toBase64().data().decode('utf-8')+"||||"+frame.toHtml()

        except Exception, e:
            print e
            print('抓取失败')
        self.app.quit()