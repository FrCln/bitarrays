import random
from time import process_time
import sys
sys.path.append('../')

from bitarray import BitArray

LEN = 100000

a = BitArray.random(LEN)
b = a.to_list()

print('BitArray slower than list')
print('Iteration')
for entity in (a, b):
    start = process_time()
    for i in entity:
        j = i
    print(entity.__class__.__name__, process_time() - start)

print('Random indexing')
ri = [random.randint(0, len(a) - 1) for i in range(LEN)]
for entity in (a, b):
    start = process_time()
    for i in ri:
        j = entity[i]
    print(entity.__class__.__name__, process_time() - start)

print('Appending')
a = BitArray()
b = []
for entity in (a, b):
    start = process_time()
    for i in range(LEN):
        entity.append(0)
    print(entity.__class__.__name__, process_time() - start)

print()
print('BitArray faster than list')
print('Count')
for entity in (a, b):
    start = process_time()
    j = entity.count(1)
    print(entity.__class__.__name__, process_time() - start)

print('Inverting')
start = process_time()
a = ~a
print('BitArray', process_time() - start)
start = process_time()
for i in range(LEN):
    b[i] = 1 - b[i]
print('list', process_time() - start)

print('Creating random array')
start = process_time()
b_cipher = BitArray.random(LEN)
print('BitArray', process_time() - start)
start = process_time()
cipher = [random.randint(0, 1) for i in range(LEN)]
print('list', process_time() - start)

print('Binary XOR')
start = process_time()
a = a ^ b_cipher
print('BitArray', process_time() - start)
start = process_time()
for i in range(len(b)):
    b[i] = b[i] ^ cipher[i]
print('list', process_time() - start)
