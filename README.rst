
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

About Wine (from `winehq.org`_): *Wine (originally an acronym
for "Wine Is Not an Emulator") is a compatibility layer
capable of running Windows applications on several POSIX-compliant operating systems,
such as Linux, MacOS and BSD. Instead of simulating internal Windows logic like a
virtual machine or emulator, Wine translates Windows API calls into POSIX calls
on-the-fly, eliminating the performance and memory penalties of other methods and
allowing you to cleanly integrate Windows applications into your desktop.*

**This project is NEITHER associated NOR affiliated in any way or form with the Wine project.**

.. _About Wine, from winehq.org: https://www.winehq.org/

Prerequisites
=============

- `CPython`_ 3.x (tested with 3.{5,6}) - No additional Python packages are required.
- `Wine`_ 2.x (tested with 2.{5,6,10,12} regular & `staging`_) - Expected to be in the user's `PATH`_.

For examples and tests, in addition:

- `pytest`_
- `mingw cross-compiler`_ - for building DLLs against which examples and tests can be run

For building the documentation:

- `Sphinx`_

.. _CPython: https://www.python.org/
.. _Wine: https://www.winehq.org/
.. _staging: https://wine-staging.com/
.. _PATH: https://en.wikipedia.org/wiki/PATH_(variable)
.. _pytest: https://www.pytest.org/
.. _mingw cross-compiler: http://mxe.cc
.. _Sphinx: http://www.sphinx-doc.org/

Installation
============

For the latest "stable" (working) **release** run:

.. code:: bash

	pip install zugbruecke

For the latest **development snapshot** (likely broken) run:

.. code:: bash

	pip install git+git://github.com/pleiszenburg/zugbruecke.git@develop

Examples
========

zugbruecke is a drop-in replacement for ctypes.

A lot of code, which was written with ``cdll``, ``windll`` or ``oledll``
in mind and which runs under Windows, should run just fine with zugbruecke
on Unix (assuming it does not use Windows features not supported by Wine).
Start an interactive Python session under Unix and try the following:

.. code:: python

	from zugbruecke import cdll, c_double

	dll_pow = cdll.msvcrt.pow
	dll_pow.argtypes = (c_double, c_double)
	dll_pow.restype = c_double
	print('You should expect "1024.0" to show up here: "%.1f".' % dll_pow(2.0, 10.0))

You have just witnessed ``msvcrt.dll`` in action on Unix. Interested in more?
Check the `examples`_ in zugbruecke's documentation or read `ctypes' documentation`_.

.. _examples: docs/examples.rst
.. _ctypes' documentation: https://docs.python.org/3/library/ctypes.html

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

**Contributions are highly welcomed!** See `CONTRIBUTING`_ for details.

.. _CONTRIBUTING: CONTRIBUTING.rst

Bugs & issues
=============

- `zugbruecke's GitHub issue tracker`_
- `Wine's WineHQ Bug Tracking System`_

Make sure you have read the chapter on `bugs`_ in zugbruecke's documentation.

.. _zugbruecke's GitHub issue tracker: https://github.com/pleiszenburg/zugbruecke/issues
.. _Wine's WineHQ Bug Tracking System: https://bugs.winehq.org/
.. _bugs: docs/bugs.rst

Miscellaneous
=============

- `FAQ`_

.. _FAQ: docs/faq.rst

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
