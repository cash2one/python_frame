# -*- coding: utf8 -*-

from basespider_separate_deal_and_store import BaseSpiderSeparateDealAndStore
from threading import Thread
import time
import traceback
import sys
from Queue import Empty
from datetime import datetime
from Queue import Queue
reload(sys)
sys.setdefaultencoding('utf8')

class BaseSpider_improve(BaseSpiderSeparateDealAndStore):
    """
    将处理结果和存储结果模块分别独立出来的爬虫类
    BaseSpiderSeparateDeal，处理结果线程deal_response只负责解析结果，解析完成后将待存储的数据放入store_queue队列里面，
    等待存储结果线程store_results去处理
    """
    def __init__(self):
        super(BaseSpider_improve, self).__init__()
        self.sended_tasks_max = 1000
        self.delaysending_queue = Queue()

    def get_user_password(self):
        return 'sunxiang', 'sxspider'

    def integer_point(self):
        # 获取当前整点
        time_now = str(datetime.today())
        start_index = time_now.find(" ")
        end_index = time_now.find(":")
        time_point = int(time_now[start_index + 1: end_index])  # 当前整点数
        return time_point

    def retry(self, u, count):
        retry_urls = list()
        if "conf_search_count" in u:
            if int(u["conf_search_count"]) <= int(count):
                u["conf_search_count"] = int(u["conf_search_count"]) + 1
                retry_urls.append(u)
            else:
                print "conf_search_count > 3 url:%s" % u["url"]
                # self.log_record.info("conf_search_count > 3 url:%s" % u)
        else:
            u["conf_search_count"] = 1
            retry_urls.append(u)
        return retry_urls

    def send_requests(self, max_idle_time):
        """
        发送请求。将sending_queue队列中的SpiderRequest对象通过downloader发送到下载中心
            这边限制发送任务数
        """
        downloader = self.get_downloader()
        start_time = time.time()
        while True:
            try:
                if self.sended_queue.qsize() < self.sended_tasks_max \
                        and self.response_queue.qsize() < self.sended_tasks_max:
                    request = self.sending_queue.get_nowait()
                    if request.user_id is None:
                        request.user_id = self.user_id
                    results = downloader.set(request)
                    self.deal_request_results(request, results)
                    start_time = time.time()
                    self.send_wait()
                else:
                    time.sleep(10)
            except Empty:
                if start_time + max_idle_time < time.time():
                    if self.is_finish():
                        break
                time.sleep(10)
            except Exception :
                print traceback.format_exc()

    def delay_requests(self, max_idle_time):
        """
            发送请求。将sending_queue队列中的SpiderRequest对象通过downloader发送到下载中心
                    这边限制发送任务数
         """
        downloader = self.get_downloader()
        start_time = time.time()
        while True:
            try:
                if self.sended_queue.qsize() < self.sended_tasks_max \
                        and self.response_queue.qsize() < self.sended_tasks_max:
                    request = self.delaysending_queue.get_nowait()
                    if request.user_id is None:
                        request.user_id = self.user_id
                    results = downloader.set(request)
                    self.deal_request_results(request, results)
                    start_time = time.time()

                    self.delay_time()
                else:
                    time.sleep(10)
            except Empty:
                if start_time + max_idle_time < time.time():
                    if self.is_finish():
                        break
                time.sleep(10)
            except Exception:
                print traceback.format_exc()

    def delay_time(self):
        time.sleep(10)

    def is_finish(self, record_finish=True):
        '''
        判断各线程是否结束
        :param record_finish: 默认True 各线程为0 时结束，设置False 各线程一直运行
        :return:
        '''
        if record_finish:
            return self.sending_queue.qsize() == 0 and self.sended_queue.qsize() == 0 \
                   and self.response_queue.qsize() == 0 and self.store_queue.qsize() == 0
        else:
            return False

    def run(self, send_num=1, get_num=1, deal_num=1, store_num=1, delay_num=1, send_idle_time=600,
                get_idle_time=600, deal_idle_time=600, store_idle_time=600, delay_idle_time=600,
                record_log=False, record_finish=True, ):
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
        threads = list()

        # 默认 10 分钟之内没任务 终止
        self.is_finish(record_finish=record_finish)
        # self.start_requests()
        threads.append(Thread(target=self.start_requests))

        for i in range(0, delay_num):
            threads.append(Thread(target=self.delay_requests, args=(delay_idle_time,)))

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
