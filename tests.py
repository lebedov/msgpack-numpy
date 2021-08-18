#!/usr/bin/env python

import gc
import sys
from unittest import main, TestCase

import msgpack
import numpy as np
from numpy.testing import assert_equal, assert_array_equal

from msgpack_numpy import patch

try:
    range = xrange # Python 2
except NameError:
    pass # Python 3

class ThirdParty(object):

    def __init__(self, foo=b'bar'):
        self.foo = foo

    def __eq__(self, other):
        return isinstance(other, ThirdParty) and self.foo == other.foo

class test_numpy_msgpack(TestCase):
    def setUp(self):
         patch()

    def encode_decode(self, x, use_list=True, max_bin_len=-1):
        x_enc = msgpack.packb(x)
        return msgpack.unpackb(x_enc, use_list=use_list,
                               max_bin_len=max_bin_len)

    def encode_thirdparty(self, obj):
        return {b'__thirdparty__': True, b'foo': obj.foo}

    def decode_thirdparty(self, obj):
        if b'__thirdparty__' in obj:
            return ThirdParty(foo=obj[b'foo'])
        return obj

    def encode_decode_thirdparty(self, x,
            use_list=True, max_bin_len=-1):
        x_enc = msgpack.packb(x, default=self.encode_thirdparty)
        return msgpack.unpackb(x_enc,
                               object_hook=self.decode_thirdparty,
                               use_list=use_list, max_bin_len=max_bin_len)

    def test_bin(self):
        # str == bytes on Python 2:
        if sys.version_info.major == 2:
            assert_equal(type(self.encode_decode(b'foo')), str)
        else:
            assert_equal(type(self.encode_decode(b'foo')), bytes)

    def test_str(self):
        # str != unicode on Python 2:
        if sys.version_info.major == 2:
            assert_equal(type(self.encode_decode('foo')), str)
            assert_equal(type(self.encode_decode(u'foo')), unicode)
        else:
            assert_equal(type(self.encode_decode(u'foo')), str)

    def test_numpy_scalar_bool(self):
        x = np.bool_(True)
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))
        x = np.bool_(False)
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))

    def test_numpy_scalar_float(self):
        x = np.float32(np.random.rand())
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))

    def test_numpy_scalar_complex(self):
        x = np.complex64(np.random.rand()+1j*np.random.rand())
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))

    def test_scalar_float(self):
        x = np.random.rand()
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))

    def test_scalar_complex(self):
        x = np.random.rand()+1j*np.random.rand()
        x_rec = self.encode_decode(x)
        assert_equal(x, x_rec)
        assert_equal(type(x), type(x_rec))

    def test_list_numpy_float(self):
        x = [np.float32(np.random.rand()) for i in range(5)]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x],
                           [type(e) for e in x_rec])

    def test_list_numpy_float_complex(self):
        x = [np.float32(np.random.rand()) for i in range(5)] + \
          [np.complex128(np.random.rand()+1j*np.random.rand()) for i in range(5)]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x],
                           [type(e) for e in x_rec])

    def test_list_float(self):
        x = [np.random.rand() for i in range(5)]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x],
                           [type(e) for e in x_rec])

    def test_list_float_complex(self):
        x = [(np.random.rand()+1j*np.random.rand()) for i in range(5)]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x],
                           [type(e) for e in x_rec])

    def test_list_str(self):
        x = [b'x'*i for i in range(5)]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x_rec], [bytes]*5)

    def test_dict_float(self):
        x = {b'foo': 1.0, b'bar': 2.0}
        x_rec = self.encode_decode(x)
        assert_array_equal(sorted(x.values()), sorted(x_rec.values()))
        assert_array_equal([type(e) for e in sorted(x.values())],
                           [type(e) for e in sorted(x_rec.values())])
        assert_array_equal(sorted(x.keys()), sorted(x_rec.keys()))
        assert_array_equal([type(e) for e in sorted(x.keys())],
                           [type(e) for e in sorted(x_rec.keys())])

    def test_dict_complex(self):
        x = {b'foo': 1.0+1.0j, b'bar': 2.0+2.0j}
        x_rec = self.encode_decode(x)
        assert_array_equal(sorted(x.values(), key=np.linalg.norm),
                           sorted(x_rec.values(), key=np.linalg.norm))
        assert_array_equal([type(e) for e in sorted(x.values(), key=np.linalg.norm)],
                           [type(e) for e in sorted(x_rec.values(), key=np.linalg.norm)])
        assert_array_equal(sorted(x.keys()), sorted(x_rec.keys()))
        assert_array_equal([type(e) for e in sorted(x.keys())],
                           [type(e) for e in sorted(x_rec.keys())])

    def test_dict_str(self):
        x = {b'foo': b'xxx', b'bar': b'yyyy'}
        x_rec = self.encode_decode(x)
        assert_array_equal(sorted(x.values()), sorted(x_rec.values()))
        assert_array_equal([type(e) for e in sorted(x.values())],
                           [type(e) for e in sorted(x_rec.values())])
        assert_array_equal(sorted(x.keys()), sorted(x_rec.keys()))
        assert_array_equal([type(e) for e in sorted(x.keys())],
                           [type(e) for e in sorted(x_rec.keys())])

    def test_dict_numpy_float(self):
        x = {b'foo': np.float32(1.0), b'bar': np.float32(2.0)}
        x_rec = self.encode_decode(x)
        assert_array_equal(sorted(x.values()), sorted(x_rec.values()))
        assert_array_equal([type(e) for e in sorted(x.values())],
                           [type(e) for e in sorted(x_rec.values())])
        assert_array_equal(sorted(x.keys()), sorted(x_rec.keys()))
        assert_array_equal([type(e) for e in sorted(x.keys())],
                           [type(e) for e in sorted(x_rec.keys())])

    def test_dict_numpy_complex(self):
        x = {b'foo': np.complex128(1.0+1.0j), b'bar': np.complex128(2.0+2.0j)}
        x_rec = self.encode_decode(x)
        assert_array_equal(sorted(x.values(), key=np.linalg.norm),
                           sorted(x_rec.values(), key=np.linalg.norm))
        assert_array_equal([type(e) for e in sorted(x.values(), key=np.linalg.norm)],
                           [type(e) for e in sorted(x_rec.values(), key=np.linalg.norm)])
        assert_array_equal(sorted(x.keys()), sorted(x_rec.keys()))
        assert_array_equal([type(e) for e in sorted(x.keys())],
                           [type(e) for e in sorted(x_rec.keys())])

    def test_numpy_array_float(self):
        x = np.random.rand(5).astype(np.float32)
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_numpy_array_complex(self):
        x = (np.random.rand(5)+1j*np.random.rand(5)).astype(np.complex128)
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_numpy_array_float_2d(self):
        x = np.random.rand(5,5).astype(np.float32)
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_numpy_array_float_2d_macos(self):
        """
        Unit test for weird data loss error on MacOS (#35).
        """
        x = np.random.rand(5, 5).astype(np.float32)
        x_rec = self.encode_decode(x, use_list=False, max_bin_len=50000000)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_numpy_array_str(self):
        x = np.array([b'aaa', b'bbbb', b'ccccc'])
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_numpy_array_mixed(self):
        x = np.array([(1, 2, b'a', [1.0, 2.0])],
                     np.dtype([('arg0', np.uint32),
                               ('arg1', np.uint32),
                               ('arg2', 'S1'),
                               ('arg3', np.float32, (2,))]))
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_numpy_array_noncontiguous(self):
        x = np.ones((10, 10), np.uint32)[0:5, 0:5]
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_equal(x.dtype, x_rec.dtype)

    def test_list_mixed(self):
        x = [1.0, np.float32(3.5), np.complex128(4.25), b'foo']
        x_rec = self.encode_decode(x)
        assert_array_equal(x, x_rec)
        assert_array_equal([type(e) for e in x],
                           [type(e) for e in x_rec])

    def test_chain(self):
        x = ThirdParty(foo=b'test marshal/unmarshal')
        x_rec = self.encode_decode_thirdparty(x)
        self.assertEqual(x, x_rec)

    def test_numpy_structured_array(self):
        structured_dtype = np.dtype([("a", float), ("b", int)])

        x = np.empty((10,), dtype=structured_dtype)
        x["a"] = np.arange(10)
        x["b"] = np.arange(10)

        x_rec = self.encode_decode(x)

        assert_array_equal(x, x_rec)
        self.assertEqual(x.dtype, x_rec.dtype)

    def test_numpy_shaped_structured_array(self):
        shaped_structured_dtype = np.dtype([("a", float, 3), ("b", int)])

        x = np.empty((10,), dtype=shaped_structured_dtype)
        x["a"] = np.arange(30).reshape(10, 3)
        x["b"] = np.arange(10)

        x_rec = self.encode_decode(x)

        assert_array_equal(x, x_rec)
        self.assertEqual(x.dtype, x_rec.dtype)

    def test_numpy_nested_structured_array(self):
        structured_dtype = np.dtype([("a", float), ("b", int)])
        nested_dtype = np.dtype([("foo", structured_dtype), ("bar", structured_dtype)])

        x = np.empty((10,), dtype=nested_dtype)
        x["foo"]["a"] = np.arange(10)
        x["foo"]["b"] = np.arange(10)
        x["bar"]["a"] = np.arange(10) + 10
        x["bar"]["b"] = np.arange(10) + 10

        x_rec = self.encode_decode(x)

        assert_array_equal(x, x_rec)
        self.assertEqual(x.dtype, x_rec.dtype)

    def test_numpy_object_str_array(self):
        dtype = "O"

        x = np.array(["a", "ab", "a"*5000], dtype=dtype)

        # encode
        x_enc = msgpack.packb(x)

        # call the garbage collector to free the memory of objects in array
        del x
        gc.collect()

        # decode
        x_rec = msgpack.unpackb(x_enc, use_list=True, max_bin_len=-1)

        # check
        a, ab, a5000 = x_rec
        self.assertEqual(a == "a")
        self.assertEqual(b == "ab")
        self.assertEqual(a5000 == "a"*5000)
        self.assertEqual(dtype, x_rec.dtype)

if __name__ == '__main__':
    main()
