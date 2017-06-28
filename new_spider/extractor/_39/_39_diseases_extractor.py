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


class _39DiseaseExtractor(SpiderExtractor):
    """
    解析39健康疾病页，获取疾病详情
    """

    def __init__(self):
        super(_39DiseaseExtractor, self).__init__()

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
            
            name = soup.select_one('h1').get_text()
            desc = soup.select_one('.detailed > p').get_text()
            hot = soup.select_one('.detailed > cite').get_text().replace('关注度','')

            div1 = soup.select('.intel > dl')
            alias = div1[0].select_one('dd').get_text()
            place = div1[1].select_one('dd').get_text()
            infectivity = div1[2].select_one('dd').get_text()
            population = div1[3].select_one('dd').get_text()
            symptom = div1[4].select_one('dd').get_text()
            complication = div1[5].select_one('dd').get_text()

            department = div1[6].select_one('dd').get_text()
            cost = div1[7].select_one('dd').get_text()
            cure_rate = div1[8].select_one('dd').get_text()
            method = div1[9].select_one('dd').get_text()
            examination = div1[10].select_one('dd').get_text()

            results.append(
            {
            'name': name,
            'description':desc,
            'alias':alias,
            'place':place,
            'infectivity':infectivity,
            'population':population,
            'symptom':symptom,
            'complication':complication,
            'department':department,
            'cost':cost,
            'cure_rate':cure_rate,
            'method':method,
            "examination":examination,
            "hot":hot
             })
        except Exception, e:
            pass
        return results
