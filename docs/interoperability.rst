:github_url:

.. _interoperability:

.. index::
	single: winepath
	pair: platform; interoperability
	statement: zugbruecke.ctypes.zb_path_unix_to_wine
	statement: zugbruecke.ctypes.zb_path_wine_to_unix

Platform Interoperability
=========================

Leveraging the features of *Wine*, *zugbruecke* tries to make things as easy as possible for the user. Some issues remain though, such as converting between *Unix* and *Wine* paths, which must be handled manually by the user. *zugbruecke* offers special APIs for this purpose:

- :meth:`zugbruecke.CtypesSession.zb_path_unix_to_wine`
- :meth:`zugbruecke.CtypesSession.zb_path_wine_to_unix`
