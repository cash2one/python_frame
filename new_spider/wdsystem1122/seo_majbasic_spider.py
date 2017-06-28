# -*- coding: utf8 -*-
import os
import sys
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
sys.path.append(os.path.join(PROJECT_PATH, 'store'))
sys.path.append(os.path.join(PROJECT_PATH, 'util'))
from spider.basespider_separate_deal_and_store import BaseSpiderSeparateDealAndStore
from spider import config
from downloader.downloader import SpiderRequest
from extractor.majestic.seo_basic_base import SeoBasicBase
from store_mysql import StoreMysql
from extractor.baidu.seo_domain import SeoDomain
from store.wdsystem.outlinks_source_store import OutlinksSourceStore
import random
from copy import copy
import time
reload(sys)
sys.setdefaultencoding('utf8')


class MajBasicSourceSpider(BaseSpiderSeparateDealAndStore):

    def __init__(self):
        super(MajBasicSourceSpider, self).__init__()
        self.basicExtractor = SeoBasicBase()
        self.start_url = 'https://zh.majestic.com/reports/site-explorer?folder=&q=%s&IndexDataSource=F'

    def get_user_password(self):
        return 'pangge','pgspider'
    def get_results(self):
        spiderstat=int(sys.argv[1])
        db = StoreMysql(**config.SITEANALYSTAPi_DB)
        sql = 'SELECT id,url from site_basicinfo where spidertype=%s' % spiderstat
        results = db.query(sql)
        return results
    def start_requests(self):
        try:
            results = self.get_results()
            left_size = len(results)
            urls = list()
            for result in results:
                left_size -= 1
                dm = SeoDomain.get_domain(result[1])
                dmend = SeoDomain.get_postfix(dm)
                if not dmend:
                    continue
                urls.append({'url': self.start_url % dm, 'type': 1, 'init':dm, 'id': result[0]})
                if len(urls) == 50 or left_size == 0:
                    request = SpiderRequest(headers={
                        'User-Agent': random.choice(self.user_agents)
                    }, config={'single': 1}, urls=urls)
                    self.sending_queue.put(request)
                    urls = list()
        except Exception, e:
            print str(e)

    def deal_request_results(self, request, results):
        if results == 0:
            pass
        else:
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        stores.append(OutlinksSourceStore())
        return stores

    def deal_response_results(self, request, results, stores):
        if results == 0:
            pass
        else:
            urls = list()
            failed_urls = list()
            for u in request.urls:
                url = u['url']
                if url in results:
                    result = results[url]
                    if str(result['status']) == '2':
                        self.deal_basic_response(u, result['result'])
                        result= None
                    elif str(result['status']) == '3':
                        failed_urls.append(u)
                    else:
                        urls.append(u)
                else:
                    self.log.error('url发送失败:%s' % url)
                    failed_urls.append(u)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)
            if len(failed_urls) > 0:
                new_request = copy(request)
                new_request.urls = failed_urls
                self.sending_queue.put(new_request)

    def deal_basic_response(self, url, html):
        try:
            r = self.basicExtractor.get_siteall(html)
            if r['domain_status'] == 1 and r['response_status'] == 1:
                res = dict()
                res['id'] = url['id']
                res['outlink_domainum'] = r['outlink_domainum']
                res['outlink_num'] = r['outlink_num']
                res['outlink_pf'] = r['outlink_pf']
                res['outlink_source'] = r['outlink_source']
                res['spiderstat'] = 1
                self.store_queue.put({'data': res, 'type': 1, 'storeIndex': 0})
        except Exception:
            pass

    def to_store_results(self, results, stores):
        try:
            if results['type']==1:
                stores[0].store_azbasic(results['data'],'id')
        except:
            pass


def Main():
    spider = MajBasicSourceSpider()
    spider.run(10, 50, 100, 50, 600, 600, 600, 600, True)

if __name__ == '__main__':
    Main()
