Changes
=======

0.0.8 (2018-XX-XX)
------------------

* FEATURE: Support for structures and pointers as return values, see issue #14.

0.0.7 (2018-03-05)
------------------

* FIX: Wine Python environment sometimes did, unintentionally, fall back to Python 2 and crash, see issue #20.
* Confirmed: Support for Mac OS X, see issue #16.

0.0.6 (2017-12-06)
------------------

* RPC speedup due to removal of extra pickling step
* Moved definition of development dependencies into ``setup.py``
* FIX: Added workaround for `CPython issue 24960`_ (embedded zip file extracted into library folder) - was triggered by latest version of ``pluggy`` (dependency of ``pytest``)
* FIX: Preexisting installation of ``wine-python`` is now always being removed completely when required due to update or new installation

.. _CPython issue 24960: https://bugs.python.org/issue24960

0.0.5 (2017-11-13)
------------------

* FEATURE: Support for light-weight pointers (``ctypes.byref``)
* FIX: Elements within structures are properly synchronized even if they are not a pointer on their own.
* FIX: Structure objects in arrays of structures are properly initialized.
* FIX: Links in ``README.rst`` work when rendered on PyPI.

0.0.4 (2017-11-05)
------------------

* FEATURE: Full support for multidimensional fixed length arrays

0.0.3 (2017-11-02)
------------------

* FEATURE: Fixed length 1D arrays
* Refactored argument packing and unpacking code
* Plenty of cleanups based on static code analysis
* Introduced ``Python``'s ``any`` functions in a number of places
* FIX: Lots of typos and grammar issues in documentation

0.0.2 (2017-07-28)
------------------

* Added and confirmed CPython 3.4 compatibility
* Added installation instructions to documentation

0.0.1 (2017-07-28)
------------------

* First official (pre-) release of *zugbruecke*
