# -*- coding: utf8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class UtilUseragent(object):
    """
    获取User-Agent
    """
    def __init__(self):
        pass

    @staticmethod
    def get(type='PC'):
        file_name = 'ua_pc_list.txt'
        if type == 'MOBILE':
            file_name = 'ua_mobile_list.txt'
        elif type == 'SPIDER':
            file_name = 'ua_spider_list.txt'
        f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name), 'r')
        uas = [l.strip() for l in f.readlines()]
        f.close()
        return uas
