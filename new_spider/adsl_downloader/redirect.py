# -*- coding: utf8 -*-
from urllib2 import HTTPRedirectHandler


class UnRedirectHandler(HTTPRedirectHandler):

    def __init__(self):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        if 'location' in headers:
            newurl = headers.getheaders('location')[0]
            return newurl, code, headers
        pass

    http_error_301 = http_error_303 = http_error_307 = http_error_302
