# -*- coding: utf8 -*-
import sys
import json
reload(sys)
sys.setdefaultencoding('utf8')
from sx_util.baidu_pc_pulldown import Find_baidu_pc_pulldown

class Find_baidu_pc_pulldown_data(object):

    def __init__(self):
        pass

    def find_pulldown_data(self, keyword):
        pulldown = []
        sx_find_pulldown = Find_baidu_pc_pulldown()
        #下拉链接
        pulldown_url = sx_find_pulldown.find_pulldown_url(keyword)
        if pulldown_url != "":
            #下拉请求内容
            body = sx_find_pulldown.find_pulldown(pulldown_url)
            if body != "":
                #内容解析
                pulldown = self.analyze_pulldown_data(body)
        if len(pulldown) == 0:
            pulldown_tup = ("no pulldown", )
            pulldown.append(pulldown_tup)
        return pulldown

    def analyze_pulldown_data(self, data):
        pulldown = []
        try:
            pulldown_json = data[17:]
            pulldown_json = pulldown_json[:-2]
            # print pulldown_json
            pulldown_item = json.loads(pulldown_json)["s"]
            pulldown_tup = ()
            if len(pulldown_item) > 0:
                for pulldown_single in pulldown_item:
                    pulldown_tup += (self.encoding(pulldown_single),)
                pulldown.append(pulldown_tup)
            return pulldown
        except Exception, e:
            print e
            return pulldown

    @staticmethod
    def encoding(data):
        types = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']
        for t in types:
            try:
                return data.decode(t).encode("gbk", "ignore")
            except Exception, e:
                pass
        return None

def Main():
    test = Find_baidu_pc_pulldown_data()
    print ('pc抓取程序开始启动...')
    data = test.find_pulldown_data("迈锐宝")
    print data

if __name__ == '__main__':
    Main()