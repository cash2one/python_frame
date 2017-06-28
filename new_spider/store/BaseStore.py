# -*- coding: utf8 -*-
import os
import sys

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
sys.path.append(os.path.join(PROJECT_PATH, 'store'))
from spider.spider import SpiderStore
from spider import config
from store_mysql import StoreMysql
import MySQLdb
import traceback
import re

reload(sys)
sys.setdefaultencoding('utf8')

class BaseStore(SpiderStore):

    def __init__(self, connection=""):
        self.db = StoreMysql(**connection)

    def store_table(self, results, table="", type=1, field=None):
        if len(results) > 0:
            for result in results:
                try:
                    if type == 1:
                        for key in result:
                            result[key] = MySQLdb.escape_string(str(result[key]))
                        return_state = self.db.save(table, result)
                        # for i in xrange(0, 2):
                        #     return_state = self.db.save(table, result)
                        #     print return_state
                        #     if return_state != -1:
                        #         break
                    elif type == 2:
                        for key in result:
                            result[key] = MySQLdb.escape_string(str(result[key]))
                        self.db.update(table, result, field)
                except Exception, e:
                    print(traceback.format_exc())
                    return -1
            return return_state

    def store_table_db(self, results, table="", type=1, field=None):
        if len(results) > 0:
            for result in results:
                try:
                    if type == 1:
                        for key in result:
                            result[key] = MySQLdb.escape_string(str(result[key]))
                        return_state = self.db.save(table, result)
                        # for i in xrange(0, 2):
                        #     return_state = self.db.save(table, result)
                        #     print return_state
                        #     if return_state != -1:
                        #         break
                    elif type == 2:
                        for key in result:
                            result[key] = MySQLdb.escape_string(str(result[key]))
                        self.db.update(table, result, field)
                except Exception, e:
                    print(traceback.format_exc())
                    return -1
            return return_state

    def store_update(self, result, ty, field):
        i = 0
        for key in result:
            if result[key] and key != field:
                result[key] = MySQLdb.escape_string(str(result[key]))
                i += 1
        if i > 0:
            self.db.update(ty, result, field)

    def store_job(self, result, ty, field):
        i = 0
        for key in result:
            if result[key] and key != field:
                result[key] = MySQLdb.escape_string(str(result[key]))
                i += 1
        if i > 0:
            self.db.update(ty, result, field)

    def store_insert(self, result, ty):
        for key in result:
            result[key] = MySQLdb.escape_string(str(result[key]))
        self.db.save(ty, result)

    def deleteByids(self, ids, table=""):
        for single_id in ids:
            try:
                sql = "delete from %s  where  id = %d " % (table, single_id['id'])
                self.db.query(sql)
            except Exception, e:
                print e
                pass

    # def updateByids(self, ids):
    #     # print ids
    #     for single_id in ids:
    #         try:
    #             sql = "update  %s  set  spiderstat =1 where id = %d  " % single_id['id']
    #             self.db.do(sql)
    #         except Exception, e:
    #             print e
    #             pass

def test():
    pass
    # store = OutlinksSourceStore()
    # # fileList = store.find_task_fileName_priority()
    # # print len(fileList)
    # # for user in fileList:
    # #     print user
    # # store.store([{
    # #     'domain': 'www.baidu.com',
    # #     'batch': '2'
    # # }])
    # results = store.getTaskList(100)
    # print len(results)
    # print results

if __name__ == '__main__':
    test()
