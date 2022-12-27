:github_url:

.. _examples:

.. index::
    pair: cdll; example
    pair: windll; example
    pair: oledll; example
    pair: memsync; example
    single: demo_dll

Getting Started
===============

.. warning::

    Read the `ctypes documentation`_ first if you have not done so already. **zugbruecke is a drop-in replacement for ctypes**. *zugbruecke*'s documentation does **NOT** cover how to use *ctypes*.

.. _ctypes documentation: https://docs.python.org/3/library/ctypes.html

Minimal Example
---------------

A lot of code, which was written with ``ctypes``' ``cdll``, ``windll`` or ``oledll`` in mind and which runs under *Windows*, should run just fine with *zugbruecke* on Unix. Let's assume you are dealing with a DLL named ``demo.dll`` containing a compiled version of the following bit of C code:

.. code:: c

    float
    __stdcall __declspec(dllimport)
    simplefunc(
        float a,
        float b
    )
    {
        return a - (a / b);
    }

On Windows, you could call it via ``ctypes`` by importing it first:

.. code:: python

    import ctypes

On Unix-like systems such as Linux, Mac OS or BSD, you simply import ``zugbruecke.ctypes`` instead:

.. code:: python

    import zugbruecke.ctypes as ctypes

From now on, the code is - in most but not all cases - the same. You can call the function as follows:

.. code:: python

    simplefunc = ctypes.windll.LoadLibrary('demo.dll').simplefunc
    simplefunc.argtypes = (ctypes.c_float, ctypes.c_float)
    simplefunc.restype = ctypes.c_float

    result = simplefunc(20.0, 1.07)
    print(f'Got "{result:f}".')

It will happily print ``Got "1.308412".``

Optional ``argtypes`` and ``restype`` annotations
-------------------------------------------------

The original *ctypes* allows to omit specifying ``argtypes`` and ``restype`` annotations in some cases. It tends to default to integers, ``ctypes.c_int``, in most cases, while also accepting pointers. *zugbruecke* is more strict in those cases and basically only allows passing integers without type annotations.

.. note::

    Differing from original *ctypes*, it is recommended to always specify ``argtypes`` and ``restype`` when using *zugbruecke*. Pointer types must be explicitly indicated. *ctypes* may accept data and even implicitly pass it as pointers in one way or another which is a mechanism not properly supported by *zugbruecke*.

Platform-Independent Code
-------------------------

Because of the drop-in replacement design of *zugbruecke*, it is therefore possible to write platform-independent *Python* code which works under both *Unices* and *Windows*.

.. code:: python

    from sys import platform
    if any(platform.startswith(name) for name in ('linux', 'darwin', 'freebsd')):
        import zugbruecke.ctypes as ctypes
    elif platform.startswith('win'):
        import ctypes
    else:
        raise SystemError('unsupported platform')

Shared Objects and DLLs
-----------------------

There is no harm in calling into both Shared Object files and DLLs from the same code base. Be aware that you have to deal with two versions of ``ctypes``:

.. code:: python

    import zugbruecke.ctypes as ctypes_windows # for DLLs
    import ctypes as ctypes_unix # for shared objects

32 bit and 64 bit DLLs
----------------------

Thanks to Wine, which can run both in 32 bit and in 64 bit mode, it is perfectly possible to call into both 32 bit and 64 bit DLLs - even side by side. For this and similar use cases, *zugbruecke* allows to start :ref:`multiple sessions <session>` simultaneously, each with its own separate :ref:`configuration <configuration>`. Instead of importing ``zugbruecke.ctypes``, you must create instances from the :class:`zugbruecke.CtypesSession` class. Consider the following example:

.. code:: python

    from zugbruecke import CtypesSession

    ctypes_windows32 = CtypesSession(arch = 'win32')
    ctypes_windows64 = CtypesSession(arch = 'win64')

.. _integerwidths:

Platform-Dependent Integer Widths
---------------------------------

The width, i.e. size in bytes, of long integer types differs between platforms and therefore also between Unix-like systems and Windows systems. *zugbruecke* is no exception here, where long integer types have different widths between the Unix-side from where you want to call a DLL function and the Wine-side where the DLL function is being executed:

.. code:: bash

    (env) user@comp:~> python -m platform
    Linux
    (env) user@comp:~> python -c "from ctypes import c_long, c_ulong, sizeof as s; \
    > print(s(c_long), s(c_ulong))"
    8 8
    (env) user@comp:~> wenv python -m platform
    Windows
    (env) user@comp:~> wenv python -c "from ctypes import c_long, c_ulong, sizeof as s; \
    > print(s(c_long), s(c_ulong))"
    4 4

For consistency, *zugbruecke* deals with this by sticking to the width of long integers on Unix-like systems, i.e. 8 bytes.

.. warning::

    `c_long` on the Unix side is being translated to `c_int64` on the Wine side. `c_ulong` on the Unix side is being translated to `c_uint64` on the Wine side. If you require `c_long` or `c_ulong` following Windows' definitions, you will have to use `c_int32` or `c_uint32` on the Unix side.

.. note::

    Integers with specified length, e.g. `c_int32`, always have the same length on both, the Unix and the Wine side.

.. _floattypes:

Platform-Dependent Floating-Point Behaviour
-------------------------------------------

Single-precision floats, `c_float`, 32 bits or 4 bytes long as per `IEEE 754`_, as well as double-precision floats, `c_double`, 64 bits or 8 bytes long as per IEEE 754, behave identical both on Unix-like systems and Windows. They can be passed to and retrieved from DLL functions without issues.

.. warning::

    `Long double`_ types or `quadruple-precision floating-point`_ types pose a special kind of problem. Long story short: Support and implementation between platforms differ significantly. Windows, a bit simplified, has virtually no support for those types although e.g. certain C compilers offer some support on Windows on their own. Since *zugbruecke* is built on top of CPython and `ctypes`, it is following its capabilities. While `c_longdouble` is in fact 128 bits or 16 bytes long on Linux for instance, it maps to `c_double` on Windows at 64 bits or 8 bytes. Passing floating point numbers longer than 64 bits is therefore basically not supported by `zugbruecke`. This may be partially worked around by passing buffers of 16 bytes per number or using numpy's `support of long double`_.

.. _IEEE 754: https://en.wikipedia.org/wiki/IEEE_754
.. _long double: https://en.wikipedia.org/wiki/Long_double
.. _quadruple-precision floating-point: https://en.wikipedia.org/wiki/Quadruple-precision_floating-point_format
.. _support of long double: https://numpy.org/doc/stable/user/basics.types.html#extended-precision

.. code:: bash

    (env) user@comp:~> python -m platform
    Linux
    (env) user@comp:~> python -c "from ctypes import c_longdouble, sizeof as s; \
    print(s(c_longdouble))"
    16
    (env) user@comp:~> wenv python -m platform
    Windows
    (env) user@comp:~> wenv python -c "from ctypes import c_longdouble, sizeof as s; \
    print(s(c_longdouble))"
    8

.. warning::

    `Half-precision floating-point`_ types have recently seen a boost in popularity thanks to machine learning applications. There are completely different variations/implementations of the idea going by different names such as `bfloat16`_. Since *zugbruecke* is built on top of CPython and `ctypes`, which does not offer any form of support for half-precision floating-point types, it is following its capabilities i.e. there is no direct support for them in *zugbruecke*. This may be partially worked around by passing buffers of 2 bytes per number or using numpy's `support of half-precision floating-point`_. numpy's `support of bfloat16`_ is still, as of late 2022, under development.

.. _Half-precision floating-point: https://en.wikipedia.org/wiki/Half-precision_floating-point_format
.. _bfloat16: https://en.wikipedia.org/wiki/Bfloat16_floating-point_format
.. _support of half-precision floating-point: https://numpy.org/doc/stable/reference/arrays.scalars.html#numpy.half
.. _support of bfloat16: https://github.com/numpy/numpy/issues/19808

.. _callingconvention:

Calling Conventions
-------------------

While the handling of different calling conventions is absolutely identical between *ctypes* and *zugbruecke*, it is actually a common trap for beginners when using *zugbruecke* (or *ctypes*) for the first time. The confusion arises around ``ctypes.CDLL`` / ``ctypes.cdll`` and ``ctypes.WinDLL`` / ``ctypes.windll``, which refer to two different `calling conventions`_. In fact, both types of calling conventions can be found on Windows. Any given DLL might use either one. While both calling conventions are ironically identical for 64-bit DLLs and can be used interchangeably in those cases, calling conventions actually differ for 32-bit DLLs. The main difference or symptom is that function arguments are passed to the function in a location differing by an offset of 8 bytes. You might see exceptions similar to "arguments 8 bytes too short" or "arguments 8 bytes too long" if using the wrong calling convention. In rare cases, you might not even get an exception but receive plain wrong results from the called function instead.

.. _calling conventions: https://en.wikipedia.org/wiki/Calling_convention

.. note::

    If the DLL's C-code is available, the calling convention can be deduced from "annotations" in front of functions. ``__stdcall`` points to ``WINDLL``, while ``__cdecl`` points to ``CDLL``.

Memory Synchronization
----------------------

Because *zugbruecke* executes DLL routines in a separate *Windows Python* process on top of *Wine*, it must translate pointers and keep memory between the *Unix Python* and the *Windows Python* processes in sync. *zugbruecke* can handle this task partially automatically but does require special ``memsync`` directives in certain cases. A good set of introductory examples is provided in the :ref:`chapter covering pointers and memory synchronization <memsync>`.

Further Examples
----------------

For an overview over its entire range of capabilities have a look at *zugbruecke*'s `test suite`_.

.. _test suite: https://github.com/pleiszenburg/zugbruecke/tree/master/tests
