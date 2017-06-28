# -*- coding: utf8 -*-
import urllib2
from redirect import UnRedirectHandler
import urllib
import config
import json
import base64
import os
import sys
import re
reload(sys)
sys.setdefaultencoding('utf8')
import subprocess
import time

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
            print e

    # 返回结果给调度中心
    def save_results(self, results, task_ids):
        request = urllib2.Request(config.TASK_SCHEDULER_URL,
                                  data=urllib.urlencode({
                                      'type': config.FETCH_TYPE_HTML,
                                      'results': json.dumps(results),
                                      'task_ids': json.dumps(task_ids),
                                      'client_id': self.id
                                  }))
        urllib2.urlopen(request)

    @staticmethod
    def encoding(data):
        types = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']
        for t in types:
            try:
                return data.decode(t)
            except Exception:
                pass
        return None

    def run(self):
        self.get_tasks()
        results = list()
        task_ids = list()
        for task in self.tasks:
            task = json.loads(task)
            task_id = {"id": str(task["id"])}
            task_ids.append(task_id)

            result = {"id": str(task["id"]), "url": task["url"], "type": task["type"],
                      "store_type": task["store_type"], "status": "3", "result": "", "header": "",
                      "redirect_url": "", "code": 0, "md5": task["md5"], "extractor_html": task["type"]
                      }


            data = None
            headers = {}
            if 'header' in task:
                headers = json.loads(task['header'])
            if 'data' in task:
                data = urllib.urlencode(json.loads(task['data']))
            request = urllib2.Request(task["url"], data=data, headers=headers)
            # opener = urllib2.build_opener()
            if 'redirect' not in task:
                redirect = "0"
            else:
                redirect = str(task['redirect'])
            redirect_handler = UnRedirectHandler()
            opener = urllib2.build_opener(redirect_handler)
            self.get_result(opener, request, result, redirect, True)
            results.append(result)
        if len(results) > 0:
            self.save_results(results, task_ids)

    def get_result(self, opener, request, result, redirect, flag):
        for i in range(0, config.RETRY_TIMES):
            if not flag:
                return flag
            else:
                try:
                    response = opener.open(request, timeout=config.REQUEST_TIMEOUT)
                    if isinstance(response, tuple):
                        header = response[2]
                        result["status"] = "2"
                        result["redirect_url"] = response[0]
                        result["code"] = response[1]
                        if str(result["type"]) == "2":
                            result["header"] = str(header)
                        if redirect == '0':
                            break
                        headers = {}
                        if "User-agent" in request.headers.keys():
                            headers = {"User-agent": request.headers.get("User-agent")}
                        request = urllib2.Request(result["redirect_url"], headers=headers)
                        flag = self.get_result(opener, request, result, redirect, flag)
                    else:
                        header = response.info()
                        body = response.read()
                        body = self.get_body(header, body)
                        if body is not None:
                            result["result"] = body
                            result["status"] = "2"
                            if str(result["type"]) == "2":
                                result["header"] = str(header)
                            return False
                            # break
                except urllib2.HTTPError, e:
                    result["code"] = e.code
                    return False
                    # break
                except Exception:
                    for count in xrange(0, 10):
                        if not self.ping():
                            time.sleep(1)
                        else:
                            break
        return False

    def get_body(self, header, body):
        if ('Content-Type' in header and self.re_image_content_type.search(header['Content-Type'])) or \
                ('content-type' in header and self.re_image_content_type.search(header['content-type'])):
            return base64.b64encode(body)

        elif ('Content-Encoding' in header and header['Content-Encoding']) or \
                ('content-encoding' in header and header['content-encoding']):
            import gzip
            import StringIO
            d = StringIO.StringIO(body)
            gz = gzip.GzipFile(fileobj=d)
            body = gz.read()
            gz.close()
        body = self.encoding(body)
        return base64.b64encode(body)

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

def main():
    downloader = AdslDownLoader()

    # sys.argv[0]
    downloader.run()

if __name__ == '__main__':
    main()
