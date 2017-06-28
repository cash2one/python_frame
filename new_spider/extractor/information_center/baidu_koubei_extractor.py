# -*- coding: utf8 -*-
import traceback
from datetime import datetime
import re
import json
from lxml.html import fromstring
from lxml import etree
import execjs
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# from store.sx_basestore import BaseStore

class SourceExtractor (object):

    '''
        1: 无内容 -1：异常  返回第一条链接
    '''
    def extractor_list_js(self, body):
        try:
            ext_result = dict()
            js_body = json.loads(body)
            mems_list = js_body["data"]["mems"]
            if mems_list:
                ext_result["memid"] = mems_list[0]["memid"]  # 口碑点评用到
                ext_result["memcode"] = mems_list[0]["memcode"]
                ext_result["purl"] = mems_list[0]["purl"]
                return ext_result
            return 1
        except:
            print traceback.format_exc()
            return -1

    # 解析详情页
    def extractor_detail(self, body):
        try:
            tree = fromstring(body.decode('utf-8', 'ignore'))  # 这种方式 可使用cssselect  不然linux 不能使用
            extractor_result = dict()
            comment_list = list()
            inf_item = dict()
            redirect_qual = ""

            bus_name = ""
            bus_domain = ""
            settled = ""
            company_name = ""
            est_time = ""
            bus_address = ""
            industry_type = ""

            # 信息
            normal_inf = tree.cssselect("div.kb-resbar")
            if normal_inf:
                h2_text = normal_inf[0].cssselect("h2")
                if h2_text:
                    span_text = h2_text[0].cssselect("span")
                    if span_text:
                        bus_name = self.getText(span_text[0])
                    em_text = h2_text[0].cssselect("em.claim-status")
                    if em_text:
                        settled = self.getText(em_text[0])
                show_text = normal_inf[0].cssselect("a.kb-show-url")
                if show_text:
                    bus_domain = self.getText(show_text[0])

                auth_text = normal_inf[0].cssselect("div.auth-siteinfo-comt")
                if auth_text:
                    span_name = auth_text[0].cssselect("span.compname-txt")
                    if span_name:
                        company_name = self.getText(span_name[0])
                    starttime_text = auth_text[0].cssselect("p.start-time")
                    if starttime_text:
                        est_time = self.cut_keyword(self.getText(starttime_text[0]).strip())
                    address = auth_text[0].cssselect("p.businessaddr")
                    if address:
                        bus_address = self.cut_keyword(self.getText(address[0]).strip())
                    trade = auth_text[0].cssselect("p.trade")
                    if trade:
                        industry_type = self.cut_keyword(self.getText(trade[0]).strip())

                # print bus_name
                # print bus_domain
                # print settled
                # print company_name
                # print est_time
                # print bus_address
                # print industry_type
                inf_item["bus_name"] = bus_name
                inf_item["bus_domain"] = bus_domain
                inf_item["settled"] = settled
                inf_item["company_name"] = company_name
                inf_item["est_time"] = est_time
                inf_item["bus_address"] = bus_address
                inf_item["industry_type"] = industry_type
                extractor_result["inf_item"] = inf_item

                moreinfo = tree.cssselect("p.siteinfo-xinurl")
                if moreinfo:
                    a_moreinfo = moreinfo[0].cssselect("a")
                    if a_moreinfo:
                        href = a_moreinfo[0].get("href")
                        extractor_result["qua_inf"] = href

                return extractor_result
            return 1
        except:
            print traceback.format_exc()
            return -1

    # 点评
    def extractor_comment_js(self, body):
        try:
            ext_result = dict()
            js_body = json.loads(body)
            comment_list = list()
            total_page = js_body["data"]["ext"]["total"]
            now_page = js_body["data"]["ext"]["page"]
            total_record = js_body["data"]["ext"]["totalrecord"]

            tpl_body = js_body["data"]["tpl"]
            tree = fromstring(tpl_body.decode('utf-8', 'ignore'))
            li_list = tree.cssselect("li.kb-list-item")
            if li_list:
                for li_one in li_list:
                    comment_item = dict()
                    author = ""
                    star_level = 0
                    com_time = ""
                    answer = ""
                    pics = ""
                    is_fine = 0

                    class_name = li_one.get("class")
                    if class_name.find(u"kb-essence") > -1:
                        is_fine = 1

                    h5_text = li_one.cssselect("h5")
                    if h5_text:
                        a_href = h5_text[0].cssselect("a")
                        if a_href:
                            author = self.getText(a_href[0])
                        span_text = h5_text[0].cssselect("span.time")
                        if span_text:
                            com_time = self.getText(span_text[0])
                            if com_time.find("-") > -1:
                                pass
                            else:
                                com_time = datetime.today()

                        i_text = h5_text[0].cssselect("i")
                        if i_text:
                            class_name_i = i_text[0].get("class")
                            end_index_i = class_name_i.rfind("-")
                            try:
                                star_level = int(class_name_i[end_index_i + 1:])
                            except:
                                pass

                    li_detail = li_one.cssselect("div.kb-comt-detail")
                    if li_detail:
                        answer, pics = self.extractor_content_images(etree.tostring(li_detail[0], encoding="utf-8"))

                    comment_item["author"] = author
                    comment_item["star_level"] = star_level
                    comment_item["com_time"] = com_time
                    comment_item["answer"] = answer
                    comment_item["pics"] = pics
                    comment_item["is_fine"] = is_fine
                    comment_list.append(comment_item)

            ext_result["comment_list"] = comment_list
            ext_result["total_page"] = total_page
            return ext_result
        except:
            print traceback.format_exc()
            return -1

    # 资质信息
    def extractor_qualify_js(self, body):
        try:
            js_body = json.loads(body)

            qua_item = dict()
            data = js_body["data"]
            reg_number = data["regNo"]
            org_code = data["orgNo"]
            legal_person = data["legalPerson"]
            bus_status = data["openStatus"]
            start_date = data["startDate"]
            bus_term = data["openTime"]
            enterpraise_type = data["entType"]
            institution_type = data["orgType"]
            adm_division = data["district"]
            reg_department = data["authority"]
            reg_address = data["regAddr"]

            shareholder = ""
            key_person = ""
            shareholder_list = data["shares"]
            for shareholder_one in shareholder_list:
                shareholder = str(shareholder_one) + ","
            key_person_list = data["directors"]
            for key_one in key_person_list:
                key_person = str(key_one) + ","

            # print reg_number
            # print org_code
            # print legal_person
            # print bus_status
            # print bus_term
            # print enterpraise_type
            # print start_date
            # print institution_type
            # print adm_division
            # print reg_department
            # print reg_address
            # print shareholder
            # print key_person

            qua_item["reg_number"] = reg_number
            qua_item["org_code"] = org_code
            qua_item["legal_person"] = legal_person
            qua_item["bus_status"] = bus_status
            qua_item["bus_term"] = bus_term
            qua_item["enterpraise_type"] = enterpraise_type
            qua_item["start_date"] = start_date
            qua_item["institution_type"] = institution_type
            qua_item["adm_division"] = adm_division
            qua_item["reg_department"] = reg_department
            qua_item["reg_address"] = reg_address
            qua_item["shareholder"] = shareholder
            qua_item["key_person"] = key_person

            return qua_item
        except:
            print traceback.format_exc()
            return -1

    def extractor_qualify_execjs(self, body):
        try:
            ext_result = dict()
            mxi_middle = re.findall(r"function mix(.*?)\(function", body)
            if mxi_middle:
                js_exe = "function mix" + mxi_middle[0]

            tkids = re.findall(r"tk = document.getElementById\('(.*?)'", body)
            if tkids:
                tk_id = tkids[0]

            attributes = re.findall(r"\).getAttribute\('(.*?)'\)", body)
            if attributes:
                tk_attribute = attributes[0]

            # print r"id=\"%s\".*?%s=\"(.*?)\"" % (tk_id, tk_attribute)
            attr_text = re.findall(r"id=\"%s\".*?%s=\"(.*?)\"" % (tk_id, tk_attribute), body)
            if attr_text:
                tk = attr_text[0]

            baiducode_content = re.findall(r"id=\"baiducode\">(.*?)<", body)
            if baiducode_content:
                bid = baiducode_content[0]

            ctx = execjs.compile(js_exe)
            tot = ctx.call("mix", tk, bid)

            pids = re.findall(r'result.*?pid\":\"(.*?)\"', body)
            if pids:
                pid = pids[0]

            ext_result["pid"] = pid
            ext_result["tot"] = tot
            return ext_result
        except:
            print traceback.format_exc()
            return -1

    def cut_keyword(self, keyword):
        start_index = keyword.find(u"：")
        return keyword[start_index + 1:]

    def extractor_content_images(self, content_images):
        try:
            author = "%s" % str(content_images)
            pics = ""
            img_srcs = re.findall(r"""src=\"(.*?)\"""", author)
            if img_srcs:
                for i, img_one in enumerate(img_srcs):
                    # if str(img_one).find("zhstatic.zhihu.com") > -1:
                    #     continue
                    # else:
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
    sxfile = open("qua.txt", "rb")
    content = sxfile.read()
    sxfile.close()
    returntext = extractor.extractor_qualify_execjs(content)
    print returntext
    print "http://xin.baidu.com/detail/basicAjax?pid=%s&tot=%s" % (returntext["pid"], returntext["tot"])

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


