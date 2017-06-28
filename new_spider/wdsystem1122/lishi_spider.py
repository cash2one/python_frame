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
from extractor.aizhan.seo_aizhan_base import SeoAizhanBase
from extractor.baidu.seo_domain import SeoDomain
from store.wdsystem.outlinks_source_store import OutlinksSourceStore
from store_mysql import StoreMysql
from util.util_useragent import UtilUseragent
from datetime import datetime
import random
import time
import json
import re
import math
from copy import copy
reload(sys)
sys.setdefaultencoding('utf8')


class LishiSpider(BaseSpiderSeparateDealAndStore):

    def __init__(self):
        super(LishiSpider, self).__init__()
        self.basicExtractor = SeoAizhanBase()
    def get_results(self):
        spiderstat=int(sys.argv[1])
        db = StoreMysql(**config.SITEANALYSTAPi_DB)
        sql = 'SELECT id,url from site_basicinfo where spidertype=%s' % spiderstat
        results = db.query(sql)
        return results
    def getlast_month(self):
        d = datetime.now()
        year = d.year
        month = d.month
        if month == 1 :
            month = 12
            year -= 1
        else :
            month -= 1
        x = datetime(year,month,1).strftime('%Y%m')
        return int(x)
    def start_requests(self):
        try:
            curt = self.getlast_month()
            spiderstat=int(sys.argv[1])
            db = StoreMysql(**config.SITEANALYSTAPi_DB)
            sql = 'SELECT id,url,user from site_basicinfo where spidertype=%s' % spiderstat
            results = db.query(sql)
            url_len = len(results)
            urls = list()
            for result in results:
		try:
                    dm = SeoDomain.get_domain(result[1])
                    dmend = SeoDomain.get_postfix(dm)
                    if not dmend:
                        url_len -= 1
                        continue
                    url_len -= 1
                except:
                    url_len -= 1
                    continue
                csql = 'select dt from site_lishi where url="%s" order by dt desc' % dm
                ces = db.query(csql)
                curls = list()
                if ces:
                    for c in ces:
                        if int(c[0])<=curt:#小于上个月的放进去
                            curls.append(c[0])
                url = 'http://lishi.aizhan.com/%s' % dm
                urls.append({'url': url, 'type': 1, 'init': dm,'dt':'','id':result[0],'surl':dm,'page':curls,'user':result[2]})
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
    def to_store_results(self, results, stores):
        try:
            if results['type']==1:
                stores[0].store_azhistory(results['data'])
        except:
            pass
    def deal_request_results(self, request, results):
	param = request.urls[0]
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
                        if req_type == 2:
                            self.deal_info_response(u, result['result'], stores)
                        result = None
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

    def deal_info_response(self, url, html, stores):
	res = {}
	try:
            r = self.basicExtractor.get_newlishiinfo_site(html)
            if r['data']==0:
	        res['urlid'] = url['id']
	        res['url'] = url['surl']
	        res['source'] = 'aizhan'
	        res['dt'] = url['dt']
                res['spider']=1
                res['user']=url['user']
	        self.store_queue.put({'data': res, 'type':1 , 'storeIndex': 0})
                return False
	    if r['domain_status'] == 1 and r['response_status'] == 1:
	        res['urlid'] = url['id']
	        res['url'] = url['surl']
	        res['user'] = url['user']
	        res['source'] = 'aizhan'
	        res['dt'] = url['dt']
	        res['kwdnum'] = r['pckwd']
                res['kwdnum_m'] = r['mkwd']
                res['pc_qz'] = r['pc_qz']
                res['m_qz']=r['m_qz']
                res['traffic_pc'] = r['traffic_pc']
                res['traffic_m']=r['traffic_m']
                res['traffic_all']=r['traffic_all']
                res['spider']=1
	        self.store_queue.put({'data': res, 'type':1 , 'storeIndex': 0})
        except:
            return False
    def deal_site_response(self, url, html, stores):
        try:
	    r = self.basicExtractor.get_lishi_site(html)
        except:
            return False
        try:
	    res ={}
	    if r['domain_status'] == 1 and r['response_status'] == 1:
	        res['id'] = url['id']
	        res['urllist'] = r['urllist']
                if len(r['urllist'])<1:
                    return False
	        if res['urllist']:
                    vurls = list()
                    url_len=len(res['urllist'])
            	    for u in res['urllist']:
                        if u in url['page']:
                            url_len -= 1
                            continue
                        url_len -= 1
            	        vurl = 'http://lishi.aizhan.com/%s/randabr/%s/' % (url['surl'],u)
		        dt = u
                        vurls.append({'url': vurl, 'type': 1, 'id': res['id'],'dt':dt,'surl':url['surl'],'user':url['user']})
                        if len(vurls) == 50 or url_len == 0:
		            basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 2},
                                                     urls=vurls)
                            self.sending_queue.put(basic_request)
                            vurls =list()
        except:
            return False
def Main():
    spider = LishiSpider()
    spider.run(5, 50, 100, 100, 600, 600, 600, 600,True)

if __name__ == '__main__':
    Main()
