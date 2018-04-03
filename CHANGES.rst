Changes
=======

0.0.11 (2018-XX-XX)
-------------------

* FEATURE: Memsync can handle pointers to memory, which was allocated by a DLL, see issue #37.
* FEATURE: Memsync can target return values or elements within, see issue #40.
* Memsync became more memory efficient and slightly faster.
* Memsync syntax for custom length functions has been changed. ``_f`` becomes obsolete. ``f`` expects a string, which be parsed into a function.
* Memsync syntax for NULL-terminated strings (both ``c_char`` and ``c_wchar``, i.e. Unicode, buffers) has been simplified: ``n`` must be set to ``True`` indicating a NULL-terminated string. ``l`` becomes optional in this context.
* Memsync syntax for Unicode strings (buffers) has been simplified: ``w`` must be set to ``True`` instead of the length of ``ctypes.c_wchar``.

0.0.10 (2018-03-23)
-------------------

* FEATURE: Support for functions calculating the length of memory sections in memsync protocol, see issue #33.
* FEATURE: Support for string buffers (and null-terminated strings), see issue #7.
* FIX: Memsync definition sometimes lost information during first call of function, second call subsequently failed, see issue #36.

0.0.9 (2018-03-21)
------------------

* FIX: Arch "win64" was broken because of wrong download URL for embedded CPython for win64/amd64, see issue #27.
* FIX: Function pointers in struct types were not handled, see issue #28.
* FIX: Memsync directives pointing to elements within structs were not handled properly, see issue #29.
* FIX: Missing DLLs of type windll and oledll now raise OSError as expected, see issue #30.
* FIX: Missing routines in DLLs now raise AttributeError as expected, see issue #31.
* FIX: Wrong or unconfigured argtypes as well as wrong number of arguments do raise appropriate errors (ValueError, ArgumentError or TypeError), see issue #32.
* Isolated argument packing and unpacking code, preparing to solve issue #25.
* Renamed "logwrite" parameter & command line option into "log_write".
* Reduced number of RPC servers to one per side (Unix and Wine).

0.0.8 (2018-03-18)
------------------

* FEATURE: Support for structures and pointers as return values, see issue #14.
* FEATURE: (Limited) support for call back functions (function pointers) as DLL argument types, see issues #3 and #4.
* FIX: ``argtypes`` definitions (with one single argument) were not raising a ``TypeError`` like ``ctypes`` does if not passed as a tuple or list, see issue #21.

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
