# -*- coding: utf8 -*-

import urllib2
import gzip
import StringIO

class HttpUrlUtils(object):

    def removeCharacters(self, previou_url):
        if previou_url.startswith("https://"):
            previou_url = previou_url.replace("https://", "")
        if previou_url.startswith("http://"):
            previou_url = previou_url.replace("http://", "")
        if previou_url.endswith("/"):
            previou_url = previou_url[0:len(previou_url)-1]
        return previou_url

    def remove_special_characters(self, domain):
        domain = domain.replace("<b>", "")
        domain = domain.replace("</b>", "")
        domain = domain.replace("&nbsp", "")
        domain = domain.replace("....", "")
        domain = domain.replace("...", "")
        return domain

def main():
    sx = HttpUrlUtils()
    print sx.removeCharacters("http://webtest.winndoo.com/lis...")
    pass

if __name__ == '__main__':
    main()