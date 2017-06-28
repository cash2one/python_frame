# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 11:23:19 2016

@author: zhangle
"""

from spider.spider import SpiderStore
from spider import config
from store_mysql import StoreMysql
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class _39DiseasesStore(SpiderStore):
    """
    39健康疾病存储器
    Attributes:
        fields: 用于保持抽取器字典的key与数据库字段的对应关系，
        如果结果字典的某个key不包含在fields中，则将直接使用key作为字段名
    """

    def __init__(self):
        self.fields = {}

    def store(self, results, type=1, field=None):
        """
        将一个数组存储到指定的存储媒介中
        Args:
            reuslts: 数组，每条为一个完整记录，记录由字典格式保存
            type: 1-只插入（出错则忽略），2-只更新（原记录不存在则忽略），3-插入更新（无记录则插入，有记录则更新）
            field: 更新时的唯一索引字段，即根据词字段判断是否为同一条记录，作为where条件
        Returns:
            1: 正常, 0: 出错
        """
        if len(results) > 0:
            db = StoreMysql(config.HEALTH_DB['host'], config.HEALTH_DB['user'],
                                 config.HEALTH_DB['password'], config.HEALTH_DB['db'])
            for result in results:
                try:
                    for key in result:
                        result[key] = MySQLdb.escape_string(str(result[key]))
                    if type == 1:
                        l = db.query('select id from health_diseases where disease_id = "%s"' % result['disease_id'])
                        if len(l) == 0:
                            db.save('health_diseases', result)
                    elif type == 2:
                        db.update('health_diseases', result, field)
                except Exception, e:
                    pass
