# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
import sxconfig
import json
import time

import utilsFunction
import domain_urllib

class MobileFunction(object):

    def __init__(self):
        self.util = utilsFunction.UtilsFunction()
        self.domainUtil = domain_urllib.SeoDomain()

    def getRankListByHtmlMobile(self, body, ck, spidertype):
        rankitem = {}
        rankList = list()
        rank_result_list = list()
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
                        searchState = 0

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
                                try:
                                    datalog = str(datalog).replace("\'", "\"")
                                    sx_data = json.loads(datalog)
                                    mu_url = sx_data["mu"]
                                except:
                                    mu_url = domain

                                if int(spidertype) == 2:
                                    # 提供url 和 真实url 相等
                                    if mu_url.find("wk.baidu.com") > -1:
                                        # 文库
                                        a_list = container.find_all("a")
                                        if a_list:
                                            for i_index, a_one in enumerate(a_list):
                                                if i_index == 0 or i_index == len(a_list) - 1:
                                                    continue
                                                else:
                                                    a_href_url = a_one.attrs["href"]
                                                    mu_url = self.util.findReal_Address_improve(a_href_url)
                                                    ck_temp = self.extractor_wenku_url(ck)
                                                    mu_url_temp = self.extractor_wenku_url(mu_url)
                                                    if mu_url_temp == ck_temp:
                                                        searchState = 1
                                                        break
                                                    else:
                                                        continue
                                            if searchState == 0:
                                                continue
                                    else:
                                        ck = self.util.removeCharacters(ck)
                                        mu_url = self.util.removeCharacters(mu_url)
                                        if mu_url == ck:
                                            pass
                                        else:
                                            if domain == "":
                                                alist = container.find_all("a")
                                                if alist:
                                                    for ahref in alist:
                                                        try:
                                                            href = ahref.attrs["href"]
                                                            href = self.util.removeCharacters(href)
                                                            ck = self.util.removeCharacters(ck)
                                                            if href == ck:
                                                                searchState = 1
                                                                break
                                                        except Exception:
                                                            continue
                                            if searchState == 0:
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
                        rank_result_list.append({"rank": toprank, "show_url": domain, "real_address": mu_url})
                        rankList.append(str(toprank))
                else:
                    pass
            except Exception, e:
                print e
        rankitem['rankList'] = rankList
        rankitem['nextPageUrl'] = nextPageUrl
        rankitem["rank_result_list"] = rank_result_list
        return rankitem

    def extractor_wenku_url(self, wenku_url):
        end_index = wenku_url.find(".html")
        temp_url = wenku_url[0: end_index]
        start_index = temp_url.rfind("/")
        return temp_url[start_index+1: end_index]

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
                if rank > 1:
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
                elif rank == 1:
                    js = '''
                        return  document.querySelectorAll('.c-result')[0]
                        '''
                    sxelement = browser.execute_script(js)
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
                if rank > 1:
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
                elif rank == 1:
                    js = '''
                        return  document.querySelectorAll('.c-result')[0]
                        '''
                    sxelement = browser.execute_script(js)
                    browser.execute_script("arguments[0].scrollIntoView();", sxelement)

            screenshot_red = browser.get_screenshot_as_base64()  # 图片
            if screenshot_red:
                returnDataDict["screenshot_red"] = screenshot_red
            else:
                return None
        return returnDataDict
