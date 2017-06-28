# -*- coding: utf8 -*-
import os
import random
import sys
import time
import urllib
from datetime import datetime

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
sys.path.append(os.path.join(PROJECT_PATH, 'store'))
sys.path.append(os.path.join(PROJECT_PATH, 'util'))

reload(sys)
sys.setdefaultencoding('utf8')

from copy import copy
import traceback
from spider import config

from downloader.downloader import SpiderRequest
from util.util_useragent import UtilUseragent
from store_mysql import StoreMysql
from util_log import UtilLogger

from spider.basespider_improve_alwaysrun import BaseSpider_improve_alwaysrun

from util.util_url import UtilUrl

from extractor.information_center.baidu_news_extractor import BaiduNewsExtractor
from store.information_center.center_store import SourceStore

class BasicSourceSpider(BaseSpider_improve_alwaysrun):
    '''
        百度新闻
        http://news.baidu.com/ns?tn=news&word=%E6%AC%A7%E8%8E%B1%E9%9B%85&f=8&rsv_bp=1&rn=20&cl=2&ie=utf-8&ct=0

        &pn=20  第2页，  20 一页

    '''

    def __init__(self):
        super(BasicSourceSpider, self).__init__()
        self.basicExtractor = BaiduNewsExtractor()
        self.log = UtilLogger('SourceSpider',
                              os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_SourceSpider'))
        # 自己的log
        # self.log_record = UtilLogger('Record_SourceSpider',
        #                         os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_RecordSourceSpider'))
        self.userpc_agents = UtilUseragent.get(type='PC')
        # 定时休眠时间  分钟
        self.difsecond = 60 * 60 * 24
        self.config = {"redirect": 1}
        self.sended_tasks_max = 1000  # 限制任务数
        self.stores = None
        self.search_url = 'http://news.baidu.com/ns?'

    def get_user_password(self):
        return 'sunxiang', 'sxspider'
        # return 'test', 'test'
        # return 'xuliang', 'xlspider'

    # def get_downloader(self):
        #     """
        #     设置下载器类型，默认为Downloader
        #     Return:
        #         SpiderDownloader
        #     """
        # return Downloader(set_mode='db', get_mode='db')
        # return HtmlLocalDownloader(set_mode='db', get_mode='db')

    def integer_point(self):
        # 获取当前整点
        time_now = str(datetime.today())
        start_index = time_now.find(" ")
        end_index = time_now.find(":")
        time_point = int(time_now[start_index + 1: end_index])  # 当前整点数
        return time_point

    def is_start(self):
        # 一直运行的程序 判断什么时候获取任务查询
        return True

    def start_requests(self):
        try:
            while True:
                # 设置几点运行
                if self.integer_point > 0:
                    db = StoreMysql(**config.content_center)
                    sql = "SELECT id, keyword FROM content_center.content_keyword ;"
                    keywords_list = db.query(sql)
                    print "时间:%s;开始执行:任务长度:%s" % (str(datetime.today()), str(len(keywords_list)))
                    # 第 1到 5页， 100条记录 一页20
                    for page_index in xrange(1, 5):
                        for keyword_one in keywords_list:
                            keyword_id = keyword_one[0]
                            keyword = keyword_one[1]
                            params = {'word': keyword, 'ie': 'utf-8', 'tn': 'news',
                                      'rn': 20, 'f': 8, 'rsv_bp': 1, 'cl': 2, 'ct': 0, 'pn': page_index * 20}
                            url = self.search_url + urllib.urlencode(params)

                            urls = [{'url': url, 'type': 1, 'id': 0, "keyword_id": keyword_id, "keyword": keyword,
                                     "ext_type": 1}]
                            request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)}, urls=urls)
                            self.sending_queue.put(request)

                    time.sleep(self.difsecond)
                else:
                    time.sleep(60 * 20)
        except Exception:
            print traceback.format_exc()

    def deal_request_results(self, request, results):
        if results == 0:
            self.log.error('参数异常 请求发送失败 urls: %s' % request.urls)
        elif results == -2:
            self.log.error('没有相应地域 urls: %s' % request.urls)
        elif results == -1:
            self.log.error("向数据库 添加任务失败  设置request 失败  urls: %s" % request.urls)
            self.sended_queue.put(request)
        else:
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        stores.append(SourceStore())
        self.stores = stores
        return stores

    def deal_response_results(self, request, results, stores):
        if results == 0:
            return False
        else:
            urls = list()
            failed_urls = list()
            purls = list()
            for u in request.urls:
                url = u['unique_md5']
                if url in results:
                    result = results[url]
                    if str(result['status']) == '2':
                        ext_type = u["ext_type"]
                        if ext_type == 1:
                            self.deal_request_html(u, result['result'])

                        elif ext_type == 2:
                            data = {'url': u["url"], 'html': result['result']}
                            self.store_queue.put({"result": [data], "type": 2, "field": "url"})

                    elif str(result['status']) == '3':
                        # 一直重试
                        # failed_urls.append(u)
                        #  重试限制次数
                        failed_urls = failed_urls + self.retry(u, 3)
                        # self.log.info("status == 3 url:%s" % u)
                    else:
                        urls.append(u)
                else:
                    failed_urls.append(u)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)
            if len(failed_urls) > 0:
                new_request = copy(request)
                new_request.urls = failed_urls
                self.sending_queue.put(new_request)
                new_request = None

    def deal_request_html(self, url, html):
        r = self.basicExtractor.extractor(html)
        for res in r:
            if res['response_status'] == 1:
                for news in res['news']:
                    item = dict()
                    item['title'] = news['title']
                    item['keyword'] = url['keyword']
                    item['url'] = news['url']
                    item['source'] = news['source']
                    item['summary'] = news['summary']
                    item['createtime'] = news['createtime']
                    self.store_queue.put({"result": [item], "type": 1})

                    new_url = UtilUrl.get_url(url, item['url'])
                    request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)}, config=self.config,
                                            urls=[{'url': new_url, 'type': 1, 'id': 0, "ext_type": 2}])
                    self.sending_queue.put(request)

    def to_store_results(self, results, stores):
        store_type = results["type"]
        if store_type == 1:
            stores[0].store_table(results['result'], "content_baidu_news")
        else:
            stores[0].store_table(results['result'], "content_baidu_news", type=2, field="url")

def Main():
    spider = BasicSourceSpider()
    # spider.run(1, 1, 1, 1, 600, 600, 600, 600, True)
    spider.run(10, 20, 20, 10, 600, 600, 600, 600, True)

if __name__ == '__main__':
    Main()
