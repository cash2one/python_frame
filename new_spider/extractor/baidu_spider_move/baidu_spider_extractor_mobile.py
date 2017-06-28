# -*- coding: utf8 -*-
import json
import os
import re
import sys
import traceback

from bs4 import BeautifulSoup

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

    def extractor_baidu_mobile_lxml(self, body, ck='', pcount=0, spidertype = 1):
        result = {}
        # 相关搜索
        result['related'] = []
        pos = body.find("</html>")
        if pos < 0:
            return 2
        else:
            try:
                # bsObj = BeautifulSoup(body, "lxml")
                # containers = bsObj.find_all("div", {"class": "c-result"})

                tree = fromstring(body)
                containers = tree.cssselect('div.c-result')
                if len(containers) > 0:
                    for container in containers:
                        toprank = ""
                        title = ''
                        des = ''  # 描述
                        evaluate = ""  # 评价
                        realaddress = ""
                        domain = ""
                        searchState = 0

                        order = int(container.get('order'))
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
                        if ck:
                            # 根据domain  和 给出的url 匹配
                            # if domain == "":
                            #     continue
                            # sx_FindDomain = FindDomain()
                            datalog = container.get('data-log')
                            if datalog:
                                try:
                                    datalog = str(datalog).replace("\'", "\"")
                                    sx_data = json.loads(datalog)
                                    mu_url = sx_data["mu"]
                                except:
                                    mu_url = ""
                                    continue

                                if int(spidertype) == 2:
                                    # 提供url 和 真实url 相等
                                    ck = self.url_util.removeCharacters(ck)
                                    mu_url = self.url_util.removeCharacters(mu_url)
                                    if mu_url == ck:
                                        pass
                                    else:
                                        if domain == "":
                                            alist = container.cssselect("a")
                                            if alist:
                                                for ahref in alist:
                                                    try:
                                                        href = ahref.get("href")
                                                        href = self.url_util.removeCharacters(href)
                                                        ck = self.url_util.removeCharacters(ck)
                                                        if href == ck:
                                                            searchState = 1
                                                            break
                                                    except Exception:
                                                        continue
                                        if searchState == 0:
                                            continue
                                else:
                                    if mu_url:
                                        mu_urlDomain = self.sx_FindDomain.sxGetDomain(mu_url)
                                        ck_domain = self.sx_FindDomain.sxGetDomain(ck)
                                        if mu_urlDomain != "" and ck_domain != "":
                                            if mu_urlDomain == ck_domain:
                                                pass
                                            else:
                                                continue
                                        else:
                                            # print "mu_urlDomain or ck_domain have kong" + mu_url
                                            continue
                                    else:
                                        continue
                            else:
                                continue

                        if domain == '' and re.search(u'百度手机助手', title) > 0:
                            domain = 'mobile.baidu.com'
                        if domain == '' and re.search(u'_相关信息', title) > 0:
                            domain = 'm.baidu.com'
                        if domain == '' and re.search(u'_相关网站', title) > 0:
                            domain = 'm.baidu.com'
                        if domain == '' and re.search(u'_百度糯米', title) > 0:
                            domain = 'nuomi.baidu.com'

                        item = {}
                        item['domain'] = domain
                        # item['srcid'] = srcid
                        # item['pos'] = pos
                        item['rank'] = toprank
                        item['title'] = title
                        item['description'] = des
                        if mu_url:
                            item['realaddress'] = mu_url
                        else:
                            item['realaddress'] = ""

                        # print domain
                        # print toprank
                        # print title
                        # print des
                        # print mu_url

                        result['rank'] = list()
                        result['rank'].append(item)
                        if ck:
                            return result
                    return result
                else:
                    return 3
            except Exception:
                print traceback.format_exc()
                return 2
        return result


    def extractor_baidu_mobile(self, body, ck='', pcount=0, spidertype = 1):
        result = {}
        # 相关搜索
        result['related'] = []
        pos = body.find("</html>")
        if pos < 0:
            return 2
        else:
            try:
                bsObj = BeautifulSoup(body, "html.parser")
                containers = bsObj.find_all("div", {"class": "c-result"})
                # resitem
                # if len(containers) == 0:
                #     containers = bsObj.find_all("div", {"class": "resitem"})

                if len(containers) > 0:
                    for container in containers:
                        toprank = ""
                        title = ''
                        des = ''  # 描述
                        evaluate = ""  # 评价
                        realaddress = ""
                        domain = ""
                        searchState = 0

                        order = int(container.attrs['order'])
                        if order:
                            toprank = order + int(pcount)
                        titles = container.find_all("h3")
                        if len(titles) > 0:
                            title = titles[0].get_text().replace(unicode("举报图片"), "").strip()
                        des_list = container.find_all("div", {"class": "wz-generalmaphotel-mapc-gap-top"})
                        if len(des_list) > 0:
                            des = 'map'
                            domain = 'map.baidu.com'
                        elif str(container.get_text()).find(u'百度百科') > 0:
                            des = 'baike.baidu.com'
                            domain = 'baike.baidu.com'
                        else:
                            des_list_two = container.find_all("p")
                            if len(des_list_two) > 0:
                                des = des_list_two[0].get_text().strip()

                        # evaluate_list = container.find_all("span", {"class": "c-pingjia"})
                        # if len(evaluate_list) > 0:
                        #     evaluate = evaluate_list[0].get_text().strip()

                        # realaddress_list = container.find_all("a")
                        # if len(realaddress_list) > 0:
                        #     realaddress = realaddress_list[0].attrs["href"]

                        # if realaddress != "":
                        #     sx = GetReal_Address()
                        #     realaddress = sx.findReal_Address(realaddress)  # 真实url

                        domain_list = container.find_all("a", {"class": "c-showurl"})
                        if len(domain_list) > 0:
                            domain = domain_list[0].get_text().strip()
                        else:
                            domain_list = container.find_all("span", {"class": "c-showurl"})
                            if len(domain_list) > 0:
                                domain = domain_list[0].get_text().strip()
                        if ck:
                            # 根据domain  和 给出的url 匹配
                            # if domain == "":
                            #     continue
                            # sx_FindDomain = FindDomain()
                            datalog = container.attrs['data-log']
                            if datalog:
                                try:
                                    datalog = str(datalog).replace("\'", "\"")
                                    sx_data = json.loads(datalog)
                                    mu_url = sx_data["mu"]
                                except:
                                    mu_url = ""
                                    continue

                                if int(spidertype) == 2:
                                    # 提供url 和 真实url 相等
                                    ck = self.url_util.removeCharacters(ck)
                                    mu_url = self.url_util.removeCharacters(mu_url)
                                    if mu_url == ck:
                                        pass
                                    else:
                                        if domain == "":
                                            alist = container.find_all("a")
                                            if alist:
                                                for ahref in alist:
                                                    try:
                                                        href = ahref.attrs["href"]
                                                        href = self.url_util.removeCharacters(href)
                                                        ck = self.url_util.removeCharacters(ck)
                                                        if href == ck:
                                                            searchState = 1
                                                            break
                                                    except Exception:
                                                        continue
                                        if searchState == 0:
                                            continue
                                else:
                                    if mu_url:
                                        mu_urlDomain = self.sx_FindDomain.sxGetDomain(mu_url)
                                        ck_domain = self.sx_FindDomain.sxGetDomain(ck)
                                        if mu_urlDomain != "" and ck_domain != "":
                                            if mu_urlDomain == ck_domain:
                                                pass
                                            else:
                                                continue
                                        else:
                                            # print "mu_urlDomain or ck_domain have kong" + mu_url
                                            continue
                                    else:
                                        continue
                            else:
                                continue

                        if domain == '' and re.search(u'百度手机助手', title) > 0:
                            domain = 'mobile.baidu.com'
                        if domain == '' and re.search(u'_相关信息', title) > 0:
                            domain = 'm.baidu.com'
                        if domain == '' and re.search(u'_相关网站', title) > 0:
                            domain = 'm.baidu.com'
                        if domain == '' and re.search(u'_百度糯米', title) > 0:
                            domain = 'nuomi.baidu.com'

                        item = {}
                        item['domain'] = domain
                        # item['srcid'] = srcid
                        # item['pos'] = pos
                        item['rank'] = toprank
                        item['title'] = title
                        item['description'] = des

                        if mu_url:
                            item['realaddress'] = mu_url
                        else:
                            item['realaddress'] = ""

                        # print domain
                        # print toprank
                        # print title
                        # print des
                        # print mu_url

                        result['rank'] = list()
                        result['rank'].append(item)
                        if ck:
                            return result
                    return result
                else:
                    return 3
            except Exception:
                print traceback.format_exc()
                return 2
        return result

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




