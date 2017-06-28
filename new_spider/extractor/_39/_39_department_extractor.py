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


class _39DepartmentExtractor(SpiderExtractor):
    """
    解析39健康科室导航，获取科室列表
    """

    def __init__(self):
        super(_39DepartmentExtractor, self).__init__()

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
            navs_div = soup.find('div', id='navs')
            if navs_div:
                depart_divs = navs_div.find_all('h2', recursive=True)
                if len(depart_divs) > 0:
                    for depart in depart_divs:
                        url = depart.find('a', recursive=True)['href']
                        department_id = url.split('_')[2]
                        results.append(
                        {
                        'name': str(depart.get_text()),
                        'department_id':department_id
                         })
        except Exception, e:
            pass
        return results
