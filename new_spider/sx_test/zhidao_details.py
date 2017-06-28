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

from spider.basespider_separate_deal_and_store import BaseSpiderSeparateDealAndStore
from downloader.downloader import SpiderRequest
from util_log import UtilLogger
import random
import copy
import traceback

from store_mysql import StoreMysql

reload(sys)
sys.setdefaultencoding('utf8')

# from store._39._39_department_store import _39DepartmentStore

from extractor.baidu_zhidao.baidu_zhidao_extractor import ZhiDaoExtractor
from datetime import datetime

from store.sx_basestore import BaseStore
from spider import config

class ZhiDaoDetails(BaseSpiderSeparateDealAndStore):

    def __init__(self):
        super(ZhiDaoDetails, self).__init__()
        self.extractor = ZhiDaoExtractor()
        self.log = UtilLogger('ZhiDaoDetails', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_ZhiDaoDetails'))
        self.dbParam = config.baidu_zhidao

        self.spider_log = UtilLogger('EngineBasicSpider',
                                     os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  'log_sxSourceSpider'))

        self.type_classify = ["default", "highScore", "hot", "feed"]
        self.pageType = ["default", "highScore", "hot"]
        self.pageTypeCount = 34
        # self.seed_url = 'http://ask.39.net/jibing/list_0_1721_1.html'
        # self.seed_url = 'https://zhidao.baidu.com/list/'
        # self.seed_head = 'https://zhidao.baidu.com'

    def get_user_password(self):
        # return 'sunxiang', 'sxspider'
        return 'test', 'test'

    # def get_downloader(self):
        """
        设置下载器类型，默认为Downloader
        Return:
            SpiderDownloader
        """
        # return Downloader(set_mode='db', get_mode='db')
        # return HtmlLocalDownloader(set_mode='http', get_mode='http')

    def start_requests(self):
        try:
            current_integer = self.get_current_integer()
            if current_integer > 0:
                db = StoreMysql(**self.dbParam)
                sql = "select id, url from sites "
                results = db.query(sql)
                print "spider length:" + str(len(results))

                for result in results:
                    for type in self.type_classify:
                        addUrl = "&type=%s" % type
                        urls = [{'url': result[1]+addUrl, 'type': 1, "site_id": result[0], "extractor_type": 1}]
                        # configs = {'priority': 3}
                        # , config = configs
                        request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)}, urls=urls)
                        self.sending_queue.put(request)

                        if type in self.pageType:
                            for page in xrange(1, self.pageTypeCount):
                                temp_url = result[1]+addUrl+"&rn=30&pn="+str(30*page)+"&_pjax=%23j-question-list-pjax-container"
                                print "temp_url:%s" % temp_url
                                urls = [{'url': temp_url, 'type': 1, 'unique_key': 1, "site_id": 1, "extractor_type": 1}]
                                configs = {'priority': 3}
                                header = {'User-Agent': random.choice(self.user_agents),
                                          'Referer': 'https://zhidao.baidu.com/list?type=default&cid=101',
                                          'X-PJAX': 'true',
                                          'X-PJAX-Container': '#j-question-list-pjax-container'
                                          }

                                request = SpiderRequest(headers=header, urls=urls, config=configs)
                                self.sending_queue.put(request)

            # urls = [{'url': "https://zhidao.baidu.com/list?cid=101&type=default&rn=30&pn=60&_pjax=%23j-question-list-pjax-container",
            #          'type': 1, 'unique_key': 1, "site_id": 1}]
            # configs = {'priority': 3}
            # header = {'User-Agent': random.choice(self.user_agents),
            #           'Referer': 'https://zhidao.baidu.com/list?type=default&cid=101',
            #           'X-PJAX': 'true',
            #           'X-PJAX-Container': '#j-question-list-pjax-container'
            #             }
            #
            # request = SpiderRequest(headers=header, urls=urls, config=configs)
            # self.sending_queue.put(request)

        except Exception, e:
            self.log.error('获取初始请求出错:%s' % str(e))

    def deal_request_results(self, request, results):
        if results == 0:
            self.spider_log.error('参数异常 请求发送失败 urls: %s' % request.urls)
        elif results == -2:
            self.spider_log.error('没有相应地域 urls: %s' % request.urls)
        elif results == -1:
            self.spider_log.error("向数据库 添加任务失败  设置request 失败  urls: %s" % request.urls)
            # self.sended_queue.put(request)
        else:
            # print "send one request"
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        stores.append(BaseStore())
        return stores

    def deal_response_results(self, request, results, stores):
        if results == 0:
            return False
        else:
            urls = list()
            failed_urls = list()  # 失败链接
            for u in request.urls:
                url = u['unique_md5']
                if url in results:
                    result = results[url]
                    if str(result['status']) == '2':
                        if len(result['result']) < 10:
                            print "failed_urls: %s" % u
                            failed_urls.append(u)
                        else:
                            return_state = self.deal_response_extractor(u, result['result'])
                    elif str(result['status']) == '3':
                        self.log.info('抓取失败:%s' % u)
                    else:
                        urls.append(u)
                else:
                    # 被别的取走
                    failed_urls.append(u)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)
            if len(failed_urls) > 0:
                new_request = copy(request)
                new_request.urls = failed_urls
                self.sending_queue.put(new_request)
                del new_request

    def deal_response_extractor(self, url, html):
        try:
            # sphtml = html
            # sxfile = open("sxsx2.txt", "wb")
            # sxfile.write(sphtml)
            # sxfile.close

            if url["extractor_type"] == 1:
                result = self.extractor.extractor_sites_list_details(html, site_id=url["site_id"])
                if result["response_status"] == 1:

                    if len(result["question_noanswer"]) > 0:
                        self.store_queue.put({'result_list': result["question_noanswer"], "type": 1})
                    if len(result["question_answer"]) > 0:

                        question_answers = result["question_answer"]
                        for question_answer in question_answers:
                            # print "have answer count"
                            urls = [{'url': question_answer["url"], 'type': 1, "site_id": url["site_id"], "extractor_type": 2,
                                     "cid": question_answer["cid"], "qid": question_answer["qid"],
                                     "title": question_answer["title"], "site_url": question_answer["url"]}]
                            request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)}, urls=urls)
                            self.sending_queue.put(request)
                            urls = list()
                else:
                    print "exception url: %s" % url
            elif url["extractor_type"] == 2:
                result = self.extractor.extractor_sites_details(html, site_id=url["site_id"], qid=url["qid"])
                if result["response_status"] == 1:
                    if result['question'] is not None:
                        question_item = result['question']
                        question_item["site_id"] = url["site_id"]
                        question_item["title"] = url["title"]
                        question_item["url"] = url["site_url"]
                        question_item["qid"] = url["qid"]
                        question_item["cid"] = url["cid"]
                        result_list = list()
                        result_list.append(question_item)
                        self.store_queue.put({'result_list': result_list, "type": 1})
                    if len(result['answers']) > 0:
                        # answers = result['answers']
                        self.store_queue.put({'result_list': result['answers'], "type": 2})
                else:
                    print "exception url: %s" % url
        except Exception:
            print(traceback.format_exc())

    def to_store_results(self, results, stores):
        if results["type"] == 2:
            return_state = stores[0].store_table_db(results["result_list"], table="answers",
                                                    db_connnection=self.dbParam)
        else:
            return_state = stores[0].store_table_db(results["result_list"], table="questions",
                                                    db_connnection=self.dbParam)
        print return_state

    def get_current_integer(self):
        time_now = str(datetime.today())
        # print time_now
        time_now = time_now.split(" ")
        time_str = time_now[1]
        time_index = time_str.index(":")
        time_point = int(time_str[0:time_index])  # 当前整点数
        return time_point

def Main():
    spider = ZhiDaoDetails()
    spider.run(1, 1, 1, 1, 60, 60, 60, 60, True)

if __name__ == '__main__':
    Main()
