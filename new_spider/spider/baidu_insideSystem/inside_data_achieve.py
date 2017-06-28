# -*- coding: utf8 -*-
import json
import os
import random
import sys
import time
import urllib
from datetime import datetime
from datetime import timedelta

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
from store.baidu_inside_system.baidu_inside_store import SpiderBaseStore

from extractor.baidu_inside_system.baidu_web_extractor import BaiduSpiderWebExtractor
from extractor.baidu_inside_system.baidu_news_extractor import BaiduSpiderNewsExtractor
from extractor.baidu_inside_system.baidu_zhidao_extractor import BaiduSpiderZhiDaoExtractor
from sx_util.inside_system_data import InsideSystem

class BasicSourceSpider(BaseSpider_improve_alwaysrun):
    '''
    移動端 ua 異常   根据ua 不同展现页不同 目前移动端ua 固定 页数
    pc:
        网页  https://www.baidu.com/s?wd=招聘&pn=10   rn=50 高级
        新闻  http://news.baidu.com/ns?cl=2&word=招聘&rn=20&pn=20
        知道  第一页11条之后每页10条  https://zhidao.baidu.com/search?word=招聘&pn=10
    mobile:
        网页  https://m.baidu.com/s?wd=招聘&pn=10
        新闻  https://m.news.baidu.com/news?tn=bdapinewsearch&ct=1&qq-pf-to=pcqq.c2c&
                kwh = {'word': keyword, 'rn': 20, 'pn': pn}   pn 以20递增
        知道  第一页11条之后每页10条 api: https://wapiknow.baidu.com/msearch/ajax/getsearchlist?word=%E6%8B%9B%E8%81%98&pn=10

    '''
    def __init__(self):
        super(BasicSourceSpider, self).__init__()
        # self.basicExtractor = SourceExtractor()
        # 定时休眠时间  分钟
        self.log = UtilLogger('SourceSpider',
                              os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_SourceSpider'))
        self.log_record = UtilLogger('record_SourceSpider',
                                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_RecordSourceSpider'))
        self.userpc_agents = UtilUseragent.get(type='PC')
        self.mobile_useragent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        self.sended_queue_maxsize = 2000  # 发送限制
        self.send_one_tasks = 500  # 一次取出

        self.baidu_store = SpiderBaseStore(config.insideSystem_DB)
        self.sleep_time = 180  # 没有任务休眠时间

        self.baidu_web = BaiduSpiderWebExtractor()
        self.baidu_xinwen = BaiduSpiderNewsExtractor()
        self.baidu_zhidao = BaiduSpiderZhiDaoExtractor()
        self.send_function = InsideSystem()
        self.separator = "||||"
        self.save_port = 1

    def get_user_password(self):
        # return 'sunxiang2', 'sxspider'
        return 'test', 'test'

    # def get_downloader(self):
        #     """
        #     设置下载器类型，默认为Downloader
        #     Return:
        #         SpiderDownloader
        #     """
        # return Downloader(set_mode='db', get_mode='db')
        # return HtmlLocalDownloader(set_mode='db', get_mode='db')

    def is_start(self):
        return self.sended_queue.qsize() < self.sended_queue_maxsize and self.sending_queue.qsize() < self.sended_queue_maxsize \
               and self.response_queue.qsize() < self.sended_queue_maxsize

    def start_requests(self):
        try:
            print "开始获取任务"
            # 获取任务
            while True:
                if self.is_start():
                    db = StoreMysql(**config.insideSystem_DB)
                    sql = "SELECT * FROM keywordrank.data_achieve where state = 0 and save_port = %d limit  %d" % (self.save_port, self.send_one_tasks)
                    # sql = "SELECT * FROM keywordrank.data_achieve where state = 0 and id = 383 "
                    task_results = db.query(sql)
                    db.close()
                    print "task_results length:%d" % len(task_results)
                    if len(task_results) > 0:
                        result_update = list()
                        for result in task_results:
                            result_update.append(result[0])
                            result_id = result[0]
                            result_file_id = result[1]
                            result_keyword_id = result[2]
                            result_page = result[3]
                            result_content_achieve_type = result[4]
                            result_search_device = result[5]
                            result_search_target = result[6]
                            keyword = result[9]

                            self.send_tasks_assort(result_id, result_file_id, result_keyword_id, result_page,
                                    result_content_achieve_type, result_search_device, result_search_target, keyword)

                        if len(result_update) > 0:
                            self.baidu_store.update_ids("data_achieve", result_update)
                        time.sleep(20)
                    else:
                        time.sleep(self.sleep_time)
                else:
                    time.sleep(self.sleep_time)

        except Exception:
            print traceback.format_exc()

    def send_tasks_assort(self, task_id, result_file_id, result_keyword_id, result_page,
                                result_content_achieve_type, result_search_device, result_search_target, keyword):
        '''
        spider_type 1:数据pc网页  2:数据pc新闻 3:数据pc知道 4:数据mobile网页 5:数据mobile新闻 6:数据mobile知道
                7:截图pc网页 8:截图pc新闻 9:截图pc知道 10:截图mobile网页 11:截图mobile新闻 12: 截图mobile知道

        send_type   1:百度网页 2：新闻 3：知道
        :param result_id:
        :param result_file_id:
        :param result_keyword_id:
        :param result_page:
        :param result_content_achieve_type:
        :param result_search_device:
        :param result_search_target:
        :param keyword:
        :return:
        百度新闻 pc http://news.baidu.com/ns?word=%E6%8B%9B%E8%81%98&pn=300&rn=10   # 高级搜索rn
        '''
        # 判断发送数据类型
        result_content_achieve_type = int(result_content_achieve_type)
        result_search_device = int(result_search_device)
        result_search_target = int(result_search_target)
        if result_content_achieve_type == 1:
            urls = list()
            if result_search_device == 1:
                # pc
                if result_search_target == 1:
                    # 网页
                    if int(result_page) > 5:
                        print "pa result_page > 5"
                    rn = int(result_page) * 10
                    kwh = {'wd': keyword, 'rn': rn}
                    url = 'https://www.baidu.com/s?' + urllib.urlencode(kwh)
                    url_one = {"url": url, "type": 1, "file_id": result_file_id, "keyword_id": result_keyword_id,
                                "result_page": result_page, "keyword": keyword, "spider_type": 1,
                                "seach_device": "pc", "page": "", "send_type": 1, "task_id": task_id, "unique_key": task_id}
                    urls.append(url_one)
                elif result_search_target == 2:
                    # 新闻
                    for i in xrange(0, int(result_page)):
                        pn = i * 20
                        kwh = {'word': keyword, 'rn': 20, 'pn': pn}
                        url = 'http://news.baidu.com/ns?cl=2&' + urllib.urlencode(kwh)
                        url_one = {"url": url, "type": 1, "file_id": result_file_id, "page": i+1,
                                    "keyword_id": result_keyword_id, "seach_device": "pc", "unique_key": task_id,
                                    "keyword": keyword, "spider_type": 2, "send_type": 2, "task_id": task_id}
                        urls.append(url_one)
                else:
                    # 知道
                    for i in xrange(0, int(result_page)):
                        pn = i * 10
                        kwh = {'word': keyword, 'pn': pn}
                        url = "https://zhidao.baidu.com/search?" + urllib.urlencode(kwh)
                        url_one = {"url": url, "type": 1, "file_id": result_file_id, "page": i+1,
                                    "keyword_id": result_keyword_id, "seach_device": "pc", "unique_key": task_id,
                                    "keyword": keyword, "spider_type": 3, "send_type": 3, "task_id": task_id}
                        urls.append(url_one)
            else:
                # mobile
                if result_search_target == 1:
                    # 网页
                    for i in xrange(0, int(result_page)):
                        rn = i * 10
                        kwh = {'wd': keyword, 'pn': rn}
                        url = 'https://m.baidu.com/s?' + urllib.urlencode(kwh)
                        url_one = {"url": url, "type": 1, "file_id": result_file_id, "page": i+1,
                                    "keyword_id": result_keyword_id, "spider_type": 4, "unique_key": task_id,
                                    "keyword": keyword, "seach_device": "mb", "send_type": 1, "task_id": task_id}
                        urls.append(url_one)
                elif result_search_target == 2:
                    # 新闻
                    # "https://m.news.baidu.com/news?tn=bdapinewsearch&word=1122&pn=0&rn=20&ct=1&qq-pf-to=pcqq.c2c"
                    for i in xrange(0, int(result_page)):
                        pn = i * 10
                        kwh = {'word': keyword, 'rn': 20, 'pn': pn}
                        url = "https://m.news.baidu.com/news?tn=bdapinewsearch&ct=1&qq-pf-to=pcqq.c2c&" + urllib.urlencode(kwh)
                        url_one = {"url": url, "type": 1, "file_id": result_file_id, "page": i+1,
                                    "keyword_id": result_keyword_id, "spider_type": 5, "unique_key": task_id,
                                    "keyword": keyword, "seach_device": "mb", "send_type": 2, "task_id": task_id}
                        urls.append(url_one)
                else:
                    # 知道
                    # "https://wapiknow.baidu.com/msearch/ajax/getsearchlist?word=%E6%8B%9B%E8%81%98&pn=10"
                    for i in xrange(0, int(result_page)):
                        pn = i * 10
                        kwh = {'word': keyword, 'pn': pn}
                        url = "https://wapiknow.baidu.com/msearch/ajax/getsearchlist?" + urllib.urlencode(kwh)
                        url_one = {"url": url, "type": 1, "file_id": result_file_id, "page": i+1,
                                    "keyword_id": result_keyword_id, "spider_type": 6, "unique_key": task_id,
                                    "keyword": keyword, "seach_device": "mb", "send_type": 3, "task_id": task_id}
                        urls.append(url_one)

            basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.userpc_agents)
                            if int(str(result_search_device)[0:1]) == "1" else self.mobile_useragent}, urls=urls)
            self.sending_queue.put(basic_request)
        else:
            # configs = {'param': {'capture_width': '414', 'capture_height': '736'}}
            # 截图
            # print "截图"
            urls = list()
            if result_search_device == 1:
                # pc
                if result_search_target == 1:
                    # 网页
                    for i in xrange(0, int(result_page)):
                        pn = i * 10
                        kwh = {'wd': keyword, 'pn': pn}
                        url = 'https://www.baidu.com/s?' + urllib.urlencode(kwh)
                        url_one = {"url": url, "type": 4, "file_id": result_file_id, "page": i+1,
                                    "keyword_id": result_keyword_id, "seach_device": "pc", "unique_key": task_id,
                                    "keyword": keyword, "spider_type": 7, "send_type": 1, "task_id": task_id}
                        urls.append(url_one)
                elif result_search_target == 2:
                    # 新闻
                    for i in xrange(0, int(result_page)):
                        pn = i * 20
                        kwh = {'word': keyword, 'rn': 20, 'pn': pn}
                        url = 'http://news.baidu.com/ns?cl=2&' + urllib.urlencode(kwh)
                        # print url
                        url_one = {"url": url, "type": 4, "file_id": result_file_id, "page": i+1,
                                    "keyword_id": result_keyword_id, "seach_device": "pc", "unique_key": task_id,
                                    "keyword": keyword, "spider_type": 8, "send_type": 2, "task_id": task_id}
                        urls.append(url_one)
                else:
                    # 知道
                    for i in xrange(0, int(result_page)):
                        pn = i * 10
                        kwh = {'word': keyword, 'pn': pn}
                        url = "https://zhidao.baidu.com/search?" + urllib.urlencode(kwh)
                        url_one = {"url": url, "type": 4, "file_id": result_file_id, "page": i+1,
                                    "keyword_id": result_keyword_id, "seach_device": "pc", "unique_key": task_id,
                                    "keyword": keyword, "spider_type": 9, "send_type": 3, "task_id": task_id}
                        urls.append(url_one)

                basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.userpc_agents)}, urls=urls)
                self.sending_queue.put(basic_request)
            else:
                configs = {'param': {'capture_width': '414', 'capture_height': '736'}}
                # mobile
                if result_search_target == 1:
                    # 网页
                    for i in xrange(0, int(result_page)):
                        rn = i * 10
                        kwh = {'wd': keyword, 'pn': rn}
                        url = 'https://m.baidu.com/s?' + urllib.urlencode(kwh)
                        url_one = {"url": url, "type": 4, "file_id": result_file_id, "page": i+1,
                                    "keyword_id": result_keyword_id, "spider_type": 10, "unique_key": task_id,
                                    "keyword": keyword, "seach_device": "mb", "send_type": 1, "task_id": task_id}
                        urls.append(url_one)
                    basic_request = SpiderRequest(headers={'User-Agent': self.mobile_useragent}, urls=urls,
                                                  config=configs)
                    self.sending_queue.put(basic_request)
                elif result_search_target == 1:
                    print "mobile  xinwen"
                    # 新闻
                    # "https://m.news.baidu.com/news?tn=bdapinewsearch&word=1122&pn=0&rn=20&ct=1&qq-pf-to=pcqq.c2c"
                    # for i in xrange(0, int(result_page)):
                    #     pn = i * 10
                    #     kwh = {'word': keyword, 'rn': 20, 'pn': pn}
                    #     url = "https://m.news.baidu.com/news?tn=bdapinewsearch&ct=1&qq-pf-to=pcqq.c2c&" + urllib.urlencode(
                    #         kwh)
                    #     url_one = [{"url": url, "type": 1, "result_file_id": result_file_id,
                    #                 "result_keyword_id": result_keyword_id, "spider_type": 5,
                    #                 "result_page": result_page, "keyword": keyword}]
                    #     urls.append(url_one)
                else:
                    print "mobile zhidao"
                    # 知道
                    # "https://wapiknow.baidu.com/msearch/ajax/getsearchlist?word=%E6%8B%9B%E8%81%98&pn=10"
                    # for i in xrange(0, int(result_page)):
                    #     pn = i * 10
                    #     kwh = {'word': keyword, 'pn': pn}
                    #     url = "https://wapiknow.baidu.com/msearch/ajax/getsearchlist?" + urllib.urlencode(kwh)
                    #     url_one = [{"url": url, "type": 1, "result_file_id": result_file_id,
                    #                 "result_keyword_id": result_keyword_id, "spider_type": 6,
                    #                 "result_page": result_page, "keyword": keyword}]
                    #     urls.append(url_one)

    def deal_request_results(self, request, results):
        if results == 0:
            self.log.error('参数异常 请求发送失败 urls: %s' % request.urls)
        elif results == -2:
            self.log.error('没有相应地域 urls: %s' % request.urls)
        elif results == -1:
            self.log.error("向数据库 添加任务失败  设置request 失败  urls: %s" % request.urls)
            # self.sended_queue.put(request)
        else:
            # print "send one request"
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        # stores.append(SourceStore())
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
                    result = None
                    result = results[url]
                    if str(result['status']) == '2':
                        spider_type = int(u["spider_type"])
                        if spider_type == 1:
                            self.deal_baidu_response_type1(u, result['result'])
                        elif spider_type == 2:
                            self.deal_baidu_response_type2(u, result['result'])
                        elif spider_type == 3:
                            self.deal_baidu_response_type3(u, result['result'])
                        elif spider_type == 4:
                            self.deal_baidu_response_type4(u, result['result'])
                        elif spider_type == 5:
                            self.deal_baidu_response_type5(u, result['result'])
                        elif spider_type == 6:
                            self.deal_baidu_response_type6(u, result['result'])
                        elif spider_type == 7:
                            self.deal_baidu_response_type7(u, result['result'])
                        elif spider_type == 8:
                            self.deal_baidu_response_type8(u, result['result'])
                        elif spider_type == 9:
                            self.deal_baidu_response_type9(u, result['result'])
                        elif spider_type == 10:
                            self.deal_baidu_response_type10(u, result['result'])
                        # elif spider_type == 11:
                        #     self.deal_baidu_response_type6(u, result['result'])
                        # elif spider_type == 12:
                        #     self.deal_baidu_response_type6(u, result['result'])

                        # if newurls:
                        #     failed_urls.append(newurls)
                        # result = None
                    elif str(result['status']) == '3':
                        # 失败
                        self.log_record.info("失败 result['status']) == 3 url:%s" % u)
                        send_results = [{"rank": -1}]
                        self.send_inside_system_data(u, send_results)

                        # failed_urls.append(u)
                    else:
                        urls.append(u)
                else:
                    self.log.info("插入数据库失败 url:%s" % u)
                    failed_urls.append(u)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)
            if len(failed_urls) > 0:
                new_request = copy(request)
                new_request.urls = failed_urls
                self.sending_queue.put(new_request)
                new_request = None

    def deal_baidu_response_type1(self, url, html):
        try:
            results = self.baidu_web.extractor_baidu_pc(html)
            if results == 3:
                send_results = [{"rank": -2}]
                self.send_inside_system_data(url, send_results)
            elif type(results) == int:
                self.log_record.info("deal_baidu_response_type1 exception url:%s;results:%s" % (url, results))
                send_results = [{"rank": -1}]
                self.send_inside_system_data(url, send_results)
            else:
                self.send_inside_system_data(url, results["rank"])
        except:
            print traceback.format_exc()
            send_results = [{"rank": -1}]
            self.send_inside_system_data(url, send_results)

    '''
    1:数据pc网页  2:数据pc新闻 3:数据pc知道 4:数据mobile网页 5:数据mobile新闻 6:数据mobile知道
                7:截图pc网页 8:截图pc新闻 9:截图pc知道 10:截图mobile网页 11:截图mobile新闻 12: 截图mobile知道
    '''
    def deal_baidu_response_type2(self, url, html):
        try:
            results = self.baidu_xinwen.extractor_baidu_news_pc(html)
            if results == 3:
                send_results = [{"rank": -2}]
                self.send_inside_system_data(url, send_results)
            elif type(results) == int:
                self.log_record.info("deal_baidu_response_type2 exception url:%s;results:%s" % (url, results))
                send_results = [{"rank": -1}]
                self.send_inside_system_data(url, send_results)
            else:
                self.send_inside_system_data(url, results)
        except:
            print traceback.format_exc()
            send_results = [{"rank": -1}]
            self.send_inside_system_data(url, send_results)

    def deal_baidu_response_type3(self, url, html):
        try:
            results = self.baidu_zhidao.extractor_baidu_zhidao_pc(html, url["page"])
            if results == 3:
                send_results = [{"rank": -2}]
                self.send_inside_system_data(url, send_results)
            elif type(results) == int:
                self.log_record.info("deal_baidu_response_type3 exception url:%s;results:%s" % (url, results))
                send_results = [{"rank": -1}]
                self.send_inside_system_data(url, send_results)
            else:
                self.send_inside_system_data(url, results)
        except:
            print traceback.format_exc()
            send_results = [{"rank": -1}]
            self.send_inside_system_data(url, send_results)

    def deal_baidu_response_type4(self, url, html):
        try:
            page = int(url["page"])
            if page > 1:
                pcount = (page - 2) * 10 + 11
            else:
                pcount = 0
            results = self.baidu_web.extractor_baidu_mobile(html, pcount=pcount)
            if results == 3:
                send_results = [{"rank": -2}]
                self.send_inside_system_data(url, send_results)
            elif type(results) == int:
                self.log_record.info("deal_baidu_response_type4 exception url:%s;results:%s" % (url, results))
                send_results = [{"rank": -1}]
                self.send_inside_system_data(url, send_results)
            else:
                self.send_inside_system_data(url, results["rank"])
        except:
            print traceback.format_exc()
            send_results = [{"rank": -1}]
            self.send_inside_system_data(url, send_results)

    def deal_baidu_response_type5(self, url, html):
        try:
            results = self.baidu_xinwen.extractor_baidu_news_mobilejs(html, url["page"], keyword=url["keyword"])
            if results == 3:
                send_results = [{"rank": -2}]
                self.send_inside_system_data(url, send_results)
            elif type(results) == int:
                self.log_record.info("deal_baidu_response_type5 exception url:%s;results:%s" % (url, results))
                send_results = [{"rank": -1}]
                self.send_inside_system_data(url, send_results)
            else:
                self.send_inside_system_data(url, results)
        except:
            print traceback.format_exc()
            send_results = [{"rank": -1}]
            self.send_inside_system_data(url, send_results)

    def deal_baidu_response_type6(self, url, html):
        try:
            results = self.baidu_zhidao.extractor_baidu_mobilejs(html, url["page"])
            if results == 3:
                send_results = [{"rank": -2}]
                self.send_inside_system_data(url, send_results)
            elif type(results) == int:
                self.log_record.info("deal_baidu_response_type6 exception url:%s;results:%s" % (url, results))
                send_results = [{"rank": -1}]
                self.send_inside_system_data(url, send_results)
            else:
                self.send_inside_system_data(url, results)
        except:
            print traceback.format_exc()
            send_results = [{"rank": -1}]
            self.send_inside_system_data(url, send_results)

    def deal_baidu_response_type7(self, url, html):
        picture, data_html = str(html).split(self.separator)
        try:
            results = self.baidu_web.extractor_baidu_pc(data_html)
            if results == 3:
                send_results = [{"rank": -2}]
                self.send_inside_system_data(url, send_results, webpage=picture)
            if type(results) == int:
                self.log_record.info("deal_baidu_response_type7 exception url:%s;results:%s" % (url, results))
                send_results = [{"rank": -1}]
                self.send_inside_system_data(url, send_results, webpage=picture)
            else:
                self.send_inside_system_data(url, results["rank"], webpage=picture)
        except:
            print traceback.format_exc()
            send_results = [{"rank": -1}]
            self.send_inside_system_data(url, send_results)

    def deal_baidu_response_type8(self, url, html):
        picture, data_html = str(html).split(self.separator)
        try:
            results = self.baidu_xinwen.extractor_baidu_news_pc(data_html)
            #  3 没数据
            if results == 3:
                send_results = [{"rank": -2}]
                self.send_inside_system_data(url, send_results, news=picture)

            elif type(results) == int:
                self.log_record.info("deal_baidu_response_type8 exception url:%s;results:%s" % (url, results))
                send_results = [{"rank": -1}]
                self.send_inside_system_data(url, send_results, news=picture)
            else:
                self.send_inside_system_data(url, results, news=picture)
        except:
            print traceback.format_exc()
            send_results = [{"rank": -1}]
            self.send_inside_system_data(url, send_results)

    def deal_baidu_response_type9(self, url, html):
        picture, data_html = str(html).split(self.separator)
        try:
            results = self.baidu_zhidao.extractor_baidu_zhidao_pc(data_html, url["page"])
            if results == 3:
                send_results = [{"rank": -2}]
                self.send_inside_system_data(url, send_results, know=picture)
            elif type(results) == int:
                self.log_record.info("deal_baidu_response_type9 exception url:%s;results:%s" % (url, results))
                send_results = [{"rank": -1}]
                self.send_inside_system_data(url, send_results, know=picture)
            else:

                self.send_inside_system_data(url, results, know=picture)
        except:
            print traceback.format_exc()
            send_results = [{"rank": -1}]
            self.send_inside_system_data(url, send_results)

    def deal_baidu_response_type10(self, url, html):
        picture, data_html = str(html).split(self.separator)
        try:
            page = int(url["page"])
            if page > 1:
                pcount = (page - 2) * 10 + 11
            else:
                pcount = 0
            results = self.baidu_web.extractor_baidu_mobile(html, pcount=pcount)
            if results == 3:
                send_results = [{"rank": -2}]
                self.send_inside_system_data(url, send_results, webpage=picture)
            elif type(results) == int:
                self.log_record.info("deal_baidu_response_type10 exception url:%s;results:%s" % (url, results))
                send_results = [{"rank": -1}]
                self.send_inside_system_data(url, send_results, webpage=picture)
            else:
                self.send_inside_system_data(url, results["rank"], webpage=picture)
        except:
            print traceback.format_exc()
            send_results = [{"rank": -1}]
            self.send_inside_system_data(url, send_results)

    def send_inside_system_data(self, url, results, webpage="", know="", news=""):
        page = url["page"]
        task_id = url["task_id"]

        send_list = list()
        send_item = {"file_id": url["file_id"], "keyword_id": url["keyword_id"], "device": url["seach_device"],
                     "page": url["page"], "webpage": webpage, "know": know, "news": news, "type": url["send_type"]}

        content_list = list()
        for result in results:
            content_item = dict()
            content_item["title"] = result.get("title", "")
            content_item["content"] = result.get("content", "")
            content_item["show_url"] = result.get("domain", "")
            content_item["real_url"] = result.get("real_url", "")
            content_item["src_id"] = result.get("srcid", "")
            content_item["rank"] = result.get("rank", "")

            # print result.get("rank", "")
            content_item["source"] = result.get("source", "")   # 来源
            content_item["ask"] = result.get("ask", "")         # 问
            content_item["answer"] = result.get("answer", "")   # 答
            content_item["time"] = result.get("time", "")       # 时间
            content_list.append(content_item)
        send_item["content_list"] = json.dumps(content_list)

        send_list.append(send_item)
        data_lists = json.dumps(send_list)

        # if webpage != "":
        #     f = open("temp/webpage%d.png" % url["page"], "wb")
        #     f.write(base64.b64decode(webpage))
        #     f.close()
        # if know != "":
        #     f = open("temp/know%d.png" % url["page"], "wb")
        #     f.write(base64.b64decode(know))
        #     f.close()
        # if news != "":
        #     f = open("temp/news%d.png" % url["page"], "wb")
        #     f.write(base64.b64decode(news))
        #     f.close()

        # url = "http://192.168.0.73:8000/GrabTask/grabReceiveData"
        if self.save_port == 1:
            url = "http://webtest.winndoo.com/GrabTask/grabReceiveData"
        else:
            url = "http://oa.winndoo.com/GrabTask/grabReceiveData"

        return_state = self.send_function.send_InsideSystem(url, data_lists, "dataLists")
        if return_state:
            self.log_record.info("exception page:%s;task_id:%s" % (str(page), str(task_id)))
        else:
            self.log_record.info("success: page:%s;task_id:%s" % (str(page), str(task_id)))

    def to_store_results(self, results, stores):
        self.clear_table()
        time.sleep(60 * 60 * 6)

    def clear_table(self):
        db = StoreMysql(**config.insideSystem_DB)
        try:
            expire_time = str(datetime.now() + timedelta(hours=-12))
            sql = "delete from data_achieve where create_time < '%s' " % expire_time
            db.do(sql)
            time.sleep(1)
            db.close()
        except Exception:
            print traceback.format_exc()
            db.close()

def Main():
    spider = BasicSourceSpider()
    spider.run(50, 50, 80, 1, 600, 600, 600, 600, True)

if __name__ == '__main__':
    Main()
