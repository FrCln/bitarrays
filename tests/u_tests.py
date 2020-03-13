import unittest
import sys
sys.path.append('../')

from bitarray import BitArray


class TestBitArray(unittest.TestCase):
    def setUp(self):
        self.ba = BitArray('011011101111000')

    def test_init(self):
        test_values = [
            (('111',), (7,)),
            (('111', 15), (7, 15)),
            (('1110',), (7, 4)),
            (('0111',), (14,)),
            (('0',), (0, 1)),
            (('000',), (0, 3)),
            (([],), (0,)),
            (([0],), (0, 1)),
            (([False],), (0, 1)),
            (([''],), (0, 1)),
            (([True],), (1,)),
            (([1],), (1,)),
            (([1], 8), (1, 8)),
            (([False, False],), (0, 2)),
            (([True, True],), (3,)),
            (([False, True],), (2,)),
            (([True, False],), (1, 2)),
            (([False] * 10,), (0, 10)),
            (([False] * 10, 5), (0, 5)),
            (([True] * 10,), ((1 << 10) - 1,)),
            ((b'0',), (ord('0'), 8)),
            ((b'01',), (ord('1') * 256 + ord('0'), 16)),
            ((b'01', 10), (ord('1') * 256 + ord('0'), 10)),
        ]
        for values, params in test_values:
            with self.subTest():
                self.assertEqual(BitArray(*values), BitArray(*params), str(values))

        with self.subTest():
            self.assertEqual(BitArray(self.ba), self.ba)

        with self.assertRaises(ValueError):
            BitArray('012')

        with self.assertRaises(TypeError):
            BitArray(self)

    @unittest.skip("not now")
    def test_read_from_file(self):
        a = BitArray.from_file('test_file.bin')
        self.assertEqual(a, BitArray(ord('0'), 8))

    # @unittest.expectedFailure
    # def test_fail(self):
    #     self.assertEqual(1, 0, "broken")


if __name__ == "__main__":
    unittest.main()
