# -*- coding: utf8 -*-
import os
import random
import sys
import time
import urllib
from threading import Thread

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
sys.path.append(os.path.join(PROJECT_PATH, 'store'))
sys.path.append(os.path.join(PROJECT_PATH, 'util'))

reload(sys)
sys.setdefaultencoding('utf8')

from copy import copy
import traceback
from spider.basespider_sx import BaseSpider_sx
from store.baidu_spider_move.baidu_spider_store import SpiderBaseStore

from downloader.downloader import SpiderRequest
from extractor.baidu_spider_move.baidu_spider_extractor_pc import BaiduSpiderExtractorPc
from extractor.baidu_spider_move.baidu_spider_extractor_mobile import BaiduSpiderExtractorMobile
from extractor.baidu.baidu_pc_rank_extractor2 import BaiduPcRankExtractor
from util.util_useragent import UtilUseragent
from store_mysql import StoreMysql
from sx_util.http_url_utils import HttpUrlUtils
from util_log import UtilLogger
# from util.util_cookiesx import UtilCookie
from datetime import datetime, timedelta

class BasicSourceSpider(BaseSpider_sx):
    '''
    移動端 ua 異常
    '''
    def __init__(self):
        super(BasicSourceSpider, self).__init__()
        self.basicExtractor = BaiduPcRankExtractor()
        # 定时休眠时间  分钟
        self.difsecond = 180
        self.log = UtilLogger('SourceSpider',
                              os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_SourceSpider'))
        self.log_record = UtilLogger('record_SourceSpider',
                                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_RecordSourceSpider'))
        self.userpc_agents = UtilUseragent.get(type='PC')
        self.usermobile_agents = UtilUseragent.get(type='MOBILE')

        self.mobile_useragent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
        self.baidu_store = SpiderBaseStore()
        self.sleep_time = 180  # 没有任务休眠时间
        self.sended_queue_maxsize = 800   # 发送限制

        self.send_one_tasks = 500  # 一次取出
        self.baidu_extractor_pc = BaiduSpiderExtractorPc()
        self.baidu_extractor_mobile = BaiduSpiderExtractorMobile()
        self.url_util = HttpUrlUtils()
        self.reset_task_time = 1800

    def get_user_password(self):
        return 'sunxiang2', 'sxspider'
        # return 'test', 'test'

    # def get_downloader(self):
        #     """
        #     设置下载器类型，默认为Downloader
        #     Return:
        #         SpiderDownloader
        #     """
        # return Downloader(set_mode='db', get_mode='db')
        # return HtmlLocalDownloader(set_mode='http', get_mode='http')

    def start_requests(self):
        try:
            while True:
                # utilcookie = UtilCookie()
                # cookie = utilcookie.getPc()
                # print cookie

                if self.sended_queue.qsize() < self.sended_queue_maxsize and self.sending_queue.qsize() < self.sended_queue_maxsize\
                        and self.response_queue.qsize() < self.sended_queue_maxsize:
                    task_results = self.baidu_store.find_task_lists(self.send_one_tasks)
                    print "task_results length:%d" % len(task_results)
                    if len(task_results) > 0:
                        for result in task_results:
                            task_id = result[0]
                            task_url_address = result[1]
                            page = result[3]
                            device = str(result[4]).lower()
                            keyword = result[5]
                            file_name = result[7]
                            is_equal = int(result[12])

                            spidertype = (1 if is_equal == 0 else 2)
                            search_device = (1 if device == "pc" else 2)

                            if device == "pc":
                                # pc 端前5 页
                                kwh = {'wd': keyword, 'rn': 50}
                                url = 'https://www.baidu.com/s?' + urllib.urlencode(kwh)
                            else:
                                kwh = {'wd': keyword}
                                url = 'https://m.baidu.com/s?' + urllib.urlencode(kwh)

                            urls = [{'url': url, 'type': 1, 'keyword': keyword, 'id': task_id, 'ckurl': task_url_address,
                                     'file_name': file_name, "page": page, "unique_key": task_id,
                                     "pnum": 1, "search_device": search_device, "spidertype": spidertype}]

                            basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.userpc_agents)
                                    if device.lower() == "pc" else self.mobile_useragent}, urls=urls)
                            # "random.choice(self.usermobile_agents)"  random.choice(self.usermobile_agents)
                            self.sending_queue.put(basic_request)
                        time.sleep(10)
                    else:
                        time.sleep(self.sleep_time)
                else:
                    time.sleep(self.sleep_time)

                # urls = list()
                # keyword = '德州一中、长诃小学、澳德乐、德百中心商圈、长河公园、太阳湖、广田地产、'
                # url = 'https://www.baidu.com/s?wd={0}&rn=50'.format(keyword)
                # print url
                # urls.append({'url': url, 'type': 1, 'ckurl': 'baixing.com'})
                # headers = {
                #     'Cookie': cookie,
                #     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari / 537.36',
                # }
                # basic_request = SpiderRequest(headers=headers, urls=urls)
                # self.sending_queue.put(basic_request)
                # time.sleep(1000)
        except Exception:
            print traceback.format_exc()

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
        stores.append(self.baidu_store)
        self.stores = stores
        return stores

    def deal_response_results(self, request, results, stores):
        if results == 0:
            self.log.info("deal_response_results results == 0")
            return False
        else:
            urls = list()
            failed_urls = list()  # 失败链接
            for u in request.urls:
                url = u['unique_md5']
                if url in results:
                    result = results[url]
                    if str(result['status']) == '2' or str(result['status']) == '3':
                        self.deal_response_results_sxself(request, u, result)
                    else:
                        urls.append(u)
                else:
                    # print "failed_urls: %s" % u
                    failed_urls.append(u)

                    # if u["type"] == 2:
                    #     spidertype = u["spidertype"]
                    #     if spidertype == 1:
                    #         self.log_record.info("u not in results spidertype ==  1 ;id:%d" % int(u["id"]))
                    #         realaddress = self.url_util.removeCharacters(u['domain'])
                    #         self.store_rank(url, u["rank"], 1, realaddress=realaddress)
                    #     else:
                    #         self.log_record.info("u not in results spidertype == 2 ;id:%d" % int(u["id"]))
                    #         self.store_rank(url, -2, 1)
                    # else:
                    #     self.log_record.info("u not in results send resend ;id:%d" % int(u["id"]))
                    #     send_urls = list()
                    #     send_urls.append(url)
                    #     new_request = copy(request)
                    #     new_request.urls = send_urls
                    #     self.sending_queue.put(new_request)
                    #     del new_request

            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)
            if len(failed_urls) > 0:
                new_request = copy(request)
                new_request.urls = failed_urls
                self.sending_queue.put(new_request)
                del new_request

    def extractor_replace(self, body):
        start_index = body.find(u"window.location.replace")
        end_index = body[start_index + 25:].find(u"\"")
        return body[start_index + 25:][0: end_index]

    def deal_response_results_sxself(self, request, url, result):
        if str(result['status']) == '2':
            search_device = int(url['search_device'])
            if url["type"] == 2:
                spidertype = url["spidertype"]
                if int(result['code']) == 0:
                    realaddress = self.extractor_replace(result["result"])
                    # realaddress = self.url_util.removeCharacters(url['url'])
                else:
                    realaddress = self.url_util.removeCharacters(result['redirect_url'])

                if spidertype == 1:
                    self.store_rank(url, url["rank"], 1, realaddress=realaddress)
                else:
                    # print "exception"
                    ckurl = self.url_util.removeCharacters(url["ckurl"])
                    if realaddress == ckurl:
                        self.store_rank(url, url["rank"], 3, realaddress=realaddress)
                    else:
                        self.store_rank(url, -2, 3)
            else:
                if search_device == 1:
                    self.deal_baidu_response_pc(url, result['result'])
                else:
                    self.deal_baidu_response_mobile(url, result['result'])
        elif str(result['status']) == '3':
            # 根据情况做处理
            self.log.info('抓取失败:%s' % url)
            if url["type"] == 2:
                spidertype = url["spidertype"]
                if spidertype == 1:
                    self.log_record.info("status == 3 spidertype ==  1 ;id:%d" % int(url["id"]))
                    realaddress = self.url_util.removeCharacters(url['domain'])
                    self.store_rank(url, url["rank"], 1, realaddress=realaddress)
                else:
                    self.log_record.info("status == 3 spidertype == 2 ;id:%d" % int(url["id"]))
                    self.store_rank(url, -2, 1)
            else:
                self.log_record.info("status == 3 send re send ;id:%d" % int(url["id"]))
                send_urls = list()
                send_urls.append(url)
                new_request = copy(request)
                new_request.urls = send_urls
                # self.log_record.info("status == 3 send resend new_request: %s" % new_request)
                self.sending_queue.put(new_request)
                del new_request

    def deal_baidu_response_pc(self, url, html):
        # start_time = time.time()
        result = self.baidu_extractor_pc.extractor_baidu_pc_lxml(html, ck=url['ckurl'], spidertype=url['spidertype'])
        # end_time = time.time()
        # print "deal_baidu_response_pc:" + str(end_time - start_time)

        if result == 0:
            self.store_rank(url, -2, 1)
        elif type(result) == int:
            self.log_record.info("result == -1 extractor failure ;id:%d" % int(url["id"]))
            self.store_rank(url, -1, 1)
        else:
            if "rank" in result:
                for rank_result in result["rank"]:
                    if "is_get_realaddress" in rank_result:
                        urls = [{'url': rank_result["realaddress"], 'type': 2, "keyword": url["keyword"],
                                "rank": rank_result["rank"], "id": url["id"], "file_name": url["file_name"],
                                "search_device": url["search_device"], "ckurl": url["ckurl"], "unique_key": url["id"],
                                 "spidertype": url["spidertype"], "domain": rank_result["domain"]}]

                        header = {'User-Agent': random.choice(self.userpc_agents)}
                        basic_request = SpiderRequest(headers=header, urls=urls)
                        self.sending_queue.put(basic_request)
                    else:
                        self.store_rank(url, rank_result["rank"], 1, realaddress=rank_result["realaddress"])
            else:
                self.store_rank(url, -2, 1)

    def deal_baidu_response_mobile(self, url, html):
        page = url["page"]  # 总页数
        pnum = url["pnum"]  # 当前页数
        if pnum > 1:
            pcount = (pnum-1)*10 + 1
        else:
            pcount = 0
        # mobile_start_time = time.time()
        result = self.baidu_extractor_mobile.extractor_baidu_mobile_lxml(html, ck=url['ckurl'], pcount=pcount,
                                                                    spidertype=url['spidertype'])
        # mobile_end_time = time.time()
        # print "deal_baidu_response_mobile:" + str(mobile_end_time - mobile_start_time)

        if result == 3:
            self.store_rank(url, -2, 1)
        if type(result) == int:
            self.store_rank(url, -1, 1)
            self.log_record.info("extractor failure result:%s; url:%s" % (str(result), url["url"]))
        else:
            if "rank" in result:
                for rank_result in result["rank"]:
                    self.store_rank(url, rank_result["rank"], 1, realaddress=rank_result["realaddress"])
            elif pnum < page:
                # self.log_record.info("send deal_baidu_response_mobile page < 5 mobile ;id:%d" % int(url["id"]))
                pn = pnum * 10  # 移动端 参数pn
                kwh = {'pn': pn, 'wd': url["keyword"]}
                tmpurl = 'https://m.baidu.com/s?' + urllib.urlencode(kwh)

                send_urls = [{'url': tmpurl, 'type': 1, 'keyword': url["keyword"], 'id': url["id"], 'ckurl': url["ckurl"],
                         'file_name': url["file_name"], "page": url["page"], "unique_key": url["id"],
                         "pnum": pnum + 1, "search_device": url["search_device"], "spidertype": url["spidertype"]}]
                # headers = {'User-Agent': random.choice(self.usermobile_agents)},
                basic_request = SpiderRequest(headers={'User-Agent': self.mobile_useragent}, urls=send_urls)
                self.sending_queue.put(basic_request)
            else:
                self.store_rank(url, -2, 1)
                # self.log_record.info("extractor failure url:%s" % url)

    def store_rank(self, url, rank, store_type, realaddress=""):
        # '''
        # store_type  1正常删除task 新增rank，2,3:判断, 3:有完全匹配
        # :param url:
        # :param rank:  排名
        # :param store_type: 存储类型
        # :param realaddress: 真实url
        # :return:
        # '''
        # if rank == -2 or rank == -1:
        #     print "no rank:%d" % rank
        item = dict()
        item["keyword"] = url["keyword"]
        item["rank"] = rank
        item["taskId"] = int(url["id"])
        item["fileName"] = url["file_name"]
        item["device"] = ("pc" if int(url["search_device"]) == 1 else "mobile")
        item["state"] = 0

        item["picUrl"] = ""
        item["title"] = ""
        item["content"] = ""
        item["srcid"] = ""
        item["insideTitle"] = ""
        item["insideDescription"] = ""
        item["insideKeywords"] = ""

        if realaddress != "":
            item["urlAddress"] = realaddress
        else:
            item["urlAddress"] = ""
        store_list = list()
        store_list.append(item)
        self.store_queue.put({"result": store_list, "task_id": url["id"], "type": store_type, "rank": rank})

    '''
        results  type 1: 正常删除task 新增rank，2,3:判断, 3:有完全匹配
                task_id  task表id
    '''
    def to_store_results(self, results, stores):
        try:
            rank_results_insert = results["result"]
            store_type = int(results["type"])
            rank = int(results["rank"])
            # store_task_id = results["task_id"]

            if store_type == 3:
                # 完全匹配
                if rank != -1 and rank != -2:
                    # 排名 不是-1，-2 到结果表中查询有无
                    stores[0].store_insert_or_update(rank_results_insert, table="rank", field="taskId")

                    # rank_result_sx = stores[0].find_rank_by_taskid("rank", results["task_id"])
                    # if rank_result_sx:
                    #     stores[0].store_table(rank_results_insert, table="rank", type=2, field="taskId")
                    # else:
                    #     stores[0].store_table(rank_results_insert, table="rank")
                    #     stores[0].delete_by_id("task", results["task_id"])
                else:
                     stores[0].store_insert_or_update(rank_results_insert, table="rank", field="taskId", isupdate=2)
            else:
                stores[0].store_table(rank_results_insert, table="rank")
            self.log_record.info("task_id:%s ;rank:%s " % (str(results["task_id"]), rank))
            stores[0].delete_by_id("task", results["task_id"])
        except:
            print traceback.format_exc()

    # 重置任务表 状态
    def reset_task(self):
        while True:
            # self.log_record.info("reset:%s" % str(datetime.today()))
            self.baidu_store.reset_task(self.reset_task_time)
            time.sleep(self.reset_task_time)

    # 清除 下载中心 表数据
    def clear_urls(self):
        while True:
            self.log_record.info("urls reset:%s" % str(datetime.today()))
            self.clear_urls_table(60 * 30)
            # self.baidu_store.reset_task(self.reset_task_time)
            time.sleep(self.reset_task_time)

    def clear_urls_table(self, interval_time):
        spider_db = {
            'host': '182.254.155.218',
            # 'host': '10.105.72.2',
            'user': 'spider_center',
            'password': 'spiderdb@wd',
            'db': 'spider'
        }
        db = StoreMysql(**spider_db)
        try:
            expire_time = str(datetime.now() + timedelta(seconds=-interval_time))
            sql = "delete from urls_8 where type = 1 and status = 2 and update_time < '%s' " % expire_time
            result = db.do(sql)
            print result
            db.close()
        except Exception:
            print traceback.format_exc()
            db.close()

    def run(self, send_num=1, get_num=1, deal_num=1, store_num=1, send_idle_time=600,
            get_idle_time=600, deal_idle_time=600, store_idle_time=600, record_log=False):
        """
        爬虫启动入口
        Args:
            send_num:发送请求线程数，默认为1
            get_num:获取结果线程数，默认为1
            deal_num:处理结果线程数，默认为1
            store_num:存储结果线程数，默认为1
            send_idle_time:发送请求线程超过该时间没有要发送的请求就停止
            get_idle_time:获取结果线程超过该时间没有要获取的结果就停止
            deal_idle_time:处理结果线程超过该时间没有要处理的结果就停止
            store_idle_time:存储结果线程超过该时间没有要存储的结果就停止
            record_log:定时记录各个队列大小，便于分析抓取效率
        """
        self.validate_user()
        # self.start_requests()
        threads = list()
        threads.append(Thread(target=self.start_requests))

        threads.append(Thread(target=self.reset_task))

        # threads.append(Thread(target=self.clear_urls))

        for i in range(0, send_num):
            threads.append(Thread(target=self.send_requests, args=(send_idle_time,)))
        for i in range(0, get_num):
            threads.append(Thread(target=self.get_response, args=(get_idle_time,)))
        for i in range(0, deal_num):
            threads.append(Thread(target=self.deal_response, args=(deal_idle_time,)))
        for i in range(0, store_num):
            threads.append(Thread(target=self.store_results, args=(store_idle_time,)))
        if record_log:
            threads.append(Thread(target=self.record_log))
        for thread in threads:
            thread.start()

    def is_finish(self):
        return False

def Main():
    spider = BasicSourceSpider()
    # spider.run(1, 1, 1, 1, 600, 600, 600, 600, True)
    spider.run(20, 40, 40, 10, 600, 600, 600, 600, True)

    # with open("window.txt", "rb") as f:
    #     content = f.read()
    #     result = spider.extractor_replace(content)
    #     print result

if __name__ == '__main__':
    Main()
