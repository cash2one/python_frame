# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 11:12:13 2016

@author: zhangle
"""

import os
import sys
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
sys.path.append(os.path.join(PROJECT_PATH, 'store'))
sys.path.append(os.path.join(PROJECT_PATH, 'util'))

from spider.basespider import BaseSpider
from downloader.downloader import SpiderRequest
from extractor._39._39_department_extractor import _39DepartmentExtractor
from store._39._39_department_store import _39DepartmentStore
from util_log import UtilLogger

reload(sys)
sys.setdefaultencoding('utf8')

class _39DepartmentSpider(BaseSpider):

    def __init__(self):
        super(_39DepartmentSpider, self).__init__()
        self.extractor = _39DepartmentExtractor()
        self.log = UtilLogger('_39DepartmentSpider', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_39_department_spider'))
        # self.seed_url = 'http://ask.39.net/jibing/list_0_1721_1.html'
        # self.seed_url = 'http://baixing.com'

    def get_user_password(self):
        # return 'test', 'test'
        return 'sunxiang', 'sxspider'
        # return 'xuliang', 'xlspider'

    # def get_downloader(self):
    #
    #     # return Downloader(set_mode='db', get_mode='db')
    #     return HtmlLocalDownloader(set_mode='http', get_mode='http')

    def start_requests(self):
        try:

            urls = [{"url": "https://zhidao.baidu.com/api/qbpv?q=363714587", "type": 1}]
            header = None
            configs = None

            # "{'url': u'https://zhidao.baidu.com/api/qbpv?q=363714587', 'qid': u'363714587', 'unique_md5': '5b35773c16769d5a9671030ede7cc52e', 'extractor_type': 3, 'type': 1," \
            # " 'question_id': 2L}; headers:{'Referer': u'https://zhidao.baidu.com/question/363714587.html'," \
            # " 'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; fr; rv:1.9.0.1) Gecko/2008070400 SUSE/3.0.1-1.1 Firefox/3.0.1'}"
            #
            header = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, sdch",
                    "Accept-Language": "zh-CN,zh;q=0.8",
                    "Cache-Control": "max-age=0",
                    "Connection": "keep-alive",
                    "Cookie": "BAIDUID=86984FE336ACA53DA816C1ACA2CAD816:FG=1; PSTM=1495875089; BIDUPSID=A73CC65DB183F0C03E8B0592090E672B; PSINO=3; H_PS_PSSID=23201_1427_21095_17001_22074; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; ZX_HISTORY=%5B%7B%22visittime%22%3A%222017-06-02+14%3A28%3A58%22%2C%22pid%22%3A%22QPwz8iDVpcnAR1XSshWrGjVLfPXMFJTzewFI%22%7D%2C%7B%22visittime%22%3A%222017-06-01+14%3A51%3A57%22%2C%22pid%22%3A%22MuXpOdN5dWWQ9vyTqdMD6kqZFUw-JyG2QA4U%22%7D%2C%7B%22visittime%22%3A%222017-06-01+14%3A51%3A26%22%2C%22pid%22%3A%22lY7EwsWNYpH0V4g4pZtid7YUHY1g6Kft0AA1%22%7D%2C%7B%22visittime%22%3A%222017-06-01+14%3A51%3A21%22%2C%22pid%22%3A%22aIt6h5C5w2MUjNnzSSMJ%2AGERzv66HzOuKA4f%22%7D%5D; Hm_lvt_baca6fe3dceaf818f5f835b0ae97e4cc=1496382053,1496382060,1496382692,1496384507; Hm_lpvt_baca6fe3dceaf818f5f835b0ae97e4cc=1496384887",
                    "Host": "xin.baidu.com",
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
                    "Upgrade-Insecure-Requests": "1",
                    }

            url = '''
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
import execjs

class AdslDownLoader(object):

    def __init__(self):
        self.re_image_content_type = re.compile('image')
        pass

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
        redirect_handler = UnRedirectHandler()
        opener = urllib2.build_opener(redirect_handler)
        request = urllib2.Request("http://xin.baidu.com/detail/compinfo?pid=PbObuEVtIKUUFMyW7w*MAHcEPPjWmHT5lg3G&from=koubei")
        redirect = "0"
        result = {"id": "", "url": "", "type": "",
                  "store_type": "", "status": "3", "result": "", "header": "",
                  "redirect_url": "", "code": 0, "md5": ""
                  }
        self.get_result(opener, request, result, redirect, True)
        # print result["result"]
        if result["result"] != 0:
            redirect_u = self.extractor_qualify_execjs(result["result"])
            # print redirect_u
            request = urllib2.Request(redirect_u)
            redirect_handler = UnRedirectHandler()
            opener = urllib2.build_opener(redirect_handler)
            self.get_result(opener, request, result, redirect, True)
            print result["result"]
        else:
            print -1

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
                except urllib2.HTTPError, e:
                    result["code"] = e.code
                    return False
                except Exception as e:
                    print e
                    for count in xrange(0, 10):
                        if not self.ping():
                            time.sleep(1)
                        else:
                            break
        return False

    def extractor_qualify_execjs(self, body):
        try:
            mxi_middle = re.findall(r"function mix(.*?)\(function", body)
            if mxi_middle:
                js_exe = "function mix" + mxi_middle[0]

            tkids = re.findall(r"tk = document.getElementById\('(.*?)'", body)
            if tkids:
                tk_id = tkids[0]

            attributes = re.findall(r"\).getAttribute\('(.*?)'\)", body)
            if attributes:
                tk_attribute = attributes[0]

            attr_text = re.findall(r'id=\"%s\" %s=\"(.*?)\"' % (tk_id, tk_attribute), body)
            if attr_text:
                tk = attr_text[0]

            baiducode_content = re.findall(r'id=\"baiducode\">(.*?)<', body)
            if baiducode_content:
                bid = baiducode_content[0]

            ctx = execjs.compile(js_exe)
            tot = ctx.call("mix", tk, bid)

            pids = re.findall(r'result.*?pid\":\"(.*?)\"', body)
            if pids:
                pid = pids[0]

            return "http://xin.baidu.com/detail/basicAjax?pid=%s&tot=%s" % (pid, tot)
        except Exception as e:
            print e
            return -1

    def get_body(self, header, body):
        if ('Content-Encoding' in header and header['Content-Encoding']) or\
                ('content-encoding' in header and header['content-encoding']):
            import gzip
            import StringIO
            d = StringIO.StringIO(body)
            gz = gzip.GzipFile(fileobj=d)
            body = gz.read()
            gz.close()
        body = self.encoding(body)
        return body

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
    downloader.run()

if __name__ == '__main__':
    main()
  '''
            # "http://xin.baidu.com/detail/compinfo?pid=Ld3n0Wqo-*G8XlLuUEfXrIiyQ5K89gy8zQHj&from=koubei"
            urls = [{"url": url, "type": 7}]
            basic_request = SpiderRequest(urls=urls, headers={})
            self.sending_queue.put(basic_request)
            # request = SpiderRequest(urls=urls, headers = header)
            # self.sending_queue.put(request)
        except Exception, e:
            self.log.error('获取初始请求出错:%s' % str(e))

    def deal_request_results(self, request, results):
        if results == 0:
            self.log.error('请求发送失败')
        elif results == -2:
            self.log.error('没有相应地域')
        else:
            self.log.info('请求发送成功')
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        stores.append(_39DepartmentStore())
        return stores

    def deal_response_results(self, request, results, stores):
        if results == 0:
            self.log.error('获取结果失败')
        else:
            urls = list()
            for u in request.urls:
                url = u['unique_md5']
                if url in results:
                    result = results[url]
                    if str(result['status']) == '2':
                        with open("detail.txt", "wb") as f:
                            f.write(result['result'])

                        # self.log.info('抓取成功:%s' % url)

                        # file = open("image.png", "wb")
                        # file.write(result['result'])
                        # file.close()

                        r = self.extractor.extractor(result['result'])
                        if len(r) > 0:
                            for depart in r:
                                item = dict()
                                item['name'] = depart['name']
                                item['department_id'] = depart['department_id']
                                # stores[0].store([item])
                    elif str(result['status']) == '3':
                        self.log.info('抓取失败:%s' % url)
                    else:
                        self.log.info('等待:%s' % url)
                        urls.append(u)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)

def Main():
    spider = _39DepartmentSpider()
    spider.run()

if __name__ == '__main__':
    Main()
