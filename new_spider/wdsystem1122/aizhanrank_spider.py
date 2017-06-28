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
from extractor.aizhan.seo_aizhan_newbase import SeoAizhanBase
from extractor.baidu.seo_domain import SeoDomain
from util.util_useragent import UtilUseragent
from store.wdsystem.outlinks_source_store import OutlinksSourceStore
from store_mysql import StoreMysql
import random
import time
import json
import re
from copy import copy
reload(sys)
sys.setdefaultencoding('utf8')


class AizhanRankSourceSpider(BaseSpiderSeparateDealAndStore):

    def __init__(self):
        super(AizhanRankSourceSpider, self).__init__()
        self.aizhanBasicExtractor = SeoAizhanBase()

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
            	#排名
		aizhan_rank_url = 'http://baidurank.aizhan.com/baidu/%s' % dm
                urls.append({'url': aizhan_rank_url, 'type': 1,'init':dm,'id':result[0]})
                url_len -= 1
                if len(urls) == 20 or url_len == 0:
		    aizhan_rank_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 8,'priority':3},
                                                     urls=urls)
                    self.sending_queue.put(aizhan_rank_request)
                    urls = list()
        except Exception, e:
	    print str(e)
    def get_user_password(self):
        return 'pangge','pgspider'
    def deal_request_results(self, request, results):
	if results == 0:
            #'请求发送失败'
            return False
        else:
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        stores.append(OutlinksSourceStore())
        return stores

    def deal_response_results(self, request, results, stores):
	param = request.urls[0]
        if results == 0:
            return False
        else:
            urls = list()
            furls = list()
            for u in request.urls:
                url = u['url']
		if url in results:
                    result = results[url]
                    f_rank_url = 'http://baidurank.aizhan.com/baidu/%s' % u['init']
                    if str(result['status']) == '2':
                        log ='抓取成功:%s' % url
                        print log
                        xw=None
                        configs = request.config
                        req_type = configs['req_type']
                        if req_type == 8:
                            self.deal_aizhan_rank_response(u, result['result'], stores)
                        elif req_type == 9:
                            xw = self.deal_aizhan_rankkwd_response(u, result['result'], stores)
                        result= None
                        if xw:
                            furls.append({'url': f_rank_url, 'type': 1,'init':u['init'],'id':u['id']})
                    elif str(result['status']) == '3':
                        furls.append({'url': f_rank_url, 'type': 1,'init':u['init'],'id':u['id']})
                    else:
                        urls.append(u)
                else:
                    furls.append({'url': f_rank_url, 'type': 1,'init':u['init'],'id':u['id']})
            if len(furls) > 0:
                aizhan_rank_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 8,'priority':3},
                                                    urls=furls)
                self.sending_queue.put(aizhan_rank_request)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)
    def deal_aizhan_rankkwd_response(self,url,html,stores):
	res = {}
	try:
            if re.search(u'验证超时',html):
                return True
            data = json.loads(html)
        except:
            return False
	try:
	    res['az_pc_kwdnum'] = data['pcWL'][0]
	except:
	    pass
	try:
	    res['az_m_kwdnum'] = data['mWL'][0]
	except:
	    pass
        if res:
            res['id'] = url['id']
            self.store_queue.put({'data': res, 'type': 1, 'storeIndex': 0})
    def to_store_results(self, results, stores):
        try:
            if results['type']==1:
                stores[0].store_azbasic(results['data'],'id')
        except:
            pass
    def deal_aizhan_rank_response(self,url,html,stores):
	res={}
        try:
	    r = self.aizhanBasicExtractor.get_rank(html)
        except:
            return False
	if r['domain_status'] == 1 and r['response_status'] == 1:
            if r['kwd_url']:
                aizhan_br_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents),'Referer':url['url']},
                                                      config={'req_type': 9,'priority':3},
                                                      urls=[{'url': r['kwd_url'], 'type': 1,'init':url['init'],'id':url['id']}])
            	self.sending_queue.put(aizhan_br_request)
	    try:
                res['id'] = url['id']
	        res['az_m_kwdnum'] = r['az_m_kwdnum']
	        res['az_pc_kwdnum'] = r['az_pc_kwdnum']
                res['az_baidupc_qz'] = r['pc_br']
	        res['az_baidum_qz'] = r['m_br']
	        res['traffic_pc'] = r['traffic_pc'].replace('~','|')
	        res['traffic_m'] = r['traffic_m'].replace('~','|')
	        res['spiderstat'] = 1
                self.store_queue.put({'data': res, 'type': 1, 'storeIndex': 0})
            except Exception,e:
                return False
            
def Main():
    spider = AizhanRankSourceSpider()
    spider.run(2, 50, 100, 50, 600, 600, 600, 600,True)

if __name__ == '__main__':
    Main()
