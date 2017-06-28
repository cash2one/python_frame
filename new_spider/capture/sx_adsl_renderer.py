# -*- coding: utf8 -*-
import os
import sys
import config
import json
# from urllib.request import urlopen
# from urllib.parse import urlencode

import urllib

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebKitWidgets import QWebPage
from PyQt5.QtCore import Qt, QUrl, QSize, QByteArray, QBuffer
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager
from PyQt5.QtGui import QImage, QPainter


class AdslRenderer(object):

    def __init__(self):
        self.dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.id = ''
        id_file = os.path.join(self.dir, 'machinenum.txt')
        if os.path.exists(id_file):
            with open(id_file) as f:
                lines = f.readlines()
                if len(lines) > 0:
                    self.id = lines[0].strip()
        self.tasks = []
        self.results = []

    # 从调度中心取任务
    def get_tasks(self):
        try:
            response = urllib.urlopen(config.TASK_SCHEDULER_URL,
                               data=urllib.urlencode({
                                   'type': config.FETCH_TYPE_CAPTURE,
                                   'size': config.TASK_FETCH_SIZE,
                                   'client_id': self.id
                               }).encode('ascii'),
                               timeout=config.TASK_FETCH_TIMEOUT)
            tasks = json.loads(response.read().decode('utf-8'))
            if len(tasks) > 0:
                for task in tasks:
                    self.tasks.append(task)
        except Exception as e:
            import traceback
            traceback.print_exc()
            pass

    # 返回结果给调度中心
    def save_results(self, results):
        urllib.urlopen(config.TASK_SCHEDULER_URL,
                 data=urllib.urlencode({
                    'type': config.FETCH_TYPE,
                    'results': json.dumps(results),
                    'client_id': self.id
                }).encode('ascii'),
                timeout=config.TASK_FETCH_TIMEOUT)

    def run(self):
        self.get_tasks()
        results = list()
        for task in self.tasks:
            task = json.loads(task)
            response = {"id": str(task["id"]), "url": task["url"], "type": task["type"],
                        "store_type": task["store_type"], "status": "3", "result": "", "header": ""}
            for i in range(0, config.RETRY_TIMES):
                try:
                    render = WebRender(task)
                    result = render.result
                    if result:
                        response['status'] = 2
                        response['result'] = result
                        break
                except Exception as e:
                    print('抓取失败：第%d次' % (i+1))
            results.append(response)
        if len(results) > 0:
            self.save_results(results)


class WebRender(QWebPage):

    def __init__(self, task):
        self.app = QApplication(sys.argv)
        super(WebRender, self).__init__()
        self.loadFinished.connect(self.save_result)
        self.type = int(task['type'])
        self.load_task(task)
        self.result = None
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
                if self.type == 4:
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

                    # image.save("abc1.png")
                    self.result = img_data.toBase64().data().decode('utf-8')
                    # print self.result

                    import base64
                    imgdata = base64.b64decode(self.result)
                    file = open('1vsx_1.png', 'wb')
                    file.write(imgdata)
                    file.close()

                    # image2 = QImage(frame.contentsSize(), QImage.Format_ARGB32_Premultiplied)
                    # image2.fill(Qt.transparent)

                    # self.result.s("cc.png")
                    # import QFile
                    # f = open('1sx.html', 'r')
                    # QFilesx = open("abc1.png", "w")  # 创建一个文件对象，存储用户选择的文件
                    # QFilesx.write(image)            # 将流中的图片写入文件对象当中
                    # QFilesx.close()
                else:
                    self.result = frame.toHtml()
        except Exception, e:
            print e
            print('抓取失败')
        self.app.quit()


def main():
    renderer = AdslRenderer()
    # renderer.run()
    url = "https://www.baidu.com/s?wd=%E6%8B%9B%E8%81%98&rsv_spt=1&rsv_iqid=0xd4454e410002b41d&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=78040160_5_pg&rsv_enter=1&rsv_t=39bbbXvTfQzBVUcO599lfPLFCv9ZxJy5lvNgDwSB852caqkcZF39qpKbyBZ5mRN4VwACzg&oq=Lucid%26lt%3Bhart&inputT=1103&rsv_pq=9da0274b00029d5e&rsv_sug3=10&rsv_sug1=11&rsv_sug7=100&bs=LucidChart"
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
    # {"id": str(task["id"]), "url": task["url"], "type": task["type"],
    #  "store_type": task["store_type"], "status": "3", "result": "", "header": ""}

    # task = {"id": 11,  "url": url, "type": 4, "store_type": 1, "status": "3", "result": "", 'param':{'capture_width': '414', 'capture_height': '736'}}
            # header  ,id,  param,    redirect,   store_type  ,type,url

    task = {'header': '''{\"User-Agent\": \"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari / 537.36\"}''', id: 11, 'redirect': 0, 'store_type':1, 'type': 4, 'url': url }
    response = {"id": '11', "url": url, "type": 4,
                "store_type": 1, "status": "3", "result": "", "header": ""}
    # response = {"id": str(task["id"]), "url": task["url"], "type": task["type"], "store_type": task["store_type"], "status": "3", "result": "", "header": ""}

    results = list()
    for i in range(0, config.RETRY_TIMES):
        try:
            import datetime
            starttime = datetime.datetime.now()
            render = WebRender(task)
            result = render.result

            endtime = datetime.datetime.now()
            print (endtime - starttime).seconds

            if result:
                response['status'] = 2
                response['result'] = result
                break

        except Exception as e:
            print('抓取失败：第%d次' % (i + 1))
    results.append(response)
    print results

if __name__ == '__main__':
    main()
