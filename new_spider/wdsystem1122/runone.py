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
            sql = 'select id from site_basicinfo where spidertype=0'
            res = db.query(sql)
            if not res:
                return False
            for r in res:
                usql = 'update site_basicinfo set spidertype=-1 where id=%s' % (r[0])
                db.do(usql)
            try:
                
                cmd= 'python aizhanbasic_spider.py -1 >/dev/null &'
                os.system(cmd)
                time.sleep(60)
                cmd= 'python aizhanrank_spider.py -1 >/dev/null &'
                os.system(cmd)
                time.sleep(60)
                cmd= 'python enginesogou_spider.py -1 >/dev/null &'
                os.system(cmd)
                time.sleep(60)
                cmd= 'python engineso_spider.py -1 >/dev/null &'
                os.system(cmd)
                time.sleep(60)
                cmd= 'python chinazbasic_spider.py -1 >/dev/null &'
                os.system(cmd)
                time.sleep(60)
                cmd= 'python enginebasic_spider.py -1 >/dev/null &'
                os.system(cmd)
                time.sleep(60)
                cmd= 'python seo_majbasic_spider.py -1 >/dev/null &'
                os.system(cmd)
                time.sleep(60)
                cmd= 'python beiannew_spider.py -1 >/dev/null &'
                os.system(cmd)
                time.sleep(60)
                cmd= 'python lishi_spider.py -1 >/dev/null &'
                os.system(cmd)
                time.sleep(60)
                print cmd
            except:
                pass
            nsql = 'update site_basicinfo set spidertype=-2 where spidertype=-1'
            db.do(nsql)
        except Exception, e:
	    print str(e),'==================='
def Main():
    spider = setSpider()
    spider.run()

if __name__ == '__main__':
    Main()
