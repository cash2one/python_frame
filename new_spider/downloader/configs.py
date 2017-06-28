# -*- coding: utf8 -*-

# 下载中心地址

DOWNLOADER_CENTER_URL = 'http://182.254.155.218/task.php'

# 发送任务方法
SEND_TASK_METHOD = 'sendTask'

# 发送任务超时时间
SEND_TASK_TIMEOUT = 300

# 查询任务方法
QUERY_TASK_METHOD = 'getResult'

# 查询任务超时时间
QUERY_TASK_TIMEOUT = 100

# 下载中心数据库
DOWNLOADER_CENTER_DB = {
    'host': '182.254.155.218',
    # 'host': '10.105.72.2',
    'user': 'spider_center',
    'password': 'spiderdb@wd',
    'db': 'spider'

    # 'host': '115.159.0.225',
    # # 'host': '10.143.32.137',
    # 'user': 'remote',
    # 'password': 'Iknowthat',
    # 'db': 'spider'
}

# 下载中心redis
DOWNLOADER_CENTER_REDIS = {
    'host': '182.254.155.218',
    # 'host': '10.105.72.2',
    'port': 6379,
    'db': 0,
    'password': '@redisForSpider$'

    # 'host': '182.254.244.167',
    # # 'host': '10.150.72.2',
    # 'port': 6379,
    # 'db': 0,
    # 'password': '@redisForSpider$'
}

# 数据库里面url type与抓取类型对应关系
FETCH_TYPES = {
    '1': 'html',
    '2': 'html',
    '3': 'render',
    '4': 'capture',
    '5': 'screenshot',
    '6': 'pulldown',
    '7': 'execute',
    '8': 'image'
}

# 任务配置
TASK_CONFIGS = {
    'html': {
        'resultStoreKey': 'html:store:%d:%d'
    },
    'render': {
        'resultStoreKey': 'render:store:%d:%d'
    },
    'capture': {
        'resultStoreKey': 'capture:store:%d:%d'
    },
    'screenshot': {
        'resultStoreKey': 'screenshot:store:%d:%d'
    },
    'pulldown': {
        'resultStoreKey': 'pulldown:store:%d:%d'
    },
    'execute': {
        'resultStoreKey': 'execute:store:%d:%d'
    },
    'image': {
        'resultStoreKey': 'image:store:%d:%d'
    }
}

# 用户抓取任务配置
USER_CONFIG = {
    'userTaskLimitKey': 'user:limit:%d',
    'userTaskSendedKey': 'user:sended:%d:%s',
    'urlsTable': 'urls_%d',
    'configsTable': 'configs_%d'
}
