# -*- coding: utf8 -*-
import os
import sys
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
sys.path.append(os.path.join(PROJECT_PATH, 'store'))
sys.path.append(os.path.join(PROJECT_PATH, 'util'))

from spider import config
from store_mysql import StoreMysql
import time
sys.setdefaultencoding('utf8')
reload(sys)


class setSpider(object):

    def __init__(self):
        pass
    def run(self):
        try:
            db = StoreMysql(**config.SITEANALYSTAPi_DB)
            sql = 'SELECT id,url,spidertype,user from site_domain where id not in(select urlid from site_basicinfo)'
            results = db.query(sql)
            if len(results)<1:
                return True
            for r in results:
                insql = 'insert into site_basicinfo(`url`,`urlid`,`spidertype`,`user`,`createtime`)values("%s",%s,%s,"%s",now())' %(r[1],r[0],r[2],r[3])
                db.do(insql)
                print insql
        except Exception, e:
	    print str(e),'==================='
def Main():
    spider = setSpider()
    spider.run()

if __name__ == '__main__':
    Main()
