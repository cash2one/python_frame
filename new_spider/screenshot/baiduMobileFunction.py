# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
import config
import json
import time
from screenshot.utilsFunction import UtilsFunction

class MobileFunction(object):

    def __init__(self):
        self.util = UtilsFunction()
        pass

    def getRankListByHtmlMobile(self, body, ck, spidertype):
        rankitem = {}
        rankList = list()
        pos = body.find("</html>")
        nextPageUrl = None

        if pos < 0:
            pass
        else:
            try:
                bsObj = BeautifulSoup(body, "lxml")

                nextPageUrlList = bsObj.find_all("a", {"class": "new-nextpage-only"})
                if nextPageUrlList:
                    nextPageUrl = nextPageUrlList[0].attrs['href']
                    # print nextPageUrl
                else:
                    nextPageUrlList = bsObj.find_all("a", {"class": "new-nextpage"})
                    if nextPageUrlList:
                        nextPageUrl = nextPageUrlList[0].attrs['href']
                        # print nextPageUrl

                containers = bsObj.find_all("div", {"class": "c-result"})

                if len(containers) > 0:
                    for container in containers:
                        toprank = ""
                        title = ''
                        des = ''  # 描述
                        evaluate = ""  # 评价
                        realaddress = ""
                        domain = ""

                        order = int(container.attrs['order'])
                        if order:
                            toprank = order

                        domain_list = container.find_all("a", {"class": "c-showurl"})
                        if len(domain_list) > 0:
                            domain = domain_list[0].get_text().strip()
                        else:
                            domain_list = container.find_all("span", {"class": "c-showurl"})
                            if len(domain_list) > 0:
                                domain = domain_list[0].get_text().strip()
                        if ck:
                            # 根据domain  和 给出的url 匹配
                            # if domain == "":
                            #     continue
                            datalog = container.attrs['data-log']
                            if datalog:
                                datalog = str(datalog).replace("\'", "\"")
                                sx_data = json.loads(datalog)
                                mu_url = sx_data["mu"]
                                if int(spidertype) == 2:
                                    # 提供url 和 真实url 相等
                                    if mu_url == ck:
                                        pass
                                    else:
                                        continue
                                else:
                                    mu_urlDomain = self.util.get_domain(mu_url)
                                    ck_domain = self.util.get_domain(ck)
                                    if mu_urlDomain != "" and ck_domain != "":
                                        if mu_urlDomain == ck_domain:
                                            pass
                                        else:
                                            continue
                                    else:
                                        # print "mu_urlDomain or ck_domain have kong" + mu_url
                                        continue
                            else:
                                continue
                        rankList.append(toprank)
                else:
                    pass
            except Exception, e:
                print "mobileFunction"
                print e
        rankitem['rankList'] = rankList
        rankitem['nextPageUrl'] = nextPageUrl
        return rankitem

    def getPictureAndScreenMobile(self, browser, ranklist, tatalWidth, tatalHeight, returnType):
        returndata = ""

        self.util.fullloaded(browser)
        tatalHeightjs = '''return  document.body.scrollHeight'''
        tatalHeight = browser.execute_script(tatalHeightjs)
        # print tatalHeight

        mobileHeight = tatalHeight+config.mobileAddHeight
        mobileRedHeight = tatalHeight + (config.borderWidth * len(ranklist)*2) + config.mobileAddHeight
        # print mobileHeight
        # print mobileRedHeight

        browser.set_window_size(tatalWidth, mobileHeight)

        # from PIL import ImageGrab, Image
        # element = browser.find_element_by_tag_name("body")
        # left = element.location['x']
        # top = element.location['y']
        # right = element.location['x'] + element.size['width']
        # bottom = element.location['y'] + element.size['height']
        # # left = element.location['10']
        # # top = element.location['10']
        # # right = element.location['10'] + element.size['200']
        # # bottom = element.location['10'] + element.size['200']
        # im = Image.open('sun.png')
        # im = im.crop((left, top, right, bottom))
        # im.save('sun.png')

        if int(returnType[0:1]) == 1:
            capture = browser.get_screenshot_as_base64()  # 图片
            returndata = capture+"||||"
        for rank in ranklist:
            js = "var products = document.querySelectorAll('.c-result');" \
                     " for(var i=0;i<products.length;i++){	if(products[i].getAttribute('order')=='%d'){	" \
                     " containers = products[i].querySelectorAll('.c-container');" \
                     "containers[0].setAttribute('style','border: %dpx solid red;');" \
                     "return;}}" % (int(rank), config.borderWidth)
            browser.execute_script(js)
        if int(returnType[1:2]) == 1:
            browser.set_window_size(tatalWidth, mobileRedHeight)
            capture_red = browser.get_screenshot_as_base64()  # 图片
            returndata = returndata+capture_red + "||||"
        return returndata
