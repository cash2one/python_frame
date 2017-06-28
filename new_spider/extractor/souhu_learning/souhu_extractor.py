# -*- coding: utf8 -*-
import traceback
import datetime
import re
import json
from lxml.html import fromstring
import sys
import random
reload(sys)
sys.setdefaultencoding('utf8')

from store.sx_basestore import BaseStore
from bs4 import BeautifulSoup
'''
    使用bs 解析
'''
class SourceExtractor (object):

    '''
        -1 解析异常
        1 无数据
    '''
    def extractor_list_lxml(self, body):
        try:
            tree = fromstring(body)  # 这种方式 可使用cssselect  不然linux 不能使用
            list_box = tree.cssselect('div.main-content')
            # .main - content
            if list_box:
                result_list = list()
                list_content = tree.cssselect("li")
                if list_content:
                    for list_one in list_content:
                        content_title = list_one.cssselect('span.content-title > a')
                        if content_title:
                            print content_title.get("href")

            else:
                return 1
        except:
            print traceback.format_exc()
            return -1

    # -1 解析异常  1 无内容 解析目录
    def extractor_list_bs_catalog(self, body):
        try:
            bsObj = BeautifulSoup(body, 'html.parser')
            dl_list = bsObj.find_all("dl")
            result_list = list()
            if dl_list:
                for dl_one in dl_list:
                    a_list = dl_one.find_all("a")
                    if a_list:
                        for i, a_one in enumerate(a_list):
                            item = dict()
                            if i == 0:
                                url = a_one.attrs["href"]
                                catalog_one = a_one.get_text()
                                catalog_two = ""
                            else:
                                url = a_one.attrs["href"]
                                catalog_two = a_one.get_text()
                            item["url"] = url
                            item["catalog_one"] = catalog_one
                            try:
                                item["catalog_two"] = catalog_two
                            except:
                                item["catalog_two"] = ""
                            result_list.append(item)
                return result_list
            return 1
        except:
            print traceback.format_exc()
            return -1

    # -1 解析异常  1 无内容 一级目录 列表页解析
    def extractor_list_bs(self, body, extractor_page=0):
        try:
            if body.find("</html>") > -1:
                pass
            else:
                return 1

            ext_result = dict()
            if extractor_page == 1:
                maxPage, showPages = self.extractor_body(body)
                ext_result["maxPage"] = maxPage
                ext_result["showPages"] = showPages

            bsObj = BeautifulSoup(body, 'html.parser')
            list_box = bsObj.find_all("div", {"class": "main-content"})
            result_list = list()
            if list_box:

                list_content = list_box[0].find_all("li")
                if list_content:
                    for list_one in list_content:
                        spans = list_one.find_all("span", {"class": "content-title"})
                        if spans:
                            a_one = spans[0].find("a").attrs["href"]
                            result_list.append(a_one)
            ext_result["result_list"] = result_list
            return ext_result
        except:
            print traceback.format_exc()
            return -1

    # -1 解析异常  1 无内容  二级 列表页解析
    def extractor_list_categoryteo_bs(self, body, extractor_page=0):
        try:
            if body.find("</html>") > -1:
                pass
            else:
                return 1
            ext_result = dict()
            if extractor_page == 1:
                maxPage, showPages = self.extractor_body(body)
                ext_result["maxPage"] = maxPage
                ext_result["showPages"] = showPages

            bsObj = BeautifulSoup(body, 'html.parser')
            span_list_box = bsObj.find_all("span", {"class": "content-title"})
            result_list = list()
            if span_list_box:
                for span_one in span_list_box:
                    a_list = span_one.find_all("a")
                    if a_list:
                        href_url = a_list[0].attrs["href"]
                        result_list.append(href_url)

            ext_result["result_list"] = result_list
            return ext_result
        except:
            print traceback.format_exc()
            return -1


    # 详情页 解析
    def extractor_detail_bs(self, body):
        try:
            html_item = dict()
            content = ""
            title = ""
            crumbs = ""
            img_srcs = list()
            file_names = list()

            content, img_srcs, file_names = self.get_content_body(body)

            # print content
            bsObj = BeautifulSoup(body, 'html.parser')
            # bsObj = BeautifulSoup(body, 'lxml')
            location = bsObj.find_all("div", {"class": "location"})
            head = ""
            if location:
                head = location[0].get_text()
                start_index = head.find(">")
                crumbs = head[start_index + 1:].replace(" ", "")

            h1 = bsObj.find_all("h1")
            if h1:
                title = h1[0].get_text()

            # print crumbs, title
            # print img_srcs, file_names
            html_item["crumbs"] = crumbs
            html_item["title"] = title
            html_item["content"] = content
            # print type(content)
            html_item["img_srcs"] = img_srcs
            html_item["file_names"] = file_names
            return html_item
            # return 1
        except:
            print traceback.format_exc()
            return -1

    def get_content_body(self, body):
        start_index = body.find("contentText")
        temp_body = body[start_index:]
        start_index = temp_body.find("<")
        temp_body = temp_body[start_index:]
        end_index = temp_body.find("</div>")
        content = temp_body[0: end_index]
        return self.analyze_content(content)

    def analyze_content(self, content):
        # 解析 图片名
        img_srcs = re.findall(r"""src=\"(.*?)\"""", content)
        file_names = list()
        if img_srcs:
            for content_one in img_srcs:
                start_index = content_one.rfind("/")
                end_index = content_one.rfind(".")
                # 分100个文件夹
                filename = "images/img%s/" % str(random.randint(1, 100)) + content_one[
                                                                          start_index + 1: end_index] + ".jpg"
                file_names.append(filename)
                content = content.replace(content_one, filename)
        return content, img_srcs, file_names

    def extractor_body(self, body):
        body_start_index = body.find("var maxPage =")
        temp_body = body[body_start_index:]
        temp_end_index = temp_body.find(";")
        maxPage = int(temp_body[14: temp_end_index])

        body_start_index = body.find("var showPages =")
        temp_body = body[body_start_index:]
        temp_end_index = temp_body.find(";")
        showPages = int(temp_body[15: temp_end_index])
        return maxPage, showPages

if __name__ == '__main__':
    # sx = HandleCsvDeal()
    extractor = SourceExtractor()
    sxfile = open("detail.txt", "rb")
    content = sxfile.read()
    # print content
    returntext = extractor.extractor_detail_bs(content)
    # returntext = extractor.extractor_list_categoryteo_bs(content)
    # returntext = extractor.extractor_list_bs_catalog(content)
    returntext["url"] = "http://learning.sohu.com/20170502/n491504271.shtml"

    # print returntext["content"]
    # self, results, table="", type=1, field=None, db_connnection=""

    con = {'host': '115.159.0.225',
            'user': 'remote',
            'password': 'Iknowthat',
            'db': 'souhu_learning'}
    sx_store = BaseStore()

    store_list = list()
    store_list.append(returntext)
    sx_store.store_table_db(store_list, table="souhu_details", db_connnection=con)
    # returntext = extractor.extractor_photojs(content, 12)
    # print len(returntext)
    # filename = "csv01010.csv"
    # sx.sx_write_File(filename, returntext)


