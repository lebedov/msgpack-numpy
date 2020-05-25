<!---
-*- mode:markdown -*-
vi:ft=markdown
-->
Numpy Data Type Serialization Using Msgpack
===========================================

Package Description
-------------------
This package provides encoding and decoding routines that enable the
serialization and deserialization of numerical and array data types provided by 
[numpy](http://www.numpy.org/) using the highly efficient
[msgpack](http://msgpack.org/) format. Serialization of Python's
native complex data types is also supported.

[![Latest Version](https://img.shields.io/pypi/v/msgpack-numpy.svg)](https://pypi.python.org/pypi/msgpack-numpy)
[![Build Status](https://travis-ci.org/lebedov/msgpack-numpy.svg?branch=master)](https://travis-ci.org/lebedov/msgpack-numpy)

Installation
------------
msgpack-numpy requires msgpack-python and numpy. If you 
have [pip](http://www.pip-installer.org/) installed on your
system, run

    pip install msgpack-numpy

to install the package and all dependencies. You can also download 
the source tarball, unpack it, and run

    python setup.py install

from within the source directory.

Usage
-----
The easiest way to use msgpack-numpy is to call its monkey patching
function after importing the Python msgpack package:

    import msgpack
    import msgpack_numpy as m
    m.patch()

This will automatically force all msgpack serialization and deserialization
routines (and other packages that use them) to become numpy-aware. 
Of course, one can also manually pass the encoder and 
decoder provided by msgpack-numpy to the msgpack routines:

    import msgpack
    import msgpack_numpy as m
    import numpy as np

    x = np.random.rand(5)
    x_enc = msgpack.packb(x, default=m.encode)
    x_rec = msgpack.unpackb(x_enc, object_hook=m.decode)

msgpack-numpy will try to use the binary (fast) extension in msgpack by default.  
If msgpack was not compiled with Cython (or if the ``MSGPACK_PUREPYTHON`` 
variable is set), it will fall back to using the slower pure Python msgpack 
implementation.

Notes
-----
The primary design goal of msgpack-numpy is ensuring preservation of numerical
data types during msgpack serialization and deserialization. Inclusion of type
information in the serialized data necessarily incurs some storage overhead; if
preservation of type information is not needed, one may be able to avoid some
of this overhead by writing a custom encoder/decoder pair that produces more
efficient serializations for those specific use cases.

Development
-----------
The latest source code can be obtained from [GitHub](https://github.com/lebedov/msgpack-numpy/).

Authors
-------
See the included [AUTHORS.md](https://github.com/lebedov/msgpack-numpy/blob/master/AUTHORS.md) file for 
more information.

License
-------
This software is licensed under the [BSD License](http://www.opensource.org/licenses/bsd-license).
See the included [LICENSE.md](https://github.com/lebedov/msgpack-numpy/blob/master/LICENSE.md) file for 
more information.
