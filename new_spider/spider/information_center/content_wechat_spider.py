# -*- coding: utf8 -*-
import os
import random
import sys
import time
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

from downloader.downloader import SpiderRequest
from util.util_useragent import UtilUseragent
from util_log import UtilLogger

from spider.basespider_improve_alwaysrun import BaseSpider_improve_alwaysrun

# from extractor.information_center.baidu_koubei_extractor import SourceExtractor
# from store.information_center.center_store import SourceStore
# from extractor.wechat.wechat_news_extractor import *
# from store.wechat.wechat_public_num_store import WechatPublicNumStore
# from store.wechat.wechat_article_store import WechatArticleStore

from extractor.information_center.wechat_news_extractor import SourceExtractor
from store.information_center.center_store import SourceStore

class BasicSourceSpider(BaseSpider_improve_alwaysrun):

    '''
    wechat 文章
        type: 2 文章  1 公众号
        http://weixin.sogou.com/weixin?query=%E6%95%99%E8%82%B2&_sug_type_=&s_from=input&_sug_=n&type=2&page=1&ie=utf8
    '''
    def __init__(self):
        super(BasicSourceSpider, self).__init__()
        self.basicExtractor = SourceExtractor()
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
        # self.publicNumSearchPageExtractor = SougouPublicNumSearchPageExtractor()
        # self.articleSearchPageExtractor = SougouArticleSearchPageExtractor()
        # self.publicNumArticlesPageExtractor = SougouPublicNumArticlesPageExtractor()
        # self.articleExtractor = SougouArticleExtractor()

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
                    # db = StoreMysql(**config.content_center)
                    # sql = "SELECT id, keyword FROM content_keyword ;"
                    # keywords_list = db.query(sql)
                    # # configs = {'req_type': 2, 'num_batch': 5, 'news_batch': 5, 'source': 2}
                    # # 第1到 10页
                    # for page_index in xrange(1, 11):
                    #     for keyword_one in keywords_list:
                    #         keyword_id = keyword_one[0]
                    #         keyword = keyword_one[1]
                    #
                    #         kwh = {"type": 2, "query": keyword, "ie": "utf8", "_sug_": "n", "page": page_index, "s_from": "input"}
                    #         url = 'http://weixin.sogou.com/weixin?' + urllib.urlencode(kwh) + '&_sug_type_='
                    #
                    #         urls = [{"url": url, "type": 1, "req_type": 1, "keyword": keyword, "keyword_id": keyword_id}]
                    #         basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.userpc_agents)},
                    #                                       urls=urls)
                    #         self.sending_queue.put_nowait(basic_request)

                    url = "http://weixin.sogou.com/weixin?s_from=input&type=2&_sug_=n&query=%E6%A0%BC%E5%85%B0%E7%8E%9B%E5%BC%97%E5%85%B0&ie=utf8&page=4&_sug_type_="
                    urls = [{"url": url, "type": 1, "req_type": 1, "keyword": "11", "keyword_id": "222"}]
                    basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.userpc_agents)},
                                                                                        urls=urls)
                    self.sending_queue.put_nowait(basic_request)

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
        # stores.append(WechatPublicNumStore())
        # stores.append(WechatArticleStore())
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
                        configs = request.config
                        req_type = u['req_type']
                        headers = request.headers
                        headers['Referer'] = u["url"]

                        # 文章列表
                        if req_type == 1:
                            self.deal_response_list(u, configs, result['result'], headers)
                        # 详情
                        elif req_type == 2:
                            self.deal_article_page_response(u, result['result'])

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

    def deal_response_list(self, url, configs, html, headers):
        try:
            r = self.basicExtractor.extractor_list(html)
            if type(r) == int:
                self.log.info("deal_response_list result:%s ;url: %s" % (str(r), url["url"]))
            else:
                new_configs = {"redirect": 1}
                new_urls = list()
                for item in r:
                    new_url = copy(url)
                    new_url['url'] = item["url"]
                    new_url['title'] = item['title']
                    new_url['summary'] = item['summary']

                    new_url['req_type'] = 2
                    new_urls.append(new_url)
                request = SpiderRequest(headers=headers, config=new_configs, urls=new_urls)
                self.sending_queue.put(request)
        except:
            print traceback.format_exc()

    # 解析文章正文
    def deal_article_page_response(self, url, html):
        r = self.basicExtractor.extractor_detail(html)
        items = list()
        for res in r:
            if 'wechat_num' in url and len(url['wechat_num']) > 0:
                res['wechat_num'] = url['wechat_num']
            if 'wechat_num' not in res or len(res['wechat_num']) == 0:
                continue
            if 'wechat_name' in url:
                res['wechat_name'] = url['wechat_name']
            res['keyword_id'] = url['keyword_id']
            res['keyword'] = url['keyword']

            res['title'] = url['title']
            res['summary'] = url['summary']
            res['url'] = url['url']
            # res['batch'] = configs['news_batch']
            items.append(res)
        self.store_queue.put({'data': items, 'type': 1, 'storeIndex': 1})

    def to_store_results(self, results, stores):
        stores[0].store_table(results['data'], "content_wechat_news")

def Main():
    spider = BasicSourceSpider()
    # spider.run(2, 5, 5, 2, 600, 600, 600, 600, True)
    spider.run(5, 20, 30, 10, 600, 600, 600, 600, True)

if __name__ == '__main__':
    Main()
