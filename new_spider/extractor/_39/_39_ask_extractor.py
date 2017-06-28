# -*- coding: utf-8 -*-
"""
Created on Sun Sep 18 11:15:56 2016

@author: zhangle
"""

from spider.spider import SpiderExtractor
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf8')


class _39AskExtractor(SpiderExtractor):
    """
    解析39闻道详情，获取闻道详情
    """

    def __init__(self):
        super(_39AskExtractor, self).__init__()

    def extractor(self, text):
        """
        将一个页面文本解析为结构化信息的字典
        Args:
            text: 需要解析的文本
        Returns:
            数组: 每条为一个完整记录，记录由字典格式保存
        """
        results = list()
        try:
            soup = BeautifulSoup(text, 'lxml')
            top = soup.select_one('.t_con')
            title = top.select_one('h1').get_text().strip()
            user = top.select_one('.user_name > span').get_text().strip()
            ask_time = top.select_one('.user_name > cite').get_text().replace('投诉', '').strip()
            desc = top.select('.user_msg > li')
            if len(desc)==1:
                basic_info = desc[0].get_text().strip()
                disease_time = ''
            elif len(desc)==2:
                basic_info = desc[0].get_text().strip()
                disease_time = desc[1].get_text().strip()
            else:
                basic_info = ''
                disease_time = ''

            description = top.select_one('.user_p').get_text().strip()
            if len(top.select('.user_p'))>1:
                addon = top.select('.user_p')[1].get_text().strip()
            else:
                addon=''
            results.append(
            {
            'title': title,
            'user':user,
            'ask_time':ask_time,
            'basic_info':basic_info,
            'disease_time':disease_time,
            'description':description,
            'addon':addon
             })
            for ans in soup.select('#doctor_reply .t_con'):
                 doctor_id = ans.select_one('.user_name > strong > a').get('href').split('net/')[1]
                 name = ans.select_one('.user_name > strong > a').get_text().strip()
                 if ans.select_one('.user_name > i') is None:
                     is_realname=0
                 else:
                     is_realname=1
                 info = ans.select_one('.user_name > b').get_text().strip()
                 if len(info.split('   '))==2:
                     hospital = info.split('   ')[0]
                     department = info.split('   ')[1]
                 elif len(info.split('   '))==1:
                     hospital = info
                     department = ''
                 else:
                     hospital = ''
                     department = ''
                 pic_url = ans.select_one('.user_img > a > img')['src']
                 answer_time = ans.select_one('.user_name > cite').get_text().replace('投诉', '').strip()

                 if 'tbox_best' in ans.find_parent("div").get('class'):
                     is_satisfied=1
                 else:
                     is_satisfied=0
                 recommendation = ans.select_one('.useful > font').get_text()
                 if len(ans.select('.user_talk'))>0:
                     ans_addon = str(ans.select_one('.user_talk')).strip()
                 else:
                     ans_addon = ''
                 content = ans.select_one('.t_right > p').get_text().strip()
                 results.append(
                 {
                 'doctor_id': doctor_id,
                 'name':name,
                 'is_realname':is_realname,
                 'hospital':hospital,
                 'department':department,
                 'pic_url':pic_url,
                 'answer_time': answer_time,
                 'is_satisfied':is_satisfied,
                 'recommendation':recommendation,
                 'content':content,
                 'addon':ans_addon
                 })
        except Exception, e:
            pass
        return results
