# -*- coding: utf8 -*-
import os
import sys

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
sys.path.append(os.path.join(PROJECT_PATH, 'store'))
sys.path.append(os.path.join(PROJECT_PATH, 'util'))
from spider.basespider_separate_deal_and_store import BaseSpiderSeparateDealAndStore
from downloader.downloader import SpiderRequest

from extractor.baidu.baidu_pc_rank_extractor2 import BaiduPcRankExtractor
from extractor.baidu.baidu_mobile_rank_extractor2 import BaiduMobileRankExtractor

from store.baidu.baidu_pc import OutlinksSourceStore
from util.util_useragent import UtilUseragent
import random
import time
import urllib
from copy import copy

reload(sys)
sys.setdefaultencoding('utf8')
from util_log import UtilLogger
from sx_util.InsideSystem import InsideSystem
import json
import base64
from store_mysql import StoreMysql
from datetime import datetime
from spider import config

from spider.basespider_sx import BaseSpider_sx

class PullDownBasicSourceSpider(BaseSpider_sx):

    def __init__(self):
        super(PullDownBasicSourceSpider, self).__init__()
        self.basicPcExtractor = BaiduPcRankExtractor()
        self.basicMobileExtractor = BaiduMobileRankExtractor()
        # 定时休眠时间  分钟
        # self.difsecond = 60*60*24
        self.difsecond = 60 * 60 * 24
        self.userpc_agents = UtilUseragent.get(type='PC')
        self.usermobile_agents = UtilUseragent.get(type='MOBILE')
        self.inside_Interfice = InsideSystem()
        self.log = UtilLogger('EngineBasicSourceSpider',
                              os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_sxPcSourceSpider'))
        self.saveport = 2

    def get_user_password(self):
        # return 'sunxiang', 'sxspider'
        return 'test', 'test'

    # def get_downloader(self):
        #     """
        #     设置下载器类型，默认为Downloader
        #     Return:
        #         SpiderDownloader
        #     """
        # return Downloader(set_mode='db', get_mode='db')
        # return HtmlLocalDownloader(set_mode='http', get_mode='http')

    def start_requests(self):
        try:
            while True:
                time_now = str(datetime.today())
                print time_now
                time_now = time_now.split(" ")
                time_str = time_now[1]
                time_index = time_str.index(":")
                time_point = int(time_str[0:time_index]) # 当前整点数
                if time_point == 0:
                    db = StoreMysql(**config.insideSystem_DB)
                    sql = "select keyword,keywordid,searchDevice,saveport,returnType,targetKeywords from keywordrank.site_keywords " \
                          "where   starttime <= now() and endtime >= date(now()) and searchRegular =1 and searchType = 2 and saveport = %d" % self.saveport

                    results = db.query(sql)
                    if db is not None:
                        db.close()
                    print "spider length:"+str(len(results))
                    db.close()
                    resultCount = len(results)
                    for index in xrange(0, resultCount):
                        result = results[index]
                        urls = list()
                        sxitem = {"keyword": result[0], "searchDevice": result[2],
                                  "returnType": result[4], "targetKeywords": result[5]}

                        sxjson = json.dumps(sxitem)
                        urls.append({'url': sxjson, 'type': 6, 'keyword': result[0],
                                     'keywordid': result[1], 'searchDevice': result[2], 'searchCount': 1,
                                      'unique_key': index, 'saveport': result[3], "returnType": result[4]})
                        basic_request = SpiderRequest(urls=urls)
                        self.sending_queue.put(basic_request)
                    time.sleep(self.difsecond)
                else:
                    time.sleep(30*60)

                # urls = list()
                # sxitem = {"keyword": "兰博基尼", "searchDevice": "2",
                #           "returnType": "0011", "targetKeywords": "官网,车型,报价,图片,Veneno"}
                # sxjson = json.dumps(sxitem)
                #
                # urls.append({'url': sxjson, 'type': 6, 'keyword': "兰博基尼",
                #              'keywordid': "310", 'searchDevice': "2",
                #              'unique_key': 1, 'saveport': "1", "returnType": "0011"})
                # basic_request = SpiderRequest(urls=urls)
                # self.sending_queue.put(basic_request)
                # time.sleep(1000)

        except Exception, e:
            print str(e)

    def deal_request_results(self, request, results):
        if results == 0:
            self.log.error('参数异常 请求发送失败 urls: %s' % request.urls)
        elif results == -2:
            self.log.error('没有相应地域 urls: %s' % request.urls)
        elif results == -1:
            self.log.error("向数据库 添加任务失败  设置request 失败  urls: %s" % request.urls)
            self.sended_queue.put(request)
        else:
            # print "send one request"
            self.sended_queue.put(request)

    def get_stores(self):
        stores = list()
        # stores.append(OutlinksSourceStore())
        # self.stores = stores
        return stores

    def deal_response_results(self, request, results, stores):
        if results == 0:
            return False
        else:
            urls = list()
            failed_urls = list()
            purls = list()
            for u in request.urls:
                # url = u['url']
                url = u['unique_md5']
                if url in results:
                    result = None
                    result = results[url]
                    if str(result['status']) == '2':
                        state = self.deal_baidu_response(u, result['result'])
                        if state:
                            response_search_count = int(u['searchCount'])
                            if response_search_count < 3:
                                self.log.info("return is -1  url:%s" % u)
                                send_list = list()
                                u['searchCount'] = response_search_count + 1
                                send_list.append(u)
                                basic_request = SpiderRequest(urls=send_list)
                                self.sending_queue.put(basic_request)
                            else:
                                print "keywordid:" + str(u["keywordid"]) + ";tempIndex:" + str(-1)
                                # self.sendNorank(u["keywordid"], -1, u['saveport'])

                                send_list = [{"keywordid": u["keywordid"], "rank": -1, "imgData": ""}]
                                send_data = json.dumps(send_list)
                                self.inside_Interfice.send_InsideSystem(send_data, u['saveport'])

                    elif str(result['status']) == '3':
                        if "searchCount" in u:
                            response_searchCount = int(u['searchCount'])
                            if response_searchCount < 3:
                                print "inside_pc_baidurank deal_response_results status ==3" + u['url']
                                send_list = list()
                                new_request = copy(request)
                                u['searchCount'] = response_searchCount + 1
                                send_list.append(u)
                                basic_request = SpiderRequest(urls=send_list)
                                self.sending_queue.put(basic_request)
                                del new_request
                                del send_list
                            else:
                                print """result['status']) == '3' exception rank:-1"""
                                self.sendNorank(u["keywordid"], -1, u['saveport'])
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
                del new_request

    def deal_baidu_response(self, url, imagedata_html):
        # print str(datetime.today())
        if len(imagedata_html) < 10:
            return True

        else:
            pictureDataDict = self.transformData_pullDown(imagedata_html, url["returnType"])
            rankIndex = pictureDataDict["rankIndex"]
            tempIndex = 15
            if len(rankIndex) > 0:
                for index in rankIndex:
                    if tempIndex > index["rank"]:
                        tempIndex = index["rank"]
                # print "tempIndex:"+str(tempIndex)
            else:
                tempIndex = -2

            print "keywordid:"+str(url["keywordid"])+";tempIndex:"+str(tempIndex)
            send_list = [{"keywordid": url["keywordid"], "rank": tempIndex, "imgData": pictureDataDict["returnData"]}]
            send_data = json.dumps(send_list)
        self.inside_Interfice.send_InsideSystem(send_data, url['saveport'])

    def transformData_pullDown(self, imagedata_html, returnType):
        transformDataDict = {}
        imagedata_htmlLoads = json.loads(imagedata_html)
        returnData = {}
        if int(returnType[0:1]) == 1:
            returnData["capture"] = imagedata_htmlLoads["capture"]
        else:
            returnData["capture"] = ""
        if int(returnType[2:3]) == 1:
            returnData["capture_red"] = imagedata_htmlLoads["capture_red"]
            # sxcapture = base64.b64decode(imagedata_htmlLoads["capture_red"])
            # file = open("%dcapture_red.png" % 1, "wb")
            # file.write(sxcapture)
            # file.close()
        else:
            returnData["capture_red"] = ""
        if int(returnType[1:2]) == 1:
            returnData["screenshot"] = imagedata_htmlLoads["screenshot"]

        else:
            returnData["screenshot"] = ""
        if int(returnType[3:4]) == 1:
            returnData["screenshot_red"] = imagedata_htmlLoads["screenshot_red"]

        else:
            returnData["screenshot_red"] = ""
        transformDataDict["returnData"] = json.dumps(returnData)
        transformDataDict["rankIndex"] = imagedata_htmlLoads["rankIndex"]
        return transformDataDict

    def to_store_results(self, results, stores):
        time.sleep(60 * 30)
        pass

    def sendNorank(self, keywordid, rank, saveport):
        print "keywordid:"+str(keywordid)+";rank:"+str(rank)
        send_list = [{"keywordid": keywordid, "imgData": "", "rank": -2, "show_url": "", "real_address": ""}]
        send_data = json.dumps(send_list)
        self.inside_Interfice.send_InsideSystem(send_data, saveport)

def Main():
    spider = PullDownBasicSourceSpider()
    print ('抓取程序开始启动...')
    spider.run(10, 20, 20, 1, 600, 600, 600, 600, False)
    # spider = EngineBasicSourceSpider()

if __name__ == '__main__':
    Main()
