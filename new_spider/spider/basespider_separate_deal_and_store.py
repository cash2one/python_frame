# -*- coding: utf8 -*-
from basespider_separate_deal import BaseSpiderSeparateDeal
from Queue import Queue
from Queue import Empty
from threading import Thread
import time
import traceback
import sys
from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf8')
from util_log import UtilLogger

class BaseSpiderSeparateDealAndStore(BaseSpiderSeparateDeal):
    """
    将处理结果和存储结果模块分别独立出来的爬虫类
    BaseSpiderSeparateDeal，处理结果线程deal_response只负责解析结果，解析完成后将待存储的数据放入store_queue队列里面，
    等待存储结果线程store_results去处理
    """

    def __init__(self):
        super(BaseSpiderSeparateDealAndStore, self).__init__()
        self.store_queue = Queue()
        # self.log = UtilLogger('EngineBasicSourceSpider',
        #                       os.path.join(os.path.dirname(os.path.abspath(__file__)),
        #                                    'log_sxMobileSourceSpider'))

    def is_finish(self):
        return self.sending_queue.qsize() == 0 and self.sended_queue.qsize() == 0 \
               and self.response_queue.qsize() == 0 and self.store_queue.qsize() == 0

    def deal_response(self, max_idle_time):
        """
        从结果队列response_queue中取出抓取结果进行解析处理
        """
        start_time = time.time()
        while True:
            try:
                request, results = self.response_queue.get_nowait()
                # request = self.response_queue.get_nowait()
                self.deal_response_results(request, results, None)
                start_time = time.time()
            except Empty:
                if start_time + max_idle_time < time.time():
                    if self.is_finish():
                        break
                time.sleep(10)
            except Exception:
                print traceback.format_exc()

    def store_results(self, max_idle_time):
        """
        从store_queue里面取出待存储的数据进行存储
        """
        stores = self.get_stores()
        start_time = time.time()
        while True:
            try:
                results = self.store_queue.get_nowait()
                self.to_store_results(results, stores)
                start_time = time.time()
            except Empty:
                if start_time + max_idle_time < time.time():
                    if self.is_finish():
                        break
                time.sleep(10)
            except Exception, e1:
                print(traceback.format_exc())

    def to_store_results(self, results, stores):
        """
        存储结果，由子类实现。
        Args:
            results:请求request结果后的返回对象
            stores:list，可能会用到的存储器（SpiderStore）列表
        """
        raise NotImplementedError()

    def record_log(self):
        """
            5 分钟打印一次 日志
            记录抓取日志，用于调整各个线程参数设置
        """
        while not self.is_finish():
            # self.log.info('抓取程序开始启动...')
            time_now = str(datetime.today())
            print('time_now:%s; sending_queue:%d; sended_queue:%d; response_queue:%d; store_queue:%d'
                  % (time_now, self.sending_queue.qsize(), self.sended_queue.qsize(), self.response_queue.qsize(),
                     self.store_queue.qsize()))
            # 需要安装objgraph包
            import objgraph
            objgraph.show_most_common_types()
            time.sleep(300)

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
        self.start_requests()
        threads = list()
        # threads.append(Thread(target=self.start_requests))

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
