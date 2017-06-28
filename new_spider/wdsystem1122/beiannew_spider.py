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
from extractor.beian.seo_basic_base import SeoBasicBase
from store.wdsystem.outlinks_source_store import OutlinksSourceStore
from store_mysql import StoreMysql
from extractor.baidu.seo_domain import SeoDomain
from util.util_useragent import UtilUseragent
import random
import time
import json
import re
from copy import copy
reload(sys)
sys.setdefaultencoding('utf8')


class BeianSpider(BaseSpiderSeparateDealAndStore):

    def __init__(self):
        super(BeianSpider, self).__init__()
        self.basicExtractor = SeoBasicBase()
 
    def get_results(self):
        spiderstat=int(sys.argv[1])
        db = StoreMysql(**config.SITEANALYSTAPi_DB)
        sql = 'SELECT id,url from site_basicinfo where spidertype=%s' % spiderstat
        results = db.query(sql)
        return results

    def start_requests(self):
        try:
            results = self.get_results()
            url_len = len(results)
            urls = list()
            for result in results:
                try:
                    dm = SeoDomain.get_domain(result[1])
                    dmend = SeoDomain.get_postfix(dm)
                    if not dmend:
                        url_len -= 1
                        continue
                except:
                    url_len -= 1
                    continue
                dsp = dm.split('.')
                zy = len(dsp)-2
                ey = len(dsp)-1
                if len(dsp)>2:
                    dm = dsp[zy]+'.'+dsp[ey]
                url = 'http://www.beianbeian.com/search/%s' % dm
                urls.append({'url': url, 'type': 1,'id':result[0]})
                url_len -= 1
                if len(urls) == 50 or url_len == 0:
                    basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                  config={'req_type': 1},
                                                  urls=urls)
                    self.sending_queue.put(basic_request)
                    urls = list()
        except Exception, e:
            print str(e)
    def get_user_password(self):
        return 'pangge','pgspider'

    def deal_request_results(self, request, results):
        if results == 0:
            return False
        else:
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        stores.append(OutlinksSourceStore())
        return stores

    def deal_response_results(self, request, results, stores):
        if results == 0:
            return False
        else:
            urls = list()
            failed_urls = list()
            for u in request.urls:
                url = u['url']
                if url in results:
                    result = results[url]
                    if str(result['status']) == '2':
                        log = '抓取成功:%s' % url
                        print log
                        configs = request.config
                        req_type = configs['req_type']
                        if req_type == 1:
                            self.deal_site_response(u, result['result'], stores)
                        result= None
                    elif str(result['status']) == '3':
                        failed_urls.append(u)
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

    def deal_site_response(self, url, html, stores):
        try:
            r = self.basicExtractor.get_beian(html)
            res ={}
            if r['domain_status'] == 1 and r['response_status'] == 1:
                res['id'] = url['id']
                res['c_name'] = r['c_name']
                res['c_ana'] = r['c_ana']
                res['s_name'] =  r['s_name']
                res['c_xz'] = r['c_xz']
                res['stime'] = r['stime']
                self.store_queue.put({'data': res, 'type': 1, 'storeIndex': 0})
        except:
            return False
    def to_store_results(self, results, stores):
        try:
            if results['type']==1:
                stores[0].store_azbasic(results['data'],'id')
        except:
            pass
    def test(self):
        fp = open('beian.html','r+')
        html = fp.read()
        fp.close()
        r = self.basicExtractor.get_beian(html)
        print r
        for i in r:
            print r[i]
def Main():
    spider = BeianSpider()
    spider.run(10, 50, 100, 50, 600, 600, 600, 600,True)

if __name__ == '__main__':
    Main()
