# -*- coding: utf8 -*-

if __name__ == '__main__':
    # json_str = """
    # """
    # import json
    # r = json.loads(json_str)
    # print r
    import re
    exp = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    r = exp.sub("",'<ul class="list-34 related-ul" alog-group="qb-relative-que">')
    print r