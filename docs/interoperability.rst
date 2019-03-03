:github_url:

.. _interoperability:

.. index::
	single: winepath
	pair: platform; interoperability
	statement: zugbruecke.ctypes._zb_path_unix_to_wine
	statement: zugbruecke.ctypes._zb_path_wine_to_unix

Platform interoperability
=========================

Leveraging the features of *Wine*, *zugbruecke* tries to make things as easy as possible for the user. Some issues remain, though, which must be handled manually by the user. *zugbruecke* offers special APIs for this purpose.

Method: ``_zb_path_unix_to_wine``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This method can either be called through the default session, ``zugbruecke.ctypes._zb_path_unix_to_wine``, or as a method of a custom session, e.g. ``zugbruecke.ctypes_session()._zb_path_unix_to_wine``

Parameters:

* ``path_in`` (str)

Return value

* ``path_out`` (str)

Converts an absolute or relative *Unix* path into a *Windows* path. It does not check, whether the path actually exists or not. It uses *Wine*'s internal implementation for path conversion.

Method: ``_zb_path_wine_to_unix``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This method can either be called through the default session, ``zugbruecke.ctypes._zb_path_wine_to_unix``, or as a method of a custom session, e.g. ``zugbruecke.ctypes_session()._zb_path_wine_to_unix``

Parameters:

* ``path_in`` (str)

Return value

* ``path_out`` (str)

Converts an absolute or relative *Windows* path into a *Unix* path. It does not check, whether the path actually exists or not. It uses *Wine*'s internal implementation for path conversion.
