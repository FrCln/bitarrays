import sys
sys.path.append('../../')

import numpy as np
from PIL import Image

from bitarray import BitArray

img = Image.open('out.bmp')
coded_array = np.array(img).flatten()

# Определяем длину сообщения
raw_length = coded_array[:32].copy()
# Оставляем только последние биты
raw_length &= 1
# Преобразовываем в число
data_length = int(BitArray(raw_length))

# Выделяем сообщение
data = coded_array[32 : 32 + data_length]
# Оставляем только последние биты
data &= 1
# Преобразовываем в BitArray
decoded = BitArray(data)
# Сохраняем в файл
decoded.to_file('out.txt')
