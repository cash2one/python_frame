# -*- coding: utf8 -*-
import sys
import urllib2
import traceback
import urllib
reload(sys)
sys.setdefaultencoding('utf8')

class Find_baidu_pc_pulldown(object):

    def __init__(self):
        pass

    def find_pulldown_url(self, keyword):
        try:
            # sx_keyword = urllib.urlencode(keyword)
            kwh = {'wd': keyword}
            # url = 'https://www.baidu.com/s?' + urllib.urlencode(kwh)
            # & sugmode = 2
            url_str = "https://sp0.baidu.com/5a1Fazu8AA54nxGko9WTAnF6hhy/su?"+urllib.urlencode(kwh)+"&json=1"
            return url_str
        except Exception, e:
            print e
            return ""

    def find_pulldown(self, url):
        try:
            data = None
            opener = urllib2.build_opener()

            # 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # 'Cookie':'PSTM=1485261995; BIDUPSID=687B320E01AA6A3979C5C22B5C03D5CE; BAIDUID=B07A8FE67DBFBC858F65A86F933B6CFF:SL=0:NR=10:FG=1; BDUSS=tlTTRSLTkwMzhuM2dPQXVxUjRURlRGOVBIT2t6aVllSGpGcHJ2VTRXTnF3cjlZSUFBQUFBJCQAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGo1mFhqNZhYcU; BDRCVFR[HHw4GR7hd6D]=mk3SLVN4HKm; PSINO=3; H_PS_PSSID=1444_21120_22036_21671_20718',
            # 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
            #
            header = {
                        'Cookie': 'BAIDUID=EC99F9478C3D07A9895A0939BEB7E00D:',
                      }
            request = urllib2.Request(url, data=data, headers=header)
            for i in range(0, 2):
                try:
                    response = opener.open(request, timeout=10)
                    header = response.info()
                    body = response.read()
                    if ('Content-Encoding' in header and header['Content-Encoding']) or \
                            ('content-encoding' in header and header['content-encoding']):
                        import gzip
                        import StringIO
                        d = StringIO.StringIO(body)
                        gz = gzip.GzipFile(fileobj=d)
                        body = gz.read()
                        gz.close()
                    body = self.encoding(body)
                    if body is not None:
                        return body
                        break
                except Exception, e:
                    traceback.print_exc()
            return ""
        except Exception:
            print 'get:' + (traceback.format_exc())
            return ""

    @staticmethod
    def encoding(data):
        types = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']
        for t in types:
            try:
                return data.decode(t)
            except Exception, e:
                pass
        return None

if __name__ == '__main__':
    sx = Find_baidu_pc_pulldown()
    body = sx.find_pulldown("https://sp0.baidu.com/5a1Fazu8AA54nxGko9WTAnF6hhy/su?wd=%E8%BF%88%E9%94%90%E5%AE%9D&json=1&csor=3")
    print body