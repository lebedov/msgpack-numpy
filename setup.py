#!/usr/bin/env python

import sys, os
from glob import glob

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup

NAME =               'msgpack-numpy'
VERSION =            '0.3.9'
AUTHOR =             'Lev Givon'
AUTHOR_EMAIL =       'lev@columbia.edu'
URL =                'https://github.com/lebedov/msgpack-numpy'
DESCRIPTION =        'Numpy data serialization using msgpack'
LONG_DESCRIPTION =   """
Package Description
-------------------
This package provides encoding and decoding routines that enable the
serialization and deserialization of numerical and array data types provided by 
`numpy <http://www.numpy.org/>`_ using the highly efficient
`msgpack <http://msgpack.org/>`_ format. Serialization of Python's
native complex data types is also supported.

.. image:: https://img.shields.io/pypi/v/msgpack-numpy.svg
    :target: https://pypi.python.org/pypi/msgpack-numpy
    :alt: Latest Version
.. Uncomment after pypi is migrated to warehouse and stats are re-enabled:
.. https://github.com/badges/shields/issues/716
.. .. image:: https://img.shields.io/pypi/dm/msgpack-numpy.svg
    :target: https://pypi.python.org/pypi/msgpack-numpy
    :alt: Downloads

Installation
------------
msgpack-numpy requires msgpack-python and numpy. If you 
have `pip <http://www.pip-installer.org/>`_ installed on your
system, run ::

    pip install msgpack-numpy

to install the package and all dependencies. You can also download 
the source tarball, unpack it, and run ::

    python setup.py install

from within the source directory.

Usage
-----
The easiest way to use msgpack-numpy is to call its monkey patching
function after importing the Python msgpack package: ::

    import msgpack
    import msgpack_numpy as m
    m.patch()

This will automatically force all msgpack serialization and deserialization
routines (and other packages that use them) to become numpy-aware. 
Of course, one can also manually pass the encoder and 
decoder provided by msgpack-numpy to the msgpack routines: ::

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

Development
-----------
The latest source code can be obtained from
`GitHub <https://github.com/lebedov/msgpack-numpy/>`_.

Authors
-------
See the included ``AUTHORS.rst`` file for more information.

License
-------
This software is licensed under the `BSD License 
<http://www.opensource.org/licenses/bsd-license>`_.
See the included ``LICENSE.rst`` file for more information.
"""
DOWNLOAD_URL =       URL
LICENSE =            'BSD'
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering',
    'Topic :: Software Development']

if __name__ == "__main__":
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    setup(
        name = NAME,
        version = VERSION,
        author = AUTHOR,
        author_email = AUTHOR_EMAIL,
        license = LICENSE,
        classifiers = CLASSIFIERS,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        url = URL,
        py_modules = ['msgpack_numpy'],
        install_requires = ['numpy',
                            'msgpack-python>=0.3.0']
        )
