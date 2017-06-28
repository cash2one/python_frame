# -*- coding: utf8 -*-
import os
import random
import sys
import urllib

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

from spider.basespider_improve import BaseSpider_improve

from extractor.baidu_collect.baidu_extractor_pc import BaiduSpiderExtractorPc
from store.baidu_brand.baidu_brand import SourceStore


class BasicSourceSpider(BaseSpider_improve):

    def __init__(self):
        super(BasicSourceSpider, self).__init__()
        self.basicExtractor = BaiduSpiderExtractorPc()
        self.log = UtilLogger('SourceSpider',
                              os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_SourceSpider'))
        # 自己的log
        # self.log_record = UtilLogger('Record_SourceSpider',
        #                         os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_RecordSourceSpider'))
        self.userpc_agents = UtilUseragent.get(type='PC')

    def get_user_password(self):
        # return 'sunxiang', 'sxspider'
        # return 'test', 'test'
        return 'xuliang', 'xlspider'

    # def get_downloader(self):
        #     """
        #     设置下载器类型，默认为Downloader
        #     Return:
        #         SpiderDownloader
        #     """
        # return Downloader(set_mode='db', get_mode='db')
        # return HtmlLocalDownloader(set_mode='db', get_mode='db')

    def start_requests(self):
        try:
            db = StoreMysql(**config.baixing_brand)
            # sql = "select id, brand   from baixing_brand.brand where is_brand <> 1"
            # sql = "SELECT id, brand FROM baixing_brand.brand where create_time < '2017-05-09 00:06:18';"
            # +官网
            sql = "SELECT id, brand FROM baixing_brand.brand "
            # +官网有数据
            # sql = "SELECT id, brand FROM baixing_brand.brand where is_brand = 1 and domain is not null;"
            rows = db.query(sql)
            print "开始获取任务"
            # print "时间:%s;开始执行:任务长度:%s" % (str(datetime.today()), str(len(keywords_list)))
            print len(rows)
            db.close()
            for row in rows:
                brand_id = row[0]
                brand_name = row[1]
                # kwh = {'wd': brand_name, 'rn': 50}
                # keyword = brand_name + "官网"
                # print keyword
                # + "官网"
                kwh = {'wd': brand_name}
                url = 'https://www.baidu.com/s?' + urllib.urlencode(kwh)
                print url
                urls = [{"url": url, "type": 1, "brand_id": brand_id}]
                basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.userpc_agents)}, urls=urls)
                self.sending_queue.put_nowait(basic_request)
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
                        self.deal_response(u, result['result'])

                    elif str(result['status']) == '3':
                        # 一直重试
                        # failed_urls.append(u)
                        #  重试限制次数
                        failed_urls = failed_urls + self.retry(u, 3)
                        self.log.info("status == 3 url:%s" % u)
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

    def deal_response(self, url, html):
        response_result = self.basicExtractor.extractor_baidu_pc_lxml(html)
        if type(response_result) == int:
            self.log.info("extractor result:%s ;url: %s" % (str(response_result), url))
        else:
            pass
            # is_brand = 0
            # if "brand_area" in extractor_result or "brand_website" in response_result:
            #     is_brand = 1
            # rank_result_list = extractor_result["rank_result_list"]
            # if len(rank_result_list) > 0:
            #     domain = rank_result_list[0]["domain"]
            #     if is_brand == 1:
            #         store_result = [{"id": url["brand_id"], "is_brand": is_brand, "domain": domain}]
            #         self.store_queue.put({"result": store_result})
            #     else:
            #         store_result = [{"id": url["brand_id"], "domain": domain}]
            #         self.store_queue.put({"result": store_result})


    '''
        results  type 1: 正常删除task 新增rank，2,3:判断, 3:有完全匹配
                task_id  task表id
    '''
    def to_store_results(self, results, stores):
        try:
            self.stores[0].store_table(results["result"], table="brand", type=2, field="id")
        except:
            print traceback.format_exc()

def Main():
    spider = BasicSourceSpider()
    spider.run(5, 15, 30, 10, 600, 600, 600, 600, True, True)

if __name__ == '__main__':
    Main()
