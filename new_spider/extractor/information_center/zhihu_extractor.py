# -*- coding: utf8 -*-
import traceback
import datetime
import re
import json
from lxml.html import fromstring
from lxml import etree
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# from store.sx_basestore import BaseStore
from bs4 import BeautifulSoup

class SourceExtractor (object):

    '''
            列表页
    '''
    def extractor_list(self, body):
        try:
            tree = fromstring(body)  # 这种方式 使用cssselect  不然linux 不能使用
            result_about_list = tree.cssselect("div.result-about-list")

            if result_about_list:
                result_list = list()
                for result_aboutin in result_about_list:
                    tree_h4_list = result_aboutin.cssselect("h4")
                    if tree_h4_list:
                        for h4_content in tree_h4_list:
                            result_one = dict()
                            asker = ""
                            try:
                                a_href = h4_content.cssselect("a")[0].get("href")
                            except:
                                continue
                            zhihu_username = result_aboutin.cssselect("p.about-answer")
                            if zhihu_username:
                                a_url = zhihu_username[0].cssselect("a")
                                if a_url:
                                    username = self.getText(a_url[0])
                                    href_url = a_url[0].get("href")
                                    asker = username + "+" + href_url if href_url else username
                                else:
                                    # print etree.tostring(zhihu_username[0])
                                    city_name = zhihu_username[0].cssselect("cite")
                                    if city_name:
                                        asker = self.getText(city_name[0])

                            # # print a_href
                            # print asker
                            result_one["a_href"] = a_href
                            result_one["asker"] = asker
                            result_list.append(result_one)
                            # print a_href
                return result_list
            return 1
        except:
            # print traceback.format_exc()
            return -1

    # 详情页
    def extractor_detail(self, body):
        try:
            tree = fromstring(body.decode('utf-8', 'ignore'))  # 这种方式 可使用cssselect  不然linux 不能使用
            extractor_result = dict()
            answer_list = list()
            question_item = dict()
            question = ""       # title
            tags = ""           # 标签,竖线分割
            description = ""    # 描述
            asker = ""          # 提问者名称和链接
            view_cnt = 0        # 浏览数
            ans_cnt = 0         # 回答数
            follower_cnt = 0    # 关注数
            pics = ""           # 图片,多图竖线分割

            tags_topics = tree.cssselect("div.QuestionHeader-topics")
            if tags_topics:
                tags_contents = tags_topics[0].cssselect("div.Popover")
                if tags_contents:
                    for i, tag_one in enumerate(tags_contents):
                        if i != len(tags_contents) - 1:
                            tags = self.getText(tag_one) + "|"
                        else:
                            tags = self.getText(tag_one)

            describe_title = tree.cssselect("h1.QuestionHeader-title")
            if describe_title:
                question = self.getText(describe_title[0])
            describe_detail = tree.cssselect("div.QuestionHeader-detail")
            if describe_detail:
                description, pics = self.extractor_content_images(etree.tostring(describe_detail[0])[0:-4])

            number_contents = tree.cssselect("div.NumberBoard")
            if number_contents:
                concenrn_contents = number_contents[0].cssselect("div.NumberBoard-item")
                if concenrn_contents:
                    for i, number_content in enumerate(concenrn_contents):
                        numberBoard_value = number_content.cssselect("div.NumberBoard-value")
                        if numberBoard_value:
                            count_temp = int(numberBoard_value[0].text)
                            if i == 0:
                                follower_cnt = count_temp
                            if i == 1:
                                view_cnt = count_temp

            question_main_content = tree.cssselect("div.Question-main")
            if question_main_content:
                question_main = question_main_content[0]
                answer_count_html = question_main.cssselect("h4.List-headerText")
                if answer_count_html:
                    ans_cnt = self.getText(answer_count_html[0])[0:-3]

            # print question
            # print tags
            # print description
            # print follower_cnt
            # print view_cnt
            # print ans_cnt
            # print pics
            question_item["question"] = question
            question_item["tags"] = tags
            question_item["description"] = description
            question_item["follower_cnt"] = follower_cnt
            question_item["view_cnt"] = view_cnt
            question_item["ans_cnt"] = ans_cnt
            question_item["pics"] = pics

            # 回答
            answer_list_item = tree.cssselect("div.List-item")
            # print len(answer_list_item)
            if answer_list_item:
                for answer_item_one in answer_list_item:
                    answer_item = dict()
                    ans_time = ""   # 回答时间
                    answer = ""     # 回答内容
                    author = ""     # 回答者
                    pics = ""       # 图片,多图竖线分割
                    agree_cnt = 0   # 赞同数

                    # 回答时间
                    answer_time = answer_item_one.cssselect("div.ContentItem-time")
                    if answer_time:
                        answer_content = self.getText(answer_time[0])
                        ans_index = answer_content.find(u"于")
                        ans_time = answer_content[ans_index + 1:]

                    # "div.AuthorInfo-content"
                    answer_username_content = answer_item_one.cssselect("a.UserLink-link")
                    if answer_username_content:
                        # print etree.tostring(answer_username_content[1])
                        # print answer_username_content[1].get("alt")
                        href_url = answer_username_content[1].get("href")
                        if href_url:
                            author = str(answer_username_content[1].text) + "+https://www.zhihu.com" + href_url
                        else:
                            author = self.getText(answer_username_content[1])
                    zantong_content = answer_item_one.cssselect("span.Voters")
                    if zantong_content:
                        agree_count_temp = self.getText(zantong_content[0]).strip()
                        end_index = agree_count_temp.find(u"人")
                        agree_cnt = int(agree_count_temp[0: end_index].strip())

                    answer_text = answer_item_one.cssselect("div.RichContent-inner")
                    if answer_text:
                        answer, pics = self.extractor_content_images(etree.tostring(answer_text[0]))

                    # print author
                    # print ans_time
                    # print answer
                    # print pics
                    # print agree_cnt
                    answer_item["author"] = author
                    answer_item["ans_time"] = ans_time
                    answer_item["answer"] = answer
                    answer_item["pics"] = pics
                    answer_item["agree_cnt"] = agree_cnt
                    answer_list.append(answer_item)

            extractor_result["question_item"] = question_item
            extractor_result["answer_list"] = answer_list
            return extractor_result
        except:
            # print traceback.format_exc()
            return -1

    def extractor_api(self, body):
        body_json = json.loads(body)
        data_list = body_json["data"]
        print len(data_list)
        for data_one in data_list:
            print data_one["voteup_count"]
            print data_one["author"]["name"]
            print data_one["author"]["headline"]
            print data_one["content"]
            # print data_one["title"]

    def extractor_content_images(self, content_images):
        try:
            author = "%s" % str(content_images)
            pics = ""
            img_srcs = re.findall(r"""src=\"(.*?)\"""", author)
            if img_srcs:
                for i, img_one in enumerate(img_srcs):
                    if str(img_one).find("zhstatic.zhihu.com") > -1:
                        continue
                    else:
                        pics = (pics + img_one if pics == "" else pics + "|" + img_one)
            return author, pics
        except:
            return content_images, ""

    # 获取标签下所有中文
    def getText(self, elem):
        rc = []
        for node in elem.itertext():
            rc.append(node.strip())
        return ''.join(rc)

if __name__ == '__main__':
    # sx_store = BaseStore()
    # sx = HandleCsvDeal()
    extractor = SourceExtractor()
    sxfile = open("zhihu_detail.txt", "rb")
    content = sxfile.read()
    returntext = extractor.extractor_detail(content)
    print returntext

    # sxfile = open("zhihu.txt", "rb")
    # content = sxfile.read()
    # returntext = extractor.extractor_list(content)
    # print returntext

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


