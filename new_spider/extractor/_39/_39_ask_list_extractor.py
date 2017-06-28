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


class _39AskListExtractor(SpiderExtractor):
    """
    解析39问答列表页，获取问题列表
    """

    def __init__(self):
        super(_39AskListExtractor, self).__init__()

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
            
            questions = soup.select('.list_ask > li')
            for ask in questions:
                url = ask.select_one('a')['href']
                ans_num = ask.select_one('.a_r > span').get_text().replace('个回答','')
                results.append(
                {
                'url': url,
                'ans_num':ans_num
                 })
        except Exception, e:
            pass
        return results
