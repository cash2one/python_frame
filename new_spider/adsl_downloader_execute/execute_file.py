# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import os
import time
import random
import config
import json

class executable_str(object):

    def __init__(self):
        pass

    def save_file(self, file_name, code_str):
        # file = dir_path + '\\test.py'
        f = open(file_name, 'w')
        f.write(code_str)
        f.close()
        time.sleep(1)

    def excute_url_str(self, dir_path, extractor_html, task_ids, client_id, task):
        file_name = "%s\\%s.py" % (dir_path, self.build_filename())
        self.save_file(file_name, extractor_html)
        globals = {"task_ids": json.dumps(task_ids), "task_url": config.TASK_SCHEDULER_URL, "client_id": client_id,
                   "task": task}
        execfile(file_name, globals)

        # # return_str = os.system("python test.py")
        # readfile = os.popen("python %s\\test.py" % dir_path)
        # sx = readfile.read()
        # readfile.close()
        # os.remove(file_name)
        # return sx

    def build_filename(self):
        time_stamp = str(time.time()).replace(".", "")
        code_list = list()
        for i in range(26):
            b = random.randint(97, 122)  # 小写
            random_uppercase_letter = chr(b)
            code_list.append(random_uppercase_letter)
        for i in range(10):
            random_num = random.randint(0, 9)  # 随机生成0-9的数字
            code_list.append(str(random_num))
        myslice = random.sample(code_list, 10)  # 从list中随机获取6个元素，作为一个片断返回
        verification_code = ''.join(myslice) + time_stamp  # list to string
        return verification_code

def test():
    pass
    sx = executable_str()
    print sx.build_filename()

if __name__ == '__main__':
    test()
