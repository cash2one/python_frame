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
sys.path.append(os.path.join(PROJECT_PATH, 'util'))# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 11:12:13 2016

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
import random
reload(sys)
sys.setdefaultencoding('utf8')
import copy

class _39DepartmentSpider(BaseSpider):

    def __init__(self):
        super(_39DepartmentSpider, self).__init__()
        self.extractor = _39DepartmentExtractor()
        self.log = UtilLogger('_39DepartmentSpider', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_39_department_spider'))
        # self.seed_url = 'http://ask.39.net/jibing/list_0_1721_1.html'
        self.seed_url = 'http://baixing.com'

    def get_user_password(self):
        return 'sunxiang', 'sxspider'
        # return 'test', 'test'

    def start_requests(self):
        try:
            self.log.info('39健康科室抓取程序开始启动...')
            self.log.info('开始获取初始请求...')

            for i in range(1):
                urls = [{'url': self.seed_url, 'type': 1, 'unique_key': 10}]
                # 'store_type': 2, 'single': 1
                configs = {'priority': 3}
                request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)}, urls=urls, config=configs)
                self.sending_queue.put(request)
        except Exception, e:
            self.log.error('获取初始请求出错:%s' % str(e))

    def deal_request_results(self, request, results):
        if results == 0:
            self.log.error('请求发送失败')
        elif results == -2:
            self.log.error('没有相应地域')
        elif results == -1:
            self.log.error("向数据库 添加任务失败  设置request 失败  urls: %s" % request.urls)
        else:
            # self.log.info('请求发送成功')
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
            failed_urls = list()  # 失败链接
            for u in request.urls:
                url = u['unique_md5']
                if url in results:
                    result = results[url]
                    if str(result['status']) == '2':
                        print "1"
                        self.log.info('抓取成功:%s' % url)
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
                # else:
                #       被别的取走
                #     failed_urls.append(u)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)
            if len(failed_urls) > 0:
                new_request = copy(request)
                new_request.urls = failed_urls
                self.sending_queue.put(new_request)
                del new_request

def Main():
    spider = _39DepartmentSpider()
    spider.run(1, 1, 1, 1, 60, 60, 60, 60, True)

if __name__ == '__main__':
    Main()

