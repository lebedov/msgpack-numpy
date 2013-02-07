.. -*- rst -*-

Numpy Data Type Serialization Using Msgpack
===========================================

Package Description
-------------------

This package provides encoding and decoding routines that enable the
serialization and deserialization of numerical and array data types provided by 
`numpy <http://www.numpy.org/>`_ using the highly efficient
`msgpack <http://msgpack.org/>`_ format. Serialization of Python's
native complex data types is also supported.

Installation
------------

msgpack_numpy requires msgpack-python and numpy. If you 
have `pip <http://www.pip-installer.org/>`_ installed on your
system, run ::

    pip install msgpack_numpy

to install the package and all dependencies. You can also download 
the source tarball, unpack it, and run ::

    python setup.py install

from within the source directory.

Usage
-----

The easiest way to use msgpack_numpy is to call its monkey patching
function after importing the Python msgpack package: ::

    import msgpack
    import msgpack_numpy as m
    m.patch()

This will automatically force all msgpack serialization and deserialization
routines (and other packages that use them) to become numpy-aware. 
Of course, one can also manually pass the encoder and 
decoder provided by msgpack_numpy to the msgpack routines: ::

    import msgpack
    import msgpack_numpy as m
    import numpy as np

    x = np.random.rand(5)
    x_enc = msgpack.packb(x, default=m.encoder)
    x_rec = msgpack.unpackb(x_enc, object_hook=m.decoder)

Authors
-------

This software was written and packaged by `Lev Givon <lev@columbia.edu>`_.

License
-------

This software is licensed under the 
`BSD License <http://www.opensource.org/licenses/bsd-license.php>`_.
See the included LICENSE.rst file for more information.

Development
-----------

The latest source code can be obtained from
`<http://github.com/lebedov/msgpack_numpy/>`_.
