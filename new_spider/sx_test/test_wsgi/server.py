# -*- coding: utf8 -*-

# 从wsgiref模块导入:
from wsgiref.simple_server import make_server
# 导入我们自己编写的application函数:
from hello import application

# "host, port, app, server_class=WSGIServer, handler_class=WSGIRequestHandler"
# 创建一个服务器，IP地址为空，端口是8000，处理函数是application:
# localhost:8111
httpd = make_server('', 8111, application)
print "Serving HTTP on port 8111..."
# 开始监听HTTP请求:
httpd.serve_forever()