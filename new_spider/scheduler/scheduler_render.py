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
reload(sys)
sys.setdefaultencoding('utf8')


class Scheduler(object):

    def __init__(self, task_type):
        self.redisPool = redis.ConnectionPool(**config.REDIS)
        self.dbParam = config.DB_SPIDER
        self.configs = config.TASK_CONFIGS[task_type]
        self.timeIntervalConfigs = config.TASK_TIME_INTERVAL_CONFIGS[task_type]
        self.userConfigs = config.USER_CONFIGS
        self.mb4_regex = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
        self.log = UtilLogger('scheduler', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs/scheduler_render'))

    def init(self):
        """
        初始化系统用户、用户权重、用户任务限制信息到redis里面
        """
        db = StoreMysql(**self.dbParam)
        try:
            rds = redis.StrictRedis(connection_pool=self.redisPool)
            rows = db.query('select id, weight, low_priority_task_limit, normal_task_limit, '
                            'high_priority_task_limit from user where status = 1')
            rds.delete(self.userConfigs['userListKey'])
            rds.delete(self.userConfigs['userWeightKey'])
            for row in rows:
                rds.lpush(self.userConfigs['userListKey'], row[0])
                rds.hset(self.userConfigs['userWeightKey'], row[0], row[1])
                rds.hmset(self.userConfigs['userTaskLimitKey'] % row[0], {
                    '1': row[2],
                    '2': row[3],
                    '3': row[4]
                })
        except Exception:
            self.log.error(traceback.format_exc())
            raise
        finally:
            db.close()

    def __push_task(self, db, rds, user_id, priority, task_types, task_size, task_queue_key, single=False, concurrent=False):
        """
        根据用户和优先级，分表查询任务，放到任务队列中
        """
        try:
            urls_table = self.userConfigs['urlsTable'] % int(user_id)
            configs_table = self.userConfigs['configsTable'] % int(user_id)
            fields = ''
            single_condition = ' and b.single = 0'
            concurrent_condition = ' and b.concurrent_num = 0'
            if single:
                single_condition = ' and b.single = 1'
            if concurrent:
                fields = ', a.config_id, b.concurrent_num'
                concurrent_condition = ' and b.concurrent_num > 0'
            sql = 'select a.id, a.url, a.type, b.header, b.post_data, b.redirect, b.store_type, b.param %s ' \
                  'from %s a join %s b on a.config_id = b.id where a.status = 0 and b.priority = %d' \
                  ' %s %s and a.type in (%s) order by a.create_time limit %d' \
                  % (fields, urls_table, configs_table, priority, single_condition, concurrent_condition, task_types, task_size)
            tasks = db.query(sql)
            if len(tasks) == 0:
                return 0
            ids = list()
            task_list = list()
            if concurrent:
                concurrent_dict = {}
            for task in tasks:
                if concurrent:
                    if task[8] not in concurrent_dict:
                        concurrent_dict[task[8]] = 0
                    if concurrent_dict[task[8]] < task[9]:
                        concurrent_dict[task[8]] += 1
                    else:
                        continue
                ids.append(str(task[0]))
                t = {'id': str(user_id) + '_' + str(task[0]), 'url': task[1], 'type': task[2], 'redirect': task[5],
                     'store_type': task[6], 'param': task[7]}
                if task[3]:
                    t['header'] = task[3]
                if task[4]:
                    t['data'] = task[4]
                task_list.append(json.dumps(t))
            if len(ids) > 0:
                db.do('update %s set status = 1 where id in (%s)' % (urls_table, ','.join(ids)))
                rds.rpush(task_queue_key, *tuple(task_list))
            return len(ids)
        except Exception, e:
            self.log.error(traceback.format_exc())
        return 0

    def __get_weight_queue(self, rds):
        """
        获取用户权重，然后组织成队列来决定各个用户抓取频率
        """
        weight_queue = Queue()
        users = rds.lrange(self.userConfigs['userListKey'], 0, -1)
        for user in users:
            weight = rds.hget(self.userConfigs['userWeightKey'], user) or 0
            for i in range(int(weight)):
                weight_queue.put(user)
        return weight_queue

    def push(self, task_type):
        """
        从数据库中取任务到redis任务队列里面，task_type代表任务类型，有效的参数有：Common、Single、Concurrent
        """
        db = StoreMysql(**self.dbParam)
        rds = redis.StrictRedis(connection_pool=self.redisPool)
        task_queue_key = self.configs['taskQueue%sKey' % task_type]
        task_max_send_num = self.configs['taskMaxSendNum%s' % task_type]
        task_types_in_database = self.configs['taskTypesInDatabase']
        push_interval = self.timeIntervalConfigs['push%s' % task_type]
        max_size = 0
        for k in task_max_send_num:
            max_size += task_max_send_num[k]
        single = False
        concurrent = False
        if task_type in ['Single']:
            single = True
        if task_type in ['Concurrent']:
            concurrent = True
            max_size = 1
        weight_queue = self.__get_weight_queue(rds)
        start_time = time.time()
        while True:
            users = list()
            sended_size = 0
            while weight_queue.qsize() > 0:
                if rds.llen(task_queue_key) < max_size:
                    user_id = weight_queue.get()
                    priority = 3
                    left_size = 0
                    while priority > 0:
                        max_size = task_max_send_num[str(priority)] + left_size
                        size = self.__push_task(db, rds, user_id, priority, task_types_in_database,
                                                max_size, task_queue_key, single, concurrent)
                        sended_size += size
                        left_size = max_size - size
                        priority -= 1
                    users.append(user_id)
                else:
                    time.sleep(push_interval)
            current_time = time.time()
            if current_time - start_time > 600:
                start_time = current_time
                weight_queue = self.__get_weight_queue(rds)
            else:
                for user in users:
                    weight_queue.put(user)
            if sended_size == 0:
                time.sleep(push_interval)
            else:
                sended_size = 0

    def save(self):
        """
        从redis结果队列里面获取结果并处理
        """
        db = StoreMysql(**self.dbParam)
        rds = redis.StrictRedis(connection_pool=self.redisPool)
        result_queue_key = self.configs['resultQueueKey']
        task_max_fail_times = self.configs['taskMaxFailTimes']
        task_fail_times_key = self.configs['taskFailTimesKey']
        save_interval = self.timeIntervalConfigs['save']
        while True:
            while rds.llen(result_queue_key) > 0:
                try:
                    v = rds.lpop(result_queue_key)
                    if v is None:
                        continue
                    results = json.loads(v)
                    for result in results:
                        user_id, url_id = result['id'].split('_')
                        urls_table = self.userConfigs['urlsTable'] % int(user_id)
                        url_type = int(result['type'])
                        if result['status'] == '3':
                            retry_times = rds.hincrby(task_fail_times_key, result['url'], 1)
                            if retry_times <= task_max_fail_times:
                                db.do('update %s set status = 0 where id = %s' % (urls_table, url_id))
                                continue
                            else:
                                rds.hdel(task_fail_times_key, result['url'])
                        if 'store_type' in result and int(result['store_type']) == 2:
                            sql = 'update %s set status = %s where id = %s' % (urls_table, result['status'], url_id)
                            val = {'url': result['url'], 'status': result['status'], 'result': result['result'],
                                   'header': result['header'], 'id': url_id}
                            result_store_key = self.configs['resultStoreKey'] % (int(user_id), url_type)
                            rds.hset(result_store_key, result['url'], json.dumps(val))
                        else:
                            res = self.mb4_regex.sub('', result['result'])
                            sql = 'update %s set status = %s, result = "%s", header = "%s" where id = %s' \
                                  % (urls_table, result['status'], MySQLdb.escape_string(res),
                                     MySQLdb.escape_string(result['header']), url_id)
                        db.do(sql)
                except Exception:
                    self.log.error(traceback.format_exc())
            time.sleep(save_interval)

    def reset(self):
        """
        发送到redis队列中后6分钟还没有获取到结果的任务重新抓取
        """
        db = StoreMysql(**self.dbParam)
        rds = redis.StrictRedis(connection_pool=self.redisPool)
        users = rds.lrange(self.userConfigs['userListKey'], 0, -1)
        reset_interval = self.timeIntervalConfigs['reset']
        start_time = time.time()
        while True:
            try:
                for user in users:
                    urls_table = self.userConfigs['urlsTable'] % int(user)
                    expire_time = str(datetime.now() + timedelta(minutes=-6))
                    db.do('update %s set status = 0 where status = 1 and update_time < "%s" and type in (%s)'
                          % (urls_table, expire_time, self.configs['taskTypesInDatabase']))
                current_time = time.time()
                if current_time - start_time > 600:
                    start_time = current_time
                    users = rds.lrange(self.userConfigs['userListKey'], 0, -1)
            except Exception:
                self.log.error(traceback.format_exc())
            time.sleep(reset_interval)

    def clear(self):
        result_store_key = self.configs['resultStoreKey']
        clear_interval = self.timeIntervalConfigs['clear']
        sqls = {
            'select id from %s where expire_time < now()': True,
            'select a.id from %s a left join %s b on a.id = b.config_id where b.config_id is null '
            'and a.create_time < "%s"': False
        }
        while True:
            db = StoreMysql(**self.dbParam)
            try:
                rds = redis.StrictRedis(connection_pool=self.redisPool)
                users = rds.lrange(self.userConfigs['userListKey'], 0, -1)
                for user in users:
                    urls_table = self.userConfigs['urlsTable'] % int(user)
                    configs_table = self.userConfigs['configsTable'] % int(user)
                    for sql in sqls:
                        if sqls[sql]:
                            configs = db.query(sql % configs_table)
                        else:
                            expire_time = str(datetime.now() + timedelta(minutes=-2))
                            configs = db.query(sql % (configs_table, urls_table, expire_time))
                        config_ids = list()
                        for c in configs:
                            config_ids.append(str(c[0]))
                        if len(config_ids) > 0:
                            db.do('delete from %s where id in (%s)' % (configs_table, ','.join(config_ids)))
                            if sqls[sql]:
                                rows = db.query('select id, url from %s where config_id in (%s)'
                                                % (urls_table, ','.join(config_ids)))
                                url_ids = list()
                                urls = list()
                                for r in rows:
                                    url_ids.append(str(r[0]))
                                    urls.append(str(r[1]))
                                if len(url_ids) > 0:
                                    rds.hdel(result_store_key, *urls)
                                    db.do('delete from %s where id in (%s)' % (urls_table, ','.join(url_ids)))
            except Exception:
                self.log.error(traceback.format_exc())
            finally:
                db.close()
            time.sleep(clear_interval)

    def record(self):
        record_interval = self.timeIntervalConfigs['record']
        user_sended_key = self.userConfigs['userTaskSendedKey']
        while True:
            db = StoreMysql(**self.dbParam)
            try:
                rds = redis.StrictRedis(connection_pool=self.redisPool)
                users = db.query('select id from user')
                yesterday_date = str((datetime.now() + timedelta(days=-1)).date())
                for user in users:
                    user_id = user[0]
                    data = {'user_id': user_id, 'date': yesterday_date}
                    key = user_sended_key % (user_id, yesterday_date)
                    data['low_priority_task_num'] = rds.hget(key, 1) or 0
                    data['normal_task_num'] = rds.hget(key, 2) or 0
                    data['high_priority_task_num'] = rds.hget(key, 3) or 0
                    rds.delete(key)
                    if len(data) > 2:
                        db.save('logs', data)
            except Exception:
                self.log.error(traceback.format_exc())
            finally:
                db.close()
            time.sleep(record_interval)

    def run(self, push_num=1, push_single_num=0, push_concurrent_num=0,
            save_num=10, reset_num=1, clear_num=0, record_num=0):
        # self.init()
        threads = list()
        for i in range(0, push_num):
            threads.append(Thread(target=self.push, args=('Common',)))
        for i in range(0, push_single_num):
            threads.append(Thread(target=self.push, args=('Single',)))
        for i in range(0, push_concurrent_num):
            threads.append(Thread(target=self.push, args=('Concurrent',)))
        for i in range(0, save_num):
            threads.append(Thread(target=self.save))
        for i in range(0, reset_num):
            threads.append(Thread(target=self.reset))
        for i in range(0, clear_num):
            threads.append(Thread(target=self.clear))
        for i in range(0, record_num):
            threads.append(Thread(target=self.record))
        for thread in threads:
            thread.start()


def main():
    scheduler = Scheduler(config.TASK_TYPE_RENDER)
    scheduler.run(1, 0, 0, 10, 1, 0, 0)

if __name__ == '__main__':
    main()
