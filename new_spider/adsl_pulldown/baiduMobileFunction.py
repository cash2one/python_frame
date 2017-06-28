# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
import sxconfig
import json
import time

import utilsFunction
import domain_urllib
import os
from PIL import Image

class MobileFunction(object):

    def __init__(self):
        self.util = utilsFunction.UtilsFunction()
        self.domainUtil = domain_urllib.SeoDomain()

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
                                    mu_urlDomain = self.domainUtil.sxGetDomain(mu_url)
                                    ck_domain = self.domainUtil.sxGetDomain(ck)
                                    if mu_urlDomain != "" and ck_domain != "":
                                        if mu_urlDomain == ck_domain:
                                            pass
                                        else:
                                            continue
                                    else:
                                        continue
                            else:
                                continue
                        rankList.append(str(toprank))
                else:
                    pass
            except Exception, e:
                print "mobileFunction"
                print e
        rankitem['rankList'] = rankList
        rankitem['nextPageUrl'] = nextPageUrl
        return rankitem

    def getPictureAndScreenMobile(self, browser, ranklist, tatalWidth, tatalHeight, returnType):
        returnDataDict = {}

        self.util.fullloaded(browser)
        tatalHeightjs = '''return  document.body.scrollHeight'''
        tatalHeight = browser.execute_script(tatalHeightjs)
        # print tatalHeight
        mobileHeight = tatalHeight + sxconfig.mobileAddHeight
        mobileRedHeight = tatalHeight + (sxconfig.borderWidth * len(ranklist) * 2) + sxconfig.mobileAddHeight


        if int(returnType[0:1]) == 1:
            browser.set_window_size(tatalWidth, mobileHeight)
            capture = browser.get_screenshot_as_base64()  # 图片
            returnDataDict["capture"] = capture

        if int(returnType[1:2]) == 1:
            browser.set_window_size(sxconfig.baiduMobileWidth, sxconfig.baiduMobileHeight)
            if len(ranklist) > 0:
                rank = int(ranklist[0])
                if rank > 2:
                    jselement = """
                                var products = document.querySelectorAll('.c-result');
                                for(var i=0;i<products.length;i++){
                                    if(products[i].getAttribute('order')=='%d'){
                                        return products[i];
                                    }
                                }
                                """ % (int(rank)-1)
                    # sxelement = browser.find_element_by_id("" + str(rank - 1))
                    sxelement = browser.execute_script(jselement)
                    browser.execute_script("arguments[0].scrollIntoView();", sxelement)
            screenshot = browser.get_screenshot_as_base64()  # 图片
            if screenshot:
                returnDataDict["screenshot"] = screenshot
            else:
                return None

        for rank in ranklist:
            js = "var products = document.querySelectorAll('.c-result');" \
                     " for(var i=0;i<products.length;i++){	if(products[i].getAttribute('order')=='%d'){	" \
                     " containers = products[i].querySelectorAll('.c-container');" \
                     "containers[0].setAttribute('style','border: %dpx solid red;');" \
                     "return;}};" % (int(rank), sxconfig.borderWidth)
            browser.execute_script(js)
        if int(returnType[2:3]) == 1:
            browser.set_window_size(tatalWidth, mobileRedHeight)
            capture_red = browser.get_screenshot_as_base64()  # 图片
            returnDataDict["capture_red"] = capture_red

        if int(returnType[3:4]) == 1:
            browser.set_window_size(sxconfig.baiduMobileWidth, sxconfig.baiduMobileHeight)
            if len(ranklist) > 0:
                rank = int(ranklist[0])
                if rank > 2:
                    jselement = """
                                var products = document.querySelectorAll('.c-result');
                                for(var i=0;i<products.length;i++){
                                    if(products[i].getAttribute('order')=='%d'){
                                        return products[i];
                                    }
                                }
                                """ % (int(rank)-1)
                    # sxelement = browser.find_element_by_id("" + str(rank - 1))
                    sxelement = browser.execute_script(jselement)
                    browser.execute_script("arguments[0].scrollIntoView();", sxelement)
            screenshot_red = browser.get_screenshot_as_base64()  # 图片
            if screenshot_red:
                returnDataDict["screenshot_red"] = screenshot_red
            else:
                return None
        return returnDataDict

    def getDataPullDown(self, browser, returnType, targetKeywords, main_keyword):
        returnDataDict = {}
        rankIndex = list()

        browser.set_window_size(sxconfig.baiduMobileWidth, sxconfig.baiduMobileHeight)
        main_keyword = self.util.wipeoff_character(main_keyword.lower())

        self.scrollRollback(browser)
        # 隐藏天气
        self.hideWeather(browser)
        # 显示下拉
        self.showPulldown(browser)
        # "sug direct d2"
        js = "return document.querySelectorAll('.direct').length"
        pulldowncount = browser.execute_script(js)
        baiduMobileCutY2 = sxconfig.baiduMobileCutY2
        if pulldowncount > 0:
            baiduMobileCutY2 = sxconfig.baiduMobileCutY2 + pulldowncount*60

        if int(returnType[0:1]) == 1:
            # get picture
            self.util.getDataPicture(browser, sxconfig.fileNamePicture)
            # cut picture
            self.cutPicture(sxconfig.fileNamePicture, sxconfig.baiduMobileCutX1, sxconfig.baiduMobileCutY1, sxconfig.baiduMobileCutX2, baiduMobileCutY2)
            returnDataDict["capture"] = self.util.getCutPictureData(sxconfig.baiduMobileCutPicture)

        self.scrollRollback(browser)
        if int(returnType[1:2]) == 1:
            # get picture
            self.util.getDataPicture(browser, sxconfig.fileNamePicture)
            # cut picture
            self.cutPicturePulldown(sxconfig.fileNamePicture)
            returnDataDict["screenshot"] = self.util.getCutPictureData(sxconfig.baiduMobileCutPicture)

        if targetKeywords:
            targetKeywordsList = str(targetKeywords).split(",")

            if pulldowncount > 0:
                rankDetails_direct = self.direct_sug_red(browser, targetKeywordsList, main_keyword, pulldowncount)
                if rankDetails_direct:
                    rankIndex.append(rankDetails_direct)

            add_count = 1
            if pulldowncount > 0:
                add_count = add_count + pulldowncount

            js = "return document.querySelectorAll('.sug').length"
            pulldowncount = browser.execute_script(js)
            # print count
            if pulldowncount > 0:
                for keyword in targetKeywordsList:
                    for count in xrange(0, pulldowncount):
                        js = '''
                            return overflows = document.querySelectorAll('.sug')[%d].innerText
                            ''' % count
                        target = str(browser.execute_script(js))
                        if target:
                            target = self.util.wipeoff_character(target.strip()).lower()
                            keyword = self.util.wipeoff_character(keyword.lower())
                            if target.find(keyword) > -1 and target.find(main_keyword) > -1:
                                targetjs = '''
                                    document.querySelectorAll('.sug')[%d].setAttribute('style', 'border: 3px solid red;');
                                    ''' % count
                                browser.execute_script(targetjs)
                                rankDetails = dict()
                                rankDetails["keyword"] = keyword
                                rankDetails["rank"] = int(count) + add_count
                                rankIndex.append(rankDetails)

            returnDataDict["rankIndex"] = rankIndex
            time.sleep(0.5)

            self.scrollRollback(browser)
            if int(returnType[2:3]) == 1:
                self.util.getDataPicture(browser, sxconfig.fileNamePicture)
                self.cutPicture(sxconfig.fileNamePicture, sxconfig.baiduMobileCutX1, sxconfig.baiduMobileCutY1, sxconfig.baiduMobileCutX2, baiduMobileCutY2)
                returnDataDict["capture_red"] = self.util.getCutPictureData(sxconfig.baiduMobileCutPicture)

            self.scrollRollback(browser)
            if int(returnType[3:4]) == 1:
                # get picture
                self.util.getDataPicture(browser, sxconfig.fileNamePicture)
                # cut picture
                self.cutPicturePulldown(sxconfig.fileNamePicture)
                returnDataDict["screenshot_red"] = self.util.getCutPictureData(sxconfig.baiduMobileCutPicture)
        return returnDataDict

    def cutPicture(self, fileNamePicture, baiduMobileCutX1, baiduMobileCutY1, baiduMobileCutX2, baiduMobileCutY2):
        try:
            if os.path.exists(fileNamePicture):
                img = Image.open(fileNamePicture)  # 打开图像
                box = (baiduMobileCutX1, baiduMobileCutY1, baiduMobileCutX2, baiduMobileCutY2)
                roi = img.crop(box)
                roi.save(sxconfig.baiduMobileCutPicture)
        except Exception, e:
            print e
            return None

    def cutPicturePulldown(self, fileNamePicture):
        try:
            if os.path.exists(fileNamePicture):
                img = Image.open(fileNamePicture)  # 打开图像
                box = (sxconfig.baiduMobileCutX1, sxconfig.baiduMobileCutY1Screen, sxconfig.baiduMobileCutX2,
                       sxconfig.baiduMobileCutY2Screen)
                roi = img.crop(box)
                roi.save(sxconfig.baiduMobileCutPicture)

                os.remove(fileNamePicture)
        except Exception, e:
            print e
            return None

    def hideWeather(self, browser):
        js = """
            document.querySelectorAll('#weather')[0].style.display = 'none'
            """
        browser.execute_script(js)

    def scrollRollback(self, browser):
        js = """
           window.scroll(0, 0);
           """
        browser.execute_script(js)

    def showPulldown(self, browser):
        js = '''
            document.querySelectorAll(".suggest-div")[0].style.display = "block"
            '''
        browser.execute_script(js)

    def direct_sug_red(self, browser, targetKeywordsList, main_keyword, pulldowncount):
        "sug direct d2"
        rankDetails = None

        for keyword in targetKeywordsList:
            for count in xrange(0, pulldowncount):
                js = '''
                    return overflows = document.querySelectorAll('.direct')[%d].innerText
                    ''' % count
                target = str(browser.execute_script(js))
                if target:
                    target = self.util.wipeoff_character(target.strip()).lower()
                    keyword = keyword.lower()
                    if target.find(keyword) > -1 and target.find(main_keyword) > -1:
                        targetjs = '''
                            document.querySelectorAll('.direct')[%d].setAttribute('style', 'border: 3px solid red;');
                            ''' % count
                        browser.execute_script(targetjs)
                        rankDetails = dict()
                        rankDetails["keyword"] = keyword
                        rankDetails["rank"] = int(count) + 1
                        return rankDetails
