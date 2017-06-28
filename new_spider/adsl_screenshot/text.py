# -*- coding:utf-8 -*-

import base64
with open("temp.txt", "rb") as f:
    content = f.read()

sxcapture = base64.b64decode(content)
file = open("scapture.png", "wb")
file.write(sxcapture)
file.close()