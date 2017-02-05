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
VERSION =            '0.3.8'
AUTHOR =             'Lev Givon'
AUTHOR_EMAIL =       'lev@columbia.edu'
URL =                'https://github.com/lebedov/msgpack-numpy'
DESCRIPTION =        'Numpy data serialization using msgpack'
LONG_DESCRIPTION =   DESCRIPTION
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
