
# -*- coding: utf8 -*-
import urllib2
import urllib
import json
import base64
import os
import sys
import re
reload(sys)
sys.setdefaultencoding('utf8')
import subprocess
import time
import execjs

re_image_content_type = re.compile('image')

def encoding(data):
    types = ['utf-8', 'gb2312', 'gbk', 'gb18030', 'iso-8859-1']
    for t in types:
        try:
            return data.decode(t)
        except Exception:
            pass
    return None

def save_results(results, task_ids):
    request = urllib2.Request(task_url,
                              data=urllib.urlencode({
                                  'type': 'html',
                                  'results': json.dumps(results),
                                  'task_ids': task_ids,
                                  'client_id': client_id
                              }))
    urllib2.urlopen(request)

def get_result(opener, request, result, redirect, flag):
    for i in range(0, 2):
        if not flag:
            return flag
        else:
            try:
                response = opener.open(request, timeout=20)
                if isinstance(response, tuple):
                    header = response[2]
                    result["status"] = "2"
                    result["redirect_url"] = response[0]
                    result["code"] = response[1]
                    if str(result["type"]) == "2":
                        result["header"] = str(header)
                    if redirect == '0':
                        break
                    headers = {}
                    if "User-agent" in request.headers.keys():
                        headers = {"User-agent": request.headers.get("User-agent")}
                    request = urllib2.Request(result["redirect_url"], headers=headers)
                    flag = get_result(opener, request, result, redirect, flag)
                else:
                    header = response.info()
                    body = response.read()
                    body = get_body(header, body)
                    if body is not None:
                        result["result"] = body
                        result["status"] = "2"
                        if str(result["type"]) == "2":
                            result["header"] = str(header)
                        return False
            except urllib2.HTTPError, e:
                result["code"] = e.code
                return False
            except Exception as e:
                print e
                for count in xrange(0, 10):
                    if not ping():
                        time.sleep(1)
                    else:
                        break
    return False

def extractor_qualify_execjs(body):
    try:
        mxi_middle = re.findall(r"function mix(.*?)\(function", body)
        if mxi_middle:
            js_exe = "function mix" + mxi_middle[0]

        tkids = re.findall(r"tk = document.getElementById\('(.*?)'", body)
        if tkids:
            tk_id = tkids[0]

        attributes = re.findall(r"\).getAttribute\('(.*?)'\)", body)
        if attributes:
            tk_attribute = attributes[0]

        attr_text = re.findall(r'id="%s" %s="(.*?)"' % (tk_id, tk_attribute), body)
        if attr_text:
            tk = attr_text[0]

        baiducode_content = re.findall(r'id="baiducode">(.*?)<', body)
        if baiducode_content:
            bid = baiducode_content[0]

        ctx = execjs.compile(js_exe)
        tot = ctx.call("mix", tk, bid)

        pids = re.findall(r'result.*?pid":"(.*?)"', body)
        if pids:
            pid = pids[0]

        return "http://xin.baidu.com/detail/basicAjax?pid=%s&tot=%s" % (pid, tot)
    except Exception as e:
        return -1

def get_body(header, body):
    if ('Content-Encoding' in header and header['Content-Encoding']) or ('content-encoding' in header and header['content-encoding']):
        import gzip
        import StringIO
        d = StringIO.StringIO(body)
        gz = gzip.GzipFile(fileobj=d)
        body = gz.read()
        gz.close()
    body = encoding(body)
    return body

def ping():
    try:
        f_null = open(os.devnull, 'w')
        result = subprocess.call('ping -n 1 -w 10 qq.com', shell=True, stdout=f_null, stderr=f_null)
        f_null.close()
        if result:
            return False
        else:
            return True
    except:
        return False

results = list()
opener = urllib2.build_opener()
request = urllib2.Request("http://xin.baidu.com/detail/compinfo?pid=PbObuEVtIKUUFMyW7w*MAHcEPPjWmHT5lg3G&from=koubei")
redirect = "0"
result = {"id": str(task["id"]), "url": "", "type": task["type"],
                      "store_type": task["store_type"], "status": "3", "result": "", "header": "",
                      "redirect_url": "", "code": 0, "md5": task["md5"]
                      }
get_result(opener, request, result, redirect, True)

if result["result"] != "":
    redirect_u = extractor_qualify_execjs(result["result"])
    request = urllib2.Request(redirect_u)
    opener = urllib2.build_opener()
    get_result(opener, request, result, redirect, True)
    result["result"] = base64.b64encode(result["result"])
    result["status"] = 2
else:
    result["result"] = ""
results.append(result)
if len(results) > 0:
    save_results(results, task_ids)

    