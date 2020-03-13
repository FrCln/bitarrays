import sys
sys.path.append('../../')

import numpy as np
from PIL import Image

from bitarray import BitArray

# Загружаем изображение
img = Image.open('test.bmp')
im_array = np.array(img)

# Загружаем данные в BitArray
tmp = BitArray.from_file('test.txt')

# Определяем длину сообщения и запсываем ее в первые 4 байта
tmp_len = BitArray(len(tmp), length=32)
tmp = tmp_len + tmp

# Преобразовываем данные в массив numpy
data = np.array(tmp.to_list(), dtype=np.uint8)
data_length = len(data)

# Подготавливаем массив
code = im_array.flatten()

#Обнуляем последний бит нужной части изображения
code[:data_length] &= 0b11111110

# Записываем данные в последние биты
code[:data_length] |= data

# Возвращаем массив к исходному размеру
new_img = code.reshape(im_array.shape)

# Записываем новое изображение
Image.fromarray(new_img).save('out.bmp')
