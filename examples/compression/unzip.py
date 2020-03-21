import pickle
import sys
sys.path.append('../../')

from bitarray import BitArray

data = BitArray.from_file('test.bin')

dict_len = int(data[:32])
code = pickle.loads(data[32 : 32 + dict_len].to_bytes())
data = data[32 + dict_len:]

decoded = data.decode(code)

with open('out.txt', 'w') as f:
    f.write(decoded)
