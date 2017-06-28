# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
# D:/pyCharm/adsl_downloader_python/adsl_downloader/testjs/

str1 = """
# -*- coding:utf-8 -*-
from lxml.html import fromstring
import traceback

print 123456
print traceback.format_exc()

"""
with open("test.py", "wb") as f:
    f.write(str1)

execfile("test.py")