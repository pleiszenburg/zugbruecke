
.. |build_master| image:: https://img.shields.io/travis/pleiszenburg/zugbruecke/master.svg?style=flat-square
	:target: https://travis-ci.org/pleiszenburg/zugbruecke
	:alt: Build Status: master / release

.. |docs_master| image:: https://readthedocs.org/projects/zugbruecke/badge/?version=latest&style=flat-square
	:target: http://zugbruecke.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status: master / release

.. |build_develop| image:: https://img.shields.io/travis/pleiszenburg/zugbruecke/develop.svg?style=flat-square
	:target: https://travis-ci.org/pleiszenburg/zugbruecke
	:alt: Build Status: development branch

.. |docs_develop| image:: https://readthedocs.org/projects/zugbruecke/badge/?version=develop&style=flat-square
	:target: http://zugbruecke.readthedocs.io/en/develop/?badge=develop
	:alt: Documentation Status: development branch

.. |license| image:: https://img.shields.io/pypi/l/zugbruecke.svg?style=flat-square
	:target: https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE
	:alt: Project License: LGPLv2

.. |status| image:: https://img.shields.io/pypi/status/zugbruecke.svg?style=flat-square
	:target: https://github.com/pleiszenburg/zugbruecke/milestone/1
	:alt: Project Development Status

.. |pypi_version| image:: https://img.shields.io/pypi/v/zugbruecke.svg?style=flat-square
	:target: https://pypi.python.org/pypi/zugbruecke
	:alt: Available on PyPi - the Python Package Index

.. |pypi_versions| image:: https://img.shields.io/pypi/pyversions/zugbruecke.svg?style=flat-square
	:target: https://pypi.python.org/pypi/zugbruecke
	:alt: Available on PyPi - the Python Package Index

.. |zugbruecke_logo| image:: http://www.pleiszenburg.de/zugbruecke_logo.png
	:target: https://github.com/pleiszenburg/zugbruecke
	:alt: zugbruecke repository

|build_master| |docs_master| |build_develop| |docs_develop| |license| |status| |pypi_version| |pypi_versions|

|zugbruecke_logo|

Synopsis
========

**zugbruecke** is an EXPERIMENTAL **Python module** (currently in development **status 3/alpha**).
It allows to **call routines in Windows DLLs from Python code running on
Unices / Unix-like systems** such as Linux, MacOS or BSD.
zugbruecke is designed as a **drop-in replacement for Python's standard library's ctypes module**.
zugbruecke is **built on top of Wine**. A stand-alone Windows Python interpreter
launched in the background is used to execute the called DLL routines.
Communication between the Unix-side and the Windows/Wine-side is based on Python's
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

.. _winehq.org: https://www.winehq.org/

Prerequisites
=============

+--------------------+-------------------------------------------------------------------------------------------------------------+
| for usage          + - `CPython`_ 3.x (tested with 3.{4,5,6}) - no additional Python packages required                           +
|                    + - `Wine`_ 2.x (tested with 2.{5 to 19} regular & `staging`_) - expected to be in the user's `PATH`_         +
+--------------------+-------------------------------------------------------------------------------------------------------------+
| for tests          + - `pytest`_                                                                                                 +
|                    + - `mingw cross-compiler`_ - for building DLLs against which examples and tests can be run                   +
+--------------------+-------------------------------------------------------------------------------------------------------------+
| for documentation  + - `Sphinx`_                                                                                                 +
+--------------------+-------------------------------------------------------------------------------------------------------------+

.. _CPython: https://www.python.org/
.. _Wine: https://www.winehq.org/
.. _staging: https://wine-staging.com/
.. _PATH: https://en.wikipedia.org/wiki/PATH_(variable)
.. _pytest: https://www.pytest.org/
.. _mingw cross-compiler: http://mxe.cc
.. _Sphinx: http://www.sphinx-doc.org/

Installation
============

+--------------------+--------------------------------------------------------------------------+
| master / release   + .. code:: bash                                                           +
|                    +                                                                          +
| |build_master|     +  pip install zugbruecke                                                  +
+--------------------+--------------------------------------------------------------------------+
| development branch + .. code:: bash                                                           +
|                    +                                                                          +
| |build_develop|    +  pip install git+https://github.com/pleiszenburg/zugbruecke.git@develop  +
+--------------------+--------------------------------------------------------------------------+

Examples
========

Start an interactive Python session under Unix and try the following:

.. code:: python

	from zugbruecke import cdll, c_double
	dll_pow = cdll.msvcrt.pow
	dll_pow.argtypes = (c_double, c_double)
	dll_pow.restype = c_double
	print('You should expect "1024.0" to show up here: "%.1f".' % dll_pow(2.0, 10.0))

You have just witnessed ``msvcrt.dll`` in action on Unix. Interested in more?
Check the `examples`_ in zugbruecke's documentation or read `ctypes' documentation`_.

A lot of code, which was written with ``ctypes``' ``cdll``, ``windll`` or ``oledll``
in mind and which runs under Windows, should run just fine with zugbruecke
on Unix (assuming it does not use Windows features not supported by Wine).

.. _examples: http://zugbruecke.readthedocs.io/en/stable/examples.html
.. _ctypes' documentation: https://docs.python.org/3/library/ctypes.html

Speed
=====

zugbruecke performs reasonably well given its complexity with **less than 0.2 µs
overhead per call** in average on modern hardware. It is not (yet) optimized for
speed. Check the latest `benchmarks`_ for more details.

.. _benchmarks: http://zugbruecke.readthedocs.io/en/stable/benchmarks.html

Security
========

zugbruecke is **notoriously insecure**. Never, ever, run it with
root / super users privileges! Do not use it where security matters!
For details, check the section on `security`_ in the documentation.

.. _security: http://zugbruecke.readthedocs.io/en/stable/security.html

Need help?
==========

Feel free to post questions in the `GitHub issue tracker`_ of this project.

.. _question: https://github.com/pleiszenburg/zugbruecke/labels/question

Bugs & issues
=============

- Report bugs in zugbruecke here: `GitHub issue tracker`_
- Report bugs in ctypes here: `Python tracker`_
- Report bug in Wine here: `WineHQ Bug Tracking System`_

Make sure you have read the chapter on `bugs`_ in zugbruecke's documentation.

.. _GitHub issue tracker: https://github.com/pleiszenburg/zugbruecke/issues
.. _Python tracker: https://bugs.python.org/
.. _WineHQ Bug Tracking System: https://bugs.winehq.org/
.. _bugs: http://zugbruecke.readthedocs.io/en/stable/bugs.html

Miscellaneous
=============

- Full project documentation

  - at `Read the Docs`_
  - at `zugbruecke repository`_

- `License`_ (**LGPL v2.1**)
- `Contributing`_ (**Contributions are highly welcomed!**)
- `FAQ`_
- `Authors`_
- `Changes`_
- `Missing features`_ (for full ctypes compatibility)
- `Long-term ideas`_
- `Upstream issues`_ (relevant bugs in dependencies)

.. _Read the Docs: http://zugbruecke.readthedocs.io/en/latest/
.. _zugbruecke repository: docs/index.rst
.. _License: https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE
.. _Contributing: https://github.com/pleiszenburg/zugbruecke/blob/master/CONTRIBUTING.rst
.. _FAQ: http://zugbruecke.readthedocs.io/en/stable/faq.html
.. _Authors: https://github.com/pleiszenburg/zugbruecke/blob/master/AUTHORS.rst
.. _Changes: https://github.com/pleiszenburg/zugbruecke/blob/master/CHANGES.rst
.. _Missing features: https://github.com/pleiszenburg/zugbruecke/issues?q=is%3Aissue+is%3Aopen+label%3A%22missing+ctypes+feature%22
.. _Long-term ideas: https://github.com/pleiszenburg/zugbruecke/milestone/2
.. _Upstream issues: https://github.com/pleiszenburg/zugbruecke/issues?q=is%3Aissue+is%3Aopen+label%3Aupstream

For production environments
===========================

**DO NOT run this code (as-is) in production environments unless you feel that you
really know what you are doing or unless you are absolutely desperate!
Being experimental in nature and of alpha quality, it is prone to fail
in a number of unpredictable ways, some of which might not be obvious or might
not even show any (intermediately) recognizable symptoms at all!
You might end up with plain wrong, nonsensical results without noticing it!**
