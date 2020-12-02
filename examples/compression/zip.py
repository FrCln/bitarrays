from collections import Counter
from math import ceil, log2
import pickle
import sys
sys.path.append('../../')

from bitarray import BitArray


def make_huffman_tree(text):
    letters = [(count, letter) for letter, count in Counter(text).items()]

    while len(letters) > 1:
        letters.sort(key=lambda it: it[0])
        f1, l1 = letters.pop(0)
        f2, l2 = letters.pop(0)
        letters.append((f1 + f2, (l1, l2)))

    return letters[0][1]


def make_huffman_code(tree_element):
    if len(tree_element) == 1:
        return {tree_element: ''}
    else:
        code = {}
        for letter, c in make_huffman_code(tree_element[0]).items():
            code[letter] = '0' + c
        for letter, c in make_huffman_code(tree_element[1]).items():
            code[letter] = '1' + c
    return code


test_string = open('test.txt').read()
tree = make_huffman_tree(test_string)
code = make_huffman_code(tree)

pickled_code = BitArray.from_bytes(pickle.dumps(code))
data = BitArray(len(pickled_code), 32) + pickled_code + BitArray.encode(code, test_string)
data.to_file('test.bin')
