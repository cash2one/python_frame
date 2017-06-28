# -*- coding: utf8 -*-
import traceback
import datetime
import re
import json
from bs4 import BeautifulSoup
from lxml.html import fromstring
from lxml import etree

from HTMLParser import HTMLParser
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# from store.sx_basestore import BaseStore

class SourceExtractor (object):

    '''
        解析搜狗微信搜索按文章搜索结果页，获取文章列表
    '''
    def extractor_list(self, body):
        try:
            result_list = list()
            pos = body.find("</html>")
            if pos < 0:
                return 2

            tree = fromstring(body.decode('utf-8', 'ignore'))  # 这种方式 可使用cssselect  不然linux 不能使用
            wrappers = tree.cssselect("div.txt-box")
            if wrappers:
                for wrapper in wrappers:
                    item = {'title': '', 'url': '', 'summary': ''}
                    h3_list = wrapper.cssselect('h3')
                    if h3_list:
                        title = self.getText(h3_list[0])
                        a_list = wrapper.cssselect("a")
                        if a_list:
                            url = a_list[0].get("href")
                    p_list = wrapper.cssselect('p')
                    if p_list:
                        summary = self.getText(p_list[0])
                    item["title"] = title
                    item["url"] = url
                    item["summary"] = summary
                    result_list.append(item)
                return result_list
            return 1
        except:
            print traceback.format_exc()
            return -1

    # '''
    #         解析搜狗微信搜索按文章搜索结果页，获取文章列表
    # '''
    # def extractor_list(self, body):
    #     try:
    #         result_list = list()
    #         tree = fromstring(body.decode('utf-8', 'ignore'))  # 这种方式 可使用cssselect  不然linux 不能使用
    #         wrappers = tree.cssselect("div.txt-box")
    #         if wrappers:
    #             for wrapper in wrappers:
    #                 item = {'title': '', 'url': '', 'summary': ''}
    #                 h3_list = wrapper.cssselect('h3')
    #                 if h3_list:
    #                     title = self.getText(h3_list[0])
    #                     a_list = wrapper.cssselect("a")
    #                     if a_list:
    #                         url = a_list[0].get("href")
    #                 p_list = wrapper.cssselect('p')
    #                 if p_list:
    #                     summary = self.getText(p_list[0])
    #                 item["title"] = title
    #                 item["url"] = url
    #                 item["summary"] = summary
    #                 result_list.append(item)
    #             return result_list
    #         return 1
    #     except:
    #         print traceback.format_exc()
    #         return -1

    # 解析文章详情页  bs
    def extractor_detail_bs(self, html):
        results = list()
        try:
            html_soup = BeautifulSoup(html, 'lxml')
            if html_soup:
                article_div = html_soup.find("div", id="img-content")
                if article_div:
                    item = {'is_original': 0, 'publish_time': '', 'content': ''}
                    auth_info_div = article_div.find("div", class_="rich_media_meta_list", recursive=False)
                    if auth_info_div:
                        original_span = auth_info_div.find("span", id="copyright_logo", recursive=False)
                        if original_span:
                            item['is_original'] = 1
                        date_em = auth_info_div.find("em", id="post-date", recursive=False)
                        if date_em:
                            item['publish_time'] = date_em.get_text().strip()
                        profile_info_div = auth_info_div.find("div", class_="profile_inner")
                        if profile_info_div:
                            name_strong = profile_info_div.find("strong", class_="profile_nickname", recursive=False)
                            if name_strong:
                                item['wechat_name'] = name_strong.get_text().strip()
                            num_label = profile_info_div.find("label", string="微信号")
                            if num_label:
                                num_span = num_label.find_next_sibling("span")
                                if num_span:
                                    item['wechat_num'] = num_span.get_text().strip()
                    content_div = article_div.find("div", id="js_content", recursive=False)
                    if content_div:
                        item['content'] = str(content_div)
                    results.append(item)
        except Exception:
            print(traceback.format_exc())
        return results

    # 解析文章详情页
    def extractor_detail(self, html):
        results = list()
        try:
            html_soup = fromstring(html.decode('utf-8', 'ignore'))
            article_div = html_soup.xpath("//div[@id='img-content']")
            if article_div:
                item = {'is_original': 0, 'publish_time': '', 'content': ''}
                auth_info_div = article_div[0].xpath("//div[@class='rich_media_meta_list']")
                if auth_info_div:
                    original_span = auth_info_div[0].xpath("//span[@id='copyright_logo']")
                    if original_span:
                        item['is_original'] = 1
                    date_em = auth_info_div[0].xpath("//em[@id='post-date']")
                    if date_em:
                        item['publish_time'] = self.getText(date_em[0]).strip()
                    profile_info_div = auth_info_div[0].xpath("//div[@class='profile_inner']")
                    if profile_info_div:
                        name_strong = profile_info_div[0].xpath("//strong[@class='profile_nickname']")
                        if name_strong:
                            item['wechat_name'] = self.getText(name_strong[0]).strip()

                        label_contents = profile_info_div[0].xpath("//p[@class='profile_meta']")
                        for i, v in enumerate(label_contents):
                            if self.getText(v).find(u'微信号') > -1:
                                num_span = v.xpath("//span[@class='profile_meta_value']")
                                if num_span:
                                    item['wechat_num'] = self.getText(num_span[0])
                content_div = article_div[0].xpath("//div[@id='js_content']")
                if content_div:
                    item['content'] = str(etree.tostring(content_div[0], encoding="utf-8"))
                results.append(item)
        except Exception:
            print(traceback.format_exc())
        return results

    # 获取标签下所有中文
    def getText(self, elem):
        rc = []
        for node in elem.itertext():
            rc.append(node.strip())
        return ''.join(rc)

if __name__ == '__main__':
    # sx_store = BaseStore()
    extractor = SourceExtractor()
    sxfile = open("wechat_list.txt", "rb")
    content = sxfile.read()
    returntext = extractor.extractor_list(content)
    print returntext
    # self, results, table="", type=1, field=None, db_connnection=""

    # con = {'host': '115.159.0.225',
    #         'user': 'remote',
    #         'password': 'Iknowthat',
    #         'db': 'mafengwo'}
    # sx_store.store_table_db(returntext, table="view_spot", db_connnection=con)
    # returntext = extractor.extractor_photojs(content, 12)
    # print len(returntext)
    # filename = "csv01010.csv"
    # sx.sx_write_File(filename, returntext)


