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

If you have `pip <http://www.pip-installer.org/>`_ installed on your
system, run ::

    pip install msgpack_numpy

You can also download the source tarball, unpack, and run ::

    python setup.py install

from within the source directory. The package requires 
msgpack-python and numpy.

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

Authors & Acknowledgemnts
-------------------------

This software was written and packaged by `Lev Givon <lev@columbia.edu>`_.

License
-------

This software is licensed under the 
`BSD License <http://www.opensource.org/licenses/bsd-license.php>`_.
See the included LICENSE file for more information.

Development
-----------

The latest source code can be obtained from
`<http://github.com/lebedov/msgpack_numpy/>`_.
