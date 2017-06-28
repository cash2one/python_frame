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

            # import base64
            # base64.b64encode(url)
            # for i in xrange(1, 2):
            url = "http://tkdaili.com/api/getiplist.aspx?vkey=3416F08BB1AA3ACB0386A0991C27C0FF&num=100&country=CN&high=1&style=1"
            urls = [{"url": url, "type": 1, "extractor_type": 4, "inf_id": 111, "unique_key": 1}]
            configs = {"priority": 3}
            basic_request = SpiderRequest(urls=urls, config=configs)
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
