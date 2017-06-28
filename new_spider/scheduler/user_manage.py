# -*- coding: utf8 -*-
import os
import sys
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'store'))
sys.path.append(os.path.join(PROJECT_PATH, 'util'))
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
from store_mysql import StoreMysql
import redis
import config
from util.util_md5 import UtilMD5
import traceback
reload(sys)
sys.setdefaultencoding('utf8')


class UserManage(object):

    def __init__(self):
        self.userConfigs = config.USER_CONFIGS
        self.db = StoreMysql(**config.DB_SPIDER)

    def add_user(self, user):
        user_id = self.db.save('user', user)
        if user_id > 0:
            urls_table = self.userConfigs['urlsTable'] % user_id
            configs_table = self.userConfigs['configsTable'] % user_id
            self.db.do('create table %s like urls_1' % urls_table)
            self.db.do('create table %s like configs_1' % configs_table)

    def update_config(self):
        try:
            rds = redis.StrictRedis(**config.REDIS)
            rows = self.db.query('select id, weight, low_priority_task_limit, normal_task_limit, '
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
            traceback.format_exc()

def main():
    u = UserManage()
    u.add_user({'user': 'xuliang', 'password': UtilMD5.md5('xlspider'), 'weight': 1})
    u.update_config()

if __name__ == '__main__':
    main()
