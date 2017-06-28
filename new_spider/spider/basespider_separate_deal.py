# -*- coding: utf8 -*-
from basespider import BaseSpider
from Queue import Queue
from Queue import Empty
from threading import Thread
import time
import traceback
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class BaseSpiderSeparateDeal(BaseSpider):
    """
    将处理结果模块独立出来的爬虫类
    相对于BaseSpider，取结果线程get_response只负责取结果，取到的结果放入response_queue队列里面，等待deal_response线程去处理
    """

    def __init__(self):
        super(BaseSpiderSeparateDeal, self).__init__()
        self.response_queue = Queue()

    def is_finish(self):
        return self.sending_queue.qsize() == 0 and self.sended_queue.qsize() == 0 and self.response_queue.qsize() == 0

    def send_wait(self):
        if self.sended_queue.qsize() > 2000:
            time.sleep(60)
        elif self.sending_queue.qsize() < 10000:
            time.sleep(1)

    def get_wait(self):
        if self.response_queue.qsize() > 10000:
            time.sleep(60)
        elif self.sended_queue.qsize() < 2000:
            time.sleep(1)

    def get_response(self, max_idle_time):
        """
        获取url爬取结果。将sended_queue队列中的SpiderRequest对象通过downloader到下载中心去获取抓取到的html，
        将抓取到的结果放到结果队列response_queue中等待处理
        """
        downloader = self.get_downloader()
        start_time = time.time()
        while True:
            try:
                request = self.sended_queue.get_nowait()
                results = downloader.get(request)
                self.response_queue.put((request, results))
                start_time = time.time()
                self.get_wait()
            except Empty:
                if start_time + max_idle_time < time.time():
                    if self.is_finish():
                        break
                time.sleep(10)
            except Exception, e1:
                print(traceback.format_exc())

    def deal_response(self, max_idle_time):
        """
        从结果队列response_queue中取出抓取结果进行解析处理
        """
        stores = self.get_stores()
        start_time = time.time()
        while True:
            try:
                request, results = self.response_queue.get_nowait()
                self.deal_response_results(request, results, stores)
                start_time = time.time()
            except Empty:
                if start_time + max_idle_time < time.time():
                    if self.is_finish():
                        break
                time.sleep(10)
            except Exception, e1:
                print(traceback.format_exc())

    def record_log(self):
        """
        记录抓取日志，用于调整各个线程参数设置
        """
        while not self.is_finish():
            print('sending_queue:%d; sended_queue:%d; response_queue:%d'
                  % (self.sending_queue.qsize(), self.sended_queue.qsize(), self.response_queue.qsize()))
            # 需要安装objgraph包
            import objgraph
            objgraph.show_most_common_types()
            time.sleep(300)

    def run(self, send_num=1, get_num=1, deal_num=1, send_idle_time=600, get_idle_time=600,
            deal_idle_time=600, record_log=False):
        """
        爬虫启动入口
        Args:
            send_num:发送请求线程数，默认为1
            get_num:获取结果线程数，默认为1
            deal_num:处理结果线程数，默认为1
            send_idle_time:发送请求线程超过该时间没有要发送的请求就停止
            get_idle_time:获取结果线程超过该时间没有要获取的结果就停止
            deal_idle_time:处理结果线程超过该时间没有要处理的结果就停止
            record_log:定时记录各个队列大小，便于分析抓取效率
        """
        self.validate_user()
        self.start_requests()
        threads = list()
        for i in range(0, send_num):
            threads.append(Thread(target=self.send_requests, args=(send_idle_time,)))
        for i in range(0, get_num):
            threads.append(Thread(target=self.get_response, args=(get_idle_time,)))
        for i in range(0, deal_num):
            threads.append(Thread(target=self.deal_response, args=(deal_idle_time,)))
        if record_log:
            threads.append(Thread(target=self.record_log))
        for thread in threads:
            thread.start()
