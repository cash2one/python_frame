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
from extractor.baidu.seo_domain import SeoDomain
#from extractor.baidu.baidu_pc_rank_extractor import BaiduPcRankExtractor
from extractor.baidu.baidu_pc_rank_extractor2 import BaiduPcRankExtractor
from store.wdsystem.baidu_pc import OutlinksSourceStore
from util.util_useragent import UtilUseragent
from store_mysql import StoreMysql
import random
import time
import MySQLdb
import urllib
from copy import copy
reload(sys)
sys.setdefaultencoding('utf8')


class EngineBasicSourceSpider(BaseSpiderSeparateDealAndStore):

    def __init__(self):
        super(EngineBasicSourceSpider, self).__init__()
        self.basicExtractor = BaiduPcRankExtractor()
    
    def get_user_password(self):
        return 'wangm', 'wangmspider'
    
    def to_store_results(self, results, stores):
        if results['type']==1:
            stores[0].store_insert_new(results['data'],'site_keywordranks',results['kwd'],results['url'],results['dt'],results['user'],results['title'],results['keywordid'])
        elif results['type']==2:
            stores[0].store_job(results['data'],'site_keywords','id')
    
    def start_requests(self):
        try:
            try:
                user = sys.argv[2]
            except:
                user = ''
            spidertype = int(sys.argv[1])
            db = StoreMysql(**config.SITEANALYSTAPi_DB)
            usql = 'update site_keywords set spiderstat=0 where spidertype=%s' % spidertype
            sql = 'SELECT id, keyword,url,user,title,keywordid from site_keywords where spidertype=%s' % spidertype
            if user:
                usql+=' and user="%s"' % user
                sql+=' and user="%s"' % user
            db.do(usql)
            results = db.query(sql)
            url_len = len(results)
            urls = list()
            for result in results:
                kwh = {'wd':result[1],'rn':50}
                url = 'https://www.baidu.com/s?'+urllib.urlencode(kwh)
                urls.append({'url': url, 'type': 1, 'keyword': result[1],'id':result[0],'ckurl':result[2],'user':result[3],'title':result[4],'keywordid':result[5]})
                url_len -= 1
                if len(urls) == 50 or url_len == 0:    
                    basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},urls=urls)
                    self.sending_queue.put(basic_request)
                    urls = list()
        except Exception, e:
	    print str(e)

    def deal_request_results(self, request, results):
        param = request.urls[0]
        if results == 0:
            return False
        else:
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        stores.append(OutlinksSourceStore())
        self.stores = stores
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
                        print u['url']
                        self.deal_baidu_response(u, result['result'], stores)
                        result =None
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

    def deal_baidu_response(self, url, html, stores):
        try:
            r = self.basicExtractor.extractor(html,url['ckurl'])
        except:
            return False
        dt = time.strftime('%Y-%m-%d %X', time.localtime())
        if r:
            val = r[0]
        try:
            if int(val['response_status'])==1:
                if len(val['rank'])>0:
                    self.store_queue.put({'data': val['rank'], 'type': 1, 'storeIndex': 0,'kwd':url['keyword'],'dt':dt,'url':url['ckurl'],'user':url['user'],'title':url['title'],'keywordid':url['keywordid']})
                else:
                    if url['ckurl']:
                        t = dict()
                        t['domain'] = url['ckurl']
                        t['title']=''
                        t['description']=''
                        t['pos']=0
                        t['rank'] = 0
                        t['srcid'] = ''
                        nval=list()
                        nval=[t]
                        self.store_queue.put({'data': nval, 'type': 1, 'storeIndex': 0,'kwd':url['keyword'],'dt':dt,'url':url['ckurl'],'user':url['user'],'title':url['title'],'keywordid':url['keywordid']})
                data=dict()
                data['spiderstat'] = 1
                data['id'] = url['id']
                self.store_queue.put({'data': data, 'type': 2, 'storeIndex': 0})
        except Exception,e:
            print str(e)
            return False
def Main():
    spider = EngineBasicSourceSpider()
    if sys.argv[1]=='test':
	    spider.test()
    else:
        spider.run(10, 50, 150,100, 600, 600, 600, 600, True)
if __name__ == '__main__':
    Main()
