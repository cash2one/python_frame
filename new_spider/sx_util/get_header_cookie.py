# -*- coding: utf8 -*-

import urllib2
import gzip
import StringIO

class GetHeader(object):

    def get_header(self, url, user_agent):
        try:
            opener = urllib2.build_opener()
            headers = {'User-Agent': user_agent, 'GET': url}
            request = urllib2.Request(url, data=None, headers=headers)
            response = opener.open(request, timeout=10)
            header = response.info()

            # print header
            if 'Set-Cookie' in header:
                cookie_lists = header.getheaders('Set-Cookie')
                print cookie_lists[len(cookie_lists)-1]
                return cookie_lists[len(cookie_lists)-1]
            # body = response.read()
            # if ('Content-Encoding' in header and header['Content-Encoding']) or \
            #         ('content-encoding' in header and header['content-encoding']):
            #     d = StringIO.StringIO(body)
            #     gz = gzip.GzipFile(fileobj=d)
            #     body = gz.read()
            #     gz.close()
            # if len(body) > 100:
            #     return True
            # else:
            #     return False
        except Exception, e:
            return ""

    # types = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']
    # for t in types:
    #     try:
    #         body = body.decode(t)
    #     except Exception, e:
    #         pass

def main():
    downloader = GetHeader()

    for i in xrange(0, 10):
        url = "http://bj.lianjia.com/chengjiao/"
        user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
        content = downloader.get_header(url, user_agent)
        file = open("lianjia_cookie.txt", "a")
        file.write(content+'\n')
        file.close()

if __name__ == '__main__':
    main()