Changes
=======

0.0.5 (2017-11-13)
------------------

* Added support for light-weight pointers (``ctypes.byref``)
* FIX: Elements within structures are properly synchronized even if they are not a pointer on their own.
* FIX: Structure objects in arrays of structures are properly initialized.
* FIX: Links in README.rst work when rendered on PyPI.

0.0.4 (2017-11-05)
------------------

* Implemented full support for multidimensional fixed length arrays

0.0.3 (2017-11-02)
------------------

* Implemented fixed length 1D arrays
* Refactored argument packing and unpacking code
* Plenty of cleanups based on static code analysis
* Introduced ``Python``'s ``any`` functions in a number of places
* Fixed lots of typos and grammar issues in documentation

0.0.2 (2017-07-28)
------------------

* Added and confirmed CPython 3.4 compatibility
* Added installation instructions to documentation

0.0.1 (2017-07-28)
------------------

* First official (pre-) release of *zugbruecke*
