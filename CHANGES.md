<!-- 
-*- mode:markdown -*-
vi:ft=markdown
-->
Change Log
==========

Release 0.4.8 (April 28, 2022)
------------------------------
* Add support for ndarrays with dtype=object (#46).

Release 0.4.7.1 (September 30, 2020)
------------------------------------
* Fix Python 2.7 regression (#45).

Release 0.4.7 (September 16, 2020)
----------------------------------
* Fix bug unpacking nested, structured dtypes (#42).

Release 0.4.6.1 (July 28, 2020)
-------------------------------
* Deprecate support for msgpack < 1.0.0 (#41).

Release 0.4.6 (May 25, 2020)
----------------------------
* Set default use_bin_type and raw params of Packer and Unpacker classes the same as in msgpack (#39).
* Convert docs to Markdown.

Release 0.4.5 (April 12, 2020)
------------------------------
* Set defaults appropriate to msgpack 1.0.0 (#38).

Release 0.4.4.3 (May 16, 2019)
------------------------------
* Configure contiguous integration with Travis.
* Move unit tests out of msgpack_numpy module.
* Add workaround for issue handling n-dim arrays on MacOS (#35).

Release 0.4.4.2 (November 8, 2018)
----------------------------------
* Fix regression handling noncontiguous arrays (#34).

Release 0.4.4.1 (September 26, 2018)
------------------------------------
* Check Py version before defining encode and tostr funcs.
* Eliminate deprecation warnings, raise minimum required msgpack version (#31).
* Fix Python 2 support (#32).

Release 0.4.4 (September 25, 2018)
----------------------------------
* Access ndarray memory view directly to slightly speed up encoding (#30).

Release 0.4.3.2 - (September 17, 2018)
--------------------------------------
* Update classifiers to list Py3 support (#29).
  
Release 0.4.3.1 - (July 11, 2018)
---------------------------------
* Switch to numpy.frombuffer to avoid deprecation warning (#27).

Release 0.4.3 - (February 25, 2018)
-----------------------------------
* Change dependency name due to package name change (#25).

Release 0.4.2 - (December 2, 2017)
----------------------------------
* Make decoding/encoding defaults identical to those of msgpack-python 0.4.* (#19).
* Fix handling of nested arrays in Py3 (#21).
* Improve decoding of complex values in Py3.
* Use numpy.testing functions to make unit test errors more informative.
* Make object_hook params consistent with those of msgack-python (#23).
  
Release 0.4.1 - (July 6, 2017)
------------------------------
* Improve ability to decode data serialized with versions before 0.3.9 (#20).
  
Release 0.4.0 - (May 24, 2017)
------------------------------
* Remove deprecated ez_setup.
* Add numpy >= 1.9.0 dependency (#18).

Release 0.3.9 - (February 7, 2017)
----------------------------------
* Complex type handling fixes.
* Handle structured dtypes (#15).
* Note: data serialized with earlier versions cannot be deserialized with 0.3.9 
  (#17).
  
Release 0.3.8 - (Februrary 4, 2017)
-----------------------------------
* Fix deserialization with Python 3.5 (#13).

Release 0.3.7 - (March 12, 2016)
--------------------------------
* Add Python 3 support (#11).

Release 0.3.6 - (July 8, 2015)
------------------------------
* Fall back to pure Python msgpack if compiled extension is unavailable (#6).

Release 0.3.5 - (February 12, 2015)
-----------------------------------
* Add support for numpy scalar booleans (#8).

Release 0.3.4 - (December 12, 2014)
-----------------------------------
* Add badges, update README.

Release 0.3.3 - (October 21, 2014)
----------------------------------
* Add missing ez_setup.py file.

Release 0.3.2 - (May 6, 2014)
-----------------------------
* Simplify encoding/decoding of numpy scalars.

Release 0.3.1.1 - (March 2, 2014)
---------------------------------
* Make package a simple module to fix dependency installation issues.

Release 0.3.1 - (March 2, 2014)
-------------------------------
* Switch to PEP 440 version numbering.
* Update to setuptools 2.2 ez_setup.py

Release 0.03 - (October 30, 2013)
---------------------------------
* Add support for msgpack 0.4.0.
* Rename to msgpack-numpy.
  
Release 0.022 - (September 10, 2013)
------------------------------------
* Fix decoding of string arrays (#4).
* Fix decoding of dicts containing ndarrays (#5).

Release 0.021 - (May 29, 2013)
------------------------------
* Improve encoding/decoding performance for arrays.
* Fix numpy type support on different platforms (#3).

Release 0.02 - (February 21, 2013)
----------------------------------
* Add support for msgpack 0.3.0 (contributed by crispamares).

Release 0.01 - (February 07, 2013)
----------------------------------
* First public release.

