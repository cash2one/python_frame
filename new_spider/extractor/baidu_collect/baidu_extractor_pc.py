# -*- coding: utf8 -*-
import sys
import re
import os
import traceback
from bs4 import BeautifulSoup
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
from spider.spider import SpiderExtractor
# from downloader.util_getRealAddress import GetReal_Address
# from util.domain_urllib import SeoDomain
# from sx_util.http_url_utils import HttpUrlUtils
reload(sys)
sys.setdefaultencoding('utf8')

# from lxml import etree
from lxml.html import fromstring

class BaiduSpiderExtractorPc(SpiderExtractor):

    def __init__(self):
        super(BaiduSpiderExtractorPc, self).__init__()
        # self.find_realaddress = GetReal_Address()
        # self.url_util = HttpUrlUtils()
        # self.sx_FindDomain = SeoDomain()

    '''
     获取pc排名数据
     response_status 0请求失败 1 请求成功 2 页面不全，封ip
     百度关键词列表页数据
        返回 页面所有内容
        2 ： 页面异常 或 不全
        0：没有数据

    brand_area   品牌专区  h2 有两个
    brand_website  官网  a 两个 内容 全匹配 官网
     '''
    def extractor_baidu_pc_lxml(self, body):
        result = dict()
        pos = body.find("</html>")
        if pos < 0 or body.find('location.href.replace') >= 0:
            return 2
        elif body.find('id="wrap"') >= 0 or body.find('<title>') < 0 or body.find('页面不存在_百度搜索') >= 0 \
                or body.find('id="container"') < 0 or body.find('id="content_left"') < 0:
            return 0
        else:
            try:
                tree = fromstring(body) # 这种方式 可使用cssselect  不然linux 不能使用
                containers = tree.cssselect('div.c-container')  # *行代码

                h2s = tree.cssselect("h2")
                if len(h2s) == 2:
                    # 品牌专区
                    for h2 in h2s:
                        if self.getText(h2).find(u"基本资料") > -1:
                            result["brand_area"] = 0
                            break
                        result["brand_area"] = 1
                # 品牌专区
                # brand_list = list()
                # for h2 in h2s:
                #     brand_list.append(self.getText(h2))
                #     # print self.getText(h2)
                # result["brand_list"] = brand_list

                if len(containers) > 0:
                    rank_result_list = list()
                    for container in containers:
                        toprank = 0
                        title = ''
                        des = ''  # 描述
                        evaluate = ""  # 评价
                        realaddress = ""
                        domain = ""
                        search_state = 0
                        baidu_href = list()

                        # find_realaddress_state = 0  # 是否需要获取真实url 0：默认不获取真实url, 1：获取真实url
                        # is_get_realaddress = 0  # 判断是否获取真实url

                        toprank = int(container.get('id'))
                        # 标题
                        # titles = container.cssselect("h3")
                        # if titles:
                        #     title = str(self.getText(titles[0])).encode("utf-8").replace(unicode("举报图片"), "").strip()

                        titles = container.cssselect("h3.t>a")
                        if len(titles) > 0:
                            title = str(self.getText(titles[0])).encode("utf-8").replace(unicode("举报图片"), "").strip()
                            if len(titles) == 2:
                                # print self.getText(titles[1])
                                # 官网
                                if self.getText(titles[1]) == u"官网":
                                    result["brand_website"] = 1

                        # 内容
                        des_list = container.cssselect("div.c-abstract")
                        if len(des_list) > 0:
                            des = self.getText(des_list[0])
                        else:
                            des_list_two = container.cssselect("div.c-span18c-span-last")
                            if len(des_list_two) > 0:
                                des = self.getText(des_list[0])
                        realaddress_list = container.cssselect("a")
                        if len(realaddress_list) > 0:
                            realaddress = realaddress_list[0].get("href")
                        # domain 显示url
                        domain_list = container.cssselect("a.c-showurl")
                        if len(domain_list) > 0:
                            domain = self.getText(domain_list[0]).strip()
                        else:
                            domain_list = container.cssselect("span.c-showurl")
                            if len(domain_list) > 0:
                                domain = self.getText(domain_list[0]).strip()

                        if domain == "":
                            domain_list = container.cssselect("div.g")
                            if len(domain_list) > 0:
                                domain = domain_list[0].text.strip()
                        if domain == "":
                            domain_list = container.cssselect("span.g")
                            if len(domain_list) > 0:
                                domain = domain_list[0].text.strip()

                        domain = self.remove_special_characters(domain)
                        if domain == "":
                            alist = container.cssselect("a")
                            if alist:
                                for ahref in alist:
                                    try:
                                        href = ahref.get("href")
                                        baidu_href.append(href)
                                    except Exception:
                                        continue
                        # if domain == "":
                        #     domain = "baike.baidu.com"

                        if title.find(u"的最新相关信息") > -1:
                            domain = "baidu"

                        item = dict()
                        item['domain'] = domain
                        item['rank'] = toprank
                        item['title'] = title
                        item['description'] = des
                        item['realaddress'] = realaddress

                        if len(baidu_href) > 0:

                            item["baidu_href"] = baidu_href
                        rank_result_list.append(item)
                    result["rank_result_list"] = rank_result_list
                    return result
                else:
                    return 0
            except Exception:
                print traceback.format_exc()
                return 2
        return 2

    # 获取标签下所有中文
    def getText(self, elem):
        rc = []
        for node in elem.itertext():
            rc.append(node.strip())
        return ''.join(rc)

    def removeCharacters(self, previou_url):
        if previou_url.startswith("https://"):
            previou_url = previou_url.replace("https://", "")
        if previou_url.startswith("http://"):
            previou_url = previou_url.replace("http://", "")
        if previou_url.endswith("/"):
            previou_url = previou_url[0:len(previou_url)-1]
        return previou_url

    def remove_special_characters(self, domain):
        domain = domain.replace("<b>", "")
        domain = domain.replace("</b>", "")
        domain = domain.replace("&nbsp", "")
        domain = domain.replace("....", "")
        domain = domain.replace("...", "")
        return domain

if __name__ == '__main__':
    pass
    b = BaiduSpiderExtractorPc()
    # print b.remove_special_characters("www.<b>robertocavalli</b>.com/ ")

    f = open('pc4.txt', 'r')
    content = f.read()
    f.close()
    # b = BaiduPcRankExtractor()
    import time
    start_time = time.time()
    l_s = b.extractor_baidu_pc_lxml(content)
    end_time = time.time()
    print end_time - start_time
    print l_s



