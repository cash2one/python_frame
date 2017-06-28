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

class SourceExtractor (object):

    '''
    '''
    def extractor_html(self, body):
        try:
            tree = fromstring(body.decode("utf-8"), "ignore")  # 这种方式 可使用cssselect  不然linux 不能使用
            wrappers = tree.cssselect("div.row-top5 > div.wrapper")
            if wrappers:
                result_list = list()
                for wrapper in wrappers:
                    h3_list = wrapper.cssselect('h3')
                    if h3_list:
                        for h3_one in h3_list:
                            a_list_one = h3_one.cssselect("a")[0]
                            url_id = self.cut_keyword_href(a_list_one.get("href"))
                            district_name = a_list_one.text

                            item = dict()
                            item["url_id"] = url_id
                            item["district_name"] = district_name
                            item["district_state"] = 3
                            result_list.append(item)
                        return result_list
                    else:
                        return 1
            else:
                return 1
        except:
            print traceback.format_exc()
            # print "body:%s" % str(body)[0: 50]
            return -1

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
    sxfile = open("jspage1.txt", "rb")
    content = sxfile.read()
    returntext = extractor.extractor_html(content)
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


