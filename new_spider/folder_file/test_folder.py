# -*- coding: utf-8 -*-
import os
save_image_folder = "D:/picture/chinapp/"

def search_file_length():
    list_one = os.listdir(save_image_folder)[-1] #列出文件夹下所有的目录与文件
    folder_path = os.path.join(save_image_folder, list_one)

    print folder_path
    file_list = os.listdir(folder_path)
    print file_list
    return len(file_list)
print search_file_length()

# for root, dirs, files in os.walk(save_image_folder):
#     for i, v in enumerate(dirs):
#         if i == len(dirs)-1:
#             print 11
#             print files
#             for file in files:
#                 print root + os.sep + file



