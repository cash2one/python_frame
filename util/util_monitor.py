#coding=utf8
import re,os,sys,time,urllib,random
from datetime import datetime,timedelta
#from xlwt import *
import email.Header
import email.MIMEBase
import email.MIMEMultipart
import email.MIMEText
import smtplib
import socket
import string
import time
import chardet
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append('/home/wangming/projects/util')

from util_log import UtilLogger
from spider import spider

#邮件服务器 后缀配置
SMTPSERVER_CONFIG={
        'winndoo.com':'smtp.exmail.qq.com',
        '163.com':'smtp.163.com',
}

class UtilMonitor(object):

    '''
    sender:发件人
    password:密码
    message_from:邮件代表
    '''
    def __init__(self,sender,password,message_from=''):
        self.log = UtilLogger("monitor", "monitor")
        self.spider = spider()
        self.message_from = message_from
        self.sender = sender
        self.password = password
        self.init_smtpserver()

    def init_smtpserver(self):
        try:
            self.smtp_server = SMTPSERVER_CONFIG.get((self.sender.split('@')[1]))
        except Exception,e:
            self.log.error('not found smtpserver')
            raise Exception,'not found smtpserver'

    '''
    recp:收件人[多个收件人用';'隔开]
    cc:抄送
    bcc:
    subject:主题
    subtype:类型
    content:内容
    importance:重要程度
    attachfilelist:附件列表[附件全路径名]
    '''
    def send_mail(self, recp, cc,subject, content,subtype="html", importance="", attachfilelist=[]):
        socket.setdefaulttimeout(180)
        msg = email.Message.Message()
        msg['to'] = recp
        msg['cc'] = cc
        if self.message_from:
            msg['From'] = self.message_from
        msg['date']    = time.ctime()
        msg['subject'] = email.Header.Header(subject,'utf8')
        if importance != "":
            msg['Importance'] = importance

        body=email.MIMEText.MIMEText(content, _subtype=subtype, _charset='utf8')

        if attachfilelist:
            attach = email.MIMEMultipart.MIMEMultipart()
            attach.attach(body)
            for attachfile in attachfilelist:
                contype = 'application/octet-stream'
                maintype, subtype = contype.split('/', 1)
                filedata=open(attachfile,'rb')
                file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
                file_msg.set_payload(filedata.read( ))
                filedata.close()
                email.Encoders.encode_base64(file_msg)
                file_msg.add_header('Content-Disposition', 'attachment', filename=attachfile[attachfile.rfind('/')+1:] )
                attach.attach(file_msg)
        '''
        if attachfile != "" :
            attach = email.MIMEMultipart.MIMEMultipart()
            attach.attach(body)
            contype = 'application/octet-stream'
            maintype, subtype = contype.split('/', 1)
            filedata=open(attachfile,'rb')
            file_msg = email.MIMEBase.MIMEBase(maintype, subtype)
            file_msg.set_payload(filedata.read( ))
            filedata.close()
            email.Encoders.encode_base64(file_msg)
            file_msg.add_header('Content-Disposition', 'attachment', filename=attachfile[attachfile.rfind('/')+1:] )
            attach.attach(file_msg) '''
        try:
            server = smtplib.SMTP(self.smtp_server)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.sender,self.password)
            if not attachfilelist:
                server.sendmail(self.sender, string.split(recp+';'+cc,";"), msg.as_string()[:-1]+body.as_string() )
            else:
                server.sendmail(self.sender, string.split(recp+';'+cc,";"), msg.as_string()[:-1]+attach.as_string())

            return
        except Exception, e:
            print e
            self.log.error("From: "+ self.sender+ "To: "+  recp +"Exception: " +str(e))
            return

    '''
    发送短信
    '''
    def send_SMS(self, content = "", mobile=''):
        try:
            if mobile == '':
                self.log.error('no conent to send!')
                return

            self.log.info(content)
            #url = "http://125.39.216.138:9999/sendsms.php?user=webmonitor&passwd=d3gq39rko&mobile=%s&content=%s" %(self.mobile, content)
            #self.spider.tryGet(url)
            #url = 'http://sms.service.kuxun.cn/task/create'
            #post_data = 'token=51d3d6fc72fba&mobile=%s&content=%s' %(mobile, content)
            url = 'http://service.message.mogubang.cn/message/sms/send.json'
            post_data = '{"sendtyep": "1",  "data": {"authcode": " %s"},  "sysid": "01",  "receivers": ["%s"],  "sign": null,  "mid": null,  "tplid": "S0101001"}' %(content,mobile)
            #self.spider.post_json(url,post_data)
            self.spider.post(url, post_data)
        except Exception,e:
            self.log.error('send sms error:' + str(e))


def test(argv=sys.argv):
    um = UtilMonitor('ming.wang@winndoo.com','m1593572648M')
    um.send_mail('ming.wang@winndoo.com','ming.wang@winndoo.com','test','test','','',['util_log.py'])
    #um.send_SMS('test','18612321506')

if __name__ == "__main__":
    test()
