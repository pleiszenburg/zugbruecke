
.. |branch_master| image:: https://travis-ci.org/pleiszenburg/zugbruecke.svg?branch=master
    :target: https://travis-ci.org/pleiszenburg/zugbruecke

.. |branch_develop| image:: https://travis-ci.org/pleiszenburg/zugbruecke.svg?branch=develop
    :target: https://travis-ci.org/pleiszenburg/zugbruecke

+--------------------+--------------------+
| master/release     + |branch_master|    +
+--------------------+--------------------+
| development branch + |branch_develop|   +
+--------------------+--------------------+

**zugbruecke** - Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD

.. image:: http://www.pleiszenburg.de/zugbruecke_logo.png

Synopsis
========

**zugbruecke** is an EXPERIMENTAL **Python module** (currently in development **status 3/alpha**).
It allows to **call routines in Windows DLLs from Python code running on
Unices / Unix-like systems** such as Linux, MacOS or BSD.
zugbruecke is designed as a **drop-in replacement for ctypes' windll interface**.
zugbruecke is **built on top of Wine**. A stand-alone Windows Python interpreter
launched in the background is used to execute the called DLL routines.
Communication between the UNIX-side and the Windows/Wine-side is based on Python's
build-in multiprocessing connection capability.
zugbruecke has (limited) support for pointers and struct types.
zugbruecke comes with extensive logging features allowing to debug problems
associated with both itself and with Wine.
zugbruecke is written using **Python 3 syntax** and primarily targets the
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

- **Wine 2.x** *(tested with 2.5, 2.6(-staging), 2.10(-staging))* - Expected to be in the user's PATH.

For examples and tests, in addition:

- pytest

- mingw cross-compiler *(for building DLLs against which examples and tests can be run)*

Installation
============

For the latest "stable" (working) **release** run:

.. code:: bash

	pip install zugbruecke

For the latest **development snapshot** (likely broken) run:

.. code:: bash

	pip install git+git://github.com/pleiszenburg/zugbruecke.git@develop

Because of the use of Wine, which should never be run with root privileges,
it is highly advisable to install this package with user privileges only into
a virtual environment.

Examples
========

zugbruecke essentially behaves like a drop-in replacement for ctypes' ``windll`` interface.
In other words, it only covers the "stdcall calling convention" at this point.
Therefore, most code, which was written with ``windll`` in mind and which runs under Windows,
should run just fine with zugbruecke.

.. code:: python

	from zugbruecke import ctypes

	simple_demo_routine = ctypes.windll.LoadLibrary('demo_dll.dll').simple_demo_routine
	simple_demo_routine.argtypes = [
		ctypes.c_float,
		ctypes.c_float
		]
	simple_demo_routine.restype = ctypes.c_float
	return_value = simple_demo_routine(20.0, 1.07)
	print('Got "%f".' % return_value)

It will print ``Got "1.308412".`` assuming that the corresponding routine in the DLL
looks somewhat like this:

.. code:: c

	float __stdcall __declspec(dllimport) simple_demo_routine(float param_a, float param_b)
	{ return param_a - (param_a / param_b); }

The following import statement also works:

.. code:: python

	from zugbruecke import windll

The ``ctypes`` object offered by zugbruecke is just the Python interpreter's
regular ``ctypes``, which is patched by zugbruecke during import.

Because of the drop-in replacement design of zugbruecke, it is possible to write
Python code which works under both Unices and Windows.

.. code:: python

	from sys import platform
	if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:
		from zugbruecke import ctypes
	elif platform.startswith('win'):
		import ctypes
	else:
		# Handle unsupported platforms

For more examples and DLL source code check the ``examples`` directory.

For the original documentation of ``ctypes`` go to: https://docs.python.org/3/library/ctypes.html

Speed
=====

zugbruecke performs reasonably well given its complexity with **less than 0.2 µs
overhead per call** in average on modern hardware.

The inter-process communication via multiprocessing connection adds overhead to
every function call. Because zugbruecke takes care of packing and unpacking of
pointers and structure for arguments and return values, this adds another bit of overhead.
Calls are slow in general, but the first call of an individual routine within
a session is even slower due to necessary initialization happening beforehand.
Depending on the use-case, instead of working with zugbruecke, it will be significantly
faster to isolate functionality depending on DLL calls into a dedicated Python
script and run it directly with a Windows Python interpreter under Wine.

For comparison and overhead measurements, see the following numbers:

===================  ==============  ================== ================= ================== ============================
example call         iterations [#]  w/o zugbruecke [s] w/ zugbruecke [s] overhead/call [ns] parameter features
===================  ==============  ================== ================= ================== ============================
simple_demo_routine  100k            0.101              11.273            111.7              2x by value
gdc                  100k            0.104              11.318            112.1              2x by value
in_mandel (inside)   100k            0.518              11.719            112.0              3x by value
in_mandel (outside)  100k            0.131              11.494            113.6              3x by value
divide               100k            0.174              11.808            116.3              2x by value, 1x by reference
distance             100k            0.230              12.760            125.3              2x struct by reference
===================  ==============  ================== ================= ================== ============================

Benchmarks were performed with an i7 3740QM CPU, Linux kernel 4.4.72, Wine 2.10,
CPython 3.6.1 x86-64 for Linux and CPython 3.5.3 x86-32 for Windows. zugbruecke was
configured with log level 0 (logs off) for minimal overhead.

For the corresponding Python code and DLL source code (written in C) check the ``examples`` directory.

Security
========

zugbruecke is **notoriously insecure by design**.

- **DO NOT** run it on any system directly exposed to the internet! Have a firewall on at all times!
- **DO NOT** run untrusted code (or DLLs)!
- **DO NOT** use zugbruecke for any security related tasks such as encryption, decryption,
  authentication and handling of keys or passwords!
- **DO NOT** run it with root / super users privileges!

The following problems also directly apply to zugbruecke:

- Wine can in fact theoretically run (some) Windows malware: https://en.wikipedia.org/wiki/Wine_(software)#Security
- **NEVER run Wine as root**: https://wiki.winehq.org/FAQ#Should_I_run_Wine_as_root.3F

License
=======

zugbruecke is licensed under **LGPL v2.1**. See ``LICENSE`` file for details.

Contribute
==========

**Contributions are highly welcomed!**

The source code is hosted on GitHub: https://github.com/pleiszenburg/zugbruecke/
Pull requests will be reviewed and, if there is nothing to object, merged promptly.
Do not break tests (unless there is a justified bug in them)!

Bugs
====

Please report bugs in zugbruecke in the zugbruecke GitHub repository: https://github.com/pleiszenburg/zugbruecke/issues

Please report bugs in Wine in the WineHQ Bug Tracking System: https://bugs.winehq.org/

Make sure to separate between zugbruecke-related and Wine-related bugs.
Calling routines in DLLs from Windows-executables (executed with Wine) with identical
parameters for narrowing down the possible sources of an error is a good way to start.

How to bisect issues
--------------------

zugbruecke is based on a session model. Each session can be launched with
parameters. Instead of leaving the session start with default parameters to
zugbruecke, the process can be triggered manually instead.
Right after import and before ``LoadLibrary`` is invoked for the first time,
start a zugbruecke session as follows and pass parameters like the "log level"
into it.

.. code:: python

	from zugbruecke import ctypes
	ctypes.windll.start_session(parameter = {'log_level': 10})
	# proceed as usual ...

The higher the log level, the more output you will get. Default is 0 for no logs.
The on-screen log is color-coded for readability. The log can also, in addition,
be written to disk, where every log item with plenty of meta data is represented
as a one-line JSON object for easy parsing and analysis of larger log files.

Have a look into the routine ``get_default_config`` in ``zugbruecke/config.py`` for
a comprehensive overview over all possible parameters.

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
Nevertheless, this approach is anything but trivial. zugbruecke is supposed
to satisfy the desire for a "quick and dirty" solution for calling routines from a
high level scripting language, Python, directly running on the Unix "host" system.
With respect to "quick", zugbruecke works just out of the box with Wine installed.
No headers, compilers, cross-compilers or any other configuration is required - one
import statement followed by well established ``ctypes`` syntax is enough.
It is pure Python doing its job.
With respect to "dirty", well, read this document from start to finish.

What are actual use cases for this project?
-------------------------------------------

- Quickly calling routines in proprietary DLLs. Reading legacy file formats and
  running mission critical legacy plugins for legacy ERP software in a modern environment
  comes to mind.

- Calling routines in DLLs which come, for some odd reason like "developer suddenly
  disappeared with source code", without source code.
  DLLs found in company-internal software or R&D projects come to mind.

- More common than one might think, calling routines in DLLs, of which the source code is available but
  can not be (re-)compiled (on another platform) / understood / ported for similarly
  odd reasons like "developer retired and nobody knows how to do this" or "developer 'went on'
  and nobody manages to understand the undocumented code". The latter is especially
  prevalent in academic environments, where what is left of years of hard work might
  only be a single "binary blob" - a copy of an old DLL file. All sorts of complicated
  and highly specialized numerical computations come to mind.

How does it work?
-----------------

During the first import of zugbruecke, a stand-alone Windows-version of the
CPython interpreter corresponding to the used Unix-version is automatically
downloaded and placed into the module's configuration folder (by default located at
``~/.zugbruecke/``). Next to it, also during first import, zugbruecke
generates its own Wine-profile directory for being used with a dedicated
``WINEPREFIX``. This way, any undesirable interferences with other Wine-profile
directories containing user settings and unrelated software are avoided.

During every import of zugbruecke, the ``ctypes`` module is patched with an
additional ``windll`` "sub-module" that would otherwise only be present under
Windows. Once ``LoadLibrary`` is invoked for the first time, zugbruecke starts
its own wineserver and, on top of it, a Windows Python interpreter. The latter is
used to run a server script (named ``_server_.py``, located in the module's folder).
From now on, zugbruecke on the "Unix side" acts as a client to its server on the
"Wine side". The client passes calls with their parameters to the server, which executes
them using the regular ``ctypes`` interface for Windows.

Is it secure?
-------------

No. See "Security" section of this document.

How fast/slow is it?
--------------------

It performs reasonably well. See "Speed" section of this document.

Can it handle structures?
-------------------------

Yes, in principle. But avoid pointers within structures, if you
can. See next question for details.

Can it handle pointers?
-----------------------

Yes and no. Pointers to simple C data types (int, float, etc.)
used as function parameters can be handled just fine. Pointers
to arbitrary data structures are a bit of a problem. Pointers
returned by a DLL pointing to memory allocated by the DLL are
problematic, too.

zugbruecke is intended to once offer ways to copy memory from
the Unix side to the Wine side as well as in the opposite
direction, but those operations must likely (a) be triggered by the
programmer (manually, so to speak) and (b) require knowledge
of the size of the data structure to be copied.

Missing features (for better ctypes compatibility)
==================================================

The following features have yet not been added to zugbruecke:

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

- ``wineserver`` start/stop must be implemented in a clean(er) way. zugbruecke is
  currently using a few odd workarounds trying not to trigger bugs in Wine.
- zugbruecke must become thread safe so it can be used with modules like ``multiprocessing``.
- A test-suite covering all features must be developed.
- Structures and pointers should be handled more appropriately.
  Especially, structures should be passed in a better way.
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

The following relevant issues exist in software zugbruecke depends on:

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

If this has not driven you off and you nevertheless want to use zugbruecke in
individual, well isolated cases in production environments, feel free to contact
its author for exploring further options: ernst@pleiszenburg.de
