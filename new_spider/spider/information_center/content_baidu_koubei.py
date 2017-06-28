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

from extractor.information_center.baidu_koubei_extractor import SourceExtractor
from store.information_center.center_store import SourceStore


class BasicSourceSpider(BaseSpider_improve_alwaysrun):

    '''
    口碑列表页
    js 内容
        https://koubei.baidu.com/search/getsearchresultajax?wd=%25E7%25BE%258E%25E5%25AE%259D%25E8%258E%25B2&page=1
        "Referer": "https://koubei.baidu.com/search?query=%E6%AC%A7%E8%8E%B1%E9%9B%85&fr=search"

        点评  js header:     "Referer": "https://koubei.baidu.com/s/37ba452ffc07b88fb3557658efc4d750?src=searchexp&page=2&tab=comt",
                            "X-Requested-With": "XMLHttpRequest",
        https://koubei.baidu.com/s/getcomtlistajax?memid=25419047&page=1&iscomp=1

        资质信息
        http://xin.baidu.com/detail/basicAjax?pid=G-e8SgdG*fTMpeLi0ckiOKlwOPx4veVluA*i&tot=Lstc8pM4SCtYO5U7Knh6RvNzxHCyDLQZuw3q&_=1496305722763

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
                    sql = "SELECT id, keyword FROM content_keyword;"
                    keywords_list = db.query(sql)
                    # for page_index in xrange(0, 10):
                    for keyword_one in keywords_list:
                        keyword_id = keyword_one[0]
                        keyword = keyword_one[1]

                        kwh = {'wd': keyword, "page": 1}
                        url = 'https://koubei.baidu.com/search/getsearchresultajax?' + urllib.urlencode(kwh)
                        # print url
                        referer = {"query": keyword, "fr": "search"}
                        hreader_referer = "https://koubei.baidu.com/search?" + urllib.urlencode(referer)

                        urls = [{"url": url, "type": 1, "extractor_type": 1, "keyword": keyword,
                                 "keyword_id": keyword_id}]
                        basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.userpc_agents),
                                                               'Referer': hreader_referer}, urls=urls)
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
            # print "send one request"
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
                        elif u["extractor_type"] == 2:
                            self.deal_response_type2(u, result['result'])
                        elif u["extractor_type"] == 3:
                            self.deal_response_type3(u, result['result'])
                        elif u["extractor_type"] == 4:
                            self.deal_response_type4(u, result['result'])
                        elif u["extractor_type"] == 5:
                            self.deal_response_type5(u, result['result'])

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

    def deal_response_type1(self, url, html):
        response_result = self.basicExtractor.extractor_list_js(html)
        if type(response_result) == int:
            self.log.info("extractor_type1 result:%s ;url: %s" % (str(response_result), url["url"]))
        else:
            memid = response_result["memid"]
            purl = response_result["purl"]
            memcode = response_result["memcode"]
            urls = [{"url": "http:" + purl, "type": 1, "keyword": url["keyword"], "extractor_type": 2, "memid": memid,
                     "keyword_id": url["keyword_id"], "memcode": memcode}]
            basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.userpc_agents)},
                                          urls=urls, config=self.config)
            self.sending_queue.put_nowait(basic_request)

    def deal_response_type2(self, url, html):
        response_result = self.basicExtractor.extractor_detail(html)
        if response_result == -1:
            self.log.info("deal_response_type2 result:%s ;url: %s" % (str(response_result), url["url"]))
            # return True
        elif response_result == 1:
            self.log.info("deal_response_type2 result:%s ;url: %s" % (str(response_result), url["url"]))
        else:
            inf_item = response_result.get("inf_item", "")
            if inf_item == "":
                pass
                print "deal_response_type2 inf_item is null url:%s" % url["url"]
            else:
                inf_item["url"] = "https://koubei.baidu.com/s/%s" % url["memcode"]
                inf_item["keyword_id"] = url["keyword_id"]

                qua_inf = response_result.get("qua_inf", "")
                store_list = list()
                store_list.append(inf_item)
                self.store_queue.put({"store_result": store_list, "store_type": 1, "memid": url["memid"],
                                      "memcode": url["memcode"], "qua_inf": qua_inf})

    def deal_response_type3(self, url, html):
        try:
            response_result = self.basicExtractor.extractor_comment_js(html)
            if type(response_result) == int:
                self.log.info("deal_response_type3 result:%s ;url: %s;inf_id:%s" % (str(response_result), url, url["inf_id"]))
            else:
                comment_list = response_result["comment_list"]
                total_page = int(response_result["total_page"])

                if "depth" in url:
                    #  第二次 页数
                    pass
                else:
                    # 第一次 后续页数
                    if total_page > 2:
                        for index in xrange(2, total_page+1):
                            memid = url["memid"]
                            memcode = url["memcode"]
                            urls = [{"url": "https://koubei.baidu.com/s/getcomtlistajax?memid=%s&page=%s&iscomp=1" % (str(memid), str(index)),
                                     "type": 1, "extractor_type": 3, "inf_id": url["inf_id"],
                                     "memid": memid, "memcode": memcode, "depth": 2}]
                            header = {
                                "Referer": "https://koubei.baidu.com/s/%s?src=searchexp&page=%s&tab=comt" % (str(memcode), str(index)),
                                "X-Requested-With": "XMLHttpRequest"}
                            basic_request = SpiderRequest(headers=header, urls=urls)
                            self.sending_queue.put_nowait(basic_request)

                store_list = list()
                for comment_one in comment_list:
                    comment_one["inf_id"] = url["inf_id"]
                    store_list.append(comment_one)
                self.store_queue.put({"store_result": store_list, "store_type": 2})
        except:
            print traceback.format_exc()

    def deal_response_type4(self, url, html):
        try:
            response_result = self.basicExtractor.extractor_qualify_execjs(html)
            if type(response_result) == int:
                self.log.info("deal_response_type4 result:%s ;url: %s;inf_id:%s" % (str(response_result), url["url"], url["inf_id"]))
            else:
                pid = response_result["pid"]
                tot = response_result["tot"]

                send_url = "http://xin.baidu.com/detail/basicAjax?pid=%s&tot=%s" % (pid, tot)
                print "type4:%s" % str(send_url)
                urls = [{"url": send_url, "type": 1, "extractor_type": 5, "inf_id": url["inf_id"]}]
                basic_request = SpiderRequest(urls=urls, config={"priority": 3})
                self.sending_queue.put_nowait(basic_request)
        except:
            print traceback.format_exc()

    def deal_response_type5(self, url, html):
        try:
            response_result = self.basicExtractor.extractor_qualify_js(html)
            if type(response_result) == int:
                self.log.info("deal_response_type4 result:%s ;url: %s;inf_id:%s" % (str(response_result), url["url"], url["inf_id"]))
            else:
                response_result["id"] = url["inf_id"]
                store_list = list()
                store_list.append(response_result)
                self.store_queue.put({"store_result": store_list, "store_type": 3})
        except:
            print traceback.format_exc()

    '''
        results  type 1:
                task_id  task表id
    '''
    def to_store_results(self, results, stores):
        try:
            store_result = results["store_result"]
            store_type = int(results["store_type"])

            if store_type == 1:
                memid = results["memid"]
                memcode = results["memcode"]
                qua_inf = results["qua_inf"]

                inf_id = self.stores[0].store_table(store_result, table="content_koubei_inf")
                if inf_id != -1:
                    # 点评  &page=1
                    # print "https://koubei.baidu.com/s/getcomtlistajax?memid=%s&iscomp=1" % str(memid)
                    urls = [{"url": "https://koubei.baidu.com/s/getcomtlistajax?memid=%s&iscomp=1" % str(memid), "type": 1,
                             "extractor_type": 3, "inf_id": inf_id, "memid": memid, "memcode": memcode}]

                    header = {"Referer": "https://koubei.baidu.com/s/%s?src=searchexp&page=1&tab=comt" % str(memcode),
                              "X-Requested-With": "XMLHttpRequest"}
                    basic_request = SpiderRequest(headers=header, urls=urls)
                    self.sending_queue.put_nowait(basic_request)

                    # 资质信息
                    #if qua_inf != "":
                    # print "zizhi:%s" % qua_inf
                    # urls = [{"url": qua_inf, "type": 1, "extractor_type": 4, "inf_id": inf_id}]
                    # basic_request = SpiderRequest(urls=urls)
                    # self.sending_queue.put(basic_request)

                else:
                    print "save exception inf_id:%s" % str(inf_id)
            elif store_type == 2:
                self.stores[0].store_table(store_result, table="content_koubei_comment")
            elif store_type == 3:
                self.stores[0].store_table(store_result, table="content_koubei_inf", type=2, field="id")
        except:
            print traceback.format_exc()

def Main():
    spider = BasicSourceSpider()
    # spider.run(1, 1, 1, 1, 600, 600, 600, 600, True)
    spider.run(10, 15, 30, 10, 600, 600, 600, 600, True)

if __name__ == '__main__':
    Main()
