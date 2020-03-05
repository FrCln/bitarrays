'''
Визуализация информации, содержащейся в последнем бите изображения.
'''

import numpy as np
from PIL import Image

for file in ('test.bmp', 'out.bmp'):
    img_src = np.array(Image.open(file))
    # Выделяем только последние биты
    img_src &= 1
    # Увеличиваем контрастность
    img_src *= 255
    # Сохраняем полученное изображение
    Image.fromarray(img_src).save('analyse' + file)
