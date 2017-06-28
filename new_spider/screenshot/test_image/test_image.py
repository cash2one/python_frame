# -*- coding: utf8 -*-


import PIL

from PIL import Image

# from PIL import ImageGrab

# import Image
im = Image.open('temp.PNG')
print im.format, im.size, im.mode
# PNG (400, 300) RGB
im.thumbnail((400, 300))
im.save('thu0.jpg', 'JPEG')


# image = ImageGrab.grab()
# image.save(fileNamePicture)


