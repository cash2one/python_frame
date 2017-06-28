# -*- coding: utf8 -*-

# 爬虫数据库
DB_SPIDER = {
    #  'host': '182.254.155.218',
    # # 'host': '10.105.72.2',
    # 'user': 'spider_center',
    # 'password': 'spiderdb@wd',
    # 'db': 'spider'

    'host': '115.159.0.225',
    'user': 'remote',
    'password': 'Iknowthat',
    'db': 'spider'
}

# redis地址
REDIS = {
    # 'host': '182.254.155.218',
    # # 'host': '10.105.72.2',
    # 'port': 6379,
    # 'db': 0,
    # 'password': '@redisForSpider$'

    'host': '182.254.244.167',
    'port': 6379,
    'db': 0,
    'password': '@redisForSpider$'

    # 'host': '182.254.159.183',
    # 'port': 6379,
    # 'db': 0,
    # 'password': '@redisForSpider$'
}

# 任务类型
TASK_TYPE_HTML = 'html'
TASK_TYPE_RENDER = 'render'
TASK_TYPE_CAPTURE = 'capture'
TASK_TYPE_SCREENSHOT = 'screenshot'
TASK_TYPE_PULLDOWN = 'pulldown'
TASK_TYPE_IMAGE = 'image'

# 任务配置
TASK_CONFIGS = {
    TASK_TYPE_HTML: {
        'taskTypesInDatabase': '1,2,7',
        'taskQueueCommonKey': 'html:task:common',
        # 新增 地域 的 查排名
        'taskQueueDistrictKey': 'html:task:%d',

        'taskMaxSendNumDistrict': {
            '3': 1000,
            '2': 400,
            '1': 100
        },

        'taskMaxSendNumCommon': {
            '3': 1000,
            '2': 400,
            '1': 100
        },
        'taskQueueSingleKey': 'html:task:single',
        'taskMaxSendNumSingle': {
            '3': 500,
            '2': 200,
            '1': 50
        },
        'taskQueueConcurrentKey': 'html:task:concurrent',
        'taskMaxSendNumConcurrent': {
            '3': 1000,
            '2': 400,
            '1': 100
        },
        'taskMaxFailTimes': 3,
        'taskFailTimesKey': 'html:task:fail',
        'resultQueueKey': 'html:result',
        'resultStoreKey': 'html:store:%d:%d'

    },
    TASK_TYPE_RENDER: {
        'taskTypesInDatabase': '3',
        'taskQueueCommonKey': 'render:task:common',
        'taskMaxSendNumCommon': {
            '3': 500,
            '2': 200,
            '1': 50
        },
        'taskQueueSingleKey': 'render:task:single',
        'taskMaxSendNumSingle': {
            '3': 250,
            '2': 100,
            '1': 25
        },
        'taskQueueConcurrentKey': 'render:task:concurrent',
        'taskMaxSendNumConcurrent': {
            '3': 500,
            '2': 200,
            '1': 50
        },

        'taskQueueDistrictKey': 'render:task:%d',
        'taskMaxSendNumDistrict': {
            '3': 1000,
            '2': 400,
            '1': 100
        },

        'taskMaxFailTimes': 3,
        'taskFailTimesKey': 'render:task:fail',
        'resultQueueKey': 'render:result',
        'resultStoreKey': 'render:store:%d:%d'
    },
    TASK_TYPE_CAPTURE: {
        'taskTypesInDatabase': '4',
        'taskQueueCommonKey': 'capture:task:common',
        'taskMaxSendNumCommon': {
            '3': 200,
            '2': 100,
            '1': 50
        },
        'taskQueueSingleKey': 'capture:task:single',
        'taskMaxSendNumSingle': {
            '3': 200,
            '2': 100,
            '1': 20
        },
        'taskQueueConcurrentKey': 'capture:task:concurrent',
        'taskMaxSendNumConcurrent': {
            '3': 200,
            '2': 100,
            '1': 20
        },

        'taskQueueDistrictKey': 'capture:task:%d',

        'taskMaxSendNumDistrict': {
            '3': 100,
            '2': 80,
            '1': 20
        },
        'taskMaxFailTimes': 3,
        'taskFailTimesKey': 'capture:task:fail',
        'resultQueueKey': 'capture:result',
        'resultStoreKey': 'capture:store:%d:%d'
    },
    TASK_TYPE_SCREENSHOT: {
        'taskTypesInDatabase': '5',
        'taskQueueCommonKey': 'screenshot:task:common',
        'taskMaxSendNumCommon': {
            '3': 150,
            '2': 100,
            '1': 50
        },
        'taskQueueSingleKey': 'screenshot:task:single',
        'taskMaxSendNumSingle': {
            '3': 150,
            '2': 100,
            '1': 50
        },
        'taskQueueConcurrentKey': 'screenshot:task:concurrent',
        'taskMaxSendNumConcurrent': {
            '3': 150,
            '2': 100,
            '1': 50
        },

        'taskQueueDistrictKey': 'screenshot:task:%d',
        'taskMaxSendNumDistrict': {
            '3': 30,
            '2': 15,
            '1': 10
        },

        'taskMaxFailTimes': 3,
        'taskFailTimesKey': 'screenshot:task:fail',
        'resultQueueKey': 'screenshot:result',
        'resultStoreKey': 'screenshot:store:%d:%d'
    },
    TASK_TYPE_PULLDOWN: {
        'taskTypesInDatabase': '6',
        'taskQueueCommonKey': 'pulldown:task:common',
        'taskMaxSendNumCommon': {
            '3': 150,
            '2': 100,
            '1': 50
        },
        'taskQueueSingleKey': 'pulldown:task:single',
        'taskMaxSendNumSingle': {
            '3': 150,
            '2': 100,
            '1': 50
        },
        'taskQueueConcurrentKey': 'pulldown:task:concurrent',
        'taskMaxSendNumConcurrent': {
            '3': 150,
            '2': 100,
            '1': 50
        },
        'taskQueueDistrictKey': 'pulldown:task:%d',
        'taskMaxSendNumDistrict': {
            '3': 30,
            '2': 15,
            '1': 10
        },
        'taskMaxFailTimes': 3,
        'taskFailTimesKey': 'pulldown:task:fail',
        'resultQueueKey': 'pulldown:result',
        'resultStoreKey': 'pulldown:store:%d:%d'
    },
    TASK_TYPE_IMAGE: {
        'taskTypesInDatabase': '8',
        'taskQueueCommonKey': 'image:task:common',
        'taskMaxSendNumCommon': {
            '3': 150,
            '2': 100,
            '1': 50
        },
        'taskQueueSingleKey': 'image:task:single',
        'taskMaxSendNumSingle': {
            '3': 150,
            '2': 100,
            '1': 50
        },
        'taskQueueConcurrentKey': 'image:task:concurrent',
        'taskMaxSendNumConcurrent': {
            '3': 150,
            '2': 100,
            '1': 50
        },
        'taskQueueDistrictKey': 'image:task:%d',
        'taskMaxSendNumDistrict': {
            '3': 30,
            '2': 15,
            '1': 10
        },
        'taskMaxFailTimes': 3,
        'taskFailTimesKey': 'image:task:fail',
        'resultQueueKey': 'image:result',
        'resultStoreKey': 'image:store:%d:%d'
    }

}

# 任务各个环节执行时间间隔配置
TASK_TIME_INTERVAL_CONFIGS = {
    TASK_TYPE_HTML: {
        'pushCommon': 10,
        'pushSingle': 30,
        'pushConcurrent': 30,
        'save': 30,
        'reset': 120,
        'clear': 3600,
        'record': 3600*12,
    },
    TASK_TYPE_RENDER: {
        'pushCommon': 10,
        'pushSingle': 30,
        'pushConcurrent': 30,
        'save': 30,
        'reset': 120,
        'clear': 3600,
        'record': 3600 * 12,

    },
    TASK_TYPE_CAPTURE: {
        'pushCommon': 10,
        'pushSingle': 30,
        'pushConcurrent': 30,
        'save': 30,
        'reset': 3600,
        'clear': 3600,
        'record': 3600 * 12,
    },
    TASK_TYPE_SCREENSHOT: {
        'pushCommon': 10,
        'pushSingle': 30,
        'pushConcurrent': 30,
        'save': 30,
        'reset': 3600,
        'clear': 3600,
        'record': 3600 * 12,

    },
    TASK_TYPE_PULLDOWN: {
        'pushCommon': 10,
        'pushSingle': 30,
        'pushConcurrent': 30,
        'save': 30,
        'reset': 3600,
        'clear': 3600,
        'record': 3600 * 12,
    },
    TASK_TYPE_IMAGE: {
        'pushCommon': 10,
        'pushSingle': 30,
        'pushConcurrent': 30,
        'save': 30,
        'reset': 1200,
        'clear': 3600,
        'record': 3600 * 12,
    }
}

# 用户抓取任务配置
USER_CONFIGS = {
    'userListKey': 'user:list',
    'userWeightKey': 'user:weight',
    'userTaskLimitKey': 'user:limit:%d',
    'userTaskSendedKey': 'user:sended:%d:%s',
    'urlsTable': 'urls_%d',
    'configsTable': 'configs_%d'
}

# ADSL机器配置
MACHINE_CONFIGS = {
    'areaKey': 'machine:area'
}