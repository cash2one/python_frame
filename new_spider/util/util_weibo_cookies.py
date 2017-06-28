# -*- coding: utf8 -*-
import os
import sys
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'util'))
import json
import base64
import requests
reload(sys)
sys.setdefaultencoding('utf8')


class UtilWeiboCookie(object):
    """
    获取新浪微博移动端登录Cookie
    """

    def __init__(self):
        pass

    @staticmethod
    def get_cookies():
        """
        获取Cookies
        """
        cookies = list()
        accounts = [
            {'no': '14768191210', 'psw': 'ajdguvfhp1919'},
            {'no': 'shudieful3618@163.com', 'psw': 'a123456'}
        ]
        loginURL = r'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.15)'
        for elem in accounts:
            account = elem['no']
            password = elem['psw']
            username = base64.b64encode(account.encode('utf-8')).decode('utf-8')
            postData = {
                "entry": "sso",
                "gateway": "1",
                "from": "null",
                "savestate": "30",
                "useticket": "0",
                "pagerefer": "",
                "vsnf": "1",
                "su": username,
                "service": "sso",
                "sp": password,
                "sr": "1440*900",
                "encoding": "UTF-8",
                "cdult": "3",
                "domain": "sina.com.cn",
                "prelt": "0",
                "returntype": "TEXT",
            }
            session = requests.Session()
            r = session.post(loginURL, data=postData)
            jsonStr = r.content.decode('gbk')
            info = json.loads(jsonStr)
            if info["retcode"] == "0":
                cookie_dict = session.cookies.get_dict()
                cookie = ''
                for key in cookie_dict:
                    cookie += str(key) + '=' + str(cookie_dict[key]) + '; '
                cookies.append(cookie[:-2])
                print "获取Cookie成功!( 账号:%s )" % account
            else:
                print "获取Cookie失败!( 原因:%s )" % info['reason']
        return cookies


def test():
    util = UtilWeiboCookie()
    cookies = util.get_cookies()
    print(cookies)

if __name__ == '__main__':
    test()
