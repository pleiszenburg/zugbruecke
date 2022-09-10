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

Memory Synchronization
----------------------

Because *zugbruecke* executes DLL routines in a separate *Windows Python* process on top of *Wine*, it must keep memory between the *Unix Python* and the *Windows Python* processes in sync, especially for pointers (or the memory pointers are pointing to). *zugbruecke* can handle this task partially automatically but does require special directives in certain cases. A good set of introductory examples is provided in the :ref:`chapter covering the memory synchronization protocol <memsyncprotocol>`.

Further Examples
----------------

For an overview over its entire range of capabilities have a look at *zugbruecke*'s `test suite`_.

.. _test suite: https://github.com/pleiszenburg/zugbruecke/tree/master/tests
