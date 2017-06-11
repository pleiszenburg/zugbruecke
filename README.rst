**pycrosscall** - Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD

.. image:: http://www.pleiszenburg.de/pycrosscall_logo.png

Synopsis
========

**pycrosscall** is an EXPERIMENTAL **Python module** (currently in development **status 3/alpha**).
It allows to **call routines in Windows DLLs from Python code running on
Unices / Unix-like systems** such as Linux, MacOS or BSD.
pycrosscall is designed as a **drop-in replacement for ctypes' windll interface**.
pycrosscall is **built on top of Wine**. A stand-alone Windows Python interpreter
launched in the background is used to execute the called DLL routines.
Communication between the UNIX-side and the Windows/Wine-side is based on Python's
build-in XML-RPC capability.
pycrosscall comes with extensive logging features allowing to debug problems
associated with both itself and with Wine.
pycrosscall is written using **Python 3 syntax** and primarily targets the
**CPython** implementation of Python.

*About Wine, from winehq.org: Wine (originally an acronym
for "Wine Is Not an Emulator") is a compatibility layer
capable of running Windows applications on several POSIX-compliant operating systems,
such as Linux, MacOS and BSD. Instead of simulating internal Windows logic like a
virtual machine or emulator, Wine translates Windows API calls into POSIX calls
on-the-fly, eliminating the performance and memory penalties of other methods and
allowing you to cleanly integrate Windows applications into your desktop.
For more details go to: https://www.winehq.org/*

**This project is NEITHER associated NOR affiliated in any way or form with the Wine project.**

Prerequisites
=============

For using the module:

- **CPython 3.x** *(tested with 3.5 and 3.6)* - No additional Python packages are required.

- **Wine 2.x** *(tested with 2.6 and 2.6-staging)* - Expected to be in the user's PATH.

For examples and tests, in addition:

- mingw cross-compiler *(for building DLLs against which examples and tests can be run)*

Installation
============

For the latest "stable" (working) **release** run:

.. code:: bash

	pip install pycrosscall

For the latest **development snapshot** (likely broken) run:

.. code:: bash

	pip install git+git://github.com/s-m-e/pycrosscal.git@develop

Because of the use of Wine, which should never be run with root privileges,
it is highly advisable to install this package with user privileges only into
a virtual environment.

Examples
========

pycrosscall essentially behaves like a drop-in replacement for ctypes' ``windll`` interface.
In other words, it only covers the "stdcall calling convention" at this point.
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

The inter-process communication via **XML-RPC adds significant overhead** to every function call.
Calls are slow as hell in general, but the first call of an individual routine within
a session is even slower due to necessary initialization happening beforehand.
Depending on the use-case, instead of working with pycrosscall, it will be significantly
faster to isolate functionality depending on DLL calls into a dedicated Python
script and run it directly with a Windows Python interpreter under Wine. For comparison,
see the following numbers:

===================  ==============  =================== ==================== ==================
Example call         iterations [#]  w/o pycrosscall [s] *w/ pycrosscall* [s] overhead/call [µs]
===================  ==============  =================== ==================== ==================
simple_demo_routine  10k             0.015               12.230               1.222
===================  ==============  =================== ==================== ==================

Benchmarks were performed with an i7 860 CPU, Linux kernel 4.4.62, Wine 2.6-Staging,
CPython 3.6.0 x86-64 for Linux and CPython 3.5.3 x86-32 for Windows. pycrosscall was
configured with log level 0 (logs off) for minimal XML-RPC overhead.

Security
========

pycrosscall is **notoriously insecure by design**.

- **DO NOT** run it on any system directly exposed to the internet! Have a firewall on at all times!
- **DO NOT** run untrusted code (or DLLs)!
- **DO NOT** use pycrosscall for any security related tasks such as encryption, decryption,
  authentication and handling of keys or passwords!
- **DO NOT** run it with root / super users privileges!

The following problems also directly apply to pycrosscall:

- XML vulnerabilities: https://docs.python.org/3/library/xml.html#xml-vulnerabilities
- Wine can in fact theoretically run (some) Windows malware: https://en.wikipedia.org/wiki/Wine_(software)#Security
- **NEVER run Wine as root**: https://wiki.winehq.org/FAQ#Should_I_run_Wine_as_root.3F

License
=======

pycrosscall is licensed under **LGPL v2.1**. See ``LICENSE`` file for details.

Contribute
==========

**Contributions are highly welcomed!**

The source code is hosted on GitHub: https://github.com/s-m-e/pycrosscall/
Pull requests will be reviewed and, if there is nothing to object, merged promptly.
Do not break tests (unless there is a justified bug in them)!

Bugs
====

Please report bugs in pycrosscall in the pycrosscall GitHub repository: https://github.com/s-m-e/pycrosscall/issues

Please report bugs in Wine in the WineHQ Bug Tracking System: https://bugs.winehq.org/

Make sure to separate between pycrosscall-related and Wine-related bugs.
Calling routines in DLLs from Windows-executables (executed with Wine) with identical
parameters for narrowing down the possible sources of an error is a good way to start.

How to bisect issues
--------------------

pycrosscall is based on a session model. Each session can be launched with
parameters. Instead of leaving the session start with default parameters to
pycrosscall, the process can be triggered manually instead.
Right after import and before ``LoadLibrary`` is invoked for the first time,
start a pycrosscall session as follows and pass parameters like the "log level"
into it.

.. code:: python

	from pycrosscall import ctypes
	ctypes.windll.start_session(parameter = {'log_level': 10})
	# proceed as usual ...

The higher the log level, the more output you will get. Default is 0 for no logs.
The on-screen log is color-coded for readability. The log can also, in addition,
be written to disk, where every log item with plenty of meta data is represented
as a one-line JSON object for easy parsing and analysis of larger log files.

Have a look into the routine ``get_default_config`` in ``pycrosscall/config.py`` for
a comprehensive overview over all possible parameters.

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

FAQ
===

Why? Seriously, WHY?
--------------------

Good question. Academic interest and frustration over the lack of a project of
this kind, mostly. The need for calling individual routines offered by DLLs
from Linux/MacOS/BSD software/scripts is reflected in numerous threads in forums and
mailing lists reaching back well over a decade. The recommended approach so far
has been (and still is!) to write a Wine application, which links against ``winelib``,
thus allowing to access DLLs. Wine applications can also access libraries
on the Unix "host" system, which provides the desired bridge between both worlds.
Nevertheless, this approach is anything but trivial. pycrosscall is supposed
to satisfy the desire for a "quick and dirty" solution for calling routines from a
high level scripting language, Python, directly running on the Unix "host" system.
With respect to "quick", pycrosscall works just out of the box with Wine installed.
No headers, compilers, cross-compilers or any other configuration is required - one
import statement followed by well established ``ctypes`` syntax is enough.
It is pure Python doing its job.
With respect to "dirty", well, read this document from start to finish.

What are actual use cases for this project?
-------------------------------------------

- Quickly calling routines in proprietary DLLs. Reading legacy file formats and
  running mission critical legacy plugins for legacy ERP software in a modern environment
  comes to mind.

- Calling routines in DLLs which come, for some odd reason (like "developer suddenly
  disappeared with source code"), without source code.
  DLLs found in company-internal software or R&D projects come to mind.

- More common than one might think, calling routines in DLLs, of which the source code is available but
  can not be (re-)compiled (on another platform) / understood / ported for similarly
  odd reasons (like "developer retired and nobody knows how to do this" or "developer died
  and nobody manages to understand the undocumented code"). The latter is especially
  prevalent in academic environments, where what is left of years of hard work might
  only be a single "binary blob" - a copy of an old DLL file. All sorts of complicated
  and highly specialized numerical computations come to mind.

Missing features (for full ctypes compatibility)
================================================

The following features have yet not been added to pycrosscall:

- Access to DLLs using the ``cdll`` and ``oledll`` calling conventions
- Access to DLL functions exported by ordinal instead of by name
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
  Running connections through SSL should be investigated.
- The log should be divided into log-levels with more or less details.
  Higher log-levels should contain details of the current stack frame
  such as line number or calling routine (based on the ``inspect``).
  Log level support exists, though all messages currently use default level 1.
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

**DO NOT run this code (as-is) in production environments unless you feel that you
really know what you are doing or unless you are absolutely desperate!
Being experimental in nature and of alpha quality, it is prone to fail
in a number of unpredictable ways, some of which might not be obvious or might
not even show any (intermediately) recognizable symptoms at all!
You might end up with plain wrong, nonsensical results without noticing it!**

If this has not driven you off and you nevertheless want to use pycrosscall in
individual, well isolated cases in production environments, feel free to contact
its author for exploring further options: ernst@pleiszenburg.de
