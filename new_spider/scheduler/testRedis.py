# -*- coding: utf8 -*-
import os
import sys
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'store'))
sys.path.append(os.path.join(PROJECT_PATH, 'util'))
from store_mysql import StoreMysql
from util_log import UtilLogger
import redis
import config
import MySQLdb
import time
from datetime import datetime, timedelta
from threading import Thread
import json
import re
from Queue import Queue
import traceback

import base64
reload(sys)
sys.setdefaultencoding('utf8')

class Scheduler(object):

    def __init__(self, task_type):
        REDIS = {
                    'host': '182.254.244.167',
                    'port': 6379,
                    'db': 0,
                    'password': 'sunxiang'
                }
        # REDIS = {
        #     'host': '182.254.159.183',
        #     # 'host': '10.133.195.238',
        #     'port': 6379,
        #     'db': 0,
        #     'password': '@redisForSpider$'
        # }

        self.redisPool = redis.ConnectionPool(**REDIS)
        # self.dbParam = config.DB_SPIDER
        # self.configs = config.TASK_CONFIGS[task_type]
        # self.timeIntervalConfigs = config.TASK_TIME_INTERVAL_CONFIGS[task_type]
        # self.userConfigs = config.USER_CONFIGS
        # self.mb4_regex = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        # self.log = UtilLogger('scheduler', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs/scheduler_html'))

    def test(self):

        rds = redis.StrictRedis(connection_pool=self.redisPool)
        # result = rds.lrange("sxsx", 0, 10)
        # count = len(result)
        # print result[2]
        #
        # for i, colour in enumerate(result):
        #     print i, colour

        # for i in range(1, count):
        #     print result.index(i)
        # for sx in result:
        #     print sx
        # print result

        # rds.lpush('abs', 111)
        # rds.hdel('abs')
        # retry_times = rds.hincrby('sxtest', 'html', 1)
        # print retry_times
        # rds.hdel('sxtest', 'html')

        # rds.setnx('sxsxsx', '111')         #只有name不存在时，执行设置操作（添加）
        # print rds.get("sun", "k1")

        # rds.mset(k1='v1', k2='v2')
        # print rds.mget("k1", "k2")

        # rds.mset({'k2': 'v1', 'k3': 'v2'})  #设置多个值

        # rds.hset('sun', 'k1', 'v2')
        rds.hset('sun', '111', '''{'k2': 'v1', 'k3': 'v2'}''')
        print rds.hget('sun', '111')
        # rds.hdel('sun', '111')
        # print rds.hgetall('sun')
        # print rds.hkeys('sun')
        # print 'success'

def main():
    import datetime
    scheduler = Scheduler(config.TASK_TYPE_HTML)
    scheduler.test()

if __name__ == '__main__':
    main()
