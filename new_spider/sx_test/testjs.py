# -*- coding:utf-8 -*-

import execjs,os


# js = '''
#     function mix(tk, bid) {
#         var tk = tk.split("").reverse().join("");
#         return tk.substring(bid.length, tk.length);}
# '''
# print execjs.compile(js)

#
# import execjs
# print execjs.eval("'red yellow blue'.split(' ')")

ctx = execjs.compile("""
     function add(x, y) {
         return x + y;
     }
 """)
print ctx.call("add", 1, 2)
