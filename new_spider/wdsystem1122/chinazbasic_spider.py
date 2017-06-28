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
from extractor.chinaz.seo_basic_base import SeoBasicBase
from extractor.baidu.seo_domain import SeoDomain
from store_mysql import StoreMysql
from util.util_useragent import UtilUseragent
from store.wdsystem.outlinks_source_store import OutlinksSourceStore
import random
import time
import json
import re
import urllib
from copy import copy
reload(sys)
sys.setdefaultencoding('utf8')


class ChinazBasicSourceSpider(BaseSpiderSeparateDealAndStore):

    def __init__(self):
        super(ChinazBasicSourceSpider, self).__init__()
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
            purls = list()
            murls = list()
            surls = list()
            for result in results:
                try:
                    dm = SeoDomain.get_domain(result[1])
                    dmend = SeoDomain.get_postfix(dm)
                    if not dmend:
                        url_len -= 1
                        continue
                except Exception,e:
                    url_len -= 1
                    continue
                kwh = {'host':dm}
            	url = 'http://seo.chinaz.com/%s' % dm
                urls.append({'url': url, 'type': 1,'id':result[0]})
                url_len -= 1
                if len(urls) == 50 or url_len == 0:
                    basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 1},
                                                     urls=urls)
                    self.sending_queue.put(basic_request)
                    urls = list()
            	#移动端
		murl = 'http://wapseo.chinaz.com/rank?'+urllib.urlencode(kwh)
                murls.append({'url': murl, 'type': 1,'id':result[0]})
                if len(murls) == 50 or url_len == 0:
		    mbasic_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 3},
                                                     urls=murls)
                    self.sending_queue.put(mbasic_request)
                    murls = list()
                               #pc权重
                purl = 'http://rank.chinaz.com/?'+urllib.urlencode(kwh)
                purls.append({'url': purl, 'type': 1,'id':result[0]})
                if len(purls) == 50 or url_len == 0:
                    pbasic_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 2},
                                                     urls=purls)
                    self.sending_queue.put(pbasic_request)
                    purls = list()
                #360
                sourl = 'http://rank.chinaz.com/sorank?'+urllib.urlencode(kwh)
                surls.append({'url': sourl, 'type': 1,'id':result[0]})
                if len(surls) == 50 or url_len == 0:
                    sobasic_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 4},
                                                     urls=surls)
                    self.sending_queue.put(sobasic_request)
                    surls = list()    
        except Exception, e:
            print str(e)
	    #self.log.error('获取初始请求出错:%s' % str(e))
    def get_user_password(self):
        return 'pangge','pgspider'
    def deal_request_results(self, request, results):
	param = request.urls[0]
	if results == 0:
            return False
        else:
            print 'send suc'
            #self.log.info('请求发送成功')
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        stores.append(OutlinksSourceStore())
        return stores

    def deal_response_results(self, request, results, stores):
	param = request.urls[0]
        if results == 0:
            pass
        else:
            urls = list()
            failed_urls=list()
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
                            self.deal_pr_basic_response(u, result['result'], stores)
                        elif req_type == 2:
                            self.deal_qz_pc_response(u, result['result'], stores)
                        elif req_type == 3:
                            self.deal_qz_m_response(u, result['result'], stores)
                        elif req_type == 4:
                            self.deal_qz_so_response(u, result['result'], stores)
                        result= None
                    elif str(result['status']) == '3':
                        failed_urls.append(u)
                    else:
                        urls.append(u)
                else:
                    failed_urls.append(u)
                    #self.log.error('url发送失败:%s' % url)
            if len(failed_urls) > 0:
                new_request = copy(request)
                new_request.urls = failed_urls
                self.sending_queue.put(new_request)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)
    def deal_qz_so_response(self, url, html, stores):
        try:
           r = self.basicExtractor.qz_so(html)
	   res ={}
	   if r['domain_status'] == 1 and r['response_status'] == 1:
	       res['id'] = url['id']
	       res['cz_so_qz'] = r['cz_so_qz']
	       res['cz_so_traffic'] = r['cz_so_traffic']
	       res['cz_so_kwdnum'] = r['cz_so_kwdnum']
               self.store_queue.put({'data': res, 'type': 1, 'storeIndex': 0})
        except Exception,e:
            return False
    def deal_pr_basic_response(self, url, html, stores):
        try:
	    r = self.basicExtractor.get_siteall(html)
	    res ={}
	    if r['domain_status'] == 1 and r['response_status'] == 1:
	        res['id'] = url['id']
	        res['cz_pr'] = r['cz_pr']
	        res['spiderstat'] = 1
	        self.store_queue.put({'data': res, 'type': 1, 'storeIndex': 0})
        except Exception,e:
            return False
    def to_store_results(self, results, stores):
        try:
            if results['type']==1:
                stores[0].store_azbasic(results['data'],'id')
        except:
            pass
    def deal_qz_pc_response(self, url, html, stores):
        try:
            r = self.basicExtractor.qz_pc(html)
	    res ={}
	    if r['domain_status'] == 1 and r['response_status'] == 1:
	        res['id'] = url['id']
	        res['cz_baidupc_qz'] = r['cz_baidupc_qz']
	        res['cz_traffic_pc'] = r['cz_traffic_pc']
	        res['cz_pc_kwdnum'] = r['cz_pc_kwdnum']
                self.store_queue.put({'data': res, 'type': 1, 'storeIndex': 0}) 
        except Exception,e:
            return False
    def deal_qz_m_response(self, url, html, stores):
        try:
            r = self.basicExtractor.qz_m(html)
	    res ={}
	    if r['domain_status'] == 1 and r['response_status'] == 1:
	        res['id'] = url['id']
	        res['cz_baidum_qz'] = r['cz_baidum_qz']
	        res['cz_traffic_m'] = r['cz_traffic_m']
	        res['cz_m_kwdnum'] = r['cz_m_kwdnum']
                self.store_queue.put({'data': res, 'type': 1, 'storeIndex': 0})
        except:
            return False
    def test(self):
	fp=open('ss.html')
	html = fp.read()
	fp.close()
	r = self.basicExtractor.get_rank(html)
	x= self.spider_test(r['kwd_url'])
	data = json.loads(x)
	res ={}
	try:
	    res['az_pc_kwdnum'] = data['pcWL'][0]
	except:
	    pass
	try:
	    res['az_m_kwdnum'] = data['mWL'][0]
	except:
	    pass
	print res
def Main():
    spider = ChinazBasicSourceSpider()
    spider.run(5, 100, 200, 100, 600, 600, 600, 600,True)

if __name__ == '__main__':
    Main()
