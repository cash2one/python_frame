# -*- coding: utf8 -*-

from bs4 import BeautifulSoup
import sxconfig
import json
import time
import domain_urllib
import utilsFunction

class PcFunction(object):

    def __init__(self):
        self.util = utilsFunction.UtilsFunction()
        self.domainUtil = domain_urllib.SeoDomain()

    def getRankListByHtmlPc(self, body, ck, spidertype):
        rankitem = {}
        rankList = list()
        rank_result_list = list()
        nextPageUrl = None

        pos = body.find("</html>")
        if pos < 0 or body.find('location.href.replace') >= 0:
            pass
        elif body.find('id="wrap"') >= 0 or body.find('<title>') < 0 or body.find('页面不存在_百度搜索') >= 0 \
                or body.find('id="container"') < 0 or body.find('id="content_left"') < 0:
            pass
        else:
            try:
                bsObj = BeautifulSoup(body, "lxml")
                nextPagelist = bsObj.find_all("a", {"class": "n"})

                if len(nextPagelist) > 0:
                    nextPageCount = len(nextPagelist) - 1
                    nextPageUrl = nextPagelist[nextPageCount].attrs["href"]

                containers = bsObj.find_all("div", {"class": "c-container"})
                if len(containers) > 0:
                    for container in containers:
                        toprank = ""
                        title = ''
                        des = ''  # 描述
                        evaluate = ""  # 评价
                        realaddress = ""
                        domain = ""
                        toprank = container.attrs["id"]

                        searchState = 0

                        realaddress_list = container.find_all("a")
                        if len(realaddress_list) > 0:
                            realaddress = realaddress_list[0].attrs["href"]

                        domain_list = container.find_all("a", {"class": "c-showurl"})
                        if len(domain_list) > 0:
                            domain = domain_list[0].get_text().strip()
                        else:
                            domain_list = container.find_all("span", {"class": "c-showurl"})
                            if len(domain_list) > 0:
                                domain = domain_list[0].get_text().strip()
                        if domain == "":
                            domain_list = container.find_all("div", {"class": "g"})
                            if len(domain_list) > 0:
                                domain = domain_list[0].get_text().strip()
                        if domain == "":
                            domain_list = container.find_all("span", {"class": "g"})
                            if len(domain_list) > 0:
                                domain = domain_list[0].get_text().strip()

                        if ck:
                            # 根据domain  和 给出的url 匹配
                            # domain 为空 跳过
                            # 提供的 url domain > 10 是 显示url 的domain 以 提供url 的domain 开头
                            # 提供的 url domain < 10  完全相等
                            # domain 解析为空 可能是 百度产品
                            if ck.find("wenku.baidu.com") > -1:
                                a_list = container.find_all("a")
                                if a_list:
                                    for i_index, a_one in enumerate(a_list):
                                        if i_index == 0 or i_index == len(a_list) - 1:
                                            continue
                                        else:
                                            try:
                                                a_href_url = a_one.attrs["href"]
                                                mu_url = self.util.findReal_Address_improve(a_href_url)

                                                ck_temp = self.extractor_wenku_url(ck)
                                                mu_url_temp = self.extractor_wenku_url(mu_url)
                                                if mu_url_temp == ck_temp:
                                                    searchState = 1
                                                    break
                                                else:
                                                    continue
                                            except:
                                                continue
                                    if searchState == 0:
                                        continue
                            else:

                                if domain == "":
                                    if spidertype == 2:
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
                                    # 文件提供的url
                                    ck_domain = self.domainUtil.sxGetDomain(ck)
                                    show_domain = self.domainUtil.sxGetDomain(domain)[0:10]

                                    if ck_domain.find(show_domain) > -1:
                                        realaddress = self.util.findReal_Address_improve(realaddress, domain=domain)  # 真实url
                                        if int(spidertype) == 2:
                                            # 提供url 和 真实url 相等
                                            ck = self.util.removeCharacters(ck)
                                            realaddress = self.util.removeCharacters(realaddress)
                                            if ck == realaddress:
                                                pass
                                            else:
                                                continue
                                        else:
                                            realaddress_domain = self.domainUtil.sxGetDomain(realaddress)

                                            if ck_domain != "" and realaddress_domain != "":
                                                if ck_domain == realaddress_domain:
                                                    pass
                                                else:
                                                    continue
                                            else:
                                                continue
                                    else:
                                        continue
                        rankList.append(toprank)
                        rank_result_list.append({"rank": toprank, "show_url": domain, "real_address": realaddress})
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

    def getPictureAndScreenPc(self, browser, ranklist, tatalWidth, tatalHeight, returnType, currentpage):
        returnDataDict = {}
        pcHeight = tatalHeight + sxconfig.pcHeightAdd
        pcRedHeight = tatalHeight + (sxconfig.borderWidth * len(ranklist) * 2) + sxconfig.pcHeightAdd

        if int(returnType[0:1]) == 1:
            browser.set_window_size(tatalWidth, pcHeight)  # 改变窗口
            time.sleep(0.5)
            capture = browser.get_screenshot_as_base64()  # 图片
            returnDataDict["capture"] = capture

        if int(returnType[1:2]) == 1:
            # browser.maximize_window()
            # browser.set_window_size(1364, 632)

            browser.set_window_size(sxconfig.pc_browser_screen_width, sxconfig.pc_browser_screen_height)
            time.sleep(0.5)
            if len(ranklist) > 0:
                rank = int(ranklist[0])
                temp_rank = (currentpage - 1) * 10
                if rank > 1 + temp_rank:
                    sxelement = browser.find_element_by_id("" + str(rank - 1))
                    browser.execute_script("arguments[0].scrollIntoView();", sxelement)

            # self.util.getScreenshot(sxconfig.fileNamePicture)  # 截屏
            screenshot = None  # 截屏
            if screenshot:
                returnDataDict["screenshot"] = screenshot
            else:
                returnDataDict["screenshot"] = browser.get_screenshot_as_base64()

        for rank in ranklist:
            # "border: 3px solid red"
            # "box-shadow: 0px 3px 0px 10px #FF0000;"
            js = "var products = document.querySelectorAll('.c-container');" \
                 " for(var i=0;i<products.length;i++){	if(products[i].getAttribute('id')=='%d'){	" \
                 "products[i].setAttribute('style','border: 3px solid red');return i+'';}}" % int(rank)
            browser.execute_script(js)

        if int(returnType[2:3]) == 1:
            browser.set_window_size(tatalWidth, pcRedHeight)
            time.sleep(0.5)
            capture_red = browser.get_screenshot_as_base64()  # 图片
            returnDataDict["capture_red"] = capture_red

        if int(returnType[3:4]) == 1:
            # self.scrollRollback(browser)
            # self.util.fullloaded(browser)

            # browser.maximize_window()
            # browser.set_window_size(1364, 632)

            browser.set_window_size(sxconfig.pc_browser_screen_width, sxconfig.pc_browser_screen_height)
            time.sleep(0.5)
            if len(ranklist) > 0:
                rank = int(ranklist[0])
                temp_rank = (currentpage - 1) * 10
                if rank > 1 + temp_rank:
                    sxelement = browser.find_element_by_id("" + str(rank - 1))
                    browser.execute_script("arguments[0].scrollIntoView();", sxelement)
                    # self.util.getScreenshot(sxconfig.fileNamePicture)  # 截屏
            screenshot_red = None  # 截屏
            if screenshot_red:
                returnDataDict["screenshot_red"] = screenshot_red
            else:
                returnDataDict["screenshot_red"] = browser.get_screenshot_as_base64()
        return returnDataDict

    def scrollRollback(self, browser):
        js = """
           window.scroll(0, 0);
           """
        browser.execute_script(js)