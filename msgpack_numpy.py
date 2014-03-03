#!/usr/bin/env python

"""
Support for serialization of numpy data types with msgpack.
"""

import numpy as np
import msgpack
import msgpack._packer as _packer
import msgpack._unpacker as _unpacker

def encode(obj):
    """
    Data encoder for serializing numpy data types.
    """
    if isinstance(obj, np.ndarray):
        return {'nd': True,
                'type': obj.dtype.str,
                'shape': obj.shape,
                'data': obj.tostring()}
    elif isinstance(obj, np.number):
        if np.iscomplexobj(obj):
            return {'np': True,
                    'complex': True,
                    'type': obj.dtype.str,
                    'r': obj.real.__repr__(),
                    'i': obj.imag.__repr__()}
        else:
            return {'np': True,
                    'type': obj.dtype.str,
                    'data': obj.__repr__()}
    elif isinstance(obj, complex):
        return {'complex': True,
                'data': obj.__repr__()}
    else:
        return obj

c2f_dict = {np.dtype('complex128'): np.float64,
            np.dtype('complex64'): np.float32}
if hasattr(np, 'float128'):
    c2f_dict[np.dtype('complex256')] = np.float128

def c2f(r, i, ctype_name):
    """
    Convert strings to complex number instance with specified numpy type.
    """

    ftype = c2f_dict[ctype_name]
    return ctype_name.type(ftype(r)+1j*ftype(i))

def decode(obj):
    """
    Decoder for deserializing numpy data types.
    """

    try:
        if 'nd' in obj:
            return np.fromstring(obj['data'],
                                 dtype=np.dtype(obj['type'])).reshape(obj['shape'])
        elif 'np' in obj:
            if 'complex' in obj:
                return c2f(obj['r'], obj['i'], np.dtype(obj['type']))
            else:
                return np.dtype(obj['type']).type(obj['data'])
        elif 'complex' in obj:
            return complex(obj['data'])
        else:
            return obj
    except KeyError:
        return obj

# Maintain support for msgpack < 0.4.0:
if msgpack.version < (0, 4, 0):
    class Packer(_packer.Packer):
        def __init__(self, default=encode,
                     encoding='utf-8',
                     unicode_errors='strict',
                     use_single_float=False,
                     autoreset=1):
            super(Packer, self).__init__(default=default,
                                         encoding=encoding,
                                         unicode_errors=unicode_errors,
                                         use_single_float=use_single_float,
                                         autoreset=1)
    class Unpacker(_unpacker.Unpacker):
        def __init__(self, file_like=None, read_size=0, use_list=None,
                     object_hook=decode,
                     object_pairs_hook=None, list_hook=None, encoding=None,
                     unicode_errors='strict', max_buffer_size=0):
            super(Unpacker, self).__init__(file_like=file_like,
                                           read_size=read_size,
                                           use_list=use_list,
                                           object_hook=object_hook,
                                           object_pairs_hook=object_pairs_hook,
                                           list_hook=list_hook,
                                           encoding=encoding,
                                           unicode_errors=unicode_errors,
                                           max_buffer_size=max_buffer_size)

else:
    class Packer(_packer.Packer):
        def __init__(self, default=encode,
                     encoding='utf-8',
                     unicode_errors='strict',
                     use_single_float=False,
                     autoreset=1,
                     use_bin_type=0):
            super(Packer, self).__init__(default=default,
                                         encoding=encoding,
                                         unicode_errors=unicode_errors,
                                         use_single_float=use_single_float,
                                         autoreset=1,
                                         use_bin_type=0)

    class Unpacker(_unpacker.Unpacker):
        def __init__(self, file_like=None, read_size=0, use_list=None,
                     object_hook=decode,
                     object_pairs_hook=None, list_hook=None, encoding=None,
                     unicode_errors='strict', max_buffer_size=0,
                     ext_hook=msgpack.ExtType):
            super(Unpacker, self).__init__(file_like=file_like,
                                           read_size=read_size,
                                           use_list=use_list,
                                           object_hook=object_hook,
                                           object_pairs_hook=object_pairs_hook,
                                           list_hook=list_hook,
                                           encoding=encoding,
                                           unicode_errors=unicode_errors,
                                           max_buffer_size=max_buffer_size,
                                           ext_hook=ext_hook)

def pack(o, stream, default=encode, **kwargs):
    """
    Pack an object and write it to a stream.
    """

    kwargs['default'] = default
    packer = Packer(**kwargs)
    stream.write(packer.pack(o))

def packb(o, default=encode, **kwargs):
    """
    Pack an object and return the packed bytes.
    """

    kwargs['default'] = default
    return Packer(**kwargs).pack(o)

def unpack(stream, object_hook=decode, **kwargs):
    """
    Unpack a packed object from a stream.
    """

    kwargs['object_hook'] = object_hook
    return _unpacker.unpack(stream, **kwargs)

def unpackb(packed, object_hook=decode, **kwargs):
    """
    Unpack a packed object.
    """

    kwargs['object_hook'] = object_hook
    return _unpacker.unpackb(packed, **kwargs)

load = unpack
loads = unpackb
dump = pack
dumps = packb

def patch():
    """
    Monkey patch msgpack module to enable support for serializing numpy types.
    """

    setattr(msgpack, 'Packer', Packer)
    setattr(msgpack, 'Unpacker', Unpacker)
    setattr(msgpack, 'load', unpack)
    setattr(msgpack, 'loads', unpackb)
    setattr(msgpack, 'dump', pack)
    setattr(msgpack, 'dumps', packb)
    setattr(msgpack, 'pack', pack)
    setattr(msgpack, 'packb', packb)
    setattr(msgpack, 'unpack', unpack)
    setattr(msgpack, 'unpackb', unpackb)

if __name__ == '__main__':
    from unittest import main, TestCase, TestSuite

    class test_numpy_msgpack(TestCase):
        def setUp(self):
             patch()
        def encode_decode(self, x):
            x_enc = msgpack.packb(x)
            return msgpack.unpackb(x_enc)
        def test_numpy_scalar_float(self):
            x = np.float32(np.random.rand())
            x_rec = self.encode_decode(x)
            assert x == x_rec and type(x) == type(x_rec)
        def test_numpy_scalar_complex(self):
            x = np.complex64(np.random.rand()+1j*np.random.rand())
            x_rec = self.encode_decode(x)
            assert x == x_rec and type(x) == type(x_rec)
        def test_scalar_float(self):
            x = np.random.rand()
            x_rec = self.encode_decode(x)
            assert x == x_rec and type(x) == type(x_rec)
        def test_scalar_complex(self):
            x = np.random.rand()+1j*np.random.rand()
            x_rec = self.encode_decode(x)
            assert x == x_rec and type(x) == type(x_rec)
        def test_list_numpy_float(self):
            x = [np.float32(np.random.rand()) for i in xrange(5)]
            x_rec = self.encode_decode(x)
            assert all(map(lambda x, y: x == y, x, x_rec)) and all(map(lambda x,y: type(x) == type(y), x, x_rec))
        def test_list_numpy_float_complex(self):
            x = [np.float32(np.random.rand()) for i in xrange(5)] + \
              [np.complex128(np.random.rand()+1j*np.random.rand()) for i in xrange(5)]
            x_rec = self.encode_decode(x)
            assert all(map(lambda x,y: x == y, x, x_rec)) and all(map(lambda x,y: type(x) == type(y), x, x_rec))
        def test_list_float(self):
            x = [np.random.rand() for i in xrange(5)]
            x_rec = self.encode_decode(x)
            assert all(map(lambda x,y: x == y, x, x_rec)) and all(map(lambda x,y: type(x) == type(y), x, x_rec))
        def test_list_float_complex(self):
            x = [(np.random.rand()+1j*np.random.rand()) for i in xrange(5)]
            x_rec = self.encode_decode(x)
            assert all(map(lambda x, y: x == y, x, x_rec)) and all(map(lambda x,y: type(x) == type(y), x, x_rec))
        def test_list_str(self):
            x = ['x'*i for i in xrange(5)]
            x_rec = self.encode_decode(x)
            assert all(map(lambda x,y: x == y, x, x_rec)) and all(map(lambda x,y: type(x) == type(y), x, x_rec))
        def test_dict_float(self):
            x = {'foo': 1.0, 'bar': 2.0}
            x_rec = self.encode_decode(x)
            assert all(map(lambda x,y: x == y, x.values(), x_rec.values())) and \
                           all(map(lambda x,y: type(x) == type(y), x.values(), x_rec.values()))
        def test_dict_complex(self):
            x = {'foo': 1.0+1.0j, 'bar': 2.0+2.0j}
            x_rec = self.encode_decode(x)
            assert all(map(lambda x,y: x == y, x.values(), x_rec.values())) and \
                           all(map(lambda x,y: type(x) == type(y), x.values(), x_rec.values()))
        def test_dict_str(self):
            x = {'foo': 'xxx', 'bar': 'yyyy'}
            x_rec = self.encode_decode(x)
            assert all(map(lambda x,y: x == y, x.values(), x_rec.values())) and \
                           all(map(lambda x,y: type(x) == type(y), x.values(), x_rec.values()))
        def test_dict_numpy_float(self):
            x = {'foo': np.float32(1.0), 'bar': np.float32(2.0)}
            x_rec = self.encode_decode(x)
            assert all(map(lambda x,y: x == y, x.values(), x_rec.values())) and \
                           all(map(lambda x,y: type(x) == type(y), x.values(), x_rec.values()))
        def test_dict_numpy_complex(self):
            x = {'foo': np.complex128(1.0+1.0j), 'bar': np.complex128(2.0+2.0j)}
            x_rec = self.encode_decode(x)
            assert all(map(lambda x,y: x == y, x.values(), x_rec.values())) and \
                           all(map(lambda x,y: type(x) == type(y), x.values(), x_rec.values()))
        def test_numpy_array_float(self):
            x = np.random.rand(5).astype(np.float32)
            x_rec = self.encode_decode(x)
            assert np.all(x == x_rec) and x.dtype == x_rec.dtype
        def test_numpy_array_complex(self):
            x = (np.random.rand(5)+1j*np.random.rand(5)).astype(np.complex128)
            x_rec = self.encode_decode(x)
            assert np.all(x == x_rec) and x.dtype == x_rec.dtype
        def test_numpy_array_float_2d(self):
            x = np.random.rand(5,5).astype(np.float32)
            x_rec = self.encode_decode(x)
            assert np.all(x == x_rec) and x.dtype == x_rec.dtype
        def test_numpy_array_str(self):
            x = np.array(['aaa', 'bbbb', 'ccccc'])
            x_rec = self.encode_decode(x)
            assert np.all(x == x_rec) and x.dtype == x_rec.dtype
        def test_list_mixed(self):
            x = [1.0, np.float32(3.5), np.complex128(4.25), 'foo']
            x_rec = self.encode_decode(x)
            assert all(map(lambda x,y: x == y, x, x_rec)) and all(map(lambda x,y: type(x) == type(y), x, x_rec))

    main()

