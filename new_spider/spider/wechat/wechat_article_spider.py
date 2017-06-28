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
from extractor.wechat.wechat_news_extractor import *
from store.wechat.wechat_public_num_store import WechatPublicNumStore
from store.wechat.wechat_article_store import WechatArticleStore
from store_mysql import StoreMysql
from util_log import UtilLogger
from util.util_url import UtilUrl
import random
from copy import copy
import traceback
reload(sys)
sys.setdefaultencoding('utf8')


class WechatArticleSpider(BaseSpiderSeparateDealAndStore):
    """
    微信公众账号及公众号文章爬虫
    爬取过程：
        初始页面：
            逻辑：从数据库中获取关键词，然后拼装成搜狗微信搜索url，进行抓取。
                  如果是按公众号进行搜索，req_type=1
                  如果是按文章进行搜索，req_type=2
        req_type=1：
            页面：搜狗微信搜索按公众号搜索结果页面，例如：http://weixin.sogou.com/weixin?type=1&query=%E6%95%99%E8%82%B2&ie=utf8&_sug_=n&_sug_type_=
            逻辑：抓取到的页面解析后得到公众号基本信息和主页url列表，
                  将公众号基本信息存入wechat_public_num表，将公众号主页url以req_type=3继续发送
            处理方法：deal_public_num_search_page_response()
        req_type=2：
            页面：搜狗微信搜索按文章搜索结果页面，例如：http://weixin.sogou.com/weixin?type=2&query=%E6%95%99%E8%82%B2&ie=utf8&_sug_=n&_sug_type_=
            逻辑：抓取到的页面解析后得到文章基本信息和url列表，
                  将文章基本信息存入wechat_news表，将文章url以req_type=4继续发送
            处理方法：deal_article_search_page_response()
        req_type=3：
            页面：公众号主页，例如：http://mp.weixin.qq.com/profile?src=3&timestamp=1475121910&ver=1&signature=t25Q6LiN8bPGFnRThNO2icxj4M*3e6V27gHkYZKyBpJ*iipKefYg4TF4pyIiBdc2eO6kiLEDfJp5tAdHGhFUQw==
            逻辑：抓取到的页面解析后得到公众号文章基本信息和url列表，
                  将文章基本信息存入wechat_news表，将文章url以req_type=4继续发送
            处理方法：deal_public_num_articles_page_response()
        req_type=4：
            页面：文章正文页面，例如：http://mp.weixin.qq.com/s?timestamp=1475121921&src=3&ver=1&signature=c5ItFtxR7LzrrRFmj1kC3OV7ERb3ghshFcuans*JYeO-d9DmnC76eR3HRkajsIhZeOh4FyefNfQLP8lK3ziJ5gClKdAB0YMiG6k*6LN5NTCHGwpbanmVksqytJusrOMeC09E-FhcMcX-Ha7LX9y4BodgB6dPqcvyePD6o0*jwO8=
            逻辑：抓取到的页面解析后得到文章正文，将文章正文存入wechat_news表相应记录中
            处理方法：deal_article_page_response()
    """

    def __init__(self):
        super(WechatArticleSpider, self).__init__()
        self.publicNumSearchPageExtractor = SougouPublicNumSearchPageExtractor()
        self.articleSearchPageExtractor = SougouArticleSearchPageExtractor()
        self.publicNumArticlesPageExtractor = SougouPublicNumArticlesPageExtractor()
        self.articleExtractor = SougouArticleExtractor()
        self.log = UtilLogger('WechatArticleSpider',
                              os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs/log_wechat_article_spider'))
        self.search_url = 'http://weixin.sogou.com/weixin'

    def get_user_password(self):
        return 'hemm', 'hmspider'

    def start_requests(self):
        try:
            self.log.info('微信公众号文章抓取程序开始启动...')
            self.log.info('开始获取初始请求...')
            db = StoreMysql(**config.NEWS_DB)
            sql = 'select keyword_id, wechat_num from wechat_public_num ' \
                  'where original_article_num > 0 order by id'
            results = db.query(sql)
            if len(results) > 0:
                left_num = len(results)
                urls = list()
                configs = {'req_type': 1, 'num_batch': 5, 'news_batch': 5, 'source': 2}
                for result in results:
                    url = self.search_url + '?type=1&query=' + result[1] + '&ie=utf8&_sug_=y&_sug_type_='
                    urls.append({'url': url, 'type': 1, 'keyword_id': result[0], 'keyword': result[1],
                                 'pages': 1, 'page': 1})
                    left_num -= 1
                    if len(urls) == 30 or left_num == 0:
                        request = SpiderRequest(headers={'User-Agent': random.choice(self.user_agents)},
                                                config=configs, urls=urls)
                        self.sending_queue.put(request)
                        urls = list()
        except Exception, e:
            self.log.error('获取初始请求出错:%s' % traceback.format_exc())

    def deal_request_results(self, request, results):
        if results == 0:
            self.log.error('请求发送失败')
        else:
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        stores.append(WechatPublicNumStore())
        stores.append(WechatArticleStore())
        return stores

    def deal_response_results(self, request, results, stores):
        if results == 0:
            self.log.error('获取结果失败')
        else:
            urls = list()
            for u in request.urls:
                url = u['url']
                if url in results:
                    result = results[url]
                    if str(result['status']) == '2':
                        configs = request.config
                        req_type = configs['req_type']
                        headers = request.headers
                        headers['Referer'] = url
                        if req_type == 1:
                            self.deal_public_num_search_page_response(u, configs, result['result'], headers)
                        elif req_type == 2:
                            self.deal_article_search_page_response(u, configs, result['result'], headers)
                        elif req_type == 3:
                            self.deal_public_num_articles_page_response(u, configs, result['result'], headers)
                        elif req_type == 4:
                            self.deal_article_page_response(u, configs, result['result'])
                    elif str(result['status']) == '3':
                        self.log.info('抓取失败:%s' % url)
                    else:
                        urls.append(u)
                else:
                    self.log.error('url发送失败:%s' % url)
            if len(urls) > 0:
                request.urls = urls
                self.sended_queue.put(request)

    def deal_public_num_search_page_response(self, url, configs, html, headers):
        r = self.publicNumSearchPageExtractor.extractor(html)
        for res in r:
            if 'items' in res:
                new_configs = copy(configs)
                new_configs['req_type'] = 3
                new_urls = list()
                for item in res['items']:
                    new_url = copy(url)
                    new_url['url'] = UtilUrl.get_url(url['url'], item['url'])
                    if configs['source'] in [2, 3, 4]:
                        if item['wechat_num'] == url['keyword']:
                            new_urls.append(new_url)
                            break
                    else:
                        new_urls.append(new_url)
                request = SpiderRequest(headers=headers, config=new_configs, urls=new_urls)
                self.sending_queue.put(request)
            if 'next_url' in res and 'pages' in url and 'page' in url \
                    and url['page'] < url['pages']:
                next_url = copy(url)
                next_url['url'] = UtilUrl.get_url(url['url'], res['next_url'])
                next_url['page'] += 1
                request = SpiderRequest(headers=headers, config=configs, urls=[next_url])
                self.sending_queue.put(request)

    def deal_article_search_page_response(self, url, configs, html, headers):
        r = self.articleSearchPageExtractor.extractor(html)
        for res in r:
            if 'items' in res:
                new_configs = copy(configs)
                new_configs['req_type'] = 4
                new_urls = list()
                for item in res['items']:
                    new_url = copy(url)
                    new_url['url'] = UtilUrl.get_url(url['url'], item['url'])
                    new_url['title'] = item['title']
                    new_url['summary'] = item['summary']
                    new_urls.append(new_url)
                request = SpiderRequest(headers=headers, config=new_configs, urls=new_urls)
                self.sending_queue.put(request)
            if 'next_url' in res and 'pages' in url and 'page' in url \
                    and url['page'] < url['pages']:
                next_url = copy(url)
                next_url['url'] = UtilUrl.get_url(url['url'], res['next_url'])
                next_url['page'] += 1
                request = SpiderRequest(headers=headers, config=configs, urls=[next_url])
                self.sending_queue.put(request)

    def deal_public_num_articles_page_response(self, url, configs, html, headers):
        r = self.publicNumArticlesPageExtractor.extractor(html)
        new_configs = copy(configs)
        new_configs['req_type'] = 4
        items = list()
        new_urls = list()
        for res in r:
            for a in res['articles']:
                new_url = copy(url)
                new_url['url'] = UtilUrl.get_url(url['url'], a['url'])
                new_url['wechat_name'] = res['wechat_name']
                new_url['wechat_num'] = res['wechat_num']
                new_url['title'] = a['title']
                new_url['summary'] = a['summary']
                new_urls.append(new_url)
            del res['articles']
            res['qr_code'] = UtilUrl.get_url(url['url'], res['qr_code'])
            res['keyword_id'] = url['keyword_id']
            res['batch'] = configs['num_batch']
            items.append(res)
        if len(new_urls) > 0:
            request = SpiderRequest(headers=headers, config=new_configs, urls=new_urls)
            self.sending_queue.put(request)
        if len(items) > 0:
            self.store_queue.put({'data': items, 'type': 1, 'storeIndex': 0})

    def deal_article_page_response(self, url, configs, html):
        r = self.articleExtractor.extractor(html)
        items = list()
        for res in r:
            if 'wechat_num' in url and len(url['wechat_num']) > 0:
                res['wechat_num'] = url['wechat_num']
            if 'wechat_num' not in res or len(res['wechat_num']) == 0:
                continue
            if 'wechat_name' in url:
                res['wechat_name'] = url['wechat_name']
            res['keyword_id'] = url['keyword_id']
            res['keyword'] = url['keyword']
            res['title'] = url['title']
            res['summary'] = url['summary']
            res['url'] = url['url']
            res['batch'] = configs['news_batch']
            items.append(res)
        self.store_queue.put({'data': items, 'type': 1, 'storeIndex': 1})

    def to_store_results(self, results, stores):
        stores[results['storeIndex']].store(results['data'], results['type'])

def Main():
    spider = WechatArticleSpider()
    spider.run(2, 20, 150, 20, 600, 600, 600, 600, True)

if __name__ == '__main__':
    Main()