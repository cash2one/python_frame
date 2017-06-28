# -*- coding: utf8 -*-
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class UtilFunction(object):

    def mkdir(self, path):
        '''
        创建文件路径
        :param path:
        :return:
        '''
        path = path.strip()
        path = path.rstrip("\\")
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            return True
        else:
            return False

    def find_last(self, string, str):
        '''
        在 string 中 最后一个str 字符
        :param string:
        :param str:
        :return:
        '''
        last_position = -1
        while True:
            position = string.find(str, last_position + 1)
            if position == -1:
                return last_position
            last_position = position

    # 判断是否有中文
    def check_contain_chinese(self, check_str):
        for ch in check_str.decode('utf-8'):
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

if __name__ == '__main__':
    pass
    # sx.readFile(filePath)
    # sx.writeFile(filePathI)


