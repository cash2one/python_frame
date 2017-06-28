# -*- coding: utf8 -*-
from spider.spider import SpiderExtractor
from bs4 import BeautifulSoup
import re
import datetime
import sys
import traceback
reload(sys)
sys.setdefaultencoding('utf8')

from bs4.diagnose import lxml_trace

class BaiduNewsExtractor(SpiderExtractor):
    """
    解析百度新闻页，获取新闻列表
    """

    def __init__(self):
        super(BaiduNewsExtractor, self).__init__()

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
            result = {}
            pos = text.find("</html>")
            if text.find('location.href.replace') >= 0 or text.find('id="wrap"') >= 0 or text.find(
                    '<title>') < 0 or text.find('页面不存在_百度搜索') >= 0 or text.find(
                    'id="container"') < 0 or pos < 0 or text.find('id="content_left"') < 0:
                result['response_status'] = 0
            else:
                result['response_status'] = 1
                result['news'] = []
                soup = BeautifulSoup(text, 'html.parser')
                content_left = soup.find(id='content_left')
                left_list = content_left.find_all('div', recursive=False)
                if left_list:
                    div_list = left_list[-1].find_all('div', recursive=False)
                    current_date = datetime.datetime.now()

                    for div in div_list:
                        title = ''
                        source = ''
                        content = ''
                        createtime = None
                        link_url = ''
                        h3 = div.find('h3')
                        if h3:
                            a = h3.find('a')
                            if a:
                                title = a.text
                                link_url = a['href']
                        c_summary = div.find('div', class_='c-summary')
                        if c_summary:
                            if 'c-gap-top-small' in c_summary['class']:  # 带缩略图
                                c_span_last = c_summary.find('div', class_='c-span-last')
                                if c_span_last:
                                    c_author = c_span_last.find('p', class_='c-author')
                                    if c_author:
                                        author = c_author.text
                                        if len(author.split('  ')) == 1:
                                            source = ''
                                            date_info = author.split('  ')[0]
                                        else:
                                            source = author.split('  ')[0]
                                            date_info = author.split('  ')[1]
                                        tmp_date_list = re.findall(u'(\d*?)年(\d*?)月(\d*?)日\s(.*)', date_info)
                                        if tmp_date_list:
                                            tmp_date = tmp_date_list[0]
                                            createtime = datetime.datetime(int(tmp_date[0]), int(tmp_date[1]),
                                                                           int(tmp_date[2]),
                                                                           int(tmp_date[3].split(':')[0]),
                                                                           int(tmp_date[3].split(':')[1]))
                                        else:
                                            per_date = re.findall('(\d+)', date_info)
                                            if per_date:
                                                if date_info.find('分钟') > 0:
                                                    createtime = current_date + datetime.timedelta(
                                                        minutes=-int(per_date[0]))
                                                elif date_info.find('小时') > 0:
                                                    createtime = current_date + datetime.timedelta(
                                                        hours=-int(per_date[0]))
                                                createtime = createtime + datetime.timedelta(
                                                    seconds=-createtime.second)  # 秒数为空
                                    c_span_last.span.extract()
                                    c_span_last.p.extract()
                                    content = c_span_last.text
                            else:
                                c_author = c_summary.find('p', class_='c-author')
                                if c_author:
                                    author = c_author.text
                                    if len(author.split('  ')) == 1:
                                        source = ''
                                        date_info = author.split('  ')[0]
                                    else:
                                        source = author.split('  ')[0]
                                        date_info = author.split('  ')[1]
                                    tmp_date_list = re.findall(u'(\d*?)年(\d*?)月(\d*?)日\s(.*)', date_info)
                                    if tmp_date_list:
                                        tmp_date = tmp_date_list[0]
                                        createtime = datetime.datetime(int(tmp_date[0]), int(tmp_date[1]),
                                                                       int(tmp_date[2]), int(tmp_date[3].split(':')[0]),
                                                                       int(tmp_date[3].split(':')[1]))
                                    else:
                                        per_date = re.findall('(\d+)', date_info)
                                        if per_date:
                                            if date_info.find('分钟') > 0:
                                                createtime = current_date + datetime.timedelta(
                                                    minutes=-int(per_date[0]))
                                            elif date_info.find('小时') > 0:
                                                createtime = current_date + datetime.timedelta(hours=-int(per_date[0]))
                                            createtime = createtime + datetime.timedelta(
                                                seconds=-createtime.second)  # 秒数为空
                                c_summary.span.extract()
                                c_summary.p.extract()
                                content = c_summary.text
                        item = {}
                        item['title'] = title
                        item['url'] = link_url
                        item['source'] = source
                        item['createtime'] = createtime
                        item['summary'] = content
                        result['news'].append(item)
            results.append(result)
        except Exception, e:
            print traceback.format_exc()
        return results
