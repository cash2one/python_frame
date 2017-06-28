#coding=utf-8
import os
import sys
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(PROJECT_PATH)
sys.path.append(os.path.join(PROJECT_PATH, 'new_spider'))
sys.path.append(os.path.join(PROJECT_PATH, 'store'))
sys.path.append(os.path.join(PROJECT_PATH, 'util'))
import traceback as tb
from ApiSDKJsonClient import *
from sms_service_KRService import *
import logging
import time
import urllib
from spider import config
from store.wdsystem.baidu_pc import OutlinksSourceStore
from store_mysql import StoreMysql
import re
class KeywordBaiduAPI(object): 
    def __init__(self):
        self.service = sms_service_KRService();
    
    '''
          一次只能请求一个种子词或url
    query:种子词或url
    querytype:1-种子词 ,2—url
    maxNum:最大请求数目 
    device:0-pc+m,1-pc,2-m
    positiveWord:返回结果包含词
    '''
    def getKRByQuery(self,query,querytype=1,maxNum=10,device=0,positiveWord = None):
        '''
                    返回:
        word:扩展词
        pv:30天内日均搜索量
        pcPv:
        mobilePv:
        competition:
        '''
        kwh = {}
        kwh['query'] = query 
        kwh['queryType'] = querytype
        seedFilter = {}
        seedFilter['maxNum'] = maxNum
        seedFilter['device'] = device
        seedFilter['positiveWord'] = positiveWord        kwh['seedFilter'] = seedFilter
        try:
            response =  self.service.getKRByQuery(kwh)
            data_list = response['body']['data']
            return data_list
        except Exception as e:
            return []
    
    '''
           根据种子词列表获取推荐词
    seedWords:最大序列100 
    maxNum:最大扩展词数
    device:0-pc+m,1-pc,2-m
    '''
    def getKRFileIdByWords(self,seedWords=[],maxNum=10,device=0):
        '''
                        返回:
            word:扩展词
            competition:竞争度
            wordPackage:包名
            businessPoints:业务名
            recBid:
            pv:30天内日均搜索量
            showReasons:展现理由
        '''
        kwh = {}
        kwh['seedWords'] = seedWords
        seedFilter= {}
        seedFilter['maxNum'] = maxNum
        seedFilter['device'] = device
        kwh['seedFilter'] = seedFilter
        try:
            response = self.service.getKRFileIdByWords(kwh)
            data = response['body']['data'][0]
            fileId = data['fileId']
            try_times = 1
            while True:
                logging.info('sleep 5 seconds ...')
                time.sleep(5)
                response = self.service.getFileStatus({"fileId":fileId})
                data = response['body']['data'][0]
                if data['isGenerated'] == 1:
                    logging.info("%s state is done" % fileId)
                elif data['isGenerated'] == 2:
                    logging.info("%s state is done" % fileId)
                elif data['isGenerated'] == 3:
                    logging.info("%s state is done" % fileId)
                    break
                if try_times > 30:
                    logging.info("%s wait too long time" % fileId)
                    return []
                
            response = self.service.getFilePath({"fileId":fileId})
            data = response['body']['data'][0]
            file_path = data['filePath']
            print file_path
            content = urllib.urlopen(file_path).read()
            file_content = content.decode('gbk').encode('utf8')
            file_content_list = file_content.split('\n')
            total_content_list = []
            for file_item in file_content_list:
                total_content_list.append(file_item)
            return total_content_list
        except Exception as e:
            return []
    def getkwd(self):
        db = StoreMysql(**config.SITEANALYSTAPi_DB)
        sql = 'select id,keyword from kwdsystem_keywords_escbx_pc'
        res =db.query(sql)
        k = KeywordBaiduAPI() 
        for kwd in res:
            data = k.getKRByQuery(kwd[1], 1, 10,1)
            keyword = re.sub(r'\.','',kwd[1])
            keyword = re.sub(r' ','',keyword)
            for d in data:
                word = d['word']
                if word== keyword:
                    updatesql='update kwdsystem_keywords_escbx_pc set pc_pv="%s" where id=%s' % (d['pcPV'],kwd[0])
                    db.do(updatesql)
                    print d['word'],d['pv'],d['competition'],d['pcPV'],d['mobilePV']
                    break
    def getkwdm(self):
        db = StoreMysql(**config.SITEANALYSTAPi_DB)
        sql = 'select id,keyword from kwdsystem_keywords_escbx_m'
        res =db.query(sql)
        k = KeywordBaiduAPI() 
        for kwd in res:
            data = k.getKRByQuery(kwd[1], 1, 10,1)
            keyword = re.sub(r'\.','',kwd[1])
            keyword = re.sub(r' ','',keyword)
            for d in data:
                word = d['word']
                if word== keyword:
                    updatesql='update kwdsystem_keywords_escbx_pc set pc_pv="%s" where id=%s' % (d['pcPV'],kwd[0])
                    db.do(updatesql)
                    print d['word'],d['pv'],d['competition'],d['pcPV'],d['mobilePV']
                    break
    def run(self):
        db = StoreMysql(**config.SITEANALYSTAPi_DB)
        sql = 'select id,keyword,cateid from kwdsystem_keywords where kuoci=0 and cateid=%s' % sys.argv[1] 
        res =db.query(sql)
        k = KeywordBaiduAPI() 
    def kwd(self):
        db = StoreMysql(**config.SITEANALYSTAPi_DB)
        sql = 'select id,keyword,cateid from kwdsystem_keywords_escbx_pc'
        res =db.query(sql)
        k = KeywordBaiduAPI()
        kwdlist = list()
        ln = len(res)
        xlist = list()
        for r in res:
            xlist.append(r[1])
        for kwd in res:
            keyword = re.sub(r'\.','',kwd[1])
            keyword = re.sub(r' ','',keyword)
            kwdlist.append(keyword)
            ln-=1
            if len(kwdlist)==50 or ln==0:
                try:
                    print ln
                    content = k.getKRFileIdByWords(kwdlist,maxNum=100,device=1)
                    cwd=''
                    for c in content:
                        try:
                            wds = c.split(',')
                            if not wds[0]:
                                continue
                            if not wds[1] in xlist:
                                continue
                            updatesql='update kwdsystem_keywords_escbx_pc set pc_pv="%s" where keyword="%s"' % (wds[6],wds[1])
                            db.do(updatesql)
                            xlist.remove(wds[1])
                            if len(xlist)<1:
                                return True
                        except:
                            continue
                    kwdlist=list()
                except Exception,e:
                    kwdlist=list()
                    print str(e)
                    continue
            
    def getrun(self):
        db = StoreMysql(**config.SITEANALYSTAPi_DB)
        sql = 'select id,keyword,cateid from kwdsystem_keywords_escbx_m order by id desc limit 11100'
        res =db.query(sql)
        k = KeywordBaiduAPI()
        kwdlist = list()
        ln = len(res)
        xlist = list()
        #for x in res:
        #    xlist.append(x[1]) 
        for kwd in res:
            print kwd[1]
            keyword = re.sub(r'\.','',kwd[1])
            keyword = re.sub(r' ','',keyword)
            kwdlist.append(keyword)
            ln-=1
            try:
                if len(kwdlist)==100 or ln==0:
                    print ln
                    content = k.getKRFileIdByWords(kwdlist,maxNum=100,device=2)
                    xl =len(content)
                    ssql = 'insert into m_keywords_tmp(`keyword`,`m_pv`)values'
                    inval = ''
                    for c in content:
                        try:
                            wds = c.split(',')
                            if not wds[0]:
                                continue
                            if int(wds[6])<1:
                                continue
                            inval='("%s","%s")' %(wds[1],wds[6])
                            try:
                                insql=ssql+inval
                                db.do(insql)
                            except:
                                continue
                        except:
                            continue
                    #    try:
                    #        wds = c.split(',')
                    #        if not wds[0]:
                    #            continue
                    #        if not wds[1] in xlist:
                    #            continue
                    #        updatesql='update kwdsystem_keywords_escbx_m set m_pv="%s" where keyword="%s"' % (wds[6],wds[1])
                    #        print updatesql
                    #        db.do(updatesql)
                    #        xlist.remove(wds[1])
                    #        if len(xlist)<1:
                    #            return True
                    #    except Exception,e:
                    #        print str(e)
                    #        continue
                    kwdlist=list()
            except Exception,e:
                kwdlist=list()
                print str(e)
                continue
            
       
def main():
    pass
    
    #批量扩词
    seedWords = keyword_list[0:1]
    content_list = k.getKRFileIdByWords(seedWords=seedWords,maxNum=3,device=2)
    for w in content_list:
        w = w.replace('\n','')
        for c in content_list:
            word = c['word']
            word = word.encode("utf-8")
            if w == word:
                f = open('kr.txt','a')
                f.write('%s\t%s\n' %(w,c['pv']))
                f.close()
                break
        
if __name__ == "__main__":
    kwd = KeywordBaiduAPI()
    if sys.argv[1]=='kwd':
        kwd.kwd()
    if sys.argv[1]=='run':
        kwd.getrun()
