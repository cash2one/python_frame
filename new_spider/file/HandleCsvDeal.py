# -*- coding: utf8 -*-
import csv
import codecs

class HandleCsvDeal(object):

    def __init__(self):
        pass

    def sx_write_File(self, filesx, data):
        try:
            csvfile = file(filesx, 'ab+')
            writersx = csv.writer(csvfile)
            writersx.writerows(data)
            csvfile.close()
        except Exception, e:
            print e

    def readFilesx(self, filesx):
        try:
            csvfile = file(filesx, 'rb')
            readersx = csv.reader(csvfile)
            for line in readersx:
                for s in line:
                    print s
            csvfile.close()
        except Exception, e:
            print e

def main():
    spider = HandleCsvDeal()
    # .decode("utf-8")  .decode("utf-8").encode("gbk")
    data = [('sxdshbhdsf你是来跨年福利是你发来考试难翻身','jkjdfs发的好地方')]
    # data = 'sxdshbhdsf你是来跨年福利是你发来考试难翻身'.decode("gbk","ignore")
    print data
    sx = "csv_test002.csv"
    # spider.readFilesx(sx)
    spider.sx_write_File(sx, data)

if __name__ == '__main__':
    main()