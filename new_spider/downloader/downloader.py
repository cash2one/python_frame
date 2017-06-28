# -*- coding: utf8 -*-
from spider.spider import SpiderDownloader
import configs
from store_mysql import StoreMysql
from util.util_md5 import UtilMD5
import MySQLdb
import redis
import json
import urllib2
import urllib
from datetime import datetime
from datetime import timedelta
import traceback
import base64
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class SpiderRequest(object):
    """
    Args:
        headers: 字典，http头信息，
            举例，{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'}
        config: 字典，可为空，用于向下载中心发送优先级、并发数等相关信息，
            举例：{'concurrent_num':0, 'priority':2, expire_time: '2016-08-08 12:00:00', 'store_type': 1,
                   'redirect': 0, 'post_data': {}, 'param': {'capture_width': 1024, 'capture_height': 768}}
        urls: 数组，将要抓取的url及类型、过期时间等
            [{'url': 'http://www.baidu.com', 'type': 1},
            {'url': 'http://www.sina.com', 'type': 2}]

        config:
            conf_district_id 表示为地域，默认为0，即不指定地域，具体值参考district表
    """

    __slots__ = ['user_id', 'headers', 'config', 'urls']

    def __init__(self, user_id=None, headers=dict(), config=dict(), urls=list()):
        self.user_id = user_id
        self.headers = headers
        self.config = config
        self.urls = urls

    def downloader_set_param(self, mode):
        if self.user_id is None:
            raise RuntimeError('未指定user_id')
        url_type = None
        new_urls = list()
        for url in self.urls:
            if url_type is None:
                url_type = url['type']
            elif url_type != url['type']:
                raise RuntimeError('抓取类型不一致')
            new_url = dict()
            new_url['url'] = url['url']
            if 'unique_key' in url.keys():
                md5 = UtilMD5.md5(MySQLdb.escape_string(url['url']) + str(url['unique_key']))
            else:
                md5 = UtilMD5.md5(MySQLdb.escape_string(url['url']))
            new_url['md5'] = md5
            new_urls.append(new_url)

            url['unique_md5'] = md5
        if len(new_urls) > 0:
            params = {
                'user_id': self.user_id,
                'url_type': url_type,
                'header': self.headers,
                'redirect': 0,
                'priority': 2,
                'single': 0,
                'concurrent_num': 0,
                'store_type': 1,
                'urls': new_urls,
                'conf_district_id': 0
            }
            if 'conf_district_id' in self.config:
                params['conf_district_id'] = self.config['conf_district_id']
            if 'redirect' in self.config and self.config['redirect'] == 1:
                params['redirect'] = self.config['redirect']
            if 'priority' in self.config and self.config['priority'] in [1, 3]:
                params['priority'] = self.config['priority']
            if 'single' in self.config and self.config['single'] == 1:
                params['single'] = self.config['single']
            if 'concurrent_num' in self.config:
                params['concurrent_num'] = self.config['concurrent_num']
            if 'store_type' in self.config and self.config['store_type'] == 2:
                params['store_type'] = 2
            if 'expire_time' in self.config:
                params['expire_time'] = self.config['expire_time']
            if 'post_data' in self.config:
                params['post_data'] = self.config['post_data']
            if 'param' in self.config:
                params['param'] = self.config['param']
            if mode == 'db':
                for key in ['header', 'post_data', 'param']:
                # for key in ['header', 'param']:
                    if key in params:
                        params[key] = json.dumps(params[key])
            return params
        return None

    def downloader_get_param(self, mode):
        if self.user_id is None:
            raise RuntimeError('未指定user_id')
        url_type = None
        urls = list()
        md5s = list()
        for url in self.urls:
            if url_type is None:
                url_type = url['type']
            urls.append(url['url'])
            md5s.append(url['unique_md5'])
            # if 'unique_key' in url.keys():
            #     md5s.append(UtilMD5.md5(MySQLdb.escape_string(url['url']) + str(url['unique_key'])))
            # else:
            #     md5s.append(UtilMD5.md5(url['url']))
        params = {
            'user_id': self.user_id,
            'url_type': url_type,
            'urls': urls,
            'md5': md5s,
            'store_type': 1
        }
        if 'store_type' in self.config and self.config['store_type'] == 2:
            params['store_type'] = 2
        return params


class Downloader(SpiderDownloader):
    """
    通用下载器
    """

    def __init__(self, set_mode='db', get_mode='db'):
        super(Downloader, self).__init__()
        if set_mode not in ['db', 'http'] or get_mode not in ['db', 'http']:
            raise RuntimeError('下载器参数错误')
        self.set_mode = set_mode
        self.get_mode = get_mode
        self.db = StoreMysql(**configs.DOWNLOADER_CENTER_DB)
        self.rds = redis.StrictRedis(**configs.DOWNLOADER_CENTER_REDIS)

        self.url = configs.DOWNLOADER_CENTER_URL
        self.set_method = configs.SEND_TASK_METHOD
        self.get_method = configs.QUERY_TASK_METHOD

    def find_district_adsl(self, conf_district_id):
        try:
            sql = "select * from district where id = %d" % int(conf_district_id)
            results = self.db.query(sql)
            if len(results) > 0:
                return True
            else:
                return False
        except Exception, e:
            print e

    def set(self, request):
        """
        设置http头或者将相关配置发到下载中心
        Args:
            request: SpiderRequest对象
        Returns:
            正常: 返回字典，key值为每个url，value值-1（失败）、0（重复发送）、1（成功）
            出错: 0
        """
        try:
            param = request.downloader_set_param(self.set_mode)
            if param is None:
                return 0
            if not self.__check_priority(param):
                raise RuntimeError('今日发送任务数量已经超过最大限制')
            if self.set_mode == 'db':
                conf_district_id = param.pop('conf_district_id')
                if conf_district_id != 0:
                    district_adsl = self.find_district_adsl(conf_district_id)
                    if not district_adsl:
                        return -2

                user_id = int(param.pop('user_id'))
                urls_table = configs.USER_CONFIG['urlsTable'] % user_id
                configs_table = configs.USER_CONFIG['configsTable'] % user_id
                urls = param.pop('urls')
                url_type = param.pop('url_type')
                if 'expire_time' not in param:
                    param['expire_time'] = str(datetime.today() + timedelta(days=1))
                # print  param
                config_id = self.db.save(configs_table, param)
                if config_id > 0:
                    records = list()
                    md5_list = list()
                    for url in urls:
                        u = MySQLdb.escape_string(url['url'])
                        records.append('("%s", "%s", %d, %d, %d, %d)' % (u, url['md5'], url_type, config_id, 0, conf_district_id))
                        md5_list.append(url['md5'])
                    result = self.db.do('insert ignore into %s(url, md5, type, config_id, status, conf_district_id) '
                                        'values %s' % (urls_table, ','.join(records)))
                    if result != -1:
                        r = self.db.query('select url, status, md5 from %s where md5 in ("%s") and type = %d' % (urls_table, '","'.join(md5_list), url_type))
                        param['user_id'] = user_id
                        self.__record_user_task(param, len(r))
                        results = dict()
                        result_store_key = configs.TASK_CONFIGS[configs.FETCH_TYPES[str(url_type)]]['resultStoreKey'] % (user_id, url_type)
                        for u in r:
                            results[u[2]] = u[1]
                            if param['store_type'] == 2:
                                self.rds.hsetnx(result_store_key, u[2], json.dumps({'url': u[0], 'status': u[1],
                                                                                    'result': '', 'header': '',
                                                                                    'code': '', 'redirect_url': '',
                                                                                    'md5': u[2]
                                                                                    }))
                        return results
                    return result
                return -1
            elif self.set_mode == 'http':
                data = {
                    'method': self.set_method,
                    'params': json.dumps(param)
                }
                response = urllib2.urlopen(self.url, data=urllib.urlencode(data), timeout=configs.SEND_TASK_TIMEOUT)
                results = response.read()
                if str(results) == '0':
                    return -1
                r = json.loads(results)
                self.__record_user_task(param, len(r))
                return r
        except Exception:
            print(traceback.format_exc())
            return 0

    def __check_priority(self, param):
        user_id = int(param['user_id'])
        priority = int(param['priority'])
        task_size = len(param['urls'])
        current_date = str(datetime.now().date())
        task_limit_key = configs.USER_CONFIG['userTaskLimitKey'] % user_id
        task_sended_key = configs.USER_CONFIG['userTaskSendedKey'] % (user_id, current_date)
        while priority > 0:
            limit_size = int(self.rds.hget(task_limit_key, priority))
            if limit_size < 0:
                param['priority'] = priority
                return True
            self.rds.hincrby(task_sended_key, priority, 0)
            send_size = int(self.rds.hget(task_sended_key, priority))
            if send_size + task_size > limit_size:
                priority -= 1
                task_limit_key = configs.USER_CONFIG['userTaskLimitKey'] % user_id
                task_sended_key = configs.USER_CONFIG['userTaskSendedKey'] % (user_id, current_date)
            else:
                param['priority'] = priority
                return True
        return False

    def __record_user_task(self, param, task_size):
        user_id = int(param['user_id'])
        priority = int(param['priority'])
        current_date = str(datetime.now().date())
        task_sended_key = configs.USER_CONFIG['userTaskSendedKey'] % (user_id, current_date)
        self.rds.hincrby(task_sended_key, priority, task_size)

    def get(self, request):
        """
        向下载中心请求特定url的结果
        Args:
            request: SpiderRequest对象
            mode: 模式，redis->直接查询redis数据库，db->直接查询数据库，http->通过http接口查询
        """
        try:
            param = request.downloader_get_param(self.get_mode)
            urls = param['urls']
            urls_md5 = param['md5']
            if len(urls) > 0:
                if self.get_mode == 'db':
                    user_id = int(param['user_id'])
                    urls_table = configs.USER_CONFIG['urlsTable'] % user_id
                    store_type = param['store_type']
                    url_type = param['url_type']
                    results = dict()
                    if store_type == 1:
                        rows = self.db.query('select url, status, result, header, id, redirect_url, code, md5 from %s '
                                             'where md5 in ("%s") and type = %d'
                                             % (urls_table, '", "'.join(urls_md5), url_type))
                        deleted_ids = list()
                        for row in rows:
                            if row[2]:
                                html = base64.b64decode(row[2])
                            else:
                                html = row[2]
                            results[row[7]] = {'status': row[1], 'result': html, 'header': row[3],
                                               'redirect_url': row[5], 'code': row[6]}
                            if str(row[1]) in ['2', '3']:
                                deleted_ids.append(str(row[4]))
                        if len(deleted_ids) > 0:
                            self.db.do('delete from %s where id in (%s)' % (urls_table, ','.join(deleted_ids)))
                    elif store_type == 2:
                        result_store_key = configs.TASK_CONFIGS[configs.FETCH_TYPES[str(url_type)]]['resultStoreKey'] % (user_id, url_type)
                        rows = self.rds.hmget(result_store_key, *urls_md5)
                        deleted_ids = list()
                        deleted_urls = list()
                        for row in rows:
                            if row:
                                result = json.loads(row)
                                if result['result']:
                                    html = base64.b64decode(result['result'])
                                else:
                                    html = result['result']
                                results[result['md5']] = {'status': result['status'], 'result': html,
                                                          'header': result['header'], 'code': result['code'],
                                                          'redirect_url': result['redirect_url']}
                                if str(result['status']) in ['2', '3']:
                                    deleted_ids.append(str(result['id']))
                                    deleted_urls.append(result['md5'])
                        if len(deleted_ids) > 0:
                            self.db.do('delete from %s where id in (%s)' % (urls_table, ','.join(deleted_ids)))
                            self.rds.hdel(result_store_key, *deleted_urls)
                    return results
                elif self.get_mode == 'http':
                    data = {
                        'method': self.get_method,
                        'params': json.dumps(param)
                    }
                    response = urllib2.urlopen(self.url, data=urllib.urlencode(data), timeout=configs.QUERY_TASK_TIMEOUT)
                    results = response.read()
                    if str(results) == '0':
                        return -1
                    results_json = json.loads(results)
                    for (k, v) in results_json.items():
                        if v['result']:
                            html = base64.b64decode(v['result'])
                            v['result'] = html
                    return results_json
        except Exception:
            print(traceback.format_exc())
            return 0
