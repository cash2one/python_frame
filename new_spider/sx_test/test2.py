# -*- coding: utf8 -*-

# 匿名函数
print map(lambda x: x * x, [1, 2, 3, 4, 5, 6, 7, 8, 9])



def log(func):
    def wrapper(*args, **kw):
        print 'call %s():' % func.__name__
        return func(*args, **kw)
    return wrapper

@log
def now():
    print '2013-12-25'

f = now
print f()
print now.__name__

