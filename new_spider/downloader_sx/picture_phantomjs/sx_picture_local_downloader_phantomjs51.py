# -*- coding: utf8 -*-
import sys
import traceback

from downloader.downloader import Downloader

# from list_pulldown_picture.sx_picture_phantomjs import FindPicture
reload(sys)
sys.setdefaultencoding('utf8')
# from downloader.picture_phantomjs

import sys
reload(sys)
sys.setdefaultencoding('utf8')

# from downloader.list_pulldown_picture.sx_picture_phantomjs import FindPicture
from downloader_sx.picture_phantomjs import FindPictureMobile
from downloader_sx.picture_phantomjs import FindPicturePc

class HtmlLocalDownloader(Downloader):
    """
    html下载器
    """

    def __init__(self, set_mode='db', get_mode='db'):
        self.pictureMobile = FindPictureMobile()
        self.picturePc = FindPicturePc()
        super(HtmlLocalDownloader, self).__init__(set_mode, get_mode)

    def set(self, request):
        try:
            results = dict()
            # param = request.downloader_get_param('http')
            param = request.downloader_set_param('http')
            for url in param['urls']:
                # print url
                results[url["url"]] = 1
            return results
        except Exception:
            print(traceback.format_exc())
            return 0

    @staticmethod
    def encoding(data):
        types = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']
        for t in types:
            try:
                return data.decode(t)
            except Exception, e:
                pass
        return None

    def get(self, request):
        param = request.downloader_set_param('http')
        if param is None:
            return 0
        urls = param['urls']
        if len(urls) > 0:
            try:
                results = dict()
                for url in urls:
                    if "param" in param:
                        task = {"url": url["url"], "type": 4, "store_type": 1, "status": "3", "result": "",
                                "param": str(param["param"])}
                    else:
                        task = {"url": url["url"], "type": 4, "store_type": 1, "status": "3", "result": ""}
                    result = {"url": url["url"], "status": "3", "result": "", "header": ""}
                    for i in range(0, 2):
                        try:
                            import datetime
                            starttime = datetime.datetime.now()
                            print "screenshot start"
                            # render = WebRender(task)
                            # sx_result = render.result

                            # sx_result = self.picturePc.picture_screenshot_html(url["url"])

                            device = str(url["url"]).split(",")
                            url_device = device[0]
                            if int(device[1]) == 1:
                                sx_result = self.picturePc.picture_screenshot_html(url_device)
                            else:
                                sx_result = self.pictureMobile.picture_screenshot_html(url_device)

                            endtime = datetime.datetime.now()
                            print (endtime - starttime).seconds
                            if sx_result:
                                result['status'] = 2
                                result['result'] = sx_result
                                break

                        except Exception as e:
                            print e
                            print('抓取失败：第%d次' % (i + 1))
                    results[url['md5']] = result
                return results
            except Exception, e:
                print e
                print 'get:'+(traceback.format_exc())
        return 0


if __name__ == "__main__":
    pass
    # sx = FindPicture()
    # sx_result = sx.picture_screenshot_html("https://www.baidu.com/s?wd=%E6%B7%AE%E5%AE%89%E4%BA%BA%E6%89%8D%E7%BD%91%E6%9C%80%E6%96%B0%E6%8B%9B%E8%81%98%E4%BF%A1%E6%81%AF&rsv_spt=1&rsv_iqid=0x9d684d0e0000cecd&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=78040160_5_pg&rsv_enter=0&oq=%E6%8B%9B%E8%81%98&rsv_t=7e39msJWAhkatRpmx%2F691Ir2BU1904ljWxb%2B3gy7cl5pNJsIfLHDNBbY7prEA2Kv9ez9OQ&rsv_pq=dd1bb49d0003954a&inputT=135689006&rsv_n=2&rsv_sug3=1298&bs=%E6%8B%9B%E8%81%98")
    # print sx_result