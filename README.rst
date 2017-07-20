
.. |branch_master| image:: https://travis-ci.org/pleiszenburg/zugbruecke.svg?branch=master
    :target: https://travis-ci.org/pleiszenburg/zugbruecke

.. |branch_develop| image:: https://travis-ci.org/pleiszenburg/zugbruecke.svg?branch=develop
    :target: https://travis-ci.org/pleiszenburg/zugbruecke

+--------------------+--------------------+
| master/release     + |branch_master|    +
+--------------------+--------------------+
| development branch + |branch_develop|   +
+--------------------+--------------------+

.. image:: http://www.pleiszenburg.de/zugbruecke_logo.png

Synopsis
========

**zugbruecke** is an EXPERIMENTAL **Python module** (currently in development **status 3/alpha**).
It allows to **call routines in Windows DLLs from Python code running on
Unices / Unix-like systems** such as Linux, MacOS or BSD.
zugbruecke is designed as a **drop-in replacement for Python's standard library's ctypes module**.
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

- **CPython 3.x** *(tested with 3.{5,6})* - No additional Python packages are required.

- **Wine 2.x** *(tested with 2.{5,6,10,12}{,-staging})* - Expected to be in the user's PATH.

For examples and tests, in addition:

- pytest

- mingw cross-compiler *(for building DLLs against which examples and tests can be run)*

For documentation:

- Sphinx

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

zugbruecke essentially behaves like a drop-in replacement for ctypes.
Most code, which was written with ``cdll``, ``windll`` or ``oledll``
in mind and which runs under Windows, should run just fine with zugbruecke.

.. code:: python

	from zugbruecke import windll, c_float

	simple_demo_routine = windll.LoadLibrary('demo_dll.dll').simple_demo_routine
	simple_demo_routine.argtypes = [c_float, c_float]
	simple_demo_routine.restype = c_float
	return_value = simple_demo_routine(20.0, 1.07)
	print('Got "%f".' % return_value)

It will print ``Got "1.308412".`` assuming that the corresponding routine in the DLL
looks somewhat like this:

.. code:: c

	float __stdcall __declspec(dllimport) simple_demo_routine(float param_a, float param_b)
	{ return param_a - (param_a / param_b); }

Because of the drop-in replacement design of zugbruecke, it is possible to write
Python code which works under both Unices and Windows.

.. code:: python

	from sys import platform
	if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:
		from zugbruecke import cdll
	elif platform.startswith('win'):
		from ctypes import cdll
	else:
		# Handle unsupported platforms

For more examples check the ``examples`` directory.
For the DLL source code check the ``demo_dll`` directory.

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

For the corresponding DLL source code (written in C) check the ``demo_dll`` directory.
For the corresponding Python code check the ``examples`` directory.

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
parameters, which can either be passed into or picked up from a configuration file
by the session constructor. It is also possible to change parameters during run-time.

If you want to increase the log level during run-time, you can do the following:

.. code:: python

	import zugbruecke
	# work with zugbruecke
	zugbruecke.current_session.set_parameter({'log_level': 10})
	# proceed as usual - with a lot more verbosity

Alternatively, you can drop a configuration file named ``.zugbruecke.json`` into
your current working directory or zugbruecke's configuration directory (likely
``~/.zugbruecke``) and add configuration parameters to it like
``{"log_level": 10, "logwrite": true}``.

The higher the log level, the more output you will get. Default is 0 for no logs.
The on-screen log is color-coded for readability. The log can also, in addition,
be written to disk, where every log item with plenty of meta data is represented
as a one-line JSON object for easy parsing and analysis of larger log files.

Have a look into the routine ``get_default_config`` in ``src/zugbruecke/config.py`` for
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

During every import, zugbruecke starts the Windows Python interpreter on top of Wine.
It is used to run a server script named ``_server_.py``, located in the module's folder.

zugbruecke offers everything ctypes would on the Unix system it is running on
plus everything ctypes would offer if it was imported under Windows. Functions
and classes, which have a platform-specific behavior, are replaced with dispatchers.
The dispatchers decide whether the Unix or the Windows behavior should be used
depending on the context of how they were invoked and what parameters where passed
into them. If Windows specific behavior is chosen, calls are passed from
zugbruecke's client code running on Unix to the server component of zugbruecke
running on Wine.

Is it secure?
-------------

No. See "Security" section of this document.

How fast/slow is it?
--------------------

It performs reasonably well. See "Speed" section of this document.

Can it handle structures?
-------------------------

Yes, in principle. Though, limitations apply. See next question for details.

Can it handle pointers?
-----------------------

Yes and no.

Pointers to simple C data types (int, float, etc.) used as function
parameters or within structures can be handled just fine.

Pointers to arbitrary data structures can be handled if another parameter of
the call contains the length of the memory section the pointer is pointing to.
zugbruecke uses a special ``memsync`` protocol for indicating which memory
sections must be kept in sync between the Unix and the Wine side of the code.
If run on Windows, the regular ``ctypes`` will just ignore any ``memsync``
directive in the code.

Pointers returned by a DLL pointing to memory allocated by the DLL are
currently not handled. Null-terminated strings are not handled yet, too.

Is it thread-safe?
------------------

Probably (yes). More extensive tests are required.

If you want to be on the safe side, start one zugbruecke session per thread
in your code manually. You can do this as follows:

.. code:: python

	from zugbruecke import session
	# start new thread - then, inside, do:
	a = session()
	# now you can do stuff like
	kernel32 = a.load_library(
		'kernel32', 'cdll', {'mode': 0, 'use_errno': False, 'use_last_error': False}
		)
	# do not forget to terminate the session (i.e. the Windows Python interpreter)
	a.terminate()

Missing features (for better ctypes compatibility)
==================================================

The following features have yet not been added to zugbruecke:

- Two (important) Windows data types: ``HRESULT`` and ``VARIANT_BOOL``
- Function prototyping with ``CFUNCTYPE`` and ``WINFUNCTYPE``
- COM: ``DllCanUnloadNow`` and ``DllGetClassObject``

All the above routines and classes can in fact be imported from zugbruecke
for compatibility with ctypes, but they are stubs only.

To do (target: BETA-status)
===========================

The following issues need to be resolved before 'Development Status :: 4 - Beta'
can be achieved:

- A test-suite covering all features must be developed.
- Structures and pointers should be handled more appropriately.
  Especially, structures should be passed in a better way.
- The log should be divided into log-levels with more or less details.
  Higher log-levels should contain details of the current stack frame
  such as line number or calling routine (based on ``inspect``).
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
