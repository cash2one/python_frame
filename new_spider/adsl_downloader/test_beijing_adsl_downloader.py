# -*- coding: utf8 -*-
import urllib2
from redirect import UnRedirectHandler
import urllib
import config
import json
import os
import re
import subprocess
import time
import traceback
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class AdslDownLoader(object):

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
        self.re_image_content_type = re.compile('image')

    # 从调度中心取任务
    def get_tasks(self):
        try:
            response = urllib2.urlopen(config.TASK_SCHEDULER_URL,
                                       data=urllib.urlencode({
                                           'type': config.FETCH_TYPE_HTML,
                                           'size': config.TASK_FETCH_SIZE,
                                           'client_id': self.id
                                       }),
                                       timeout=config.TASK_FETCH_TIMEOUT)
            tasks = json.loads(response.read())
            if len(tasks) > 0:
                for task in tasks:
                    self.tasks.append(task)
        except Exception, e:
            pass

    # 返回结果给调度中心
    def save_results(self, results):
        request = urllib2.Request(config.TASK_SCHEDULER_URL,
                                  data=urllib.urlencode({
                                      'type': config.FETCH_TYPE_HTML,
                                      'results': json.dumps(results),
                                      'client_id': self.id
                                  }))
        urllib2.urlopen(request)

    @staticmethod
    def encoding(data):
        types = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']
        for t in types:
            try:
                return data.decode(t)
            except Exception, e:
                pass
        return None

    @staticmethod
    def ping():
        try:
            f_null = open(os.devnull, 'w')
            result = subprocess.call('ping -n 1 -w 10 qq.com', shell=True, stdout=f_null, stderr=f_null)
            f_null.close()
            if result:
                return False
            else:
                return True
        except:
            return False

    def run(self):
        self.get_tasks()
        results = list()
        for task in self.tasks:
            task = json.loads(task)
            result = {"id": str(task["id"]), "url": task["url"], "type": task["type"],
                      "store_type": task["store_type"], "status": "3", "result": "", "header": ""}
            data = None
            headers = {}
            if 'header' in task:
                headers = json.loads(task['header'])
            if 'data' in task:
                if 'Content-Type' in headers and headers['Content-Type'] == 'application/json':
                    data = task['data']
                else:
                    data = urllib.urlencode(json.loads(task['data']))
            request = urllib2.Request(task['url'], data=data, headers=headers)
            opener = urllib2.build_opener()
            if 'redirect' in task and str(task['redirect']) == '0':
                redirect_handler = UnRedirectHandler()
                opener = urllib2.build_opener(redirect_handler)
            for i in range(0, config.RETRY_TIMES):
                try:
                    response = opener.open(request, timeout=config.REQUEST_TIMEOUT)
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
                    if ('Content-Type' in header and self.re_image_content_type.search(header['Content-Type'])) or \
                            ('content-type' in header and self.re_image_content_type.search(header['content-type'])):
                        import base64
                        body = base64.b64encode(body)
                    else:
                        body = self.encoding(body)
                    if body is not None:
                        result["result"] = body
                        result["status"] = "2"
                        if str(result["type"]) == "2":
                            result["header"] = str(header)
                        break
                except Exception, e:
                    # traceback.print_exc()
                    while not self.ping():
                        time.sleep(1)
            results.append(result)
        if len(results) > 0:
            self.save_results(results)

    def test(self):
        url = "http%3A//map.onegreen.net/%E5%9B%9B%E5%B7%9D%E7%9C%81%E9%80%9A%E6%B1%9F%E5%8E%BF2.jpg"
        result = {"id": 11, "url": url, "type": 1,
                  "store_type": 1, "status": "3", "result": "", "header": ""}
        data = None
        headers = {}

        request = urllib2.Request(url, data=data, headers=headers)
        opener = urllib2.build_opener()
        # if 'redirect' in task and str(task['redirect']) == '0':
        #     redirect_handler = UnRedirectHandler()
        #     opener = urllib2.build_opener(redirect_handler)
        for i in range(0, config.RETRY_TIMES):
            try:
                response = opener.open(request, timeout=config.REQUEST_TIMEOUT)
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
                if ('Content-Type' in header and self.re_image_content_type.search(header['Content-Type'])) or \
                        ('content-type' in header and self.re_image_content_type.search(header['content-type'])):
                    import base64
                    body = base64.b64encode(body)
                else:
                    body = self.encoding(body)

                sxcapture = base64.b64decode(body)
                file = open("screenshot.png", "wb")
                file.write(sxcapture)
                file.close()


                # if body is not None:
                #     result["result"] = body
                #     result["status"] = "2"
                #     if str(result["type"]) == "2":
                #         result["header"] = str(header)
                    # break
            except Exception, e:
                print e

def main():
    downloader = AdslDownLoader()
    downloader.test()
    # print downloader.ping()

    # url = "http://www.onegreen.net/maps/Upload_maps/201303/2013032811552069_S.jpg"
    # # 'param':{'capture_width': '414', 'capture_height': '736'}
    # task = {"id": 11, "url": url, "type": 4, "store_type": 1, "status": "3", "result": ""}
    # response = {"id": str(task["id"]), "url": task["url"], "type": task["type"], "store_type": task["store_type"],
    #             "status": "3", "result": "", "header": ""}

    # results = list()
    # for i in range(0, 2):
    #     try:
    #         # import datetime
    #         # starttime = datetime.datetime.now()
    #         render = WebRender(task)
    #         result = render.result
    #         break
    #     except Exception as e:
    #         print('抓取失败：第%d次' % (i + 1))
    # results.append(response)
    # print(len(results))
    # downloader.run()

if __name__ == '__main__':
    main()
