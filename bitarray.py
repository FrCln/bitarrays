from __future__ import annotations

from secrets import token_bytes
import sys


class BitArray:
    def __init__(self, init_value=0, length=None):

        if isinstance(init_value, int):
            self._int = init_value
            self.length = length or init_value.bit_length()

        elif isinstance(init_value, str):
            try:
                self._int = int(init_value[::-1], 2)
            except ValueError as ex:
                raise ValueError("str for BitArray must contain only '0' and '1'")
            self.length = length or len(init_value)

        elif isinstance(init_value, (bytes, bytearray)):
            self.from_bytes(init_value, length)

        elif isinstance(init_value, BitArray):
            self._int = init_value._int
            self.length = init_value.length

        elif hasattr(init_value, '__iter__'):
            self._int = 0
            for i, a in enumerate(init_value):
                if a:
                    self._int |= 1 << i
            self.length = length or len(init_value)

        else:
            raise TypeError(
                f'init_value for BitArray must be iterable or int or string '
                'in binary format, not {init_value.__class__.__name__}'
            )

        if self.length < self._int.bit_length():
            self._int &= (1 << self.length) - 1

    def __len__(self):
        return self.length

    def __repr__(self):
        if self.length == 0:
            return 'BitArray()'
        elif self.length <= 70:
            bin_value = f'{self._int:0{self.length}b}'[::-1]
            return f"BitArray('{bin_value}')"
        elif self.length <= 56 * 4:
            hex_value = f'{self._int:0{(self.length + 3) // 4}x}'[::-1]
            return f"BitArray(0x{hex_value}, length={self.length})"
        else:
            first_bytes = f'{self._int & (1 << 16) - 1:016b}'[::-1]
            last_bytes = f'{(self._int >> (self.length - 16)):016b}'[::-1]
            return (f"BitArray('{first_bytes} <...> "
                    f"{last_bytes}', length={self.length})")

    def __add__(self, other):
        if not isinstance(other, BitArray):
            raise TypeError(
                f'unsupported operation + between BitArray and {other.__class__.__name__}'
            )
        return BitArray(
            self._int + (other._int << self.length), self.length + other.length
        )

    def __and__(self, other):
        if isinstance(other, BitArray):
            return BitArray(
                self._int & other._int,
                min(self.length, other.length)
            )
        elif isinstance(other, int):
            return BitArray(
                self._int & other,
                self.length
            )
        else:
            raise TypeError(
                f'unsupported operation & between BitArray and {other.__class__.__name__}'
            )

    def __bool__(self):
        return bool(self._int)

    def __eq__(self, other):
        if isinstance(other, BitArray):
            return self.length == other.length and self._int == other._int
        else:
            return False

    def __int__(self):
        return self._int

    def __invert__(self):
        invert_value = ~self._int & (1 << self.length) - 1
        return BitArray(invert_value, self.length)

    def __iter__(self):
        self._index = 0
        self._val = self._int << 1
        return self

    def __next__(self):
        if self._index >= self.length:
            raise StopIteration
        self._index += 1
        self._val >>= 1
        return self._val & 1

    def __or__(self, other):
        if isinstance(other, BitArray):
            return BitArray(
                self._int | other._int,
                max(self.length, other.length)
            )
        elif isinstance(other, int):
            return BitArray(
                self._int | other,
                self.length
            )
        else:
            raise TypeError(
                f'unsupported operation | between BitArray and {other.__class__.__name__}'
            )

    def __xor__(self, other):
        if isinstance(other, BitArray):
            return BitArray(
                self._int ^ other._int,
                max(self.length, other.length)
            )
        elif isinstance(other, int):
            return BitArray(
                self._int ^ other,
                self.length
            )
        else:
            raise TypeError(
                f'unsupported operation ^ between BitArray and {other.__class__.__name__}'
            )

    def __getitem__(self, index):
        if isinstance(index, int):
            if index < 0:
                index += self.length
            return self._int >> index & 1
        elif isinstance(index, slice):
            start, stop, step = self._slice_check(index)
            if step == 1:
                return BitArray(
                    self._int >> start & ((1 << (stop - start)) - 1),
                    length=(stop - start)
                )
            else:
                res = 0
                if step > 0:
                    for i in range(start, stop, step):
                        res |= (self._int >> i & 1) << (i - start) // step
                else:
                    for i in reversed(range(start, stop, -step)):
                        res |= (self._int >> i & 1) << (stop - i - 1) // -step
                return BitArray(res, abs((stop - start) // step))
        else:
            raise TypeError(
                f'BitArray indices must be integers or slices, not {index.__class__.__name__}'
            )

    def __setitem__(self, index, item):
        if isinstance(index, int):
            if item:
                self._int |= 1 << index
            else:
                self._int -= (self._int >> index & 1) << index
        elif isinstance(index, slice):
            start, stop, step = self._slice_check(index)
            if step == 1:
                result = self[:start] + BitArray(item) + self[stop:]
                self._int = result._int
                self.length = result.length
            else:
                raise UserWarning('only slices with step 1 implemented')
        else:
            raise TypeError(
                f'BitArray indices must be integers or slices, not {index.__class__.__name__}'
            )

    def _slice_check(self, sl):
        start = sl.start or 0
        stop = sl.stop or self.length
        step = sl.step or 1
        if not (isinstance(start, int) and isinstance(stop, int) and isinstance(step, int)):
            raise TypeError('slice indices must be integers or None')
        if step == 0:
            raise ValueError('slice step cannot be zero')
        if start < 0:
            start += self.length
        if stop < 0:
            stop += self.length
        return start, stop, step

    def __sizeof__(self):
        size = 56 + sys.getsizeof(self.__dict__)
        for k, v in self.__dict__.items():
            size += sys.getsizeof(k) + sys.getsizeof(v)
        return size

    def append(self, item):
        self._int |= bool(item) << self.length
        self.length += 1

    def to_bytes(self, byteorder=sys.byteorder):
        return self._int.to_bytes((self.length + 7) // 8, byteorder)

    @classmethod
    def from_bytes(cls, byteobject, length=None, byteorder=sys.byteorder):
        if not isinstance(byteobject, (bytes, bytearray)):
            raise TypeError(
                f'bytes or bytearray object required for method from_bytes, '
                f'not {byteobject.__class__.__name__}'
            )
        _int = int.from_bytes(byteobject, byteorder)
        length = length or len(byteobject) * 8
        return cls(_int, length)

    def to_file(self, file, byteorder=sys.byteorder):
        file.write(self.to_bytes(byteorder))

    @classmethod
    def from_file(cls, file, length=None, byteorder=sys.byteorder):
        return cls.from_bytes(file.read(), length, byteorder)

    def set_all(self, value=True):
        if value:
            self._int = (1 << self.length) - 1
        else:
            self._int = 0

    @classmethod
    def encode(cls, code_dict, string):
        cls._check_dict(code_dict, string)
        temp_str = ''
        for c in string:
            temp_str += code_dict[c]
        return cls(temp_str)

    def decode(self, code_dict):
        self._check_dict(code_dict)
        rev_dict = {v: k for k, v in sorted(code_dict.items(), key=lambda x: x[1])}
        max_code_len = max(map(len, rev_dict.keys()))
        temp_str = f'{self._int:0{self.length}b}'[::-1]
        i = 1
        res = ''
        while i <= len(temp_str):
            if temp_str[:i] in rev_dict:
                res += rev_dict[temp_str[:i]]
                temp_str = temp_str[i:]
                i = 1
            else:
                i += 1
                if i > max_code_len:
                    raise ValueError(f"cannot resolve code '{temp_str[:i]}'")
        if len(temp_str) > 0:
            raise ValueError(f"cannot resolve code '{temp_str}'")
        return res

    @staticmethod
    def _check_dict(code_dict, string=''):
        for sym, code in code_dict.items():
            if not isinstance(sym, str):
                raise ValueError(f'keys for code_dict must be str not {sym.__class__.__name__}')
            if not isinstance(code, str):
                raise ValueError(f'codes must be str not {code.__class__.__name__}')
            if len(code) == 0:
                raise ValueError(f'empty code for symbol {sym}')
            try:
                int(code, 2)
            except ValueError:
                raise ValueError(f'non-binary code {code}')
        for c in string:
            if c not in code_dict:
                raise ValueError(f'no code for symbol {c} in code_dict')
        codes = sorted(code_dict.items(), key=lambda x: x[1])
        for i in range(1, len(codes)):
            if codes[i][1].startswith(codes[i - 1][1]):
                raise ValueError(
                    f'code {codes[i][1]} for symbol {codes[i][0]} '
                    f'starts with code {codes[i - 1][1]} for symbol {codes[i - 1][0]}'
                )

    @classmethod
    def random(cls, length):
        val = int.from_bytes(token_bytes((length + 7) // 8), sys.byteorder)
        return cls(val, length)

    def count(self, value=1):
        res = 0
        val = self._int
        test = 0 if value else 1
        for i in range(self.length):
            res += val & 1 ^ test
            val >>= 1
        return res

    @staticmethod
    def encrypt(msg: str):
        bin_msg = BitArray.from_bytes(msg.encode('utf-8'))
        token = BitArray.random(len(bin_msg))
        secret_msg = bin_msg ^ token
        return secret_msg, token

    def decrypt(self, key: BitArray):
        temp = self ^ key
        msg_bytes = temp.to_bytes()
        return msg_bytes.decode('utf-8')

    def to_list(self):
        return list(map(int, self.binstr))

    @property
    def binstr(self):
        res = bin(self._int)[:1:-1]
        res += '0' * (len(self) - len(res))
        return res

