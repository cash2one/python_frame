
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

file = 'result.txt'
f = open(file, 'w')
f.write('I love python')
f.close()
    