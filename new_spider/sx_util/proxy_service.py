# coding: utf-8
import urllib2

class proxyService(object):

    def __init__(self):
        self.proxy_list = list()
        self.curproxy_list = list()
        self.curroxy_count = 40
        self.url = "http://42.51.201.58:33453//api/getiplist.aspx?vkey=3416F08BB1AA3ACB0386A0991C27C0FF&num=100&country=CN&high=1&style=1"

    def find_proxy(self):
        request = urllib2.Request(self.url)
        response = urllib2.urlopen(request, timeout=10)
        proxy = str(response.read()).split("<br>")
        for i in xrange(0, 100):
            self.proxy_list.append(proxy[i])
        return self.proxy_list
    # def findCur_proxy(self):
    #     if len(self.curproxy_list) > 40:


def main():
    sx = proxyService()
    sx.find_proxy()
    print len(sx.proxy_list)


if __name__ == '__main__':
    main()