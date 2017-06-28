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

class SourceExtractor (object):

    # 列表页  1:页面不全 2: 解析错误 3：无内容
    def extractor_baidu_zhidao_list(self, body, page=1):
        pos = body.find("</html>")
        if pos < 0:
            return 1
        else:
            try:
                results = list()

                # tree = fromstring(u""+body)
                # print tree.body
                # containers = tree.cssselect('dl.dl')  # *行代码

                soup = BeautifulSoup(body, "html.parser")
                html_results = soup.find_all("dl", {"class": "dl"})
                if html_results:
                    for result_one in html_results:
                        real_url = ""
                        a_content = result_one.find_all("a")
                        if a_content:
                            real_url = a_content[0].attrs["href"]
                            if real_url.find("/question/") > -1:
                                real_url = real_url[0: real_url.find("?")]
                            else:
                                continue
                        item = dict()
                        item["real_url"] = real_url
                        print real_url
                        results.append(item)
                    return results
                return 3
            except Exception:
                print traceback.format_exc()
                return 2
        return result

    # 浏览次数  https://zhidao.baidu.com/api/qbpv?q=453702572  加referer
    def extractor_html_detail_bs(self, body):
        try:
            extractor_result = dict()
            question_item = dict()
            answer_list = list()

            description = "" # 描述
            asker = ""       # 提问者名称和链接
            view_cnt = 0     # 浏览数
            pics = ""         # 图片,多图竖线分割
            description_text = "" # 描述纯文本

            html_tree = BeautifulSoup(body, 'html.parser')
            title_html = html_tree.find_all("h1")
            if title_html:
                description_text = title_html[0].text.strip()
                description, pics = self.extractor_content_images(title_html[0])

                ask_info = html_tree.find("div", {"id": "ask-info"})
                if ask_info:
                    ask_info_question = ask_info.get_text().strip()
                    a_inf = ask_info.find("a")
                    href_url = ""
                    try:
                        if a_inf:
                            href_url = "https://zhidao.baidu.com" + a_inf.attrs["href"]
                        asker = (ask_info_question + "+" + href_url if href_url != "" else ask_info_question)
                    except:
                        asker = ask_info_question

                question_item["description"] = description
                question_item["asker"] = asker
                question_item["pics"] = pics
                question_item["description_text"] = description_text

                wgt_best = html_tree.find("div", {"class": "wgt-best"})
                # 最佳回答
                if wgt_best:
                    best_answer_item = self.extractor_best_answer(html_tree)
                    answer_list.append(best_answer_item)

                # 其他回答
                other_answer_content = html_tree.find("div", {"id": "wgt-answers"})
                if other_answer_content:
                    other_answers = other_answer_content.find_all("div", {"class": "answer"})
                    if other_answers:
                        other_answers_list = self.extractor_other_answer_type1(other_answers)
                        if len(other_answers_list) > 0:
                            answer_list = answer_list + other_answers_list

            else:
                # 样式 2
                question_box = html_tree.find("div", {"class": "question-box"})
                # 问
                if question_box:
                    question_item = self.extractor_detail_html_type2(question_box)

                # 其他回答
                other_answer_content = html_tree.find("div", {"class": "other-answer"})
                if other_answer_content:
                    other_answers = other_answer_content.find_all("div", {"class": "answer-detail"})
                    if other_answers:
                        other_answers_list = self.extractor_other_answer_type2(other_answers)
                        if len(other_answers_list) > 0:
                            answer_list = answer_list + other_answers_list

            extractor_result["question_item"] = question_item
            extractor_result["answer_list"] = answer_list
            return extractor_result
        except:
            print traceback.format_exc()
            return -1

    # 样式1 其它回答
    def extractor_other_answer_type1(self, other_answers):
        answer_list = list()
        for other_answer in other_answers:
            answer_item = dict()
            ans_time = ""  # 回答时间
            answer = ""  # 回答内容
            is_best = 0  # 是否最佳  1;最佳
            author = ""  # 回答者
            pics = ""  # 图片,多图竖线分割
            agree_cnt = 0  # 赞同数
            disagree_cnt = 0  # 反对数
            answer_text = ""  # 回答内容 纯文本

            content = other_answer.find("div", {"accuse": "aContent"})
            if content:
                answer_text = content.get_text().strip()
                answer, pics = self.extractor_content_images(content)

            # 作者
            a_user_name = other_answer.find("a", {"class": "user-name"})
            if a_user_name:
                ask_info_question = a_user_name.get_text().strip()
                href_url = ""
                try:
                    href_url = "https://zhidao.baidu.com" + a_user_name.attrs["href"]
                    author = (ask_info_question + "+" + href_url if href_url != "" else ask_info_question)
                except:
                    author = ask_info_question

            if author == "":
                author_content_user = other_answer.find("div", {"class": "pt-5"})
                if author_content_user:
                    author_content = author_content_user.get_text().strip()
                    author = author_content[0: author_content.find("|")]

            pos_time = other_answer.find("span", {"class": "pos-time"})
            if pos_time:
                ans_time = pos_time.get_text().strip()[3:]

            qb_zan_eva = other_answer.find("div", {"class": "qb-zan-eva"})
            if qb_zan_eva:
                span_list = qb_zan_eva.find_all("span")
                if span_list:
                    for i, span_one in enumerate(span_list):
                        if i == 0:
                            agree_cnt = int(span_one.attrs["data-evaluate"])
                        if i == 1:
                            disagree_cnt = int(span_one.attrs["data-evaluate"])

            # print answer.strip()
            # print pics
            # print author.strip()
            # print ans_time
            # print agree_cnt
            # print disagree_cnt
            answer_item["answer"] = answer
            answer_item["pics"] = pics
            answer_item["author"] = author
            answer_item["ans_time"] = ans_time
            answer_item["is_best"] = is_best
            answer_item["agree_cnt"] = agree_cnt
            answer_item["disagree_cnt"] = disagree_cnt
            answer_item["answer_text"] = answer_text
            answer_list.append(answer_item)
        return answer_list

    def extractor_other_answer_type2(self, other_answers):
        answer_list = list()
        for other_answer in other_answers:
            answer_item = dict()
            ans_time = ""  # 回答时间
            answer = ""  # 回答内容
            is_best = 0  # 是否最佳  1;最佳
            author = ""  # 回答者
            pics = ""  # 图片,多图竖线分割
            agree_cnt = 0  # 赞同数
            disagree_cnt = 0  # 反对数
            answer_text = ""  # 回答内容 纯文本

            content = other_answer.find("p", {"accuse": "answer-detail-content"})
            if content:
                answer_text = content.get_text().strip()
                answer, pics = self.extractor_content_images(content)

            # 作者
            a_user_name = other_answer.find("a", {"class": "username"})
            if a_user_name:
                ask_info_question = a_user_name.get_text().strip()
                href_url = ""
                try:
                    href_url = "https://zhidao.baidu.com" + a_user_name.attrs["href"]
                    author = (ask_info_question + "+" + href_url if href_url != "" else ask_info_question)
                except:
                    author = ask_info_question

            if author == "":
                author_content_user = other_answer.find("div", {"class": "pt-5"})
                if author_content_user:
                    author_content = author_content_user.get_text().strip()
                    author = author_content[0: author_content.find("|")]

            pos_time = other_answer.find("span", {"class": "time"})
            if pos_time:
                ans_time = pos_time.get_text().strip()

            qb_zan_eva = other_answer.find("div", {"class": "qb-zan-eva"})
            if qb_zan_eva:
                span_list = qb_zan_eva.find_all("span")
                if span_list:
                    for i, span_one in enumerate(span_list):
                        if i == 0:
                            agree_cnt = int(span_one.attrs["data-evaluate"])
                        if i == 1:
                            disagree_cnt = int(span_one.attrs["data-evaluate"])

            # print answer.strip()
            # print pics
            # print author.strip()
            # print ans_time
            # print agree_cnt
            # print disagree_cnt
            answer_item["answer"] = answer
            answer_item["pics"] = pics
            answer_item["author"] = author
            answer_item["ans_time"] = ans_time
            answer_item["is_best"] = is_best
            answer_item["agree_cnt"] = agree_cnt
            answer_item["disagree_cnt"] = disagree_cnt
            answer_item["answer_text"] = answer_text
            answer_list.append(answer_item)
        return answer_list

    # 详情页样式2  问
    def extractor_detail_html_type2(self, question_box):
        question_item = dict()
        description = ""  # 描述
        asker = ""  # 提问者名称和链接
        view_cnt = 0  # 浏览数
        pics = ""  # 图片,多图竖线分割
        description_text = ""  # 描述纯文本

        title_html = question_box.find("h2")
        if title_html:
            description_text = title_html.get_text().strip()
            description, pics = self.extractor_content_images(title_html)
            # description = description_text

            ahref = question_box.find("a", {"class": "username"})
            if ahref:
                asker = ahref.get_text()
        else:
            return False
        question_item["description"] = description
        question_item["asker"] = asker
        question_item["pics"] = pics
        question_item["description_text"] = description_text
        return question_item

    # 解析最佳回答
    def extractor_best_answer(self, html_tree):
        answer_item = dict()
        ans_time = ""  # 回答时间
        answer = ""  # 回答内容
        is_best = 0  # 是否最佳  1;最佳
        author = ""  # 回答者
        pics = ""  # 图片,多图竖线分割
        agree_cnt = 0  # 赞同数
        disagree_cnt = 0  # 反对数
        answer_text = ""  # 回答内容 纯文本
        answer_time = html_tree.find("span", {"class": "answer-time"})
        if answer_time:
            ans_time = answer_time.get_text().strip()[3:]

        answer_title = html_tree.find("span", {"class": "answer-title"})
        if answer_title:
            answer_type = answer_title.get_text().strip()
            if answer_type == u"最佳答案":
                is_best = 1

        content = html_tree.find("pre", {"accuse": "aContent"})
        if content:
            answer_text = content.get_text()
            answer, pics = self.extractor_content_images(content)

        answer_name = html_tree.find("a", {"class": "user-name"})
        if answer_name:
            ask_info_question = answer_name.get_text().strip()
            href_url = ""
            try:
                href_url = "https://zhidao.baidu.com" + answer_name.attrs["href"]
                author = (ask_info_question + "+" + href_url if href_url != "" else ask_info_question)
            except:
                author = ask_info_question

        qb_zan_eva = html_tree.find("div", {"class": "qb-zan-eva"})
        if qb_zan_eva:
            span_list = qb_zan_eva.find_all("span")
            if span_list:
                for i, span_one in enumerate(span_list):
                    if i == 0:
                        agree_cnt = int(span_one.attrs["data-evaluate"])
                    if i == 1:
                        disagree_cnt = int(span_one.attrs["data-evaluate"])

        # print agree_cnt
        # print disagree_cnt
        # print ans_time
        # print is_best
        # print answer
        # print author
        # print pics
        answer_item["answer"] = answer
        answer_item["author"] = author
        answer_item["ans_time"] = ans_time
        answer_item["is_best"] = is_best
        answer_item["pics"] = pics
        answer_item["agree_cnt"] = agree_cnt
        answer_item["disagree_cnt"] = disagree_cnt
        answer_item["answer_text"] = answer_text
        return answer_item


    def extractor_html_view_count(self, body):
        try:
            html_tree = BeautifulSoup(body, 'html.parser')
            view_count_content = html_tree.find("body")
            if view_count_content:
                view_vount = int(view_count_content.get_text())
                return view_vount
            else:
                return -1
        except:
            print traceback.format_exc()
            return -1

    def extractor_content_images(self, content_images):
        try:
            author = "%s" % content_images
            pics = ""
            img_srcs = re.findall(r"""src=\"(.*?)\"""", author)
            if img_srcs:
                for i, img_one in enumerate(img_srcs):
                    if str(img_one).find("zhidao.baidu.com") > -1:
                        continue
                    else:
                        pics = (pics + img_one if pics == "" or i == (len(img_srcs) - 1) else pics + "|" + img_one)
            return author, pics
        except:
            return "", ""

    # def extractor_content_body_images(self, content_imgs):
    #     img_srcs = re.findall(r"""src=\"(.*?)\"""", content_imgs)
    #     file_names = list()
    #     if img_srcs:
    #         for content_one in img_srcs:
    #             start_index = content_one.rfind("/")
    #             end_index = content_one.rfind(".")
    #             # 分100个文件夹
    #             filename = "images/img%s/" % str(random.randint(1, 100)) + content_one[
    #                                                                        start_index + 1: end_index] + ".jpg"
    #             file_names.append(filename)
    #             content = content.replace(content_one, filename)
    #     return content, img_srcs, file_names

    # 获取标签下所有中文
    def getText(self, elem):
        rc = []
        for node in elem.itertext():
            rc.append(node.strip())
        return ''.join(rc)

if __name__ == '__main__':
    # sx = HandleCsvDeal()
    extractor = SourceExtractor()
    # sxfile = open("zhidao_list.txt", "rb")
    # content = sxfile.read()
    # returntext = extractor.extractor_baidu_zhidao_list(content)
    # print returntext

    sxfile = open("zhidao_detail_1.txt", "rb")
    content = sxfile.read()
    returntext = extractor.extractor_html_detail_bs(content)
    print returntext

    # returntext = [{"keyword": "gsgsg"}]
    # sx_store = BaseStore()
    # con = {'host': '115.159.158.157',
    #         # 'host': '10.143.32.137',
    #         'user': 'sunxiang',
    #         'password': 'sx2017@',
    #         'db': 'content_center'}
    # print sx_store.store_table_db(returntext, table="content_keyword", db_connnection=con)
    # returntext = extractor.extractor_photojs(content, 12)
    # print len(returntext)
    # filename = "csv01010.csv"
    # sx.sx_write_File(filename, returntext)


