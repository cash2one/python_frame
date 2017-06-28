

# sx_dict = dict()
# sx_dict["username"] = "111"
# sx_dict["rr"] = "1"
#
# print type(str(sx_dict))

import json
sx = ["{\"redirest\": 1}"]
tem = json.dumps(sx)
# print tem
# print json.loads(tem)

# text = """[
#     "{\"redirect\": 0, \"store_type\": 1, \"url\": \"dhhd\", \"param\": null, \"header\": \"{}\", \"type\": 7, \"id\": \"1_12\", \"md5\": \"bef4db29dee47f7bc4e28764cfbbbe85\"}",
#     "{\"redirect\": 0, \"store_type\": 1, \"url\": \"www.baidu.com\", \"param\": null, \"header\": \"{}\", \"type\": 7, \"id\": \"1_14\", \"md5\": \"dab19e82e1f9a681ee73346d3e7a575e\"}"
# ]"""

# text = '''["{\"redirect\": 0, \"store_type\": 1, \"url\": \"www.baidu.com\", \"param\": null, \"header\": \"{}\", \"type\": 7, \"id\": \"1_14\", \"md5\": \"dab19e82e1f9a681ee73346d3e7a575e\"}"]'''


sx = """["{\"redirect\": 0, \"store_type\": 1, \"url\": \"https://m.baidu.com/s?wd=%E6%B8%A9%E5%B7%9E%E6%B1%82%E8%81%8C&pn=20\", \"param\": null, \"header\": \"{\\\"User-Agent\\\": \\\"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36\\\"}\", \"type\": 1, \"id\": \"8_575674\", \"md5\": \"6956fff18787cefbe739db409822df8e\"}","{\"redirect\": 0, \"store_type\": 1, \"url\": \"https://m.baidu.com/s?wd=%E6%89%BE%E5%B7%A5%E4%BD%9C%E5%A4%A7%E5%BA%86&pn=20\", \"param\": null, \"header\": \"{\\\"User-Agent\\\": \\\"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36\\\"}\", \"type\": 1, \"id\": \"8_575675\", \"md5\": \"8507d3f9e99038b77c9077e267db51d4\"}","{\"redirect\": 0, \"store_type\": 1, \"url\": \"http://www.baidu.com/link?url=L6Y_VhpsAl8cTMNF4LxAAXMzNDRSJXZetoHs7c0-XPDZL1GnOwNcypTvZC5-MfbjujA-9jxPZxV1GXDQZrN_A_\", \"param\": null, \"header\": \"{\\\"User-Agent\\\": \\\"Mozilla/5.0 (X11; U; Linux i686; hu-HU; rv:1.9.0.7) Gecko/2009030422 Ubuntu/8.10 (intrepid) Firefox/3.0.7 FirePHP/0.2.4\\\"}\", \"type\": 2, \"id\": \"8_575677\", \"md5\": \"014ad90f255e8dd585f727387499da57\"}"]"""
print json.loads(sx)
