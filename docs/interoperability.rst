:github_url:

.. _interoperability:

.. index::
	single: winepath
	pair: platform; interoperability
	statement: zugbruecke.wine.path_unix_to_wine
	statement: zugbruecke.wine.path_wine_to_unix
	module: zugbruecke.wine

Platform interoperability
=========================

Leveraging the features of *Wine*, *zugbruecke* tries to make things as easy
as possible for the user. Some issues remain, though, which must be handled
manually by the user. *zugbruecke* offers special APIs for this purpose.

Module: ``zugbruecke.ctypes.wine``
----------------------------------

Method: ``path_unix_to_wine``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parameters:

* ``path_in`` (str)

Return value

* ``path_out`` (str)

Converts an absolute or relative *Unix* path into a *Windows* path. It does
not check, whether the path actually exists or not. It uses *Wine*'s internal
implementation for path conversion.

Method: ``path_wine_to_unix``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parameters:

* ``path_in`` (str)

Return value

* ``path_out`` (str)

Converts an absolute or relative *Windows* path into a *Unix* path. It does
not check, whether the path actually exists or not. It uses *Wine*'s internal
implementation for path conversion.
