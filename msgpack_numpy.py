#!/usr/bin/env python

"""
Support for serialization of numpy data types with msgpack.

Security note
-------------
``object``-dtype ndarrays are serialized via the ``pickle`` protocol.  Because
``pickle.loads`` can execute arbitrary code as a side effect of unpickling,
this module refuses to unpickle ``kind=b'O'`` payloads by default (CWE-502).

To deserialize ``object``-dtype arrays, pass ``allow_pickle='restricted'`` for
a restricted unpickler that only permits NumPy reconstruction primitives and
common Python builtins, or ``allow_pickle=True`` for the legacy unrestricted
``pickle.loads`` path.  ``allow_pickle=True`` should only ever be used with
data from fully trusted sources.
"""

# Copyright (c) 2013-2022, Lev E. Givon
# All rights reserved.
# Distributed under the terms of the BSD license:
# http://www.opensource.org/licenses/bsd-license

import sys
import functools
import io
import pickle
import warnings

import msgpack
from msgpack import Packer as _Packer, Unpacker as _Unpacker, \
    unpack as _unpack, unpackb as _unpackb
import numpy as np

if sys.version_info >= (3, 0):
    def ndarray_to_bytes(obj):
        if obj.dtype == 'O':
            return obj.dumps()
        else:
            if sys.platform == 'darwin':
                return obj.tobytes()
            else:
                return obj.data if obj.flags['C_CONTIGUOUS'] else obj.tobytes()

    num_to_bytes = lambda obj: obj.data

    def tostr(x):
        if isinstance(x, bytes):
            return x.decode()
        else:
            return str(x)
else:
    def ndarray_to_bytes(obj):
        if obj.dtype == 'O':
            return obj.dumps()
        else:
            if sys.platform == 'darwin':
                return obj.tobytes()
            else:
                return memoryview(obj.data) if obj.flags['C_CONTIGUOUS'] else obj.tobytes()

    num_to_bytes = lambda obj: memoryview(obj.data)

    def tostr(x):
        return x


# Restricted-unpickler allowlist.  Modules listed here are accepted in full;
# anything else triggers UnpicklingError.  numpy's own ndarray reduce protocol
# references multiarray._reconstruct, dtype, and ndarray under both the legacy
# ``numpy.core`` path and the post-2.0 ``numpy._core`` path.
_ALLOWED_PICKLE_MODULES = frozenset({
    'numpy',
    'numpy.core',
    'numpy.core.multiarray',
    'numpy.core.numeric',
    'numpy._core',
    'numpy._core.multiarray',
    'numpy._core.numeric',
    'builtins',
    'collections',
    'copy_reg',          # Python 2 compat (no-op on Py3)
    '_codecs',           # bytes.decode reconstruction
})

# Builtins explicitly blocked even when ``builtins`` is allowed.  ``getattr``
# / ``eval`` / ``exec`` / ``__import__`` are pickle-RCE gadgets.
_BLOCKED_BUILTINS = frozenset({
    'eval', 'exec', 'compile', 'open', '__import__',
    'getattr', 'setattr', 'delattr', 'globals', 'locals', 'vars',
    'breakpoint', 'help', 'input', 'print',
    'classmethod', 'staticmethod', 'property',
})


class _RestrictedUnpickler(pickle.Unpickler):
    """Pickle unpickler restricted to a small allowlist of safe modules.

    Sufficient for round-tripping numpy ``object``-dtype ndarrays whose
    elements are themselves builtin primitives (str, bytes, int, float, bool,
    list, tuple, dict, set, complex, None).  Arbitrary user classes will
    raise ``pickle.UnpicklingError``.
    """

    def find_class(self, module, name):
        if module not in _ALLOWED_PICKLE_MODULES:
            raise pickle.UnpicklingError(
                "msgpack_numpy: refusing to unpickle %s.%s "
                "(module not on restricted allowlist). "
                "Pass allow_pickle=True if the data source is fully trusted."
                % (module, name))
        if module == 'builtins' and name in _BLOCKED_BUILTINS:
            raise pickle.UnpicklingError(
                "msgpack_numpy: refusing to unpickle builtins.%s "
                "(blocked as a pickle-RCE gadget)." % name)
        return super().find_class(module, name)


def _loads_restricted(data):
    return _RestrictedUnpickler(io.BytesIO(data)).load()


def _resolve_pickle_loader(allow_pickle):
    """Return the callable used to deserialize ``kind=b'O'`` payloads, or
    ``None`` if pickle is disabled.  Raises ``ValueError`` on bad input.
    """
    if allow_pickle is False or allow_pickle is None:
        return None
    if allow_pickle is True:
        return pickle.loads
    if allow_pickle == 'restricted':
        return _loads_restricted
    raise ValueError(
        "msgpack_numpy: allow_pickle must be False, True, or 'restricted'; "
        "got %r" % (allow_pickle,))


def encode(obj, chain=None):
    """
    Data encoder for serializing numpy data types.
    """

    if isinstance(obj, np.ndarray):
        # If the dtype is structured, store the interface description;
        # otherwise, store the corresponding array protocol type string:
        if obj.dtype.kind in ('V', 'O'):
            kind = bytes(obj.dtype.kind, 'ascii')
            descr = obj.dtype.descr
        else:
            kind = b''
            descr = obj.dtype.str

        return {b'nd': True,
                b'type': descr,
                b'kind': kind,
                b'shape': obj.shape,
                b'data': ndarray_to_bytes(obj)}
    elif isinstance(obj, (np.bool_, np.number)):
        return {b'nd': False,
                b'type': obj.dtype.str,
                b'data': num_to_bytes(obj)}
    elif isinstance(obj, complex):
        return {b'complex': True,
                b'data': obj.__repr__()}
    else:
        return obj if chain is None else chain(obj)

def decode(obj, chain=None, allow_pickle=False):
    """
    Decoder for deserializing numpy data types.

    Parameters
    ----------
    allow_pickle : bool or str, default False
        Controls deserialization of ``object``-dtype arrays, which are stored
        as a pickle stream.  ``False`` (the default) refuses pickle entirely
        and raises ``ValueError``.  ``'restricted'`` uses a restricted
        unpickler that allowlists NumPy reconstruction primitives and common
        Python builtins.  ``True`` calls ``pickle.loads`` directly and is
        equivalent to executing arbitrary code from the payload — only use
        with fully trusted sources.
    """

    try:
        if b'nd' in obj:
            if obj[b'nd'] is True:

                # Check if b'kind' is in obj to enable decoding of data
                # serialized with older versions (#20) or data
                # that had dtype == 'O' (#46):
                if b'kind' in obj and obj[b'kind'] == b'V':
                    descr = [tuple(tostr(t) if type(t) is bytes else t for t in d) \
                             for d in obj[b'type']]
                elif b'kind' in obj and obj[b'kind'] == b'O':
                    loader = _resolve_pickle_loader(allow_pickle)
                    if loader is None:
                        raise ValueError(
                            "msgpack_numpy: refusing to unpickle object-dtype "
                            "ndarray (kind=b'O') because allow_pickle=False. "
                            "Pass allow_pickle='restricted' for a restricted "
                            "unpickler, or allow_pickle=True for the legacy "
                            "pickle.loads behavior (only with trusted data).")
                    return loader(obj[b'data'])
                else:
                    descr = obj[b'type']
                return np.ndarray(buffer=obj[b'data'],
                                  dtype=_unpack_dtype(descr),
                                  shape=obj[b'shape'])
            else:
                descr = obj[b'type']
                return np.frombuffer(obj[b'data'],
                            dtype=_unpack_dtype(descr))[0]
        elif b'complex' in obj:
            return complex(tostr(obj[b'data']))
        else:
            return obj if chain is None else chain(obj)
    except KeyError:
        return obj if chain is None else chain(obj)

def _unpack_dtype(dtype):
    """
    Unpack dtype descr, recursively unpacking nested structured dtypes.
    """

    if isinstance(dtype, (list, tuple)):
        # Unpack structured dtypes of the form: (name, type, *shape)
        dtype = [
            (subdtype[0], _unpack_dtype(subdtype[1])) + tuple(subdtype[2:])
            for subdtype in dtype
        ]
    return np.dtype(dtype)

if msgpack.version < (1, 0, 0):
    warnings.warn('support for msgpack < 1.0.0 will be removed in a future release',
                   DeprecationWarning)

# Maintain support for msgpack < 0.4.0:
if msgpack.version < (0, 4, 0):
    class Packer(_Packer):
        def __init__(self, default=None,
                     encoding='utf-8',
                     unicode_errors='strict',
                     use_single_float=False,
                     autoreset=1):
            default = functools.partial(encode, chain=default)
            super(Packer, self).__init__(default=default,
                                         encoding=encoding,
                                         unicode_errors=unicode_errors,
                                         use_single_float=use_single_float,
                                         autoreset=autoreset)
    class Unpacker(_Unpacker):
        def __init__(self, file_like=None, read_size=0, use_list=None,
                     object_hook=None,
                     object_pairs_hook=None, list_hook=None, encoding='utf-8',
                     unicode_errors='strict', max_buffer_size=0,
                     allow_pickle=False):
            object_hook = functools.partial(decode, chain=object_hook,
                                            allow_pickle=allow_pickle)
            super(Unpacker, self).__init__(file_like=file_like,
                                           read_size=read_size,
                                           use_list=use_list,
                                           object_hook=object_hook,
                                           object_pairs_hook=object_pairs_hook,
                                           list_hook=list_hook,
                                           encoding=encoding,
                                           unicode_errors=unicode_errors,
                                           max_buffer_size=max_buffer_size)

elif msgpack.version < (1, 0, 0):
    class Packer(_Packer):
        def __init__(self, default=None,
                     unicode_errors='strict',
                     use_single_float=False,
                     autoreset=1,
                     use_bin_type=True,
                     strict_types=False):
            default = functools.partial(encode, chain=default)
            super(Packer, self).__init__(default=default,
                                         unicode_errors=unicode_errors,
                                         use_single_float=use_single_float,
                                         autoreset=autoreset,
                                         use_bin_type=use_bin_type,
                                         strict_types=strict_types)

    class Unpacker(_Unpacker):
        def __init__(self, file_like=None, read_size=0, use_list=None,
                     raw=False,
                     object_hook=None,
                     object_pairs_hook=None, list_hook=None,
                     unicode_errors='strict', max_buffer_size=0,
                     ext_hook=msgpack.ExtType,
                     allow_pickle=False):
            object_hook = functools.partial(decode, chain=object_hook,
                                            allow_pickle=allow_pickle)
            super(Unpacker, self).__init__(file_like=file_like,
                                           read_size=read_size,
                                           use_list=use_list,
                                           raw=raw,
                                           object_hook=object_hook,
                                           object_pairs_hook=object_pairs_hook,
                                           list_hook=list_hook,
                                           unicode_errors=unicode_errors,
                                           max_buffer_size=max_buffer_size,
                                           ext_hook=ext_hook)

else:
    class Packer(_Packer):
        def __init__(self,
                     default=None,
                     use_single_float=False,
                     autoreset=True,
                     use_bin_type=True,
                     strict_types=False,
                     datetime=False,
                     unicode_errors=None):
            default = functools.partial(encode, chain=default)
            super(Packer, self).__init__(default=default,
                                         use_single_float=use_single_float,
                                         autoreset=autoreset,
                                         use_bin_type=use_bin_type,
                                         strict_types=strict_types,
                                         datetime=datetime,
                                         unicode_errors=unicode_errors)

    class Unpacker(_Unpacker):
        def __init__(self,
                     file_like=None,
                     read_size=0,
                     use_list=True,
                     raw=False,
                     timestamp=0,
                     strict_map_key=True,
                     object_hook=None,
                     object_pairs_hook=None,
                     list_hook=None,
                     unicode_errors=None,
                     max_buffer_size=100 * 1024 * 1024,
                     ext_hook=msgpack.ExtType,
                     max_str_len=-1,
                     max_bin_len=-1,
                     max_array_len=-1,
                     max_map_len=-1,
                     max_ext_len=-1,
                     allow_pickle=False):
            object_hook = functools.partial(decode, chain=object_hook,
                                            allow_pickle=allow_pickle)
            super(Unpacker, self).__init__(file_like=file_like,
                                           read_size=read_size,
                                           use_list=use_list,
                                           raw=raw,
                                           timestamp=timestamp,
                                           strict_map_key=strict_map_key,
                                           object_hook=object_hook,
                                           object_pairs_hook=object_pairs_hook,
                                           list_hook=list_hook,
                                           unicode_errors=unicode_errors,
                                           max_buffer_size=max_buffer_size,
                                           ext_hook=ext_hook,
                                           max_str_len=max_str_len,
                                           max_bin_len=max_bin_len,
                                           max_array_len=max_array_len,
                                           max_map_len=max_map_len,
                                           max_ext_len=max_ext_len)

def pack(o, stream, **kwargs):
    """
    Pack an object and write it to a stream.
    """

    kwargs.pop('allow_pickle', None)  # packer never unpickles
    packer = Packer(**kwargs)
    stream.write(packer.pack(o))

def packb(o, **kwargs):
    """
    Pack an object and return the packed bytes.
    """

    kwargs.pop('allow_pickle', None)  # packer never unpickles
    return Packer(**kwargs).pack(o)

def unpack(stream, **kwargs):
    """
    Unpack a packed object from a stream.

    Pass ``allow_pickle`` (default ``False``) to control deserialization of
    ``object``-dtype ndarrays.  See :func:`decode` for accepted values.
    """

    allow_pickle = kwargs.pop('allow_pickle', False)
    object_hook = kwargs.get('object_hook')
    kwargs['object_hook'] = functools.partial(decode, chain=object_hook,
                                              allow_pickle=allow_pickle)
    return _unpack(stream, **kwargs)

def unpackb(packed, **kwargs):
    """
    Unpack a packed object.

    Pass ``allow_pickle`` (default ``False``) to control deserialization of
    ``object``-dtype ndarrays.  See :func:`decode` for accepted values.
    """

    allow_pickle = kwargs.pop('allow_pickle', False)
    object_hook = kwargs.get('object_hook')
    kwargs['object_hook'] = functools.partial(decode, chain=object_hook,
                                              allow_pickle=allow_pickle)
    return _unpackb(packed, **kwargs)

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
