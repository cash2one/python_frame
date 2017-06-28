# -*- coding: utf8 -*-
import os
import sys
import random
import time
import urllib
from copy import copy
from datetime import datetime
import traceback
import json

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
sys.path.append(os.path.join(PROJECT_PATH, 'store'))
sys.path.append(os.path.join(PROJECT_PATH, 'util'))

reload(sys)
sys.setdefaultencoding('utf8')

from spider import config
from spider.basespider_sx import BaseSpider_sx
from downloader.downloader import SpiderRequest
from extractor.baidu.baidu_pc_rank_extractor2 import BaiduPcRankExtractor
from extractor.baidu.baidu_mobile_rank_extractor2 import BaiduMobileRankExtractor
from sx_util.InsideSystem import InsideSystem
from util_log import UtilLogger
from util.util_useragent import UtilUseragent
from store_mysql import StoreMysql
from threading import Thread

class BaiduRankSourceSpider(BaseSpider_sx):
    '''
    内部系统排名
    '''
    def __init__(self):
        super(BaiduRankSourceSpider, self).__init__()
        self.basicPcExtractor = BaiduPcRankExtractor()
        self.basicMobileExtractor = BaiduMobileRankExtractor()
        # 定时休眠时间  分钟
        self.difsecond = 60 * 60 * 24
        self.userpc_agents = UtilUseragent.get(type='PC')
        self.usermobile_agents = UtilUseragent.get(type='MOBILE')
        self.inside_Interfice = InsideSystem()
        self.log = UtilLogger('BaiduRankSourceSpider',
                              os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_BaiduRankSourceSpider'))
        self.log_record = UtilLogger('log_record_SourceSpider',
                              os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_record_SourceSpider'))
        self.saveport = 2

    def get_user_password(self):
        # return 'sunxiang', 'sxspider'
        return 'test', 'test'

    def deal_request_results(self, request, results):
        if results == 0:
            self.log.error('参数异常 请求发送失败 urls: %s' % request.urls)
        elif results == -2:
            self.log.error('没有相应地域 urls: %s' % request.urls)
        elif results == -1:
            self.log.error("向数据库 添加任务失败  设置request 失败  urls: %s" % request.urls)
            self.sended_queue.put(request)
        else:
            self.sended_queue.put(request)

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
                if time_point > 0:
                    db = StoreMysql(**config.insideSystem_DB)
                    # sql = "select keyword,url,spidertype,keywordid,searchDevice,saveport,returnType from keywordrank.site_keywords " \
                    #       "where  starttime <= now() and endtime >= date(now()) and searchRegular =1 and searchType = 1 and saveport = %d order by priority desc" % self.saveport

                    sql = "select keyword,url,spidertype,keywordid,searchDevice,saveport,returnType from keywordrank.site_keywords " \
                          "where  starttime <= now() and endtime >= date(now()) and searchRegular =1 and searchType = 1 and saveport = %d " \
                          " and keywordid in (11682,11688,10943,11517,4011,7885,4010,10944,11471,11486,1320,1322,1328,1329,1330,1331,1332,1333,1334,1335,1336,1337,1338,1339,1340,1341,1342,1343,1346,1347,1400,1403,1405,1410,1419,1421,1422,1708,1709,1710,1711,1712,1713,1714,1715,1716,1717,1718,1719,1720,1721,1722,1723,1724,1725,1726,1727,1728,1729,1730,1731,1732,1733,1734,1735,1736,1737,1738,1739,1740,1741,1742,1743,1744,1745,1746,1747,1748,1749,1750,1751,1752,1753,1754,1755,1756,1757,1758,1759,7887,10945,11507,1856,2998,1857,1858,1859,1860,1861,1862,1863,1864,1865,1866,1867,1868,1869,1870,11158,3000,3002,3004,3005,3010,3011,3014,3015,3016,3192,3193,3194,3195,3196,3197,3198,3199,3200,3201,3202,3203,3204,3205,3206,3207,3208,3209,3210,3211,3212,3213,3214,3215,3216,3217,3218,3219,3220,3221,3222,3223,3224,3225,3226,3227,3228,3229,3230,3231,3232,3233,3234,3235,3236,3237,3238,3239,3240,3241,3242,3243,3244,3245,3246,3247,3248,3249,3250,3251,3252,3253,3254,3255,3256,3257,3258,3259,3260,3261,3262,3263,3266,3270,3277,3279,3282,3286,3448,3449,3450,3451,3452,3453,3454,3455,3456,3457,3458,3459,3460,3461,3462,3463,3464,3465,3466,3467,3468,3469,3470,3471,3472,3473,3474,3475,3476,3477,3478,3479,3480,3481,3482,3483,3484,3485,3486,3487,3488,3489,3490,3491,3492,3493,3494,3495,3496,3497,3498,3499,3500,3501,3502,3503,3504,3505,3506,3507,3508,3509,3510,3511,3512,3513,3514,3515,3516,3517,3518,3519,3529,3533,3534,3536,3539,3541,3545,3548,3549,3704,3705,3706,3707,3708,3709,3710,3711,3712,3713,3714,3715,3716,3717,3718,3719,3720,3721,3722,3723,3724,3725,3726,3727,3728,3729,3730,3731,3732,3733,3734,3735,3736,3737,3738,3739,3740,3741,3742,3743,3744,3745,3746,3747,3748,3749,3750,3751,3752,3753,3754,3755,3756,3757,3758,3759,3760,3761,3762,3763,3764,3765,3766,3767,3768,3769,3770,3771,3772,3773,3774,3775,3778,3783,3784,3785,3786,3787,3788,3793,3796,3798,3799,3800,3802,7900,7889,10185,10259,11519,9919,10255,11525,11520,11518,11514,10160,10163,10164,10187,11472,11481,11492,10326,11479,11523,11487,10170,10171,10172,10173,10174,10175,10176,10177,10178,10179,10180,10181,10182,10183,10184,10324,10186,10188,10189,10190,10191,10192,10193,10194,10195,10198,10203,10204,10206,10207,10208,10209,10210,10212,10213,10220,10222,10223,10470,10471,10472,10473,10474,10475,10476,10477,10478,10505,10479,10480,10481,10482,10483,10484,10485,10486,10487,10488,10489,10490,10491,10492,10493,10494,10495,10496,10497,10498,10499,10500,10501,10502,10503,10504,10506,10508,10509,10510,10512,10513,10514,10515,10516,10517,10518,10519,10520,10521,10522,10523,10524,10525,10526,10527,10528,10529,10530,10531,10532,10533,10534,10535,10536,10537,10538,10539,10540,10541,10542,10546,10553,10556,10558,10564,10569,10570,10572,11488,11501,10820,10821,10822,10823,10824,10825,10826,10827,10828,10829,10830,10831,10832,10833,10834,10835,10836,10837,10838,10839,10840,10841,10842,10843,10844,10845,10846,10847,10848,10851,10855,10858,10860,10861,10863,10864,10865,10866,10869,10870,10872,10876,11044,11045,11046,11047,11048,11049,11050,11051,11052,11053,11054,11055,11056,11057,11058,11059,11528,11060,11061,11062,11063,11064,11065,11066,11067,11068,11069,11070,11071,11072,11073,11074,11075,11076,11077,11078,11079,11080,11081,11082,11083,11084,11085,11086,11087,11088,11089,11090,11091,11092,11093,11094,11095,11096,11097,11098,11099,11100,11101,11102,11103,11104,11105,11106,11107,11108,11109,11110,11111,11112,11113,11121,11122,11124,11129,11135,11144,11300,11301,11302,11303,11304,11305,11306,11307,11308,11309,11310,11311,11312,11313,11314,11315,11316,11317,11318,11319,11320,11321,11322,11323,11324,11325,11326,11327,11328,11329,11330,11331,11332,11333,11334,11335,11336,11337,11338,11339,11340,11341,11342,11343,11344,11345,11346,11347,11348,11349,11350,11351,11352,11353,11354,11355,11356,11357,11358,11359,11360,11361,11362,11363,11364,11365,11366,11367,11368,11369,11370,11371,11378,11381,11382,11383,11385,11390,11395,11403,11683,11684,11685,11686,11687,11717,11703,11689,11690,11691,11692,11693,11694,11695,11696,11697,11698,11699,11700,11701,11702,11704,11705,11706,11707,11708,11720,11882,11883,11884,11885,11886,11887,11888,11889,11890,11891,11892,11893,11894,11895,11896,11897,11898,11899,11900,11901,11902,11903,11904,11905,11906,11907,11908) order by priority desc" % self.saveport

                    results = db.query(sql)
                    print "spider length:"+str(len(results))
                    db.close()
                    resultCount = len(results)
                    for index in xrange(0, resultCount):
                        result = results[index]
                        urls = list()
                        sxitem = {"keyword": result[0], "ckurl": result[1], "searchDevice": result[4],
                                  "spidertype": result[2], "searchPage": 5, "returnType": result[6]}

                        sxjson = json.dumps(sxitem)
                        urls.append({'url': sxjson, 'type': 5, 'keyword': result[0], 'ckurl': result[1],
                                     'keywordid': result[3], 'rn': '1', 'pnum': '0', 'spidertype': result[2],
                                     'searchDevice': result[4], 'unique_key': index, 'searchCount': 1,
                                     'saveport': result[5], "returnType": result[6]})
                        basic_request = SpiderRequest(headers={'User-Agent': random.choice(self.userpc_agents)
                                         if result[4] == 1 else random.choice(self.usermobile_agents)}, urls=urls)
                        self.sending_queue.put(basic_request)
                    time.sleep(self.difsecond)
                else:
                    time.sleep(30*60)
        except Exception:
            self.log.info(traceback.format_exc())

    def get_stores(self):
        stores = list()
        # stores.append(OutlinksSourceStore())
        # self.stores = stores
        return stores

    def deal_response_results_sxself(self, request, url, result):
        if str(result['status']) == '2':
            state = self.deal_baidu_response(url, result['result'])
            send_list = list()
            if state == -1:
                response_search_count = int(url['searchCount'])
                if response_search_count < 4:
                    self.log.info("return is -1  url:%s" % url)

                    new_request = copy(request)
                    url['searchCount'] = response_search_count + 1
                    send_list.append(url)

                    retry_config = {"priority": 3}
                    basic_request = SpiderRequest(urls=send_list, config=retry_config)
                    self.sending_queue.put(basic_request)
                    del new_request
                    del send_list
                else:
                    self.sendNorank(url["keywordid"], -1, url['saveport'])

            if state == -2:
                # self.log.info("return is -2  url:%s" % url["url"])
                # send_list.append(url)
                # basic_request = SpiderRequest(urls=send_list)
                # self.sending_queue.put(basic_request)

                response_search_count = int(url['searchCount'])
                if response_search_count < 3:
                    self.log.info("return is -2  url:%s" % url["url"])
                    # retry_config = {"priority": 3}
                    send_list = list()
                    url['searchCount'] = response_search_count + 1
                    send_list.append(url)
                    basic_request = SpiderRequest(urls=send_list)
                    self.sending_queue.put(basic_request)
                else:
                    self.sendNorank(url["keywordid"], -2, url['saveport'])

        elif str(result['status']) == '3':
            # 根据情况做处理
            self.log.info('抓取失败:%s' % url)
            response_search_count = int(url['searchCount'])
            if response_search_count < 3:
                self.log.info("response_searchCount<3  url:%s" % url)
                print "inside_pc_baidurank deal_response_results status ==3" + url['url']
                send_list = list()
                new_request = copy(request)
                url['searchCount'] = response_search_count + 1
                send_list.append(url)
                basic_request = SpiderRequest(urls=send_list)
                self.sending_queue.put(basic_request)
                del new_request
                del send_list
            else:
                print """result['status']) == '3' exception rank:-1"""
                self.sendNorank(url["keywordid"], -1, url['saveport'])

    '''
        无论有没有排名 数据都会存到结果表
        type = 1  存到结果表
        type = 2 更新任务表 ，表明 已经 查询结束
    '''
    def deal_baidu_response(self, url, imagedata_html):
        if imagedata_html == "-1":
            return -1
        if imagedata_html == "-2":
            self.sendNorank(url["keywordid"], -2, url['saveport'])
            return -2
        pictureDataDict = self.transformData(imagedata_html, url["returnType"])

        send_list = [{"keywordid": url["keywordid"], "rank": pictureDataDict["rank"],
                     "show_url": pictureDataDict["show_url"],
                     'real_address': pictureDataDict["real_address"], "imgData": pictureDataDict["returnData"]}]
        send_data = json.dumps(send_list)
        self.log_record.info("pc keywordid:" + str(url["keywordid"]) + ";pc rank:" + str(pictureDataDict["rank"]) + ";realaddress:" + pictureDataDict["real_address"])
        self.inside_Interfice.send_InsideSystem(send_data, url['saveport'])

    def transformData(self, imagedata_html, returnType):
        transformDataDict = {}
        imagedata_htmlLoads = json.loads(imagedata_html)
        returnData = {}
        if int(returnType[0:1]) == 1:
            returnData["capture"] = imagedata_htmlLoads["capture"]
        else:
            returnData["capture"] = ""
        if int(returnType[2:3]) == 1:
            returnData["capture_red"] = imagedata_htmlLoads["capture_red"]
        else:
            returnData["capture_red"] = ""
        if int(returnType[1:2]) == 1:
            returnData["screenshot"] = imagedata_htmlLoads["screenshot"]
        else:
            returnData["screenshot"] = ""
        if int(returnType[3:4]) == 1:
            returnData["screenshot_red"] = imagedata_htmlLoads["screenshot_red"]
            # sxcapture = base64.b64decode(imagedata_htmlLoads["screenshot_red"])
            # file = open("%sscreenshot_red.png" % 1, "wb")
            # file.write(sxcapture)
            # file.close()
        else:
            returnData["screenshot_red"] = ""
        transformDataDict["returnData"] = json.dumps(returnData)
        # transformDataDict["html"] = imagedata_htmlLoads["html"]
        # transformDataDict["page"] = imagedata_htmlLoads["page"]
        transformDataDict["rank"] = imagedata_htmlLoads["rank"]
        transformDataDict["show_url"] = imagedata_htmlLoads["show_url"]
        transformDataDict["real_address"] = imagedata_htmlLoads["real_address"]
        return transformDataDict

    def to_store_results(self, results, stores):
        time.sleep(60*30)
        pass

    def sendNorank(self, keywordid, rank, saveport):
        self.log_record.info("keywordid:"+str(keywordid)+";rank:"+str(rank))
        send_list = [{"keywordid": keywordid, "imgData": "", "rank": rank, "show_url": "", "real_address": ""}]
        send_data = json.dumps(send_list)
        self.inside_Interfice.send_InsideSystem(send_data, saveport)

    def timed_cleanup(self):
        try:
            while True:
                # 晚上十点 清空数据
                if self.integer_point == 22:
                    for i in xrange(0, self.response_queue.qsize()):
                        try:
                            response_result = self.response_queue.get_nowait()
                        except:
                            continue
                    for i in xrange(0, self.sended_queue.qsize()):
                        try:
                            sended_result = self.sended_queue.get_nowait()
                        except:
                            continue

                    db = StoreMysql(**config.DOWNLOADER_CENTER_DB)
                    sql = "delete from urls_7;"
                    results = db.do(sql)
                    print "timed_cleanup:%s" % str(datetime.today())
                    db.close()
                    time.sleep(60 * 60)
                else:
                    time.sleep(60 * 30)
        except:
            print traceback.format_exc()

    def run(self, send_num=1, get_num=1, deal_num=1, store_num=1, send_idle_time=600,
            get_idle_time=600, deal_idle_time=600, store_idle_time=600, record_log=False):
        """
        爬虫启动入口
        Args:
            send_num:发送请求线程数，默认为1
            get_num:获取结果线程数，默认为1
            deal_num:处理结果线程数，默认为1
            store_num:存储结果线程数，默认为1
            send_idle_time:发送请求线程超过该时间没有要发送的请求就停止
            get_idle_time:获取结果线程超过该时间没有要获取的结果就停止
            deal_idle_time:处理结果线程超过该时间没有要处理的结果就停止
            store_idle_time:存储结果线程超过该时间没有要存储的结果就停止
            record_log:定时记录各个队列大小，便于分析抓取效率
        """
        self.validate_user()
        # self.start_requests()
        threads = list()
        threads.append(Thread(target=self.start_requests))

        threads.append(Thread(target=self.timed_cleanup))

        for i in range(0, send_num):
            threads.append(Thread(target=self.send_requests, args=(send_idle_time,)))
        for i in range(0, get_num):
            threads.append(Thread(target=self.get_response, args=(get_idle_time,)))
        for i in range(0, deal_num):
            threads.append(Thread(target=self.deal_response, args=(deal_idle_time,)))
        for i in range(0, store_num):
            threads.append(Thread(target=self.store_results, args=(store_idle_time,)))
        if record_log:
            threads.append(Thread(target=self.record_log))
        for thread in threads:
            thread.start()

    def integer_point(self):
        # 获取当前整点
        time_now = str(datetime.today())
        start_index = time_now.find(" ")
        end_index = time_now.find(":")
        time_point = int(time_now[start_index + 1: end_index])  # 当前整点数
        return time_point

def Main():
    spider = BaiduRankSourceSpider()
    print ('抓取程序开始启动...')
    spider.run(10, 20, 20, 0, 600, 600, 600, 600, False)
    # spider.timed_cleanup()

if __name__ == '__main__':
    Main()