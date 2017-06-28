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
from extractor.baidu.baidu_mobile_rank_extractor2 import BaiduMobileRankExtractor
from store.wdsystem.baidu_mobile import OutlinksSourceStore
from util.util_useragent import UtilUseragent
from store_mysql import StoreMysql
import random
import time
import json
import re
import MySQLdb
import urllib
from copy import copy
reload(sys)
sys.setdefaultencoding('utf8')


class EngineBasicSourceSpider(BaseSpiderSeparateDealAndStore):

    def __init__(self):
        super(EngineBasicSourceSpider, self).__init__()
        self.basicExtractor = BaiduMobileRankExtractor()
    
    def get_user_password(self):
        return 'wangm', 'wangmspider'
    
    def to_store_results(self, results, stores):
        try:
            if results['type']==1:
                stores[0].store_insert(results['data'],'site_keywordranks_mobile')
            elif results['type']==2:
                stores[0].store_job(results['data'],'site_keywords_mobile','id')
        except:
            pass
    
    def start_requests(self):
        try:
            spidertype= int(sys.argv[1])
            try:
                user = sys.argv[2]
            except:
                user = ''
            db = StoreMysql(**config.SITEANALYSTAPi_DB)
            usql = 'update site_keywords_mobile set spiderstat=0 where spidertype=%s' % spidertype
            sql = 'SELECT id, keyword,url,user,title,keywordid from site_keywords_mobile where spidertype=%s' % spidertype
            if user:
                usql+=' and user="%s"' % user 
                sql+=' and user="%s"' % user 
            #db.do(usql)
            results = db.query(sql)
            url_len = len(results)
            urls = list()
            for result in results:
                kwh = {'wd':result[1]}
                url = 'https://m.baidu.com/s?'+urllib.urlencode(kwh)
                urls.append({'url': url, 'type': 1, 'keyword': result[1],'id':result[0],'ckurl':result[2],'pn':1,'pnum':0,'user':result[3],'title':result[4],'keywordid':result[5]})
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
            pass
        else:
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        stores.append(OutlinksSourceStore())
        self.stores = stores
        return stores

    def deal_response_results(self, request, results, stores):
        if results == 0:
            pass
        else:
            urls = list()
            failed_urls = list()
            purls=list()
            for u in request.urls:
                url = u['url']
                if url in results:
                    result=None
                    result = results[url]
                    if str(result['status']) == '2':
                        print u['url']
                        newurls = self.deal_baidu_response(u, result['result'])
                        if newurls:
                            failed_urls.append(newurls)
                        result=None
                    elif str(result['status']) == '3':
                        failed_urls.append(u)
                    else:
                        urls.append(u)
                else:
                    failed_urls.append(u)
            #if len(purls)>0:
            #    page_request = copy(request)
            #    page_request.urls = purls
            #    self.sending_queue.put(page_request)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)
            if len(failed_urls) > 0:
                new_request = copy(request)
                new_request.urls = failed_urls
                self.sending_queue.put(new_request)
                new_request = None

    def deal_baidu_response(self, url, html):
        try:
            r = self.basicExtractor.extractor(html,url['ckurl'],url['title'])
            dt = time.strftime('%Y-%m-%d %X', time.localtime())
            val = r[0]
            if int(val['response_status'])==1:
                pn = url['pn']
                num = url['pnum']
                sending_urls = list()
                newurl=None
                for t in val['rank']:
                    res=dict()
                    if url['ckurl'] and not re.search(url['ckurl'],t['domain']):
                        continue
                    res['title']=  re.sub(r'\s','',t['title'])
                    if url['title'] and not re.search(url['title'],res['title']):
                        continue
                    res['keyword'] = url['keyword']
                    res['keywordid'] = url['keywordid']
                    res['date'] =  dt
                    try:
                        res['url'] =''
                        tdomain= re.sub(r'http:\/\/','',t['domain'])
                        ts = tdomain.split('/')
                        res['url']= ts[0].strip()
                    except Exception,e:
                        res['url'] =''
                    res['srcid']=  t['srcid']
                    res['createtime']= dt
                    res['des']= re.sub(r'\s','',t['description'])
                    res['baidu_pos']= t['pos']
                    if num>0:
                        res['baidurank']= t['rank']+num+1#每页11个结果
                    else:
                        res['baidurank']= t['rank']+num
                    res['user'] = url['user']
                    self.store_queue.put({'data': res, 'type': 1, 'storeIndex': 0})
                    data=dict()
                    data['spiderstat'] = 1
                    data['id'] = url['id']
                    self.store_queue.put({'data': data, 'type': 2, 'storeIndex': 0})
                    return False
                if url['ckurl'] and pn==5:
                    nval=dict()
                    nval['baidurank']= 0
                    nval['user'] = url['user']
                    nval['baidu_pos']=0
                    nval['date'] =  dt
                    nval['keyword'] = url['keyword']
                    nval['keywordid'] = url['keywordid']
                    self.store_queue.put({'data': nval, 'type': 1, 'storeIndex': 0})
                    data=dict()
                    data['spiderstat'] = 1
                    data['id'] = url['id']
                    self.store_queue.put({'data': data, 'type': 2, 'storeIndex': 0})   
                    return False
                if pn<5:
                    pnindex = pn+1
                    pnum = pn*10
                    kwh = {'wd':url['keyword'],'pn':pnum}
                    tmpurl = 'https://m.baidu.com/s?'+urllib.urlencode(kwh)
                    newurl = {'url': tmpurl,'type': 1,'keyword': url['keyword'],'id':url['id'],'ckurl':url['ckurl'],'pn':pnindex,'pnum':pnum,'user':url['user'],'title':url['title'],'keywordid':url['keywordid']}
                    return newurl
            else:
                if url['ckurl']:
                    nval=dict()
                    nval['baidurank']= 0
                    nval['user'] = url['user']
                    nval['baidu_pos']=0
                    nval['date'] =  dt
                    nval['keyword'] = url['keyword']
                    nval['keywordid'] = url['keywordid']
                    self.store_queue.put({'data': nval, 'type': 1, 'storeIndex': 0})
                    data=dict()
                    data['spiderstat'] = 1
                    data['id'] = url['id']
                    self.store_queue.put({'data': data, 'type': 2, 'storeIndex': 0})
                return False
        except Exception,e:
            print str(e)
            return False
def Main():
    spider = EngineBasicSourceSpider()
    spider.run(30, 100, 150,100, 600, 600, 600, 600, True)

if __name__ == '__main__':
    Main()
