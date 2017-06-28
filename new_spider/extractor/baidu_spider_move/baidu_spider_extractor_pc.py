# -*- coding: utf8 -*-
import os
import sys
import traceback

from bs4 import BeautifulSoup

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
from spider.spider import SpiderExtractor
from downloader_sx.util_getRealAddress import GetReal_Address
# from extractor.baidu.sx_domain import FindDomain
from util.domain_urllib import SeoDomain
from sx_util.http_url_utils import HttpUrlUtils
reload(sys)
sys.setdefaultencoding('utf8')

# from lxml import etree
from lxml.html import fromstring

class BaiduSpiderExtractorPc(SpiderExtractor):

    def __init__(self):
        super(BaiduSpiderExtractorPc, self).__init__()
        # self.sx_FindDomain = FindDomain()
        self.find_realaddress = GetReal_Address()
        self.url_util = HttpUrlUtils()
        self.sx_FindDomain = SeoDomain()

    '''
     获取pc排名数据
     response_status 0请求失败 1 请求成功 2 页面不全，封ip
     百度关键词列表页数据
     '''
    def extractor_baidu_pc_lxml(self, body, ck='', spidertype=1):
        result = {}
        # result['rank'] = []
        # 相关搜索
        result['related'] = []

        pos = body.find("</html>")
        if pos < 0 or body.find('location.href.replace') >= 0:
            return 2
        elif body.find('id="wrap"') >= 0 or body.find('<title>') < 0 or body.find('页面不存在_百度搜索') >= 0 \
                or body.find('id="container"') < 0 or body.find('id="content_left"') < 0:
            return 0
        else:
            try:
                tree = fromstring(body)
                # print type(tree)
                # 文件提供的url
                ck_domain = self.sx_FindDomain.sxGetDomain(ck)
                containers = tree.cssselect('div.c-container')  # *行代码
                result['response_status'] = 1
                if len(containers) > 0:
                    result['rank'] = list()  # 只返回一个
                    for container in containers:
                        toprank = ""
                        title = ''
                        des = ''  # 描述
                        evaluate = ""  # 评价
                        realaddress = ""
                        domain = ""
                        search_state = 0

                        find_realaddress_state = 0  # 是否需要获取真实url 0：默认不获取真实url, 1：获取真实url
                        is_get_realaddress = 0  # 判断是否获取真实url

                        toprank = container.get('id')
                        # 标题
                        titles = container.cssselect("h3.t>a")
                        if len(titles) > 0:
                            title = str(self.getText(titles[0])).encode("utf-8").replace(unicode("举报图片"), "").strip()
                            # title = titles[0].text.encode("utf-8").replace(unicode("举报图片"), "").strip()
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
                            domain = str(domain_list[0].text).strip()
                        else:
                            domain_list = container.cssselect("span.c-showurl")
                            if len(domain_list) > 0:
                                domain = str(domain_list[0].text).strip()
                        # print domain
                        if ck:
                            # 提供的 url domain > 10 是 显示url 的domain 以 提供url 的domain 开头
                            # 提供的 url domain < 10  完全相等
                            # domain 解析为空 可能是 百度产品
                            if domain == "":
                                if spidertype == 2:
                                    alist = container.cssselect("a")
                                    if alist:
                                        for ahref in alist:
                                            try:
                                                href = ahref.get("href")
                                                href = self.url_util.removeCharacters(href)
                                                ck = self.url_util.removeCharacters(ck)
                                                if href == ck:
                                                    search_state = 1
                                                    break
                                            except Exception:
                                                continue
                                if search_state == 0:
                                    continue
                            else:
                                if domain.find("...") > 0:
                                    find_realaddress_state = 1
                                domain = self.url_util.remove_special_characters(domain)

                                # 显示url
                                show_domain = self.sx_FindDomain.sxGetDomain(domain)[0:15]
                                if ck_domain.find(show_domain) > -1:
                                    if int(spidertype) == 2:
                                        is_get_realaddress = 1
                                        pass
                                        # realaddress = self.find_realaddress.findReal_Address_improve(realaddress,
                                        #                                                              domain=domain)  # 真实url
                                        # # 提供url 和 真实url 相等
                                        # ck = self.removeCharacters(ck)
                                        # realaddress = self.removeCharacters(realaddress)
                                        # if ck == realaddress:
                                        #     pass
                                        # else:
                                        #     continue
                                    else:
                                        is_get_realaddress = 1
                                        pass
                                        # 获取真实 url 的主域， 主域包含 domain 主域ok 代表匹配到
                                        # if find_realaddress_state == 1:
                                        #     # print "realaddress:%s;domain:%s;toprank:%s" % (realaddress, domain, str(toprank))
                                        #     realaddress = self.find_realaddress.findReal_Address_improve(realaddress, domain=domain)  # 真实url
                                        #     realaddress_domain = self.sx_FindDomain.sxGetDomain(realaddress)
                                        # else:
                                        #     realaddress_domain = self.sx_FindDomain.sxGetDomain(domain)
                                        #     realaddress = domain
                                        # if ck_domain != "" and realaddress_domain != "":
                                        #     if ck_domain == realaddress_domain:
                                        #         pass
                                        #     else:
                                        #         continue
                                        # else:
                                        #     continue
                                else:
                                    continue
                        item = dict()
                        item['domain'] = domain
                        item['rank'] = toprank
                        item['title'] = title
                        item['description'] = des

                        if int(spidertype) == 2:
                            item['realaddress'] = realaddress
                            item['is_get_realaddress'] = 1
                        else:
                            if is_get_realaddress == 1:
                                item['is_get_realaddress'] = 1
                                item['realaddress'] = realaddress
                            else:
                                item['realaddress'] = domain

                        result['rank'].append(item)
                        if ck and int(spidertype) == 1:
                            return result
                    return result
                else:
                    return 0
            except Exception:
                print traceback.format_exc()
                return 2
        return result

    def get_real_address_noscript(self, body):
        if body.find("window.location.replace") > 0 and body.find("noscript") > 0:
            start_index = body.find("window.location.replace(")
            cut_body = body[start_index+25:]
            end_index = cut_body.find("\"")
            cut_url = cut_body[0:end_index]
            return cut_url
        else:
            return None

    # 获取标签下所有中文
    def getText(self, elem):
        rc = []
        for node in elem.itertext():
            rc.append(node.strip())
        return ''.join(rc)

    '''
     获取pc排名数据
     response_status 0请求失败 1 请求成功 2 页面不全，封ip
     百度关键词列表页数据
     '''
    def extractor_baidu_pc(self, body, ck='', spidertype=1):
        result = {}
        # result['rank'] = []
        # 相关搜索
        result['related'] = []

        pos = body.find("</html>")
        if pos < 0 or body.find('location.href.replace') >= 0:
            return 2
        elif body.find('id="wrap"') >= 0 or body.find('<title>') < 0 or body.find('页面不存在_百度搜索') >= 0 \
                or body.find('id="container"') < 0 or body.find('id="content_left"') < 0:
            return 0
        else:
            try:
                bsObj = BeautifulSoup(body, "lxml")

                # 文件提供的url
                ck_domain = self.sx_FindDomain.sxGetDomain(ck)

                # 相关搜索解析
                # rs_html = bsObj.find_all("div", {"id": "rs"})
                # related_tup = ()
                # if len(rs_html) > 0:
                #     related_lists = rs_html[0].find_all("th")
                #     if len(related_lists) > 0:
                #         for related_html in related_lists:
                #             # related = self.encoding(related_html.get_text())
                #             tup_sx = (self.encoding(related_html.get_text()),)
                #             related_tup = related_tup + tup_sx
                #         # tup_related = related_tup
                #         result['related'].append(related_tup)
                #     else:
                #         tup_related = ("no related")
                #         result['related'].append(tup_related)
                # else:
                #     tup_related = ("no related")
                #     result['related'].append(tup_related)

                containers = bsObj.find_all("div", {"class": "c-container"})
                result['response_status'] = 1

                if len(containers) > 0:
                    for container in containers:
                        toprank = ""
                        title = ''
                        des = ''  # 描述
                        evaluate = ""  # 评价
                        realaddress = ""
                        domain = ""
                        search_state = 0

                        find_realaddress_state = 0  # 是否需要获取真实url 0：默认不获取真实url, 1：获取真实url
                        is_get_realaddress = 0      # 判断是否获取真实url

                        toprank = container.attrs["id"]
                        # unicode("中文字符")
                        titles = container.find_all("h3")
                        if len(titles) > 0:
                            title = titles[0].get_text().replace(unicode("举报图片"), "").strip()

                        des_list = container.find_all("div", {"class": "c-abstract"})
                        if len(des_list) > 0:
                            des = des_list[0].get_text().strip()
                        else:
                            des_list_two = container.find_all("div", {"class": "c-span18c-span-last"})
                            if len(des_list_two) > 0:
                                des = des_list_two[0].get_text().strip()

                        # 评价
                        # evaluate_list = container.find_all("span", {"class": "c-pingjia"})
                        # if len(evaluate_list) > 0:
                        #     evaluate = evaluate_list[0].get_text().strip()

                        realaddress_list = container.find_all("a")
                        if len(realaddress_list) > 0:
                            realaddress = realaddress_list[0].attrs["href"]

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
                            # domain 为空 跳过
                            # 提供的 url domain > 10 是 显示url 的domain 以 提供url 的domain 开头
                            # 提供的 url domain < 10  完全相等
                            # domain 解析为空 可能是 百度产品
                            if domain == "":
                                if spidertype == 2:
                                    alist = container.find_all("a")
                                    if alist:
                                        for ahref in alist:
                                            try:
                                                href = ahref.attrs["href"]
                                                href = self.url_util.removeCharacters(href)
                                                ck = self.url_util.removeCharacters(ck)
                                                if href == ck:
                                                    search_state = 1
                                                    break
                                            except Exception:
                                                continue
                                if search_state == 0:
                                    continue
                            else:
                                if domain.find("...") > 0:
                                    find_realaddress_state = 1
                                domain = self.url_util.remove_special_characters(domain)

                                # 显示url
                                show_domain = self.sx_FindDomain.sxGetDomain(domain)[0:15]
                                if ck_domain.find(show_domain) > -1:
                                    if int(spidertype) == 2:
                                        # 完全匹配 直接获取 真实url
                                        realaddress = self.find_realaddress.findReal_Address_improve(realaddress, domain=domain)  # 真实url
                                        # 提供url 和 真实url 相等
                                        ck = self.removeCharacters(ck)
                                        realaddress = self.removeCharacters(realaddress)
                                        if ck == realaddress:
                                            pass
                                        else:
                                            continue
                                    else:
                                        is_get_realaddress = 1
                                        pass
                                        # 获取真实 url 的主域， 主域包含 domain 主域ok 代表匹配到
                                        # if find_realaddress_state == 1:
                                        #     # print "realaddress:%s;domain:%s;toprank:%s" % (realaddress, domain, str(toprank))
                                        #     realaddress = self.find_realaddress.findReal_Address_improve(realaddress, domain=domain)  # 真实url
                                        #     realaddress_domain = self.sx_FindDomain.sxGetDomain(realaddress)
                                        # else:
                                        #     realaddress_domain = self.sx_FindDomain.sxGetDomain(domain)
                                        #     realaddress = domain
                                        # if ck_domain != "" and realaddress_domain != "":
                                        #     if ck_domain == realaddress_domain:
                                        #         pass
                                        #     else:
                                        #         continue
                                        # else:
                                        #     continue
                                else:
                                    continue
                        item = dict()
                        item['domain'] = domain
                        item['rank'] = toprank
                        item['title'] = title
                        item['description'] = des

                        if int(spidertype) == 2:
                            item['realaddress'] = realaddress
                        else:
                            if is_get_realaddress == 1:
                                item['is_get_realaddress'] = 1
                                item['realaddress'] = realaddress
                            else:
                                item['realaddress'] = domain

                        result['rank'] = list()  # 只返回一个
                        result['rank'].append(item)
                        if ck:
                            return result
                    return result
                else:
                    print "containers length == 0"
                    return 0
            except Exception:
                print traceback.format_exc()
                return 2
        return result

    @staticmethod
    def encoding(data):
        types = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']
        for t in types:
            try:
                return data.decode(t).encode("gbk", "ignore")
            except Exception, e:
                pass
        return ""

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
    # print b.remove_special_characters("www.<b>dhdh</b>")
    f = open('wenku_html.txt', 'r')
    content = f.read()
    f.close()
    # b = BaiduPcRankExtractor()
    import time
    start_time = time.time()
    l_s = b.extractor_baidu_pc_lxml(content, ck="https://wenku.baidu.com/view/79e0e526ba68a98271fe910ef12d2af90242a818.html", spidertype=2)
    end_time = time.time()
    print end_time - start_time
    print l_s



