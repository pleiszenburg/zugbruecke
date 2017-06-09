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
associate with both itself and with Wine.

*About Wine: Wine (originally an acronym for "Wine Is Not an Emulator") is a compatibility layer
capable of running Windows applications on several POSIX-compliant operating systems,
such as Linux, MacOS and BSD. Instead of simulating internal Windows logic like a
virtual machine or emulator, Wine translates Windows API calls into POSIX calls
on-the-fly, eliminating the performance and memory penalties of other methods and
allowing you to cleanly integrate Windows applications into your desktop.*

*For more details go to: https://www.winehq.org/*

***This project is NEITHER associated NOR affiliated in any way or form with the Wine project.***

System requirements
===================

For using the module:

- Wine 2.x *(tested with 2.6 and 2.6-staging)*

For examples and testing, in addition:

- mingw cross-compiler *(for building DLLs against which examples and tests can be run)*

pycrosscall is written using **Python 3 syntax**.
It is known to work with and targeted at **CPython 3** *(tested with 3.5 and 3.6)*.
A corresponding stand-alone Windows-version of the CPython interpreter is
automatically downloaded during the installation of pycrosscall.
No additional Python packages are required on either side.
