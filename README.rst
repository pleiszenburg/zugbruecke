**pycrosscall** - Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD

Synopsis
========

The **pycrosscall** Python module allows you to call routines in Windows DLLs on
Unices / Unix-like systems like Linux, MacOS or BSD.

System requirements
===================

For using the module:

- Wine 2.x *(tested with 2.6 and 2.6-staging)*

For testing, in addition:

- mingw cross-compiler *(for building DLLs against which tests can be run)*

pycrosscall is written using **Python 3 syntax**.
It is known to work with and targeted at **CPython 3** *(tested with 3.5 and 3.6)*.
A corresponding stand-alone Windows version of the CPython interpreter is
automatically downloaded during the installation of pycrosscall.
No additional Python packages are required on either side.
