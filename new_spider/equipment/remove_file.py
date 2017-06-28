

# import shutil
# file = """D://aaa"""
# shutil.rmtree(file)

import os
import shutil

class RemoveTemp(object):

    def __init__(self):
        self.tempFile = "C:\Users\Administrator\AppData\Local\Temp"
        pass

    def removeTemp(self):
        delList = []
        # delDir = "D://aaaa"
        delList = os.listdir(self.tempFile)
        for f in delList:
            filePath = os.path.join(self.tempFile, f)
            if os.path.isfile(filePath):
                try:
                    os.remove(filePath)
                except Exception, e:
                    print filePath+"was not"
                    pass
                print filePath + " was removed!"
            elif os.path.isdir(filePath):
                shutil.rmtree(filePath, True)
            print "Directory: " + filePath + " was removed!"