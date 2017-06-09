**pycrosscall** - Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD

Synopsis
========

**pycrosscall** is an EXPERIMENTAL **Python module**.
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


*About Wine: Wine (originally an acronym for "Wine Is Not an Emulator") is a compatibility layer
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

A stand-alone Windows-version of the CPython interpreter corresponding to the
used Unix-version is automatically downloaded during the installation of pycrosscall.
