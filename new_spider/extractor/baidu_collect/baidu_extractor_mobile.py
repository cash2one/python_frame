# -*- coding: utf8 -*-
import json
import os
import re
import sys
import traceback

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
from spider.spider import SpiderExtractor
from sx_util.http_url_utils import HttpUrlUtils
from util.domain_urllib import SeoDomain
reload(sys)
sys.setdefaultencoding('utf8')

# from lxml import etree
from lxml.html import fromstring

class BaiduSpiderExtractorMobile(SpiderExtractor):

    def __init__(self):
        super(BaiduSpiderExtractorMobile, self).__init__()
        self.url_util = HttpUrlUtils()
        self.sx_FindDomain = SeoDomain()
        # self.find_realaddress = GetReal_Address()

    # 获取标签下所有中文
    def getText(self, elem):
        rc = []
        for node in elem.itertext():
            rc.append(node.strip())
        return ''.join(rc)

    '''
        返回 0:　没有数据


    '''
    def extractor_baidu_mobile_lxml(self, body, ck='', pcount=0, spidertype = 1):
        # 相关搜索
        pos = body.find("</html>")
        if pos < 0:
            return 0
        else:
            try:
                tree = fromstring(body)
                containers = tree.cssselect('div.c-result')
                if len(containers) > 0:
                    rank_result_list = list()
                    for container in containers:
                        toprank = ""
                        title = ''
                        des = ''  # 描述
                        evaluate = ""  # 评价
                        realaddress = ""
                        domain = ""
                        searchState = 0
                        srcid = ""
                        mu_url = ""

                        order = int(container.get('order'))
                        try:
                            srcid = container.get('new_srcid')
                        except:
                            srcid = ""

                        if order:
                            toprank = order + int(pcount)
                        titles = container.cssselect("h3")
                        if len(titles) > 0:
                            title = self.getText(titles[0]).replace(unicode("举报图片"), "").strip()
                            # title = titles[0].get_text().replace(unicode("举报图片"), "").strip()
                        # des_list = container.find_all("div", {"class": "wz-generalmaphotel-mapc-gap-top"})
                        des_list = container.cssselect("div.wz-generalmaphotel-mapc-gap-top")
                        if len(des_list) > 0:
                            des = 'map'
                            domain = 'map.baidu.com'
                        elif str(self.getText(container)).find(u'百度百科') > 0:
                            des = 'baike.baidu.com'
                            domain = 'baike.baidu.com'
                        else:
                            des_list_two = container.cssselect("p")
                            if len(des_list_two) > 0:
                                des = self.getText(des_list_two[0]).strip()

                        # evaluate_list = container.find_all("span", {"class": "c-pingjia"})
                        # if len(evaluate_list) > 0:
                        #     evaluate = evaluate_list[0].get_text().strip()

                        domain_list = container.cssselect("a.c-showurl")
                        if len(domain_list) > 0:
                            domain = self.getText(domain_list[0]).strip()
                            # domain = domain_list[0].get_text().strip()
                        else:
                            domain_list = container.cssselect("span.c-showurl")
                            if len(domain_list) > 0:
                                domain = self.getText(domain_list[0]).strip()
                                # domain = domain_list[0].get_text().strip()
                        datalog = container.get('data-log')
                        if datalog:
                            try:
                                datalog = str(datalog).replace("\'", "\"")
                                sx_data = json.loads(datalog)
                                mu_url = sx_data["mu"]
                            except:
                                mu_url = ""

                        if domain == '' and re.search(u'百度手机助手', title) > 0:
                            domain = 'mobile.baidu.com'
                        if domain == '' and re.search(u'_相关信息', title) > 0:
                            domain = 'm.baidu.com'
                        if domain == '' and re.search(u'_相关网站', title) > 0:
                            domain = 'm.baidu.com'
                        if domain == '' and re.search(u'_百度糯米', title) > 0:
                            domain = 'nuomi.baidu.com'

                        item = dict()
                        item['domain'] = domain
                        item['srcid'] = srcid
                        # item['pos'] = pos
                        item['rank'] = toprank
                        item['title'] = title
                        item['description'] = des
                        item['realaddress'] = mu_url

                        # print domain
                        # print toprank
                        # print title
                        # print des
                        # print mu_url
                        rank_result_list.append(item)
                    return rank_result_list
                else:
                    return 0
            except Exception:
                print traceback.format_exc()
                return 2
        return 2

if __name__ == '__main__':
    pass
    f = open("mobile.txt", "rb")
    content = f.read()
    f.close()
    spider = BaiduSpiderExtractorMobile()
    import time
    start_time = time.time()
    sx = spider.extractor_baidu_mobile(content, ck='http://m.zhaopin.com/', spidertype= 2)
    end_time = time.time()
    print end_time - start_time
    print sx