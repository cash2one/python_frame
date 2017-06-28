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
from store.wdsystem.outlinks_source_store import OutlinksSourceStore
from store_mysql import StoreMysql
import random
import time
import re
from copy import copy
sys.setdefaultencoding('utf8')
reload(sys)


class AizhanKwdSpider(BaseSpiderSeparateDealAndStore):

    def __init__(self):
        super(AizhanKwdSpider, self).__init__()
        self.aizhanBasicExtractor = SeoAizhanBase()
    def start_requests(self):
        try:
            sql='select id,url from site_basicinfo limit 100'
            url_len = len(results)
            urls = list()
            for result in results:
                url = 'http://baidurank.aizhan.com/mobile/%s' % result[1]
                urls.append({'url': url, 'type': 1,'id':result[0]})
                url_len -= 1
                if len(urls) == 50 or url_len == 0:
                    aizhan_kwd_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 1},
                                                     urls=urls)
                    self.sending_queue.put(aizhan_rank_request)
                    urls = list()
        except Exception, e:
            print str(e)
            return False
    def to_store_results(self, results, stores):
        if results['type']==1:
            stores[0].store_aizhankwd(results['data'],'site_azmobile_keywords')
    def get_user_password(self):
        return 'xuliang','xulspider'

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
            for u in request.urls:
                url = u['url']
                if url in results:
                    result = results[url]
                    if str(result['status']) == '2':
                        log ='抓取成功:%s' % url
                        print log
                        configs = request.config
                        req_type = configs['req_type']
                        if req_type == 1:
                            self.deal_aizhan_response(u, result['result'], stores)
                        elif req_type == 2:
                            self.deal_aizhan_kwd_response(u, result['result'], stores)
                        result=None
                    elif str(result['status']) == '3':
                        log = '抓取失败:%s' % url
                        print log
                    else:
                        urls.append(u)
                else:
                    pass
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)
    def deal_aizhan_kwd_response(self,url,html,stores):
        res={}
        try:
            r = self.aizhanBasicExtractor.get_kwd_detail(html) 
        except:
            return False
        if r['domain_status'] == 1 and r['response_status'] == 1:
            dt = time.strftime('%Y-%m-%d %X', time.localtime())
            if r['pagelist']:
                for v in r['pagelist']:
                    data = dict()
                    data = {'keyword': v['kwd'],'m_search': v['sear'],'createtime':dt}
                    self.store_queue.put({'data': data, 'type':1 , 'storeIndex': 0})
    def deal_aizhan_response(self,url,html,stores):
        res={}
        try:
            r = self.aizhanBasicExtractor.get_kwd(html)
        except:
            return False
        if r['domain_status'] == 1 and r['response_status'] == 1:
            if r['pagelist']:
                url_len = len(r['pagelist'])
                urls = list()
                for p in r['pagelist']:
                    vurl = '%s/-1/0/%s/' % (url['url'],p)
                    urls.append({'url': vurl, 'type': 1,'id':url['id']})
                    url_len -= 1
                    if len(urls) == 50 or url_len == 0:
                        aizhan_kwd_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                     config={'req_type': 2},
                                                     urls=urls)
                        self.sending_queue.put(aizhan_rank_request)
                        urls = list()
    def test(self):
        fp=open('xx.html','r+')
        con = fp.read()
        fp.close()
        r = self.aizhanBasicExtractor.get_kwd_detail(con)
        print r
def Main():
    spider = AizhanKwdSpider()
    spider.run(50, 50, 100, 50, 600, 600, 600, 600,True)

if __name__ == '__main__':
    Main()
