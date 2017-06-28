# -*- coding: utf8 -*-

# def application(environ, start_response):
#     start_response('200 OK', [('Content-Type', 'text/html')])
#     return '<h1>Hello, %s!</h1>' % (environ['PATH_INFO'][1:] or 'web')

def application(environ, start_response):
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']

    return "method: %s;path:%s" % (str(method), str(path))

    # if method=='GET' and path=='/':
    #     return "method is get"
    #     # return handle_home(environ, start_response)
    # if method=='POST' and path='/signin':
    #     return "method is post"
    #     # return handle_signin(environ, start_response)

    # if method=='GET' and path=='/':
    #     return handle_home(environ, start_response)
    # if method=='POST' and path='/signin':
    #     return handle_signin(environ, start_response)