# -*- coding:utf-8 -*-
# str = "<em>hdhjhdd<em>"
# print str.replace("<em>", "")


# sx = [1,2,3,5,4,32,2,1]
# print sx.index(1)
#
# print sx
#
#
# sxstr = u'24岁（1993年1月12日）'
# print type(sxstr)
# print sxstr.find(u"（")
# print sxstr.split(u"（")[1]

# kwh = {'k': "阿皮亚"}
# # url = 'https://koubei.baidu.com/search/getsearchresultajax?' + urllib.urlencode(kwh)
# import urllib
# print "http://guides.okmk.com/search.html?" + urllib.urlencode(kwh)
#
# print "阿皮亚".decode("gbk")
#
# # "http://guides.okmk.com/search.html?k=007%u5C9B"
# "http://guides.okmk.com/search.html?k=阿皮亚"
#
#
# print urllib.quote("阿皮亚")

sx = "%u963F%u76AE%u4E9A"
print sx.decode("unicode-escape")


import execjs
ctx = execjs.compile("""
    function text(content){
        return "http://guides.okmk.com/search.html?k=" + escape(content)
        }
    """)

print ctx.call("text", "阿皮亚")
