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
from extractor.engine.seo_basic_base import SeoBasicBase
from store.wdsystem.outlinks_source_store import OutlinksSourceStore
from store_mysql import StoreMysql
from extractor.baidu.seo_domain import SeoDomain
from util.util_useragent import UtilUseragent
import random
import time
import json
import re
import urllib
from copy import copy
reload(sys)
sys.setdefaultencoding('utf8')


class EngineBasicSourceSpider(BaseSpiderSeparateDealAndStore):

    def __init__(self):
        super(EngineBasicSourceSpider, self).__init__()
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
            durls = list()
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
                wd = 'site:%s' % dm
                kwh = {'wd':wd}
                url = 'https://www.baidu.com/s?'+urllib.urlencode(kwh)
                urls.append({'url': url, 'type': 1, 'init': dm,'id':result[0]})
                url_len -= 1
                if len(urls) == 50 or url_len == 0:
                    basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 1},
                                                     urls=urls)
                    self.sending_queue.put(basic_request)
                    urls = list()
                wd = 'domain:"%s"' % dm
                kwh = {'wd':wd}
                durl = 'https://www.baidu.com/s?'+urllib.urlencode(kwh)
                durls.append({'url': durl, 'type': 1, 'init': dm,'id':result[0]})
                if len(durls) == 50 or url_len == 0:
		    dbasic_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 2},
                                                     urls=durls)
                    self.sending_queue.put(dbasic_request)
                    durls = list()
        except Exception, e:
	    print str(e)
    def get_user_password(self):
        return 'pangge','pgspider'
    def deal_request_results(self, request, results):
	param = request.urls[0]
	if results == 0:
            print 'send false'
            return False
        else:
            print 'send suc'
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
            furls = list()
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
                            self.deal_baidusite_response(u, result['result'], stores)
                        if req_type == 2:
                            self.deal_baidudomain_response(u, result['result'], stores)
                        result= None
                    elif str(result['status']) == '3':
                        furls.append(u)
                    else:
                        urls.append(u)
                else:
                    furls.append(u)
            if len(furls) > 0:
                new_request = copy(request)
                new_request.urls = furls
                self.sending_queue.put(new_request)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)

    def deal_baidusite_response(self, url, html, stores):
	try:
            r = self.basicExtractor.get_baidu_site(html)
	    res ={}
	    if r['domain_status'] == 1 and r['response_status'] == 1:
	        res['id'] = url['id']
	        res['sl_num_baidu'] = r['sl_num_baidu']
                res['baidu_site'] = r['baidu_site']
                res['spiderstat'] = 1
                self.store_queue.put({'data': res, 'type': 1, 'storeIndex': 0})
        except:
            return False
    def deal_baidudomain_response(self, url, html, stores):
	try:
            r = self.basicExtractor.get_baidu_domain(html)
	    res ={}
	    if r['domain_status'] == 1 and r['response_status'] == 1:
	        res['id'] = url['id']
	        res['baidu_domain'] = r['baidu_domain']
                self.store_queue.put({'data': res, 'type': 1, 'storeIndex': 0})
        except:
            return False
    def to_store_results(self, results, stores):
        try:
            if results['type']==1:
                stores[0].store_azbasic(results['data'],'id')
        except:
            pass
def Main():
    spider = EngineBasicSourceSpider()
    spider.run(10, 50, 100, 50, 600, 600, 600, 600,True)

if __name__ == '__main__':
    Main()
