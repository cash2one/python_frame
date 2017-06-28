# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import gevent
from gevent import monkey, pool
monkey.patch_all()
jobs = []
links = []
p = pool.Pool(10)

'''
    协程池的使用
'''

urls = [
    'https://www.baidu.com/'
    # ... another 100 urls
]
def get_links(url):
    r = requests.get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "lxml")
        print links + soup.find_all('a')

for url in urls:
    jobs.append(p.spawn(get_links, url))

gevent.joinall(jobs)

'''
    monkey可以使一些阻塞的模块变得不阻塞，机制：遇到IO操作则自动切换，手动切换可以用gevent.sleep(0)（将爬虫代码换成这个，效果一样可以达到切换上下文）
    gevent.spawn 启动协程，参数为函数名称，参数名称
    gevent.joinall 停止协程
'''