# -*- coding: utf8 -*-
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class UtilFile(object):
    '''
        1、读取指定目录下的所有文件
        2、读取指定文件，输出文件内容
        3、创建一个文件并保存到指定目录
    '''

    # 遍历指定目录，显示目录下的所有文件名
    def __init__(self):
        pass

    def eachFile(self, filepath):
        pathDir = os.listdir(filepath)
        dir = []
        for allDir in pathDir:
            child = os.path.join('%s/%s' % (filepath, allDir))
            # print child.decode('gbk')  # .decode('gbk')是解决中文显示乱码问题
            dir.append(child.decode('gbk'))
        return dir

    # 读取文件内容并打印
    def readFile(self, filename):
        fopen = open(filename, 'r')  # r 代表read
        for eachLine in fopen:
            pass
            # print "读取到得内容如下：", eachLine
        fopen.close()

    # 输入多行文字，写入指定文件并保存到指定文件夹
    def writeFile(self, filename):
        fopen = open(filename, 'w')
        # print "\r请任意输入多行文字", " ( 输入 .号回车保存)"
        while True:
            aLine = raw_input()
            if aLine != ".":
                fopen.write('%s%s' % (aLine, os.linesep))
            else:
                # print "文件已保存!"
                break
        fopen.close()

    def mkdir(self, path):
        path = path.strip()
        path = path.rstrip("\\")
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            return True
        else:
            return False

if __name__ == '__main__':
    sx = UtilFile()
    filePath = "D:/regular/python_screenshot"
    # filePathI = "D:\\FileDemo\\Python\\pt.py"
    # filePathC = "C:\\"
    import csv
    dirs = sx.eachFile(filePath)
    for fileName in dirs:
        print fileName
        csvfile = file(fileName, 'rb')
        readersx = csv.reader(csvfile)
        for line in readersx:
            for s in line:
                print s.decode('gbk')
            # child.decode('gbk')
        csvfile.close()
    # sx.readFile(filePath)
    # sx.writeFile(filePathI)


