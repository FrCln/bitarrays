from collections import Counter
from math import ceil, log2
import pickle
import sys
sys.path.append('../../')

from bitarray import BitArray


def generate_bit_codes(length, value=''):
    if not length:
        yield value
    else:
        for c in '01':
            yield from generate_bit_codes(length - 1, value + c)


test_string = open('test.txt').read()

cnt = Counter(test_string)

new_len = ceil(log2(len(cnt))) * len(test_string)

val = sorted(cnt.items(), key=lambda x: x[1])
cmpr = []

while val:
    prev_len = new_len
    cmpr.append(val.pop())
    compr_len = sum(cmpr[i][1] * (i + 1) for i in range(len(cmpr)))
    if val:
        add_len = (ceil(log2(len(val))) + len(cmpr)) * (len(test_string) - sum(cnt[x[0]] for x in cmpr))
    else:
        add_len = 0
    new_len = compr_len + add_len
    if new_len >= prev_len:
        cmpr.pop()
        break

code = {}
for i, (symbol, _) in enumerate(cmpr):
    code[symbol] = '1'*i + '0'
    cnt.pop(symbol)

gen = generate_bit_codes(ceil(log2(len(cnt) + 1)))
for symbol in cnt:
    code[symbol] = '1' + next(gen)

data = BitArray.from_bytes(pickle.dumps(code))
data = BitArray(len(data), 32) + data + BitArray.encode(code, test_string)
data.to_file('test.bin')

