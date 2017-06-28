# -*- coding: utf8 -*-
import traceback
import datetime
import re
import json
from lxml.html import fromstring
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# from store.sx_basestore import BaseStore

class SourceExtractor (object):

    '''
        返回 ext_result 列表
            列表中字典  dict
                data_value 编号
                city   地区名
    '''
    def extractor_district(self, body):
        try:
            str=body.split('{')[1].split('}')[0]
            strlist=str.split(',')
            returndoc =dict()
            ext_result = list()
            for item in strlist:
                returndoc=self.getdoc(item,returndoc)
                print returndoc
                ext_result.append(item)
            return ext_result
        except:
            print traceback.format_exc()
            # print "body:%s" % str(body)[0: 50]
            return -1

    '''
        列表页解析
        ext_result dict()
             url_list()   直接放链接
            next_url      下一页地址
    '''
    def extractor_list(self, body):
        try:
            ext_result = dict()
            tree = fromstring(body.decode('utf-8', 'ignore') )  # 这种方式 可使用cssselect  不然linux 不能使用
            # firstdiv=tree.cssselect('div.el')
            # container = tree.cssselect('div.dw_table')  # *行代码
            containers = tree.cssselect('div#resultList')
            pagination = tree.cssselect('div.p_in>ul>li')
            nexturl = ""
            if (pagination) > 0:
                for li in pagination:
                    if self.getText(li).find(u"下一页") > -1:
                        next_a = li.cssselect("a")
                        if next_a:
                            nexturl = next_a[0].get("href")
            url_list=list()
            if len(containers) > 0:
                for container in containers:
                    div_a = container.cssselect("a")
                    if div_a:
                        geturlid = div_a[0].get("href")
                        url_list.append(geturlid)
            ext_result["url_list"] = url_list
            ext_result["next_url"] = nexturl

            return 1
        except:
            print traceback.format_exc()
            # print "body:%s" % str(body)[0: 50]
            return -1

    def getdoc(self,item,returndoc):
      itemlist=item.split(':')
      name=itemlist[1].replace('\'','')
      value=itemlist[0].replace('\'','').strip()
      returndoc["data_value"]=value
      returndoc["city"]=name
      return returndoc
if __name__ == '__main__':
    # sx_store = BaseStore()
    # sx = HandleCsvDeal()
    extractor = SourceExtractor()
    sxfile = open("test.txt", "rb")
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
