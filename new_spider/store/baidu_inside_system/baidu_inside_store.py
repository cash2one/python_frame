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
from datetime import datetime, timedelta

reload(sys)
sys.setdefaultencoding('utf8')

class SpiderBaseStore(SpiderStore):

    def __init__(self, connection):
        self.connection = connection
        # self.db = StoreMysql(**config.baidu_spider_move)

    # def find_task_data(self, task_count):
    #     task_results = tuple()
    #     results = self.find_tasks_by_count(task_count)


    # def find_tasks_by_count(self, task_count):
    #     db = StoreMysql(**self.connection)
    #     try:
    #         sql = " select * from task WHERE state <> 1   and fileName = '%s' and isEqual in (0,1) limit %d ;" % (
    #         filename, count)
    #         result = db.query(sql)
    #         db.close()
    #         return result
    #     except Exception:
    #         print traceback.format_exc()
    #         db.close()
    #         return -1


    def find_task_lists(self, task_count):
        '''
        获取查排名任务
        :return:
        '''
        task_results = tuple()
        filename_list = self.find_filename_list()
        # 根据文件名取任务  限制任务数
        if len(filename_list) > 0:
            count = task_count / len(filename_list)
            for filename in filename_list:
                results = self.find_tasks_by_filename(filename, count)
                if results != -1:
                    task_results = task_results + results
        # 更新状态 state
        if len(task_results) > 0:
            change_state_ids = list()
            for task in task_results:
                change_state_ids.append(task[0])
                if len(change_state_ids) == 50:
                    self.update_ids("task", change_state_ids)
                    change_state_ids = list()
            if len(change_state_ids) > 0:
                self.update_ids("task", change_state_ids)
        return task_results

    def find_filename_list(self):
        db = StoreMysql(**config.baidu_spider_move)
        try:
            file_name_list = list()
            # "and device = 'mobile'"
            sql = """select fileName from task WHERE  state <> 1 and customer =0 and isEqual in (0,1)  GROUP BY fileName"""
            results = db.query(sql)
            for result in results:
                file_name_list.append(result[0])
            db.close()
            return file_name_list
        except Exception:
            print traceback.format_exc()
            db.close()
            return -1

    def find_tasks_by_filename(self, filename, count):
        db = StoreMysql(**self.connection)
        try:
            sql = " select * from task WHERE state <> 1   and fileName = '%s' and isEqual in (0,1) limit %d ;" % (filename, count)
            result = db.query(sql)
            db.close()
            return result
        except Exception:
            print traceback.format_exc()
            db.close()
            return -1

    def store_table(self, results, table="", type=1, field=None):
        db = StoreMysql(**config.baidu_spider_move)
        try:
            if len(results) > 0:
                for result in results:
                    if type == 1:
                        for key in result:
                            result[key] = MySQLdb.escape_string(str(result[key]))
                        return_state = db.save(table, result)
                    elif type == 2:
                        for key in result:
                            result[key] = MySQLdb.escape_string(str(result[key]))
                        return_state = db.update(table, result, field)
                db.close()
                return return_state
        except Exception:
            print(traceback.format_exc())
            db.close()
            return -1

    def store_table_db(self, results, table="", type=1, field=None, db_connnection=""):
        db = StoreMysql(**db_connnection)
        return_state = 0
        if len(results) > 0:
            for result in results:
                try:
                    if type == 1:
                        for key in result:
                            result[key] = MySQLdb.escape_string(str(result[key]))
                        return_state = db.save(table, result)
                    elif type == 2:
                        for key in result:
                            result[key] = MySQLdb.escape_string(str(result[key]))
                        db.update(table, result, field)
                except Exception, e:
                    print(traceback.format_exc())
                    return -1
                finally:
                    if db is not None:
                        db.close()
            return return_state

    def store_update(self, result, ty, field):
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
        db = StoreMysql(**self.connection)
        try:
            for single_id in ids:
                sql = "delete from %s  where  id = %d " % (table, single_id['id'])
                db.do(sql)
            db.close()
        except:
            print traceback.format_exc()
            db.close()

    def update_ids(self, table_name, ids):
        db = StoreMysql(**self.connection)
        try:
            for single_id in ids:
                sql = "update  %s  set  state = 1 where id = %d  " % (table_name, single_id)
                db.do(sql)
            db.close()
        except Exception:
            print traceback.format_exc()
            db.close()

    def delete_by_id(self, table_name, table_id):
        db = StoreMysql(**config.baidu_spider_move)
        try:
            sql = "delete from %s where id = %d" % (table_name, table_id)
            db.do(sql)
            db.close()
        except Exception:
            print traceback.format_exc()
            db.close()

    def find_rank_by_taskid(self, table_name, table_id):
        db = StoreMysql(**config.baidu_spider_move)
        try:
            sql = "select * from %s where taskId = %d " % (table_name, table_id)
            result = db.query(sql)
            db.close()
            return result
        except Exception:
            print traceback.format_exc()
            db.close()

    def find_task_by_id(self, table_name, table_id):
        db = StoreMysql(**config.baidu_spider_move)
        try:
            sql = "select * from %s where id = %d " % (table_name, table_id)
            result = db.query(sql)
            db.close()
            return result
        except Exception:
            print traceback.format_exc()
            db.close()

    def reset_task(self, interval_time):
        db = StoreMysql(**config.baidu_spider_move)
        try:
            expire_time = str(datetime.now() + timedelta(seconds=-interval_time))
            sql = "update task set state = 0 where  isEqual in (0, 1) and update_time < '%s' " % expire_time
            # print sql
            result = db.do(sql)
            db.close()
            return result
        except Exception:
            print traceback.format_exc()
            db.close()

    def judge(self):
        if self.db is None:
            self.db = StoreMysql(**config.baidu_spider_move)

    def test_task(self):
        db = StoreMysql(**config.baidu_spider_move)
        try:
            sql = """insert into task(urlAddress,searchWay,page,device,keyword,state,fileName,isEqual,customer)
            values("1", "pc", 5,"pc","jjd",0, "1.csv", 0,1);"""
            # print sql
            result = db.do(sql)
            db.close()
            return result
        except Exception:
            print traceback.format_exc()
            db.close()

def test():
    store = SpiderBaseStore()
    store.test_task()
    # store.delete_by_id("task", 12)

if __name__ == '__main__':
    test()
