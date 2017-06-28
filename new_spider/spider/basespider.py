# -*- coding: utf8 -*-
from spider import Spider
from downloader.downloader import Downloader
from downloader.configs import DOWNLOADER_CENTER_DB
from util.util_md5 import UtilMD5
from util.util_useragent import UtilUseragent
from Queue import LifoQueue
from Queue import Queue
from Queue import Empty
from store_mysql import StoreMysql
from threading import Thread

from downloader import configs
import time
import traceback
from datetime import datetime
from datetime import timedelta
import sys
from copy import copy
import types

reload(sys)
sys.setdefaultencoding('utf8')

class BaseSpider(Spider):
    """
    基本的爬虫类
    该爬虫维护两个队列：待发送队列sending_queue和已发送队列sended_queue
    发送的对象统一封装成SpiderRequest对象
    启动时，通过start_requests方法构造一批待发送的SpiderRequest对象送到待发送队列里面
    发送线程send_requests依次从sending_queue队列取值并发送，获取的结果通过deal_request_results来处理
    如果发送成功，将SpiderRequest对象送入已发送队列sended_queue，如果发送失败则重新回到待发送队列sending_queue
    取结果线程get_response依次从sended_queue队列取值并发送，获取的结果通过deal_response_results来处理
    如果抓取成功，将对应结果存入数据库，如果发送失败则重新回到已发送队列sended_queue
    """
    def __init__(self):
        self.user_agents = UtilUseragent.get()
        # self.sending_queue = LifoQueue() # 后进先出

        self.sending_queue = Queue()       # 先进先出
        self.sended_queue = Queue()
        self.user_id = 0
        self.db = StoreMysql(**configs.DOWNLOADER_CENTER_DB)

    def get_user_password(self):
        """
        设置用户名和密码，由子类实现。用于爬取前验证是否合法
        """
        raise NotImplementedError()

    def validate_user(self):
        """
        验证用户
        """
        user, password = self.get_user_password()
        db = StoreMysql(**DOWNLOADER_CENTER_DB)
        rows = db.query('select id from user where user = "%s" and password = "%s"' % (user, UtilMD5.md5(password)))
        db.close()
        if len(rows) == 1:
            self.user_id = rows[0][0]
        else:
            raise RuntimeError('用户验证失败')

    def validate_Count(self):
        '''
        验证数据量
        :return:
        '''
        urls_table = configs.USER_CONFIG['urlsTable'] % self.user_id
        db = StoreMysql(**DOWNLOADER_CENTER_DB)
        rows = db.query('select count(*) from %s' % urls_table)
        db.close()
        if len(rows) == 1:
            count = rows[0][0]
        else:
            # print '获取数据库数量失败'
            count = 0
        if count < configs.SEND_TASK_LIMITCOUNT:
            return True
        else:
            return False
            # raise RuntimeError('用户验证失败')

    def get_downloader(self):
        """
        设置下载器类型，默认为Downloader
        Return:
            SpiderDownloader
        """
        return Downloader(set_mode='db', get_mode='db')

    def start_requests(self):
        """
        初始化待发送请求队列，由子类实现。拼装一串SpiderRequest对象并送到sending_queue队列中
        """
        raise NotImplementedError()

    def is_finish(self):
        """
        根据相关队列是否全都为空来判断任务处理结束
        """
        return self.sending_queue.qsize() == 0 and self.sended_queue.qsize() == 0

    def send_wait(self):
        """
        发送等待
        """
        time.sleep(1)

    def send_requests(self, max_idle_time):
        """
        发送请求。将sending_queue队列中的SpiderRequest对象通过downloader发送到下载中心
        """
        downloader = self.get_downloader()
        start_time = time.time()
        while True:
            try:
                request = self.sending_queue.get_nowait()
                if request.user_id is None:
                    request.user_id = self.user_id
                results = downloader.set(request)
                self.deal_request_results(request, results)
                start_time = time.time()
                self.send_wait()
            except Empty:
                if start_time + max_idle_time < time.time():
                    if self.is_finish():
                        break
                time.sleep(10)
            except Exception :
                print 'send_requests:'+(traceback.format_exc())

    def deal_request_results(self, request, results):
        """
        发送请求send_requests后的处理逻辑，由子类实现
        Args:
            request:SpiderRequest对象
            results:发送request后的返回对象
        """
        raise NotImplementedError()

    def get_wait(self):
        """
        取结果等待
        """
        time.sleep(1)

    def get_response(self, max_idle_time):
        """
        获取url爬取结果。将sended_queue队列中的SpiderRequest对象通过downloader到下载中心去获取抓取到的html
        """
        downloader = self.get_downloader()
        stores = self.get_stores()
        start_time = time.time()
        while True:
            try:
                request = self.sended_queue.get_nowait()
                results = downloader.get(request)

                self.deal_response_results(request, results, stores)
                start_time = time.time()
                self.get_wait()
            except Empty:
                if start_time + max_idle_time < time.time():
                    if self.is_finish():
                        break
                time.sleep(10)
            except Exception, e1:
                print 'get_response:'+(traceback.format_exc())

    def get_stores(self):
        """
        设置存储器，供deal_response_results调用
        Return:
            list,成员为SpiderStore对象
        """
        raise NotImplementedError()

    def deal_response_results(self, request, results, stores):
        """
        获取url爬取结果后的处理逻辑，由子类实现。
        Args:
            request:SpiderRequest对象
            results:请求request结果后的返回对象
            stores:list，可能会用到的存储器（SpiderStore）列表
        """
        raise NotImplementedError()

    # def record_log(self):
    #     """
    #     记录抓取日志，用于调整各个线程参数设置
    #     """
    #     while not self.is_finish():
    #         print('sending_queue:%d; sended_queue:%d' % (self.sending_queue.qsize(), self.sended_queue.qsize()))
    #         # 需要安装objgraph包
    #         import objgraph
    #         objgraph.show_most_common_types()
    #         time.sleep(300)

    def run(self, send_num=1, get_num=1, send_idle_time=600, get_idle_time=600, record_log=False):
        """
        爬虫启动入口
        Args:
            send_num:发送请求线程数，默认为1
            get_num:获取结果线程数，默认为1
            send_idle_time:发送请求线程超过该时间没有要发送的请求就停止
            get_idle_time:获取结果线程超过该时间没有要获取的结果就停止
            record_log:定时记录各个队列大小，便于分析抓取效率
        """
        self.validate_user()
        self.start_requests()
        threads = list()
        for i in range(0, send_num):
            threads.append(Thread(target=self.send_requests, args=(send_idle_time,)))
        for i in range(0, get_num):
            threads.append(Thread(target=self.get_response, args=(get_idle_time,)))
        if record_log:
            threads.append(Thread(target=self.record_log))
        for thread in threads:
            thread.start()
