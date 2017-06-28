# -*- coding: utf-8 -*-

import json

str = """{"highlights":["五险一金","包吃","包住","加班补助"],"graduates":false,"hasyan":true,"experience":"不限","salary":"5000-8000元","xueliyaoqiu":"不限","zhaopinrenshu":"10人","jobname":"服务员","content":"男女服务员（包吃住无押金）<br />（1）工作内容：服务员主要负责房间卫生打扫，收拾桌面等工作，微笑服务。<br />（2）工作时间：晚上7点到凌晨2点左右 ，一月4天休息。<br />（3）招聘要求：男女不限，身体健康18到30周岁<br />（4）薪资待遇：底薪4000+包厢小费200左右<br />面试时间为下午1点到6点（营业时间不接待面试人员，请应聘者安排好时间）"}"""
print type(str)

print json.loads(str)

# import re
# str = "共10页，到第"
#
# list =  re.findall(r'共(.+)页', str)[0]
# print list
#
# id = 1
# print id in (1,2)

print 41/8