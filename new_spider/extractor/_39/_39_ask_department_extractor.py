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


class _39AskDeparmentExtractor(SpiderExtractor):
    """
    解析39问答科室入口页
    """

    def __init__(self):
        super(_39AskDeparmentExtractor, self).__init__()

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
            
            pages = soup.select('.pgleft > a')
            if len(pages)>0:
                results.append(
                {
                'useful': True
                 })
            else:
                results.append(
                {
                    'useful': False
                })
        except Exception, e:
            pass
        return results
