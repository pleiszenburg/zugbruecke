**pycrosscall** - Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD

Synopsis
========

The **pycrosscall** Python module allows you to call routines in Windows DLLs on
Unices / Unix-like systems like Linux, MacOS or BSD.

System requirements
===================

For using the module:
* Wine 2.x *(tested with 2.6 and 2.6-staging)*

For testing, in addition:
* mingw cross-compiler *(for building DLLs against which tests can be run)*

pycrosscall uses **Python 3** syntax.
It is known to work with and targeted at **CPython 3** *(tested with .5.x and .6.x)*.
No additional Python packages are required.
