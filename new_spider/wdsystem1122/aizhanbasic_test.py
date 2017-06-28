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
from store.wdsystem.outlinks_source_store import OutlinksSourceStore
from store_mysql import StoreMysql
from util.util_useragent import UtilUseragent
import random
import time
import json
import re
from copy import copy
sys.setdefaultencoding('utf8')
reload(sys)


class AizhanBasicSourceSpider(BaseSpiderSeparateDealAndStore):

    def __init__(self):
        super(AizhanBasicSourceSpider, self).__init__()
        self.aizhanBasicExtractor = SeoAizhanBase()
    def get_results(self):
        spidertype=int(sys.argv[1])
        db = StoreMysql(**config.SITEANALYSTAPi_DB)
        sql = 'SELECT id,url from site_basicinfo where spidertype=%s limit 10' % spidertype
	results = db.query(sql)
        return results
    def start_requests(self):
        try:
	    results = self.get_results()
            url_len = len(results)
            if url_len<1:
                sys.exit(1)
            urls = list()
            for result in results:
                #基本信息
                try:
                    dm = SeoDomain.get_domain(result[1])
                    dmend = SeoDomain.get_postfix(dm)
                    if not dmend:
                        url_len -= 1
                        continue
                except:
                    url_len -= 1
                    continue
            	#rank_url = 'http://www.aizhan.com/cha/%s' % dm
                rank_url = 'http://www.aizhan.com/ajaxAction/pr.php?callback=jsonp&domain=szlsy.cn&rn=1479442207&cc=b1f474b52d8dd725bebaaba32157d28d'
                urls.append({'url': rank_url,'init':dm,'type': 3,'id':result[0]})
                url_len -=1
                if len(urls) == 50 or url_len == 0:
		    rank_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 2},
                                                     urls=urls)
                    self.sending_queue.put(rank_request)
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
	param = request.urls[0]
        if results == 0:
            return False
        else:
            urls = list()
            failed_urls = list()
            for u in request.urls:
                url = u['url']
		if url in results:
                    result = results[url]
                    r_url = 'http://www.aizhan.com/cha/%s' % u['init']
                    if str(result['status']) == '2':
                        log ='抓取成功:%s' % url
                        print log
                        configs = request.config
                        req_type = configs['req_type']
                        if req_type == 2:
                            self.deal_aizhan_basic_response(u, result['result'], stores)
                        elif req_type == 3:
                            xs = self.deal_aizhan_pr_response(u, result['result'], stores)
                            if xs:
                                failed_urls.append({'url': r_url, 'type': 3,'init':u['init'],'id':u['id']})
                        elif req_type == 4:
                            xs = self.deal_aizhan_br_response(u, result['result'], stores)
                            if xs:
                                failed_urls.append({'url': r_url, 'type': 3,'init':u['init'],'id':u['id']})
                        elif req_type == 5:
                            xs = self.deal_aizhan_whois_response(u, result['result'], stores)
                            if xs:
                                failed_urls.append({'url': r_url, 'type': 3,'init':u['init'],'id':u['id']})
                        elif req_type == 6:
                            xs = self.deal_aizhan_dns_response(u, result['result'], stores)
                            if xs:
                                failed_urls.append({'url': r_url, 'type': 3,'init':u['init'],'id':u['id']})
                        elif req_type == 7:
                            xs = self.deal_aizhan_speed_response(u, result['result'], stores)
                            if xs:
                                failed_urls.append({'url': r_url, 'type': 3,'init':u['init'],'id':u['id']})
                        result = None
                    elif str(result['status']) == '3':
                        failed_urls.append({'url': r_url, 'type': 3,'init':u['init'],'id':u['id']})
                    else:
                        urls.append(u)
                else:
                    failed_urls.append({'url': r_url, 'type': 3,'init':u['init'],'id':u['id']})
            if len(failed_urls) > 0:
                r_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                          config={'req_type': 2},
                                          urls=failed_urls)
                self.sending_queue.put(r_request)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)
    def deal_aizhan_whois_response(self,url,html,stores):
	res ={}
	try:
            if re.search(u'验证超时',html):
                return True
	    whois_data = json.loads(html)
	    res['id'] = url['id']
	    res['whois_name'] = whois_data['registrant']
	    res['whois_email'] = whois_data['email']
	    res['whois_name_num'] = whois_data['registrantSum']
	    res['whois_email_num']  = whois_data['emailSum']
	    age  = whois_data['created']
	    res['age'] = self.get_date_diff(age)
	    if res:
                self.store_queue.put({'data': res, 'type':1 , 'storeIndex': 0})
        except Exception,e:
            return False
    def deal_aizhan_dns_response(self,url,html,stores):
	res={}
	try:
            if re.search(u'验证超时',html):
                return True
            dns_data = json.loads(html)
	    #dns_data = html
	    res['id'] = url['id']
            res['siteip'] = dns_data['ip']
            res['siteipadress'] = dns_data['address']
            res['siteipnum'] = dns_data['num']
            res['ipdomain'] = '|'.join(dns_data['domains'])
	    if res:
                self.store_queue.put({'data': res, 'type':1 , 'storeIndex': 0})
        except:
            return False

    def deal_aizhan_speed_response(self,url,html,stores):
        res = {}
	try:
            if re.search(u'验证超时',html):
                return True
            r = self.aizhanBasicExtractor.get_speed(html)
            if r==-1:
	        return True
	    res['site_cesu'] = r
	    res['id'] = url['id']
            self.store_queue.put({'data': res, 'type':1 , 'storeIndex': 0})
        except:
            return False
	
    def deal_aizhan_basic_response(self, url, html, stores):
        if re.search(u'验证超时',html):
            return True
        try:
            r = self.aizhanBasicExtractor.get_siteall(html)
        except:
            return False
        try:
	    if r['domain_status'] == 1 and r['response_status'] == 1:
	        if r['pr'] == -1 and r['pr_url']:
		    aizhan_pr_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents),'Referer':url['url']},
					      config={'req_type': 3,'priority':3},
					      urls=[{'url': r['pr_url'], 'type': 1,'init':url['init'],'id':url['id']}])
	    	    self.sending_queue.put(aizhan_pr_request)
	        if r['whostat'] == -1 and  r['whoisurl']:
		    aizhan_br_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents),'Referer':url['url']},
                                                      config={'req_type': 5,'priority': 3},
                                                      urls=[{'url': r['whoisurl'], 'type': 1,'init':url['init'],'id':url['id']}])
		    self.sending_queue.put(aizhan_br_request)
	        if r['dnsstat'] == -1 and r['dnsurl']:
		    aizhan_br_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents),'Referer':url['url']},
                                                      config={'req_type': 6,'priority': 3},
                                                      urls=[{'url': r['dnsurl'], 'type': 1,'init':url['init'],'id':url['id']}])
                    self.sending_queue.put(aizhan_br_request)
	        if r['websd'] == -1 and  r['speedurl']:
		    aizhan_br_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents),'Referer':url['url']},
                                                      config={'req_type': 7,'priority': 3},
                                                     urls=[{'url': r['speedurl'], 'type': 1,'init':url['init'],'id':url['id']}])
                    self.sending_queue.put(aizhan_br_request)
                if len(r) > 1:
		    newdata={}
		    newdata['id'] = url['id']
		    if r['pr']==-1:
                        newdata['az_pr'] = ''
                    else:
                        newdata['az_pr'] = r['pr']
		    newdata['az_baidupc_qz'] = r['bd_pc_pr']
		    newdata['az_baidum_qz'] = r['bd_m_pr']
		    newdata['az_links'] = r['az_links']
		    newdata['siteip'] = r['siteip']
		    newdata['siteipadress'] = r['siteipadress']
		    newdata['siteipnum'] = r['siteipnum']
		    newdata['whois_name'] = r['whois']
		    newdata['whois_name_num'] = r['whois_name_num']
		    newdata['whois_email'] = r['whois_email']
		    newdata['alexa'] = r['alxea']
		    newdata['whois_email_num'] = r['whois_email_num']
		    newdata['domain_year'] = r['age']
		    newdata['site_cesu'] = r['websd']
		    newdata['ipdomain'] = r['ipdomain']
                    self.store_queue.put({'data': newdata, 'type':1 , 'storeIndex': 0})
        except Exception,e:
            print str(e)
            return False
    def deal_aizhan_pr_response(self, url, html, stores):
        try:
            if re.search(u'验证超时',html):
                return True
	    jsondata = re.findall(r'.*\((.*?)\)',html)
	    res ={}
	    if jsondata:
		res['id']= url['id']
	    	prlist = json.loads(jsondata[0])
		res['az_pr'] = prlist['pr']
		res['spiderstat'] = 1
	        if res:
                    self.store_queue.put({'data': res, 'type':1 , 'storeIndex': 0})
	except:
            return False
	
    def deal_aizhan_br_response(self, url, html, stores):
        try:
            if re.search(u'验证超时',html):
                return True
            r = self.aizhanBasicExtractor.get_baidu_pr(html)
            if r['response_status'] == 1:
                data = {'id': url['id'],'az_baidupc_qz': r['pc_pr'], 'az_baidum_qz': r['m_pr']}
                self.store_queue.put({'data': data, 'type':1 , 'storeIndex': 0})
        except:
            return False
    def to_store_results(self, results, stores):
        try:
            if results['type']==1:
                print results['data']
                #stores[0].store_azbasic(results['data'],'id')
        except:
            pass
def Main():
    spider = AizhanBasicSourceSpider()
    spider.run(1, 20, 20, 5, 6, 6, 6, 6,True)

if __name__ == '__main__':
    Main()
