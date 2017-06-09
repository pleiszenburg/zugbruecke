**pycrosscall** - Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD

Synopsis
========

**pycrosscall** is an EXPERIMENTAL **Python module** (currently "Development Status :: 3 - Alpha").
It allows to **call routines in Windows DLLs from Python code running on
Unices / Unix-like systems** such as Linux, MacOS or BSD.
pycrosscall is designed as a **drop-in replacement for ctypes' windll interface**.
*Based on Wine*, it starts a stand-alone Windows Python interpreter in
the background, which is used to execute the called DLL routines.
Communication between the UNIX-side and the Windows/Wine-side is based on Python's
build-in XML-RPC capability.
pycrosscall comes with extensive logging features allowing to debug problems
associated with both itself and with Wine.
pycrosscall is written using **Python 3 syntax** and primarely targets the
**CPython** implementation of Python.


*About Wine, from winehq.org: Wine (originally an acronym
for "Wine Is Not an Emulator") is a compatibility layer
capable of running Windows applications on several POSIX-compliant operating systems,
such as Linux, MacOS and BSD. Instead of simulating internal Windows logic like a
virtual machine or emulator, Wine translates Windows API calls into POSIX calls
on-the-fly, eliminating the performance and memory penalties of other methods and
allowing you to cleanly integrate Windows applications into your desktop.*

*For more details go to: https://www.winehq.org/*

**This project is NEITHER associated NOR affiliated in any way or form with the Wine project.**

Prerequisites
=============

For using the module:

- CPython 3.x *(tested with 3.5 and 3.6)* - No additional Python packages are required.

- Wine 2.x *(tested with 2.6 and 2.6-staging)* - Expected to be in the user's PATH.

For examples and tests, in addition:

- mingw cross-compiler *(for building DLLs against which examples and tests can be run)*

Installation
============

For the latest "stable" release run:

.. code:: bash

	pip install pycrosscall

For the latest development snapshot run:

.. code:: bash

	pip install git+git://github.com/s-m-e/pycrosscal.git@develop

Because of the use of Wine, which should never be run with root privileges,
it is highly advisable to install this package with user privileges only into
a virtual environment.

Examples
========

pycrosscall essentially behaves like a drop-in replacement for ctypes' ``windll`` interface.
Therefore, most code, which was written with ``windll`` in mind and which runs under Windows,
should run just fine with pycrosscall.

.. code:: python

	from pycrosscall import ctypes

	_call_demo_routine_ = ctypes.windll.LoadLibrary('demo_dll.dll').simple_demo_routine
	_call_demo_routine_.argtypes = [
		ctypes.c_float,
		ctypes.c_float
		]
	_call_demo_routine_.restype = ctypes.c_float
	return_value = _call_demo_routine_(20.0, 1.07)
	print('Got "%f".' % return_value)

It will print ``Got "1.308412".`` assuming that the corresponding routine in the DLL
looks somewhat like this:

.. code:: c

	float __stdcall __declspec(dllimport) simple_demo_routine(float param_a, float param_b)
	{ return param_a - (param_a / param_b); }

The following import statement also works:

.. code:: python

	from pycrosscall import windll

The ``ctypes`` object offered by pycrosscall is just the Python interpreter's
regular ``ctypes``, which is patched by pycrosscall during import.

Because of the drop-in replacement design of pycrosscall, it is possible to write
Python code which works under both Unices and Windows.

.. code:: python

	from sys import platform
	if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:
		from pycrosscall import ctypes
	elif platform.startswith('win'):
		import ctypes
	else:
		# Handle unsupported platforms

For more examples and DLL source code check the ``examples`` directory.

Speed
=====

...


Security
========

...

License
=======

pycrosscall is licensed under **GPL v2**. See ``LICENSE`` file for details.


Contribute
==========

Contributions are highly welcomed!

The source code is hosted on GitHub: https://github.com/s-m-e/pycrosscall/
Pull requests will be reviewed and, if there is nothing to object, merged promptly.
Do not break tests (unless there is a justified bug in them)!

Bugs
====

Please report bugs in pycrosscall in the pycrosscall GitHub repository: https://github.com/s-m-e/pycrosscall/issues

Please report bugs in Wine in the WineHQ Bug Tracking System: https://bugs.winehq.org/

Make sure to separate between pycrosscall-related and Wine-related bugs.
Calling routines in DLLs from Windows-executable (executed with Wine) with identical
parameters for narrowing down the possible sources of an error is a good way to start.

Implementation details
======================

During the installation of pycrosscall, a stand-alone Windows-version of the
CPython interpreter corresponding to the used Unix-version is automatically
downloaded and placed into the module's folder. Next to it, pycrosscall
generates its own Wine-profile directory for being used with a dedicated
``WINEPREFIX``. This way, any undesirable interferences with other Wine-profile
directories containing user settings and unrelated software are avoided.

During the import of pycrosscall, the ``ctypes`` module is patched with an
additional ``windll`` "sub-module" that would otherwise only be present under
Windows.

Why?
====

Good question.

Missing features (for full ctypes compatibility)
================================================

The following features have yet not been added to pycrosscall:

- Access to DLLs using the ``cdll`` and ``oledll`` calling conventions
- Windows data types (``wintypes``)
- Related functions for handling DLLs and routines (``WINFUNCTYPE``, ``DllCanUnloadNow``, ``DllGetClassObject``)
- Error-handling, Windows-style (``FormatError``, ``GetLastError``, ``get_last_error``, ``set_last_error``, ``WinError``)
- Access to default Windows APIs e.g. from kernel32.dll (as far as Wine offers them)
- Explicitly differentiating between ANSI and Unicode versions of routines

To do (target: BETA-status)
===========================

The following issues need to be resolved before 'Development Status :: 4 - Beta'
can be achieved:

- ``wineserver`` start/stop must be implemented in a clean way. pycrosscall is
  currently using ``time.sleep`` with hard coded time spans, waiting for the server to start and stop.
- ``wineserver`` and ``wine`` related code should be isolated into an independent module or sub-module.
- Ports for XML-RPC communication must be dynamically allocated instead of being hard coded - allowing
  multiple simultaneous pycrosscall sessions to coexist peacefully.
- pycrosscall must become thread safe so it can be used with modules like ``multiprocessing``.
- A test-suite covering all features must be developed.
- Structures and pointers should be handled more appropriately.
  Especially, structures should be passed in a better, more secure and faster way than via ``/dev/shm``.
- XML-RPC clients should authenticate themselves before being allowed to access servers.
- The log should be divided into log-levels with more or less details.
  Higher log-levels should contain details of the current stack frame
  such as line number or calling routine (based on the ``inspect``).
- Dedicated error types for catching more errors and their details.

Beyond beta-status
==================

Potentially interesting features, which might (or might not) be investigated after reaching beta status:

- Support for popular "alternative" Python interpreters such as PyPy
- Support for Python 2 syntax interpreters
- Support for other versions of Wine such as CrossOver

Known issues
============

The following relevant issues exist in software pycrosscall depends on:

- Wine bug #42474 ("Python 3.6 needs function api-ms-win-core-path-l1-1-0.dll.PathCchCombineEx")
  renders CPython 3.6.x for Windows unusable under Wine. 3.5 or prior has to be used instead.
  More details: https://bugs.winehq.org/show_bug.cgi?id=42474
- The CPython installer for Windows does not work with Wine at all.
  In a similar fashion, msi-files also fail to install.
  The current work-around is to use the "embedded" stand-alone version of CPython for Windows,
  which is offered as a zip-file.
- CPython for Windows prior to version 3.5 is not offered as a zipped
  "embedded" stand-alone version without installer. 3.5 or later has to be used.

For production environments
===========================

Do NOT run this code (as-is) in production environments unless you feel that you
really know what you are doing or unless you are absolutely desperate.
Being experimental in nature and of alpha quality, it is prone to fail
in a number of unpredictable ways, some of which might not be obvious or might
not even show any (intermediately) recognizable symptoms at all.

If this has not driven you off and you nevertheless want to use pycrosscall in
individual, well isolated cases in production environments, feel free to contact
its author for exploring further options: ernst@pleiszenburg.de
