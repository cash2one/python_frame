# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os, time

class CodeFileExcutor(object):

    def __init__(self):
        pass

    def save_2_file(self, code_str):
        file = 'test.py'
        f = open(file, 'w')
        f.write(code_str)
        f.close()
        # time.sleep(5)
        return file

    def excute_file(self, file):
        execfile(file)
        # os.remove(file)

def test(code_str):
    excutor = CodeFileExcutor()
    excutor.excute_file(excutor.save_2_file(code_str))

if __name__ == '__main__':
    text = '''
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

file = 'result.txt'
f = open(file, 'w')
f.write('I love python')
f.close()
    '''
    test(text)