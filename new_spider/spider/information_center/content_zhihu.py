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

from extractor.information_center.zhihu_extractor import SourceExtractor
from store.information_center.center_store import SourceStore


class BasicSourceSpider(BaseSpider_improve_alwaysrun):
    '''
        http://zhihu.sogou.com/zhihu?query=%E6%AC%A7%E8%8E%B1%E9%9B%85&page=1
        extractor_type  1: 列表页
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

    # def is_start(self):
    #     # 一直运行的程序 判断什么时候获取任务查询
    #     return True

    def start_requests(self):
        try:
            while True:
                # 设置几点运行
                if self.integer_point > 0:
                    db = StoreMysql(**config.content_center)
                    sql = "SELECT id, keyword FROM content_center.content_keyword;"
                    keywords_list = db.query(sql)

                    for page_index in xrange(1, 11):
                        for keyword_one in keywords_list:
                            keyword_id = keyword_one[0]
                            keyword = keyword_one[1]
                            kwh = {'query': keyword, "page": page_index}
                            url = 'http://zhihu.sogou.com/zhihu?' + urllib.urlencode(kwh)
                            # print url
                            urls = [{"url": url, "type": 1, "extractor_type": 1, "keyword": keyword, "keyword_id": keyword_id}]
                            basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.userpc_agents)}, urls=urls)
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
            # 判断是否处理  url 可能相同
            self.log.error("向数据库 添加任务失败 设置request 失败  urls: %s" % request.urls)
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

                        if u["extractor_type"] == 1:
                            self.deal_response_type1(u, result['result'])
                        if u["extractor_type"] == 2:
                            self.deal_response_type2(u, result['result'])

                    elif str(result['status']) == '3':
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

    def deal_response_type1(self, url, html):
        response_result = self.basicExtractor.extractor_list(html)
        if type(response_result) == int:
            self.log.info("deal_response_type1  result:%s ;url: %s" % (str(response_result), url))
        else:
            for response_one in response_result:
                send_url = response_one["a_href"]
                asker = response_one["asker"]
                if send_url.find("www.zhihu.com") > -1:

                    urls = [{"url": send_url, "type": 1, "extractor_type": 2, "keyword": url["keyword"], "asker": asker,
                             "keyword_id": url["keyword_id"]}]
                    # headers={'User-Agent': random.choice(self.userpc_agents)},
                    basic_request = SpiderRequest(urls=urls, config=self.config)
                    self.sending_queue.put_nowait(basic_request)
                else:
                    self.log.info("result_one not contain www.zhihu.com url:%s" % url["url"])

    def deal_response_type2(self, url, html):
        response_result = self.basicExtractor.extractor_detail(html)
        if type(response_result) == int:
            self.log.info("deal_response_type2  result:%s ;url: %s" % (str(response_result), url))
        else:
            question_item = response_result["question_item"]
            answer_list = response_result["answer_list"]
            question_item["url"] = url["url"]
            question_item["keyword_id"] = url["keyword_id"]
            question_item["asker"] = url["asker"]

            if question_item:
                if question_item.get("description", "") != "":
                    self.store_queue.put({"question_item": question_item, "answer_list": answer_list})
                else:
                    self.log.info("deal_response_detail type error 222;url: %s" % url["url"])
            else:
                self.log.info("deal_response_detail type error ;url: %s" % url["url"])

    '''
        results  type 1:
                task_id  task表id
    '''
    def to_store_results(self, results, stores):
        try:
            question_item = results["question_item"]
            answer_list = results["answer_list"]
            store_question_list = list()
            store_question_list.append(question_item)
            question_id = self.stores[0].store_table(store_question_list, table="content_zhihu_question")

            if question_id != -1:
                store_answer_list = list()
                for answer_one in answer_list:
                    answer_one["question_id"] = question_id
                    store_answer_list.append(answer_one)
                self.stores[0].store_table(store_answer_list, table="content_zhihu_answer")

                # question_count_url = "https://zhidao.baidu.com/api/qbpv?q=%s" % qid
                # urls = [
                #     {"url": question_count_url, "type": 1, "extractor_type": 3, "qid": qid,
                #      "question_id": question_id}]
                # basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.userpc_agents),
                #                                        "Referer": "https://zhidao.baidu.com/question/%s.html" % qid},
                #                               urls=urls)
                # self.sending_queue.put_nowait(basic_request)
            else:
                print "save exception url exception question_item:%s" % str(question_item)
        except:
            print traceback.format_exc()

def Main():
    spider = BasicSourceSpider()
    # spider.run(3, 5, 5, 3, 600, 600, 600, 600, True)
    spider.run(10, 30, 30, 10, 600, 600, 600, 600, True)

if __name__ == '__main__':
    Main()
