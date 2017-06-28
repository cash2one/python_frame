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


class _39DiseaseListExtractor(SpiderExtractor):
    """
    解析39健康疾病列表页，获取疾病列表
    """

    def __init__(self):
        super(_39DiseaseListExtractor, self).__init__()

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
            
            url = soup.select('.list_all > li > a')
            pages = soup.select('.pgleft > a ')
            total_page = 1
            if len(pages) == 0:
                pass
            else:
                last = 1
                for page in pages:
                    if page.get_text() == '上一页':
                        total_page = last
                        break
                    last = page.get_text()

            for link in url:
                results.append(
                {
                'url': 'http://ask.39.net'+link['href'],
                'pages':total_page
                 })
        except Exception, e:
            pass
        return results



