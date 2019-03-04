Changes
=======

0.1.0 (2019-XX-XX)
------------------

Caution: **MODULE LAYOUT CHANGE BREAKING BACKWARDS COMPATIBILITY!**

Previously, *zugbruecke* or parts of it could be imported as follows:

.. code:: python

	import zugbruecke as ctypes
	from zugbruecke import c_double

From now on, the ``ctypes`` drop-in replacement interface is located inside a new sub-module, ``zugbruecke.ctypes``. Import as follows:

.. code:: python

	import zugbruecke.ctypes as ctypes
	from zugbruecke.ctypes import c_double

The above significant change was mandatory for allowing to cleanup a lot of old code and to remove long-standing bugs. The main issue was that importing ``zugbruecke`` was implying that new wine-python session was started automatically. This could not be prohibited. With the new package layout, it becomes possible to import sub-modules of ``zugbruecke`` without implicitly starting a session. One of the more significant added benefits therefore is that this change also allows much more fine-grained tests.

As a consequence, ``zugbruecke.current_session`` is no longer available. ``zugbruecke.ctypes`` on its own is now the default session. Besides, the class ``zugbruecke.session`` was renamed into ``zugbruecke.ctypes_session`` and has now a fully compatible ``ctypes`` drop-in replacement interface as well. Both, ``zugbruecke.ctypes`` and custom sessions constructed from ``zugbruecke.ctypes_session``, now have methods and properties prefixed with ``_zb_`` for manipulating their configuration, termination and Wine-related tasks.

Furthermore, the shell scripts ``wine-python``, ``wine-pip`` and ``wine-pytest`` have been removed. Their functionality was consolidated into a single new script, ``wenv``. One can now call ``wenv python``, ``wenv pip`` and ``wenv pytest``. This change was necessary for allowing a more generic interface to entry points of arbitrary third party packages. Run ``wenv help`` for more information.

* FEATURE: ``wineprefix`` becomes a configuration parameter definable by users allowing custom wine prefixes, see issue #44.
* FEATURE: Introduced new error types specific to this package.
* FIX: ``wine-pip`` previously would, on every launch, download ``get-pip.py`` and try to install it first before running - even if ``pip`` was already installed. ``wenv pip`` does not show this behavior anymore.
* FIX: A proper TimeoutError is raised (instead of a SyntaxError) if *zugbruecke*'s server component does not start.
* The configuration module was refactored and made clearer and faster, allowing to implement new options.

0.0.13 (2019-02-03)
-------------------

* FIX: Documentation could (sometimes) not be built on readthedocs.

0.0.12 (2019-02-02)
-------------------

* FEATURE: Added official support for CPython 3.7.
* FEATURE: Added official support for Wine 4.
* FIX: Build folder was not automatically cleaned up before wheels were build, therefore they sometimes contained obsolete files & code.
* FIX: Travis configuration was missing new Wine repository key, which was breaking builds.
* Lots of fixes in documentation.
* New test script for easier development of new tests and features.

0.0.11 (2018-04-10)
-------------------

Caution: This release features a significant re-implementation (with additional, new functionality) of the memory synchronization protocol, ``memsync``.
As a part of it, overcoming old limitations, its syntax changed - effectively breaking backwards compatibility in almost call cases.
Please check the updated documentation, examples and tests for details.

* FEATURE: Memsync can handle pointers to memory, which was allocated by a DLL, see issue #37.
* FEATURE: Memsync can target return values or elements within, see issue #40.
* FEATURE: Memsync can be applied to callback functions, see issue #41 - support at this stage is largely untested.
* Memsync became more memory efficient and slightly faster.
* Memsync syntax for custom length functions has been changed. ``_f`` becomes obsolete. ``f`` expects a string, which can be parsed into a function.
* Memsync syntax for NULL-terminated strings (both ``c_char`` and ``c_wchar``, i.e. Unicode, buffers) has been simplified: ``n`` must be set to ``True`` indicating a NULL-terminated string. ``l`` becomes optional in this context.
* Memsync syntax for Unicode strings (buffers) has been simplified: ``w`` must be set to ``True`` instead of the length of ``ctypes.c_wchar``.

0.0.10 (2018-03-23)
-------------------

* FEATURE: Support for functions calculating the length of memory sections in memsync protocol, see issue #33.
* FEATURE: Support for string buffers (and null-terminated strings), see issue #7.
* FIX: Memsync definition sometimes lost information during first call of function, second call subsequently failed, see issue #36.

0.0.9 (2018-03-21)
------------------

Caution: This release introduces a change in configuration parameter naming, breaking backwards compatibility in rare cases.

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
