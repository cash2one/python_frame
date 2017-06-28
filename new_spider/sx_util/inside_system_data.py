# -*- coding: utf8 -*-

import urllib
import urllib2
import traceback
import sys
from datetime import datetime
import configurl
import traceback
import time
from util_log import UtilLogger
import os
reload(sys)
sys.setdefaultencoding('utf8')


class InsideSystem(object):

    def __init__(self):
        pass

    def send_InsideSystem(self, url, data_lists, param):
        '''

        :param url:
        :param dataLists:  发送数据
        :return:        发送数据参数
        '''
        # send_configurl = configurl.sendurl[str(saveport)]
        # send_config_pulldown_url = configurl.pulldownUrl[str(saveport)]

        # send_configurl = "http://192.168.0.72:3000/DropDown/dropDownReceiveData"
        # self.log_record.info("send insideSystem" + str(datetime.today()))
        for i in range(0, configurl.RETRY_TIMES):
            try:
                request = urllib2.Request(url, data=urllib.urlencode({param: data_lists}))
                response = urllib2.urlopen(request, timeout=20)
                sx = response.read()
                print str(sx)[0:20]
                if str(sx) != "success":
                    return True
                break
            except Exception :
                print "第%d 次发送" % i
                traceback.print_exc()
                time.sleep(1)

def Main():
    pass
    print configurl.sendurl[str("1")]

if __name__ == '__main__':
    Main()
